# -*- coding: utf-8 -*-
"""
Evaluates the definition graph.

Three groups:

  STRUCTURE   generic graph metrics, but only the ones that mean something for a
              definition layer. Degree, components, cycles, depth, tangledness.
  RICHNESS    OntoQA-style ontology metrics: relationship, attribute and
              inheritance richness. Comparable across releases.
  INVARIANTS  claims this model makes about itself. These are the ones that fail
              loudly when something is wrong.

Deliberately NOT computed, because they would produce numbers without meaning
here: clustering coefficient (assumes triadic closure, a definition graph has
almost none by construction), betweenness and eigenvector centrality (dominated
by the anatomy root, which is an artifact of import depth rather than a fact
about the model), diameter (on a mostly-tree hierarchy this is just depth),
assortativity, PageRank. Each is a well-defined number on this graph and none of
them would tell you anything you could act on.

Exit code is non-zero if any invariant fails, so it can gate a build.
"""
import json, sys, collections, datetime
import networkx as nx

OUT = "/mnt/user-data/outputs/radcde-alpha"
HIER = {"SUBTYPE_OF", "IS_A"}
MEREO = {"PART_OF"}

results = []


def record(group, name, value, ok=None, note=""):
    results.append((group, name, value, ok, note))


def load():
    g = json.load(open(f"{OUT}/graph/definition-graph.json"))
    G = nx.MultiDiGraph()
    for n in g["nodes"]:
        G.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
    for e in g["edges"]:
        G.add_edge(e["from"], e["to"], key=e.get("id"), edge=e["edge"], **e.get("props", {}))
    return g, G


def structure(g, G):
    nt = nx.get_node_attributes(G, "node")
    name = nx.get_node_attributes(G, "name")

    record("STRUCTURE", "nodes", G.number_of_nodes())
    record("STRUCTURE", "edges", G.number_of_edges())

    # Orphans split in two, and only one kind is a defect.
    #
    # VOCABULARY types exist to be referenced. An unreferenced etiology or
    # subspecialty is unused vocabulary, which is worth reporting and is not
    # broken. ScopeResolution is referenced only by instances, which live in the
    # OWL, so it is always unreferenced here.
    #
    # STRUCTURAL types have to hang off something. A Measurement or FindingClass
    # nothing points at is either unfinished or dead, and is a defect.
    VOCAB = {"Etiology", "Modality", "Subspecialty", "AssessmentScheme", "ScopeResolution"}
    orphans = [n for n in G if G.degree(n) == 0]
    structural = [n for n in orphans if nt.get(n) not in VOCAB]
    vocab = [n for n in orphans if nt.get(n) in VOCAB]
    record("STRUCTURE", "structural orphans", len(structural), ok=(len(structural) == 0),
           note=", ".join(f"{name.get(o)} [{nt.get(o)}]" for o in structural[:6]))
    record("STRUCTURE", "unreferenced vocabulary", len(vocab),
           note=", ".join(f"{name.get(o)} [{nt.get(o)}]" for o in vocab[:8]))

    # Components, counted over structural nodes only, for the same reason.
    S = G.subgraph([n for n in G if nt.get(n) not in VOCAB])
    comps = list(nx.weakly_connected_components(S))
    sizes = sorted((len(c) for c in comps), reverse=True)
    record("STRUCTURE", "weakly connected components", len(comps),
           ok=(len(comps) == 1), note=f"sizes {sizes[:6]}; vocabulary excluded")
    if len(comps) > 1:
        for c in comps[1:4]:
            record("STRUCTURE", "  detached", len(c),
                   note=", ".join(f"{name.get(x)} [{nt.get(x)}]" for x in list(c)[:5]))

    # cycles in a taxonomy or partonomy are always bugs
    for label, keep in [("taxonomy (SUBTYPE_OF, IS_A)", HIER), ("partonomy (PART_OF)", MEREO)]:
        H = nx.DiGraph()
        H.add_nodes_from(G.nodes)
        for u, v, d in G.edges(data=True):
            if d["edge"] in keep:
                H.add_edge(u, v)
        try:
            cyc = list(nx.find_cycle(H, orientation="original"))
        except nx.NetworkXNoCycle:
            cyc = []
        record("STRUCTURE", f"cycles in {label}", len(cyc), ok=(len(cyc) == 0),
               note=" -> ".join(name.get(u, u) for u, v, _ in cyc[:5]))
        if not cyc and H.number_of_edges():
            depth = 0
            roots = [n for n in H if H.out_degree(n) == 0 and H.in_degree(n) > 0]
            for n in H:
                if H.out_degree(n) and H.in_degree(n) == 0:
                    for r in roots:
                        if nx.has_path(H, n, r):
                            depth = max(depth, nx.shortest_path_length(H, n, r))
            record("STRUCTURE", f"max depth, {label}", depth)

    # tangledness: nodes with more than one parent
    tang = collections.Counter()
    for u, v, d in G.edges(data=True):
        if d["edge"] in HIER:
            tang[u] += 1
    multi = {k: v for k, v in tang.items() if v > 1}
    record("STRUCTURE", "nodes with >1 parent", len(multi),
           note=", ".join(f"{name.get(k)}({v})" for k, v in list(multi.items())[:5]))

    # degree: hubs and isolates by type
    deg = sorted(((G.degree(n), n) for n in G), reverse=True)
    record("STRUCTURE", "highest degree", deg[0][0],
           note=f"{name.get(deg[0][1])} [{nt.get(deg[0][1])}]")
    for t in ("FindingClass", "Diagnosis", "DataElement"):
        ns = [n for n in G if nt.get(n) == t]
        if ns:
            d = [G.degree(n) for n in ns]
            record("STRUCTURE", f"mean degree, {t}", round(sum(d) / len(d), 1),
                   note=f"min {min(d)}, max {max(d)}")


