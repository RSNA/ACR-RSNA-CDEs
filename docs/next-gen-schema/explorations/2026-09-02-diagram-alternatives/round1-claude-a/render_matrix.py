#!/usr/bin/env python3
"""Alternative 2: relationship matrix.

Rows are every class in the view, laid out as the taxonomy tree (indent = descent, so
subsumption reads as the row header, crossing the finding/diagnosis label freely).
Columns are the classes that receive a typed edge. A cell at (row, column) is the edge
row -> column: its kind as a coloured strip and word, typicality as a Harvey ball plus the
word, specificity as diamonds plus the word, the `expected` hint as text. Fan-in becomes a
column with one cell per cause, so nothing can be mis-attributed. See README.md.

Usage: render_matrix.py VIEW.json > out.svg
"""
import json, sys, os, html, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "docs", "next-gen-schema", "tools")))
from graph import load_graph  # noqa: E402

ACCENT = {
    "FindingClass": ("#2563eb", "#1e3a8a", "#eff6ff"),
    "Diagnosis":    ("#7c3aed", "#4c1d95", "#f5f3ff"),
    "Grouping":     ("#64748b", "#334155", "#f8fafc"),
}
ELEM, ANAT = ("#16a34a", "#14532d", "#f0fdf4"), ("#d97706", "#78350f", "#fffbeb")
INK, MUTED, RULE, STRIPE = "#1f2937", "#64748b", "#cbd5e1", "#f8fafc"
EDGE = {"MAY_CAUSE": "#dc2626", "MAY_MANIFEST_AS": "#7c3aed", "MAY_PROGRESS_TO": "#0891b2", "OCCURS_WITH": "#64748b"}
WORD = {"MAY_CAUSE": "causes", "MAY_MANIFEST_AS": "manifests as", "MAY_PROGRESS_TO": "progresses to", "OCCURS_WITH": "occurs with"}
TYPICALITY = ["excluded", "very_rare", "occasional", "frequent", "very_frequent", "obligate"]
SPECIFICITY = {"suggestive": 1, "highly_suggestive": 2, "pathognomonic": 3}
IMPLICIT_ELEMENTS = {"RDE2_000001"}

MARGIN, HEAD_W, COL_W, INDENT, TOP = 24, 316, 104, 16, 56
FS_NAME, FS_SUB, FS_CELL, FS_HINT = 12, 9, 8, 8
_NUM = re.compile(r'-?\d+\.\d+')


def esc(s): return html.escape(str(s), quote=True)
def tw(s, fs, bold=False): return len(s) * fs * (0.62 if bold else 0.55)
def fmt(svg): return _NUM.sub(lambda m: f'{float(m.group()):.1f}'.rstrip("0").rstrip("."), svg)


def wrap(text, fs, width, bold=False):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(t, fs, bold) <= width or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def kind_of(n):
    return {"FindingClass": "finding", "Diagnosis": "diagnosis", "Grouping": "grouping · negative-only"}.get(n["node"], n["node"].lower())


def harvey(cx, cy, r, level, color):
    """A Harvey ball: level 0..5 -> 0, 1/8, 1/4, 1/2, 3/4, 1 filled; 0 gets a slash."""
    frac = [0, 0.125, 0.25, 0.5, 0.75, 1.0][level]
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#ffffff" stroke="{color}" stroke-width="1.2"/>']
    if frac >= 1:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>')
    elif frac > 0:
        a = 2 * math.pi * frac
        x, y = cx + r * math.sin(a), cy - r * math.cos(a)
        out.append(f'<path d="M{cx},{cy} L{cx},{cy - r} A{r},{r} 0 {1 if frac > 0.5 else 0},1 {x},{y} z" fill="{color}"/>')
    else:
        out.append(f'<path d="M{cx - r * 0.7},{cy + r * 0.7} L{cx + r * 0.7},{cy - r * 0.7}" stroke="{color}" stroke-width="1.2"/>')
    return "".join(out)


