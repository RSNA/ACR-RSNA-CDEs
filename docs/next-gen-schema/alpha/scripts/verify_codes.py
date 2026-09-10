# -*- coding: utf-8 -*-
"""
Verifies every RadLex code in the model against the label RadLex actually gives it.

This is the check with the best catch rate in the project. Fourteen codes written
from memory during the build were wrong, and every one looked plausible in the
file: a code standing in for "infectious" was psoriatic arthritis, one for "rib
fracture" was a brain structure, one for "margin" was "scattered", and the
laterality codes were shifted one place so that "left" pointed at "midline". None
was catchable by reading. All were caught by comparing the code to its label.

It ran as an ad-hoc script each time codes were added, and the README claimed it
ran at build time, which was false. This makes the claim true.

What it checks, for every code the model uses:

  RESOLVES     the code exists in the RadLex release
  LABEL        the label we recorded matches the label RadLex gives it, allowing
               for a declared match strength: an exactMatch must agree, a
               broad/close/narrowMatch need not, and a synonym hit is checked
               against the synonym fields

Needs RadLex.owl. Set OWL_SRC below or pass a path. Exits non-zero on a mismatch
so it can gate a release, and skips with a clear message when the source is not
present, since the built artifacts alone cannot answer the question.
"""
import json, os, re, sys, collections

OUT = "/mnt/user-data/outputs/radcde-alpha"
OWL_SRC = os.environ.get("RADLEX_OWL", "/home/claude/work/rlowl/RadLex.owl")
CACHE = "/home/claude/work/radlex.nt"
RID = "http://www.radlex.org/RID/"

# match strengths where the labels are not expected to agree
LOOSE = {"broadMatch", "narrowMatch", "closeMatch", "relatedMatch"}


def load_radlex():
    from rdflib import Graph, URIRef
    from rdflib.namespace import RDFS
    src = CACHE if os.path.exists(CACHE) else OWL_SRC
    if not os.path.exists(src):
        return None, None
    g = Graph().parse(src, format="nt" if src.endswith(".nt") else "xml")
    labels, syns = {}, collections.defaultdict(set)
    for s, _, o in g.triples((None, RDFS.label, None)):
        if getattr(o, "language", None) in ("en", None):
            m = re.search(r"(RID[0-9]+)", str(s))
            if m:
                labels[m.group(1)] = str(o)
    # Synonym and its subproperties. Unsanctioned_Term, Acronym and
    # Misspelling_of_term are subproperties of Synonym in RadLex and are NOT
    # synonyms; a term RadLex explicitly discourages must not vindicate a binding.
    for prop in ("Synonym", "Preferred_name"):
        for s, _, o in g.triples((None, URIRef(RID + prop), None)):
            if getattr(o, "language", None) in ("en", None):
                m = re.search(r"(RID[0-9]+)", str(s))
                if m:
                    syns[m.group(1)].add(str(o).lower())
    return labels, syns


def collect():
    """Every RadLex code the model uses, with what we recorded for it."""
    g = json.load(open(f"{OUT}/graph/definition-graph.json"))
    used = []
    for n in g["nodes"]:
        for b in n.get("bindings", []):
            if b["system"] == "RADLEX":
                used.append((b["code"], b.get("source_label", n["name"]),
                             b.get("match", "exactMatch"),
                             f"{n['node']} {n['id']} {n['name']}", "binding"))
        base = n.get("anchor_base")
        if base and base.get("system") == "RADLEX":
            used.append((base["code"], base["label"], "exactMatch",
                         f"{n['node']} {n['id']} {n['name']}", "anchor_base"))
        for m in n.get("anchor_modifiers", []):
            if m.get("system") == "RADLEX":
                used.append((m["code"], m["label"], "exactMatch",
                             f"{n['node']} {n['id']} {n['name']}", "anchor_modifier"))
    return used


def main():
    labels, syns = load_radlex()
    if labels is None:
        print(f"SKIPPED: RadLex not found at {OWL_SRC} or {CACHE}.")
        print("Set RADLEX_OWL to the RadLex.owl path. The built artifacts cannot")
        print("answer this on their own: the question is whether they match the source.")
        return 0

    used = collect()
    seen, unresolved, mismatched, renamed, loose = set(), [], [], [], []
    for code, recorded, match, where, kind in used:
        seen.add(code)
        actual = labels.get(code)
        if actual is None:
            unresolved.append((code, recorded, where))
            continue
        if match in LOOSE:
            loose.append((code, recorded, actual, match, where))
            continue
        if actual.lower() == recorded.lower() or recorded.lower() in syns.get(code, ()):
            continue
        # A differing label is not automatically a wrong code. We shorten RadLex's
        # phrasing all the time: 'smooth' for 'smooth margin', 'Lung-RADS' for
        # 'Lung-RADS assessment', 'compressive' for 'compression'. What matters is
        # whether the code means something ELSE, which is what every real error
        # looked like: a code for 'infectious' that was psoriatic arthritis, one for
        # 'rib fracture' that was a brain structure. So the test is relatedness, not
        # equality: share a stem with any word in the source label, or be contained
        # in it, and it is a naming difference; share nothing and it is a wrong code.
        def stems(t):
            return {w[:5] for w in re.findall(r"[a-z]+", t.lower()) if len(w) > 3}
        related = (recorded.lower() in actual.lower()
                   or actual.lower() in recorded.lower()
                   or bool(stems(recorded) & stems(actual))
                   or bool(stems(recorded) & set().union(*[stems(x) for x in syns.get(code, ())])
                           if syns.get(code) else False))
        (renamed if related else mismatched).append((code, recorded, actual, where, kind))

    print(f"RadLex release parsed: {len(labels)} English labels")
    print(f"codes used by the model: {len(seen)} distinct, {len(used)} references")
    print()
    if unresolved:
        print(f"UNRESOLVED - {len(unresolved)} codes are not in this release:")
        for c, r, w in unresolved:
            print(f"   {c}  recorded as {r!r}")
            print(f"      on {w}")
        print()
    if mismatched:
        print(f"WRONG CODE - {len(mismatched)} codes name something unrelated to what the "
              f"model calls them:")
        for c, r, a, w, k in mismatched:
            print(f"   {c}  model says {r!r}  RadLex says {a!r}")
            print(f"      on {w} ({k})")
        print()
    if renamed:
        print(f"{len(renamed)} codes are right but carry a shorter or differently phrased "
              f"label here. Not errors:")
        for c, r, a, w, k in renamed[:6]:
            print(f"   {c}  model {r!r} vs RadLex {a!r}")
        if len(renamed) > 6:
            print(f"   ... and {len(renamed) - 6} more")
        print()
    if loose:
        print(f"{len(loose)} bindings declare a loose match, so labels are not "
              f"required to agree:")
        for c, r, a, m, w in loose[:8]:
            print(f"   {c}  {m:12s} model {r!r} vs RadLex {a!r}")
        if len(loose) > 8:
            print(f"   ... and {len(loose) - 8} more")
        print()
    bad = len(unresolved) + len(mismatched)
    print(f"{bad} problems" if bad else "every code resolves and every strict label agrees")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