def richness(g, G):
    """OntoQA-style. Comparable across releases; meaningless in isolation."""
    nt = nx.get_node_attributes(G, "node")
    edges = [d["edge"] for _, _, d in G.edges(data=True)]
    total = len(edges)
    inherit = sum(1 for e in edges if e in HIER)
    record("RICHNESS", "relationship richness",
           round((total - inherit) / total, 3),
           note="non-inheritance edges / all edges. 0 = a bare taxonomy, 1 = no taxonomy")

    fcs = [n for n in G if nt.get(n) == "FindingClass"]
    attr = sum(1 for _, _, d in G.edges(data=True) if d["edge"] == "HAS_DATA_ELEMENT")
    record("RICHNESS", "attribute richness", round(attr / len(fcs), 2),
           note="element edges per finding class")

    subs = collections.Counter()
    for u, v, d in G.edges(data=True):
        if d["edge"] == "SUBTYPE_OF":
            subs[v] += 1
    parents = [n for n in fcs if subs.get(n)]
    record("RICHNESS", "inheritance richness",
           round(sum(subs.values()) / len(fcs), 2),
           note=f"subtypes per finding class; {len(parents)} classes have any")

    de = [n for n in G if nt.get(n) == "DataElement"]
    uses = collections.Counter(v for _, v, d in G.edges(data=True)
                               if d["edge"] == "HAS_DATA_ELEMENT")
    reuse = [uses.get(n, 0) for n in de]
    record("RICHNESS", "element reuse", round(sum(reuse) / len(de), 2),
           note=f"references per element; {sum(1 for r in reuse if r == 0)} unused, "
                f"{sum(1 for r in reuse if r == 1)} used once")