def diamonds(x, cy, n, color):
    out = []
    for k in range(3):
        cx = x + 5 + k * 10
        fill = color if k < n else "#ffffff"
        out.append(f'<path d="M{cx},{cy - 4.5} L{cx + 4.5},{cy} L{cx},{cy + 4.5} L{cx - 4.5},{cy} z" fill="{fill}" stroke="{color}" stroke-width="1"/>')
    return "".join(out)


def render(g, view):
    ids = list(view["nodes"]); inview = set(ids)
    rel = {n["id"]: n for n in g.nodes.values() if n["node"] == "RelationshipType"}
    parent, children = {}, {i: [] for i in ids}
    for e in g.edges:
        if e["edge"] == "SUBTYPE_OF" and e["from"] in inview and e["to"] in inview and e["from"] not in parent:
            parent[e["from"]] = e["to"]; children[e["to"]].append(e["from"])
    for p in children: children[p].sort(key=ids.index)
    edges = sorted((e for e in g.edges if e["edge"] in EDGE and e["from"] in inview and e["to"] in inview),
                   key=lambda e: (e["edge"], e["from"], e["to"]))
    # row order: family trees, then other imaging classes, then clinical causes (only outgoing MAY_CAUSE)
    roots = [i for i in ids if i not in parent]
    def is_cause(r):
        es = [e for e in edges if r in (e["from"], e["to"])]
        return not children[r] and es and all(e["edge"] == "MAY_CAUSE" and e["from"] == r for e in es)
    family = [r for r in roots if children[r] or g.nodes[r]["node"] == "Grouping"]
    others = [r for r in roots if r not in family and not is_cause(r)]
    causes = [r for r in roots if is_cause(r)]
    rows = []   # (id, depth, section)
    def walk(i, d, sec):
        rows.append((i, d, sec))
        for c in children[i]: walk(c, d + 1, sec)
    for r in family: walk(r, 0, "family")
    for r in others: walk(r, 0, "other")
    for r in causes: walk(r, 0, "cause")
    row_index = {i: k for k, (i, _, _) in enumerate(rows)}
    # columns: every target of a typed edge (both ends for symmetric types), in row order
    targets = set()
    for e in edges:
        targets.add(e["to"])
        if rel[e["edge"]].get("symmetric"): targets.add(e["from"])
    cols = [i for i, _, _ in rows if i in targets]
    col_index = {i: k for k, i in enumerate(cols)}
    # cells
    cells = {}
    for e in edges:
        cells.setdefault((e["from"], e["to"]), []).append((e, False))
        if rel[e["edge"]].get("symmetric"):
            cells.setdefault((e["to"], e["from"]), []).append((e, True))

    # ---- row content
    def elements(i):
        above = set(); p = parent.get(i)
        while p:
            above |= {e["to"] for e in g.out_edges(p) if e["edge"] == "HAS_ELEMENT"}; p = parent.get(p)
        out = []
        for e in g.out_edges(i):
            if e["edge"] != "HAS_ELEMENT" or e["to"] in IMPLICIT_ELEMENTS or e["to"] in above: continue
            el = g.nodes.get(e["to"], {"name": e["to"]}); label = el["name"]
            if e.get("props", {}).get("note"): label += f" · {e['props']['note']}"
            if el.get("units"): label += " (HU)" if el["units"][0] == "[hnsf'U]" else f" ({el['units'][0]})"
            out.append(label)
        for e in g.out_edges(i):
            if e["edge"] == "INTERPRETED_FROM":
                b = g.edge_by_id(e["to"])
                if b: out.append(f"≈ interpreted from {g.nodes[b['to']]['name']} bound to {g.nodes[b['from']]['name']}")
        return out
    def scope(i):
        mine = [e["to"] for e in g.out_edges(i) if e["edge"] == "SCOPED_TO"]
        if not mine: return None
        p = parent.get(i)
        if p and [e["to"] for e in g.out_edges(p) if e["edge"] == "SCOPED_TO"] == mine: return None
        return g.nodes.get(mine[0], {"name": mine[0]})["name"]

    def cell_lines(entries):
        """Height and drawing plan for one cell."""
        plan, h = [], 4
        for e, mirrored in entries:
            p = e.get("props", {})
            plan.append(("kind", e["edge"], mirrored)); h += 11
            if "typicality" in p:
                lines = wrap(p["typicality"].replace("_", " "), FS_CELL, COL_W - 28)
                plan.append(("typ", lines, e["edge"])); h += 14 + 10 * (len(lines) - 1)
            if "specificity" in p:
                lines = wrap(p["specificity"].replace("_", " "), FS_CELL, COL_W - 40)
                plan.append(("spec", (p["specificity"], lines), e["edge"])); h += 14 + 10 * (len(lines) - 1)
            if "expected" in p:
                exp = "; ".join(f"{k} {v}" for k, v in sorted(p["expected"].items(), key=lambda kv: kv[0] != "location"))
                for ln in wrap(exp, FS_HINT, COL_W - 10): plan.append(("hint", ln, e["edge"])); h += 10
            elif p.get("note"):
                for ln in wrap(p["note"], FS_HINT, COL_W - 10): plan.append(("note", ln, e["edge"])); h += 10
        return h + 4, plan

    # ---- measure rows
    row_h, row_plan = {}, {}
    for i, d, sec in rows:
        els = elements(i)
        el_lines = wrap(" · ".join(els), FS_SUB, HEAD_W - 20 - INDENT * d) if els else []
        h = 8 + 14 + 12 + len(el_lines) * 12 + 8
        for c in cols:
            if (i, c) in cells:
                ch, _ = cell_lines(cells[(i, c)]); h = max(h, ch)
        row_h[i] = h; row_plan[i] = el_lines
    # column header height
    col_lines = {c: wrap(g.nodes[c]["name"], 9.5, COL_W - 8, bold=True) for c in cols}
    head_h = 14 + max(len(v) for v in col_lines.values()) * 12 + 10
    sections = [k for k in range(1, len(rows)) if rows[k][2] != rows[k - 1][2]]

    W = MARGIN + HEAD_W + len(cols) * COL_W + MARGIN
    ys, y = {}, TOP + head_h + 6
    for k, (i, d, sec) in enumerate(rows):
        if k in sections: y += 22
        ys[i] = y; y += row_h[i]
    H = y + 62

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="system-ui, sans-serif" role="img" aria-label="{esc(view.get("aria", view.get("title", "")))}">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
    if view.get("title"):
        out.append(f'<text x="{MARGIN}" y="28" font-size="15" font-weight="700" fill="{INK}">{esc(view["title"])}</text>')
    out.append(f'<text x="{MARGIN}" y="{TOP - 8}" font-size="10" letter-spacing="1.2" font-weight="600" fill="{MUTED}">TAXONOMY · INDENTED UNDER ITS PARENT</text>')
    gx = MARGIN + HEAD_W
    out.append(f'<text x="{gx}" y="{TOP - 8}" font-size="10" letter-spacing="1.2" font-weight="600" fill="{MUTED}">READ ACROSS: THE ROW CLASS → THE COLUMN CLASS</text>')
    # column headers
    for k, c in enumerate(cols):
        n = g.nodes[c]; a, dark, bg = ACCENT.get(n["node"], ACCENT["Grouping"])
        x = gx + k * COL_W
        out.append(f'<rect x="{x}" y="{TOP}" width="{COL_W}" height="{head_h}" fill="{bg}"/>'
                   f'<rect x="{x}" y="{TOP + head_h - 3}" width="{COL_W}" height="3" fill="{a}"/>')
        for j, ln in enumerate(col_lines[c]):
            out.append(f'<text x="{x + COL_W / 2}" y="{TOP + 14 + j * 12}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{dark}">{esc(ln)}</text>')
        out.append(f'<text x="{x + COL_W / 2}" y="{TOP + head_h - 7}" text-anchor="middle" font-size="7.5" fill="{MUTED}">{esc(kind_of(n).split(" ·")[0])}</text>')
    # rows
    for k, (i, d, sec) in enumerate(rows):
        n = g.nodes[i]; a, dark, bg = ACCENT.get(n["node"], ACCENT["Grouping"])
        y0, h = ys[i], row_h[i]
        if k in sections:
            label = {"other": "OTHER IMAGING CLASSES IN THE FAMILY", "cause": "CLINICAL CAUSES · NO ELEMENTS OF THEIR OWN"}[sec]
            out.append(f'<line x1="{MARGIN}" y1="{y0 - 12}" x2="{W - MARGIN}" y2="{y0 - 12}" stroke="{RULE}"/>'
                       f'<text x="{MARGIN}" y="{y0 - 3}" font-size="9" letter-spacing="1" font-weight="600" fill="{MUTED}">{label}</text>')
        if k % 2: out.append(f'<rect x="{MARGIN}" y="{y0}" width="{W - 2 * MARGIN}" height="{h}" fill="{STRIPE}"/>')
        out.append(f'<line x1="{MARGIN}" y1="{y0 + h}" x2="{W - MARGIN}" y2="{y0 + h}" stroke="{RULE}" stroke-width="0.6"/>')
        # tree connector from parent
        x = MARGIN + INDENT * d
        if i in parent:
            px = MARGIN + INDENT * (d - 1) + 6
            out.append(f'<path d="M{px},{ys[parent[i]] + row_h[parent[i]]} L{px},{y0 + 16} L{x},{y0 + 16}" fill="none" stroke="{a}" stroke-width="1.2"/>')
        rx = 8 if n["node"] == "Diagnosis" else 2
        dash = ' stroke-dasharray="4 3"' if n["node"] == "Grouping" else ''
        out.append(f'<g data-node="{esc(i)}"><rect x="{x}" y="{y0 + 4}" width="{HEAD_W - x + MARGIN - 6}" height="{h - 8}" rx="{rx}" fill="{bg}" stroke="{a}" stroke-width="1"{dash}/>'
                   f'<rect x="{x}" y="{y0 + 8}" width="4" height="{h - 16}" rx="2" fill="{a}"/>'
                   f'<text x="{x + 12}" y="{y0 + 20}" font-size="{FS_NAME}" font-weight="700" fill="{dark}">{esc(n["name"])}</text>'
                   f'<text x="{x + 12}" y="{y0 + 32}" font-size="{FS_SUB}" fill="{MUTED}">{esc(kind_of(n))} · {esc(i)}</text>')
        for j, ln in enumerate(row_plan[i]):
            out.append(f'<text x="{x + 12}" y="{y0 + 44 + j * 12}" font-size="{FS_SUB}" fill="{ELEM[1]}">{esc(ln)}</text>')
        sc = scope(i)
        if sc:
            lw = tw(sc, FS_SUB) + 12; tx = MARGIN + HEAD_W - 8 - lw
            out.append(f'<rect x="{tx}" y="{y0 + 8}" width="{lw}" height="15" rx="7.5" fill="{ANAT[2]}" stroke="{ANAT[0]}"/>'
                       f'<text x="{tx + lw / 2}" y="{y0 + 19}" text-anchor="middle" font-size="{FS_SUB}" fill="{ANAT[1]}">{esc(sc)}</text>')
        out.append('</g>')
        # cells
        for c in cols:
            cx = gx + col_index[c] * COL_W
            if (i, c) not in cells:
                if i == c: out.append(f'<rect x="{cx + 1}" y="{y0 + 1}" width="{COL_W - 2}" height="{h - 2}" fill="{RULE}" fill-opacity="0.35"/>')
                continue
            ch, plan = cell_lines(cells[(i, c)])
            yy = y0 + 4
            color0 = EDGE[plan[0][1]]
            out.append(f'<rect x="{cx + 2}" y="{y0 + 2}" width="{COL_W - 4}" height="{h - 4}" rx="3" fill="{color0}" fill-opacity="0.07" stroke="{color0}" stroke-width="0.8"/>')
            for item in plan:
                if item[0] == "kind":
                    _, et, mirrored = item; color = EDGE[et]
                    word = WORD[et]
                    out.append(f'<rect x="{cx + 2}" y="{yy}" width="{COL_W - 4}" height="11" fill="{color}"/>'
                               f'<text x="{cx + 7}" y="{yy + 8.5}" font-size="7.5" font-weight="700" letter-spacing="0.6" fill="#ffffff">{esc(word.upper())}</text>')
                    yy += 11
                elif item[0] == "typ":
                    _, lines, et = item; color = EDGE[et]
                    out.append(harvey(cx + 12, yy + 8, 5.5, TYPICALITY.index("_".join(lines).replace(" ", "_")), color))
                    for j, ln in enumerate(lines):
                        out.append(f'<text x="{cx + 22}" y="{yy + 11 + 10 * j}" font-size="{FS_CELL}" fill="{INK}">{esc(ln)}</text>')
                    yy += 14 + 10 * (len(lines) - 1)
                elif item[0] == "spec":
                    _, (v, lines), et = item; color = EDGE[et]
                    out.append(diamonds(cx + 6, yy + 8, SPECIFICITY[v], color))
                    for j, ln in enumerate(lines):
                        out.append(f'<text x="{cx + 38}" y="{yy + 11 + 10 * j}" font-size="{FS_CELL}" fill="{INK}">{esc(ln)}</text>')
                    yy += 14 + 10 * (len(lines) - 1)
                else:
                    _, ln, et = item
                    out.append(f'<text x="{cx + 6}" y="{yy + 9}" font-size="{FS_HINT}" font-style="italic" fill="{EDGE[et] if item[0] == "hint" else MUTED}">{esc(ln)}</text>')
                    yy += 10
    # column rules
    for k in range(len(cols) + 1):
        x = gx + k * COL_W
        out.append(f'<line x1="{x}" y1="{TOP}" x2="{x}" y2="{y}" stroke="{RULE}" stroke-width="0.6"/>')
    # key
    ky = H - 34; kx = MARGIN
    out.append(f'<text x="{kx}" y="{ky + 3}" font-size="9" fill="{MUTED}">typicality</text>'); kx += 52
    for lvl, v in enumerate(TYPICALITY):
        out.append(harvey(kx + 6, ky, 5.5, lvl, INK) + f'<text x="{kx + 15}" y="{ky + 3}" font-size="9" fill="{MUTED}">{esc(v.replace("_", " "))}</text>')
        kx += 20 + tw(v, 9) + 10
    kx += 16
    out.append(f'<text x="{kx}" y="{ky + 3}" font-size="9" fill="{MUTED}">specificity</text>'); kx += 58
    for v, n_ in SPECIFICITY.items():
        out.append(diamonds(kx, ky, n_, INK) + f'<text x="{kx + 34}" y="{ky + 3}" font-size="9" fill="{MUTED}">{esc(v.replace("_", " "))}</text>')
        kx += 40 + tw(v, 9) + 10
    out.append(f'<text x="{MARGIN}" y="{ky + 18}" font-size="9" fill="{MUTED}">An absent glyph means no judgment is recorded. Every class also binds presence. An amber tag is the anatomic scope where it differs from the parent row. Occurs-with is symmetric and is shown in both cells.</text>')
    out.append("</svg>")
    return fmt("".join(out)) + "\n"


if __name__ == "__main__":
    g = load_graph()
    sys.stdout.write(render(g, json.load(open(sys.argv[1], encoding="utf-8"))))
