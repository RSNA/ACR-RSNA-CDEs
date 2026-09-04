#!/usr/bin/env python3
"""Validate the OKF knowledge bundle: frontmatter, links, section refs, index
coverage, markdown sanity, diagram freshness, and a leak sweep.

Run from the repo root:  python3 docs/check_bundle.py
Exit status is non-zero on any ERROR (warnings do not fail the run).
"""
import os, re, sys, glob, json, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BUNDLE_DIRS = ["docs/next-gen-schema", "notes"]
errors, warnings = [], []
def err(msg): errors.append(msg)
def warn(msg): warnings.append(msg)

def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def frontmatter(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    return m.group(1) if m else None

try:
    import yaml
    def parse_fm(s): return yaml.safe_load(s)
except ImportError:
    yaml = None
    def parse_fm(s):
        # structural fallback: top-level keys + balanced quotes/brackets per line
        d = {}
        for line in s.split("\n"):
            if line.count('"') % 2 or line.count("{") != line.count("}") or line.count("[") != line.count("]"):
                raise ValueError(f"unbalanced: {line!r}")
            m = re.match(r'^([A-Za-z_]\w*):\s*(.*)$', line)
            if m: d[m.group(1)] = m.group(2)
        return d

# ---------------------------------------------------------------- collect files
RESERVED = {"index.md", "log.md"}          # OKF §3: reserved filenames, not concept documents
md_files = ["index.md"] + sorted(f for d in BUNDLE_DIRS for f in glob.glob(os.path.join(d, "**", "*.md"), recursive=True))
concepts = [f for f in md_files if os.path.basename(f) not in RESERVED]
indexes  = [f for f in md_files if os.path.basename(f) == "index.md"]
logs     = [f for f in md_files if os.path.basename(f) == "log.md"]
headings = {}   # file -> set of numbered headings like "2.6.3"
descs    = {}   # file -> frontmatter description

# ---------------------------------------------------------------- 1. frontmatter
for f in md_files:
    text = read(f); fm = frontmatter(text); is_index = f in indexes
    if f in logs:
        if fm is not None: err(f"{f}: log.md must not carry frontmatter (OKF §9)")
        if not re.search(r'^## \d{4}-\d{2}-\d{2}', text, re.M): err(f"{f}: log.md needs date headings (## YYYY-MM-DD)")
        continue
    if is_index:
        if f == "index.md":
            if fm is None: err(f"{f}: bundle-root index should declare okf_version")
            else:
                try: keys = set(parse_fm(fm))
                except Exception as e: err(f"{f}: frontmatter unparseable: {e}"); keys = set()
                if keys != {"okf_version"}: err(f"{f}: root index frontmatter must contain only okf_version, has {sorted(keys)}")
        elif fm is not None:
            err(f"{f}: non-root index.md must not carry frontmatter (OKF §8)")
        continue
    if fm is None:
        err(f"{f}: missing frontmatter"); continue
    try: data = parse_fm(fm)
    except Exception as e: err(f"{f}: frontmatter unparseable: {e}"); continue
    if not data.get("type"): err(f"{f}: frontmatter has no `type` (OKF's one required key)")
    for k in ("title", "description"):
        if not data.get(k): warn(f"{f}: frontmatter lacks `{k}`")
    descs[f] = str(data.get("description", "")).strip().strip('"')
    if yaml and isinstance(data.get("sources"), list):
        for s in data["sources"]:
            if isinstance(s, dict) and not s.get("resource"): err(f"{f}: a `sources` entry has no `resource`")

# ---------------------------------------------------------------- 2. headings, fences
for f in md_files:
    text = read(f)
    headings[f] = set(re.findall(r'^#{2,4}\s+(\d+(?:\.\d+)*)[.\s]', text, re.M))
    if text.count("```") % 2: err(f"{f}: unbalanced ``` code fence")
    body = re.sub(r'```.*?```', '', text, flags=re.S)
    for m in re.finditer(r'^(#+)\s*$', body, re.M): err(f"{f}: empty heading")

# ---------------------------------------------------------------- 3. links + section refs
doc_alias = {"00": "docs/next-gen-schema/00-current-understanding.md",
             "01": "docs/next-gen-schema/01-what-the-vocabulary-must-express.md",
             "02": "docs/next-gen-schema/02-review-questions.md",
             "03": "docs/next-gen-schema/03-draft-structures.md",
             "04": "docs/next-gen-schema/04-anatomy-gaps.md",
             "05": "docs/next-gen-schema/05-radlex-baseline.md",
             "06": "docs/next-gen-schema/06-next-steps.md",
             "07": "docs/next-gen-schema/07-relationship-family.md",
             "08": "docs/next-gen-schema/08-worked-examples.md",
             "09": "docs/next-gen-schema/09-mat-and-tree.md",
             "10": "docs/next-gen-schema/10-decision-record-2026-09-02.md"}
for f in md_files:
    text = read(f)
    body = re.sub(r'```.*?```', '', text, flags=re.S)
    for m in re.finditer(r'\]\(([^)]+)\)', body):
        tgt = m.group(1).strip().split(" ")[0]
        if re.match(r'^(https?:|mailto:|#)', tgt): continue
        path = tgt.split("#")[0]
        if not path: continue
        resolved = os.path.normpath(os.path.join(ROOT, path.lstrip("/"))) if path.startswith("/") \
                   else os.path.normpath(os.path.join(ROOT, os.path.dirname(f), path))
        if not os.path.exists(resolved): err(f"{f}: broken link -> {tgt}")
    # cross-doc section refs like [00 §2.6.3] or [01 §3.1, §4]
    for m in re.finditer(r'\[(0[0-9]|10)[ ,]+§([\d.]+)', body):
        target = doc_alias[m.group(1)]
        if m.group(2).rstrip(".") not in headings.get(target, set()):
            err(f"{f}: section ref [{m.group(1)} §{m.group(2)}] has no heading in {os.path.basename(target)}")
    # intra-doc refs: §N.N not on a line that is a cross-doc ref
    if f in doc_alias.values():
        for line in body.split("\n"):
            if re.search(r'\[[^\]]*§', line): continue   # any bracketed ref ([00 §2], [exchange §1.2]) is not an intra-doc ref
            for r in re.findall(r'§(\d+\.\d+(?:\.\d+)?)', line):
                if r not in headings[f]: err(f"{f}: intra-doc ref §{r} has no such heading")

# ---------------------------------------------------------------- 4. index coverage
for idx in indexes:
    d = os.path.dirname(idx) or "."
    text = read(idx)
    listed = {}
    for m in re.finditer(r'^\*\s+\[([^\]]+)\]\(([^)]+)\)\s*-\s*(.*)$', text, re.M):
        listed[os.path.normpath(os.path.join(d, m.group(2)))] = (m.group(1), m.group(3).strip())
    for p, (title, desc) in listed.items():
        if not os.path.exists(os.path.join(ROOT, p)): err(f"{idx}: entry '{title}' points at missing {p}")
    # every concept in this directory must be listed
    for c in concepts:
        if os.path.dirname(c) == d and os.path.normpath(c) not in listed:
            err(f"{idx}: concept {os.path.basename(c)} is not listed")
    # description should match frontmatter description (OKF §8 SHOULD)
    for p, (title, desc) in listed.items():
        if p in descs and desc and descs[p] and desc != descs[p]:
            warn(f"{idx}: description for {os.path.basename(p)} differs from its frontmatter")
# subdirectories with concepts must appear in the root index
root_text = read("index.md")
for d in BUNDLE_DIRS:
    if f"({d}/)" not in root_text and f"({d})" not in root_text:
        err(f"index.md: bundle directory {d}/ is not listed")

# ---------------------------------------------------------------- 5. diagrams in sync with specs
tool_n = os.path.join(ROOT, "docs/next-gen-schema/tools/render_neighborhood.py")
tool_c = os.path.join(ROOT, "docs/next-gen-schema/tools/render_cards.py")
tool_r = os.path.join(ROOT, "docs/next-gen-schema/tools/render_report.py")
spec_map = {"examples/pulmonary-nodule.neighborhood.json": (tool_n, "diagrams/fc-neighborhood.svg"),
            "examples/thyroid-nodule.neighborhood.json": (tool_n, "diagrams/thyroid-neighborhood.svg"),
            "examples/presence.element.json": (tool_n, "diagrams/de-presence.svg"),
            "examples/severity.element.json": (tool_n, "diagrams/de-severity.svg"),
            "examples/size-mean-diameter.element.json": (tool_n, "diagrams/de-size-mean-diameter.svg"),
            "examples/common-bile-duct.location.json": (tool_n, "diagrams/al-common-bile-duct.svg"),
            "examples/pleural-effusion.mat.json": (tool_c, "diagrams/mat-pleural-effusion.svg"),
            "examples/acute-pyelonephritis.mat.json": (tool_c, "diagrams/mat-acute-pyelonephritis.svg"),
            "examples/pleural-abnormality.tree.json": (tool_c, "diagrams/tree-pleural-abnormality.svg"),
            "examples/renal-abnormality.tree.json": (tool_c, "diagrams/tree-renal-abnormality.svg"),
            "examples/pyelonephritis.report.jsonl": (tool_r, "diagrams/report-pyelonephritis.svg")}
base = os.path.join(ROOT, "docs/next-gen-schema")
# the canonical graph: valid, and every file byte-exact in canonical order
gcheck = subprocess.run([sys.executable, os.path.join(base, "tools/graph.py"), "check"], capture_output=True)
if gcheck.returncode:
    for line in gcheck.stdout.decode("utf-8", errors="replace").splitlines():
        if line.startswith(("ERROR", "NOT CANONICAL")): err(f"graph: {line}")
    if not gcheck.stdout.strip(): err(f"graph check failed: {gcheck.stderr.decode('utf-8', errors='replace')[:200]}")
for spec, (tool, svg) in spec_map.items():
    sp, sv = os.path.join(base, spec), os.path.join(base, svg)
    if not os.path.exists(sp): err(f"missing spec {spec}"); continue
    if not os.path.exists(sv): err(f"missing diagram {svg}"); continue
    out = subprocess.run([sys.executable, tool, sp], capture_output=True)
    if out.returncode: err(f"renderer failed on {spec}: {out.stderr.decode('utf-8', errors='replace').strip()[:200]}"); continue
    if out.stdout != open(sv, "rb").read(): err(f"{svg} is stale — regenerate from {spec}")
# every svg referenced from a doc must exist (covered by link check) and every diagram file must be referenced
referenced = set()
for f in md_files:
    for m in re.finditer(r'\]\((diagrams/[^)]+\.svg)\)', read(f)): referenced.add(m.group(1))
for svg in glob.glob(os.path.join(base, "diagrams/*.svg")):
    rel = "diagrams/" + os.path.basename(svg)
    if rel not in referenced: warn(f"{rel} is not referenced from any document")

# ---------------------------------------------------------------- 6. leak sweep
email = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
deny_path = os.path.join(ROOT, "raw_sources", "denylist.txt")     # gitignored; one term per line
deny = [l.strip() for l in open(deny_path)] if os.path.exists(deny_path) else []
deny = [d for d in deny if d and not d.startswith("#")]
for f in md_files:
    text = read(f)
    for m in email.finditer(text): err(f"{f}: email address present: {m.group(0)}")
    low = text.lower()
    for term in deny:
        if term.lower() in low: err(f"{f}: denylisted term present: {term!r}")
tracked = subprocess.run(["git", "ls-files", "raw_sources", ".preview", "docs/next-gen-schema/.preview"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
if tracked: err(f"files tracked inside ignored dirs: {tracked.splitlines()[:3]}")
if not deny: warn("no raw_sources/denylist.txt — name sweep skipped (emails still checked)")

# ---------------------------------------------------------------- report
for w in warnings: print(f"WARN  {w}")
for e in errors:   print(f"ERROR {e}")
print(f"\n{len(md_files)} documents · {len(spec_map)} diagrams · {len(errors)} errors · {len(warnings)} warnings")
sys.exit(1 if errors else 0)