def invariants(g, G):
    """Claims the model makes about itself. A failure here is a defect."""
    nt = nx.get_node_attributes(G, "node")
    name = nx.get_node_attributes(G, "name")
    ids = set(G.nodes)

    # referential integrity
    dangling = [(e["edge"], e["from"], e["to"]) for e in g["edges"]
                if e["from"] not in ids or e["to"] not in ids]
    record("INVARIANTS", "dangling edge endpoints", len(dangling),
           ok=(len(dangling) == 0), note=str(dangling[:3]))

    # every non-component finding is anatomically anchored
    comp = {n for n in G if G.nodes[n].get("component")}
    scoped = {u for u, _, d in G.edges(data=True) if d["edge"] == "SCOPED_TO"}
    subtyped = {u for u, _, d in G.edges(data=True) if d["edge"] == "SUBTYPE_OF"}
    fcs = {n for n in G if nt.get(n) == "FindingClass"}
    unanchored = fcs - scoped - comp - subtyped
    record("INVARIANTS", "findings with no anatomic anchor", len(unanchored),
           ok=(len(unanchored) == 0),
           note=", ".join(name.get(x) for x in list(unanchored)[:5]))

    # every value belongs to exactly one element
    owner = collections.Counter(v for _, v, d in G.edges(data=True) if d["edge"] == "HAS_VALUE")
    vals = {n for n in G if nt.get(n) == "Value"}
    bad = [v for v in vals if owner.get(v, 0) != 1]
    record("INVARIANTS", "values not owned by exactly one element", len(bad),
           ok=(len(bad) == 0), note=", ".join(name.get(x) for x in bad[:5]))

    # OCCURS_WITH relates like to like
    ow_bad = [(name.get(e["from"]), name.get(e["to"])) for e in g["edges"]
              if e["edge"] == "OCCURS_WITH" and nt.get(e["from"]) != nt.get(e["to"])]
    record("INVARIANTS", "OCCURS_WITH across node types", len(ow_bad),
           ok=(len(ow_bad) == 0), note=str(ow_bad[:3]))

    # every finding reaches an anatomic location, directly or through its parent
    H = nx.DiGraph()
    for u, v, d in G.edges(data=True):
        if d["edge"] in ("SCOPED_TO", "SUBTYPE_OF", "COMPONENT_OF"):
            H.add_edge(u, v)
    als = {n for n in G if nt.get(n) == "AnatomicLocation"}
    unreach = []
    for f in fcs:
        if f not in H:
            unreach.append(f); continue
        if not any(nx.has_path(H, f, a) for a in als if a in H):
            unreach.append(f)
    record("INVARIANTS", "findings that cannot reach anatomy", len(unreach),
           ok=(len(unreach) == 0), note=", ".join(name.get(x) for x in unreach[:5]))

    # every diagnosis reaches at least one finding
    dxs = {n for n in G if nt.get(n) == "Diagnosis"}
    linked = {u for u, v, d in G.edges(data=True)
              if d["edge"] in ("MAY_MANIFEST_AS", "MAY_CAUSE") and nt.get(v) == "FindingClass"}
    noimg = {n for n in dxs if G.nodes[n].get("no_imaging_elements")}
    stranded = dxs - linked - noimg
    record("INVARIANTS", "diagnoses with no route to a finding", len(stranded),
           ok=(len(stranded) == 0), note=", ".join(name.get(x) for x in list(stranded)[:5]))

    # anchor verdict present on every finding and diagnosis
    missing = [n for n in fcs | dxs if not G.nodes[n].get("anchor_verdict")]
    record("INVARIANTS", "nodes missing an anchor verdict", len(missing),
           ok=(len(missing) == 0), note=", ".join(name.get(x) for x in missing[:5]))

    # every reified edge carries an id and a version
    unreified_ok = {"IS_A", "PART_OF", "CONTAINED_IN"}
    noid = [e["edge"] for e in g["edges"]
            if e["edge"] not in unreified_ok and not e.get("id")]
    record("INVARIANTS", "authored edges without an id", len(noid),
           ok=(len(noid) == 0), note=str(collections.Counter(noid).most_common(3)))


def owl_agreement(g, G):
    """The OWL and the graph are built from one source and must agree.

    They are generated by different code walking the same spec, so a misplaced
    line in one produces restrictions the other does not have. That has happened:
    scope and modality intended for a DataElement landed on its values, and on one
    Subspecialty, in the OWL only. The round-trip check cannot see it, because it
    compares Turtle against RDF/XML of the same build.

    Checks the node types that carry scope and modality, which is where the
    divergence showed up, rather than every axiom.
    """
    import os
    from rdflib import Graph as RG, URIRef, BNode
    from rdflib.namespace import RDFS, OWL
    CDE = "https://radelement.org/ng/"
    path = f"{OUT}/radcde-alpha.ttl"
    if not os.path.exists(path):
        record("STRUCTURE", "OWL agreement", "skipped", note="radcde-alpha.ttl not present")
        return
    o = RG().parse(path, format="turtle")
    NEVER = {"Value", "Subspecialty", "Modality", "AssessmentScheme", "Etiology",
             "ScopeResolution"}
    bad = []
    for s_, _, obj in o.triples((None, RDFS.subClassOf, None)):
        if not isinstance(obj, BNode):
            continue
        pr = o.value(obj, OWL.onProperty)
        if pr is None or not any(k in str(pr) for k in ("scopedTo", "seenOn")):
            continue
        t = o.value(s_, URIRef(CDE + "nodeType"))
        if t is not None and str(t) in NEVER:
            bad.append(f"{t} {str(s_).rsplit('/', 1)[-1]} carries {str(pr).rsplit('/', 1)[-1]}")
    record("INVARIANTS", "scope or modality on a node type that cannot have it",
           len(bad), ok=(not bad), note="; ".join(bad[:4]))


def upstream(g, G):
    """The relationship with the source vocabulary, rather than the state of our graph.

    Two kinds of change request. A NODE request asks for a concept that does not
    exist upstream. An EDGE request asks for a relationship between two concepts
    that both already exist. They are counted separately because they are different
    submissions and are satisfied by different upstream changes.
    """
    nt = nx.get_node_attributes(G, "node")
    name = nx.get_node_attributes(G, "name")

    av = collections.Counter(n.get("anchor_verdict") for n in g["nodes"]
                             if n["node"] in ("FindingClass", "Diagnosis"))
    for v in ("anchored", "post_coordinated", "structurally_expressed",
              "unanchored_requestable", "out_of_primary_scope"):
        record("UPSTREAM", f"anchor: {v}", av.get(v, 0))

    node_reqs = sorted({n["request"] for n in g["nodes"] if n.get("request")})
    edge_reqs = sorted({e["props"]["request"] for e in g["edges"]
                        if e.get("props", {}).get("request")})
    record("UPSTREAM", "change requests, concepts", len(node_reqs),
           note=", ".join(node_reqs))
    record("UPSTREAM", "change requests, relationships", len(edge_reqs),
           note=", ".join(edge_reqs))
    record("UPSTREAM", "change requests, total", len(set(node_reqs) | set(edge_reqs)),
           note="a request reused on both a node and the edge that places it counts once")

    dual = sum(1 for n in g["nodes"] if len({b["system"] for b in n.get("bindings", [])}) > 1)
    anchored = sum(1 for n in g["nodes"] if n.get("bindings"))
    record("UPSTREAM", "nodes with any binding", anchored,
           note=f"of {len(g['nodes'])}")
    record("UPSTREAM", "nodes bound to more than one system", dual)
    sysc = collections.Counter(b["system"] for n in g["nodes"] for b in n.get("bindings", []))
    for k, v in sorted(sysc.items()):
        record("UPSTREAM", f"bindings: {k}", v)


def smells(g, G):
    """Not failures. Things worth a look."""
    nt = nx.get_node_attributes(G, "node")
    name = nx.get_node_attributes(G, "name")
    uses = collections.Counter(v for _, v, d in G.edges(data=True)
                               if d["edge"] == "HAS_DATA_ELEMENT")
    once = [name.get(n) for n in G if nt.get(n) == "DataElement" and uses.get(n, 0) <= 1]
    record("SMELLS", "elements used once or never", len(once), note=", ".join(once[:8]))

    dup = collections.defaultdict(list)
    for n in G:
        if nt.get(n) == "Value":
            dup[name.get(n, "").lower()].append(n)
    d = {k: len(v) for k, v in dup.items() if len(v) > 1}
    record("SMELLS", "duplicated value labels", len(d), note=str(dict(list(d.items())[:6])))

    leaf_nodx = [name.get(n) for n in G if nt.get(n) == "FindingClass"
                 and not any(d["edge"] == "MAY_MANIFEST_AS" for _, _, d in G.in_edges(n, data=True))]
    record("SMELLS", "findings no diagnosis points at", len(leaf_nodx),
           note=", ".join(leaf_nodx[:8]))


GROUP_INTRO = {
    "INVARIANTS": "Claims the model makes about itself. A failure here is a defect, and the "
                  "script exits non-zero so it can gate a build.",
    "STRUCTURE":  "Generic graph analysis, restricted to measures that mean something for a "
                  "definition layer.",
    "RICHNESS":   "OntoQA-style. Comparable across releases rather than meaningful in "
                  "isolation: watch the direction of travel, not the value.",
    "UPSTREAM":   "The relationship with the source vocabulary rather than the state of this "
                  "graph. Change requests are counted in two kinds: a concept request asks for "
                  "something that does not exist upstream, an edge request asks for a "
                  "relationship between two concepts that both already do.",
    "SMELLS":     "Not failures. Things worth a look.",
}

NOT_COMPUTED = [
    ("clustering coefficient", "assumes triadic closure; a definition graph has almost none by construction"),
    ("betweenness centrality", "dominated by the anatomy root, which reflects import depth"),
    ("eigenvector centrality / PageRank", "same, and there is no notion of authority here to rank"),
    ("diameter", "on a mostly-tree hierarchy this is just depth, already reported"),
    ("assortativity", "degree correlation between node types is an artifact of the schema, not a property of the content"),
]


def history():
    """Past runs, oldest first, for the trend table."""
    import re, os
    out = []
    d = f"{OUT}/evaluation"
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        m = re.fullmatch(r"(\d{4}-\d{2}-\d{2})\.md", f)
        if not m:
            continue
        vals = {}
        for line in open(os.path.join(d, f)):
            if line.startswith("| ") and line.count("|") >= 4:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) > 3 and parts[2] and parts[2] != "Value":
                    vals[parts[1]] = parts[2]
        out.append((m.group(1), vals))
    return out


TRACKED = ["nodes", "edges", "structural orphans", "weakly connected components",
           "change requests, total", "change requests, concepts",
           "change requests, relationships", "anchor: unanchored_requestable",
           "relationship richness", "attribute richness", "inheritance richness",
           "element reuse", "duplicated value labels", "findings no diagnosis points at"]


def write_md(failed):
    import os
    os.makedirs(f"{OUT}/evaluation", exist_ok=True)
    today = datetime.date.today().isoformat()
    prior = [h for h in history() if h[0] != today]

    L = []
    w = L.append
    w(f"# Graph evaluation — {today}")
    w("")
    w("Generated by `scripts/evaluate_graph.py` against `graph/definition-graph.json`.")
    w("One file per run, kept so the richness numbers can be read as a series; they mean")
    w("little in isolation.")
    w("")
    inv = [r for r in results if r[0] == "INVARIANTS"]
    passed = sum(1 for r in inv if r[3] is True)
    w(f"**{passed} of {len(inv)} invariants pass.** "
      + ("No defects." if not failed else f"{failed} failing — see below."))
    w("")
    if prior:
        runs = prior[-4:] + [(today, {nm.strip(): str(val) for _, nm, val, _, _ in results})]
        w("## Trend")
        w("")
        w("| Measure | " + " | ".join(d for d, _ in runs) + " |")
        w("|---" * (len(runs) + 1) + "|")
        for k in TRACKED:
            cells = [r.get(k, "—") for _, r in runs]
            if any(c != "—" for c in cells):
                w(f"| {k} | " + " | ".join(cells) + " |")
        w("")

    w("---")
    w("")
    order = ["INVARIANTS", "STRUCTURE", "RICHNESS", "UPSTREAM", "SMELLS"]
    for grp in order:
        rows = [r for r in results if r[0] == grp]
        if not rows:
            continue
        w(f"## {grp.title()}")
        w("")
        w(GROUP_INTRO[grp])
        w("")
        w("| Measure | Value | | Detail |")
        w("|---|---:|:-:|---|")
        for _, nm, val, ok, note in rows:
            mark = "" if ok is None else ("ok" if ok else "**FAIL**")
            w(f"| {nm.strip()} | {val} | {mark} | {note[:200] if note else ''} |")
        w("")
    w("## Not computed, on purpose")
    w("")
    w("Each is well defined on this graph and none would be actionable. Listed so that")
    w("their absence reads as a decision rather than an oversight.")
    w("")
    w("| Measure | Why not |")
    w("|---|---|")
    for m, why in NOT_COMPUTED:
        w(f"| {m} | {why} |")
    w("")
    text = "\n".join(L) + "\n"
    open(f"{OUT}/evaluation/{today}.md", "w").write(text)

    runs = sorted(f[:-3] for f in os.listdir(f"{OUT}/evaluation")
                  if f.endswith(".md") and f != "README.md")
    idx = ["# Evaluation runs", "",
           "One file per run of `scripts/evaluate_graph.py`. The richness numbers are",
           "comparable across releases rather than meaningful in isolation, so the series",
           "is the point. Each run carries a trend table of the last few.", "",
           "| Run | Invariants |", "|---|---|"]
    for r in runs:
        body = open(f"{OUT}/evaluation/{r}.md").read()
        line = next((l for l in body.splitlines() if l.startswith("**")), "")
        idx.append(f"| [{r}](./{r}.md) | {line.replace('**', '').strip()} |")
    idx.append("")
    open(f"{OUT}/evaluation/README.md", "w").write("\n".join(idx) + "\n")
    return f"evaluation/{today}.md"


def main():
    g, G = load()
    for fn in (structure, richness, invariants, owl_agreement, upstream, smells):
        fn(g, G)
    cur = None
    failed = 0
    for grp, nm, val, ok, note in results:
        if grp != cur:
            print(f"\n{grp}"); print("-" * 78); cur = grp
        mark = "" if ok is None else ("  ok" if ok else "  FAIL")
        if ok is False:
            failed += 1
        print(f"  {nm:44s} {str(val):>8s}{mark}")
        if note:
            print(f"      {note[:120]}")
    path = write_md(failed)
    print(f"\n{failed} invariant failures | {path} written")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
