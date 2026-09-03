#!/usr/bin/env python3
"""Convert the interim example specs (examples/*.neighborhood.json, *.element.json,
*.location.json) into canonical graph lines, so the site and the validator see one graph.

The specs remain the source for the dossier diagrams (render_neighborhood.py); this
converter is a bridge until the renderer reads the graph directly (06 §4).

Usage: spec_to_graph.py [EXAMPLES_DIR] > out.jsonl
As a library: convert_all(dir) yields (obj, origin) pairs.
"""
import json, os, sys, glob, re

# Names in spec `related`/`bound_by`/`scoped_classes` lists that already have ids in the documents.
NAME_IDS = {
    "solid component": "RDE2_000130",
    "pleural effusion": "RDE2_000502",
    "upper abdominal abnormality": "RDE2_000610",
    "bile duct dilation": "RDE2_000702",
    "choledocholithiasis": "RDE2_000703",
    "pacemaker": "RDE2_000777",
}
NAME_TYPES = {  # node type / entity_type for stubs that the specs only name
    "nodule": ("FindingClass", "finding"),
    "lung cancer": ("Diagnosis", None),
    "thyroid cancer": ("Diagnosis", None),
    "Fleischner recommendation": ("FindingClass", "assessment"),
    "Lung-RADS category": ("FindingClass", "assessment"),
    "TI-RADS category": ("FindingClass", "assessment"),
    "pacemaker": ("FindingClass", "device"),
    "upper abdominal abnormality": ("Grouping", None),
}


# Specs may assert the inverse direction; the canonical form stores the assertion direction of 07 §1.
INVERSES = {"MAY_REPRESENT": "MAY_MANIFEST_AS", "MAY_BE_CAUSED_BY": "MAY_CAUSE", "MAY_BE_COMPONENT_OF": "MAY_HAVE_COMPONENT",
            "MAY_PROGRESS_FROM": "MAY_PROGRESS_TO", "ASSESSES": "ASSESSED_BY", "HAS_SUBTYPE": "SUBTYPE_OF"}


def oriented(edge_type, frm, to):
    if edge_type in INVERSES:
        return INVERSES[edge_type], to, frm
    return edge_type, frm, to


_CONCEPTS = None
def concept_index():
    """(scheme, normalized name or alias) -> concept id, from graph/concepts.jsonl."""
    global _CONCEPTS
    if _CONCEPTS is None:
        _CONCEPTS = {}
        cp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "graph", "concepts.jsonl")
        if os.path.exists(cp):
            for line in open(cp, encoding="utf-8"):
                c = json.loads(line)
                for key in [c["name"]] + c.get("aliases", []):
                    _CONCEPTS[(c["scheme"], norm(key))] = c["id"]
    return _CONCEPTS


def norm(s):
    return re.sub(r"\s*:\s*", ":", s.strip().lower()).replace("_", " ").replace("-", " ")


def concept_ids(scheme, name):
    """Resolve a spec's metadata entry to concept ids; time-course phrases split into duration and modifiers."""
    idx = concept_index()
    parts = [name]
    if scheme == "ExpectedTimeCourse":
        parts = [x for x in re.split(r"\s*-\s*|\s+or\s+", name) if x]
    out = []
    for part in parts:
        cid = idx.get((scheme, norm(part)))
        out.append(cid or f"{scheme}-{slug(part)}")
    return out


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")


def stub_id(name):
    return NAME_IDS.get(name) or "STUB-" + slug(name)


def kind_of(k):
    """Spec kind strings -> (kind, extras)."""
    k = (k or "").lower()
    if k.startswith("categorical"):
        return "categorical", {"ordered": True} if "ordinal" in k else {}
    if k in ("length",):
        return "quantitative", {"quantity_type": "length"}
    return k or "categorical", {}


def element_lines(owner_id, e, origin):
    """HAS_ELEMENT edge plus the element (stub or full) and its values."""
    props = {}
    if e.get("edge_note"): props["note"] = e["edge_note"]
    edge = {"edge": "HAS_ELEMENT", "from": owner_id, "to": e.get("ref") or e["id"]}
    if e.get("binding_id"): edge["id"] = e["binding_id"]
    if props: edge["props"] = props
    yield edge, origin
    kind, extras = kind_of(e.get("kind"))
    if e.get("ref"):
        node = {"node": "DataElement", "id": e["ref"], "name": e["name"], "kind": kind}
        node.update(extras)
        if e.get("multi_select"): node["multi_select"] = True
        yield node, origin
        return
    node = {"node": "DataElement", "id": e["id"], "name": e["name"], "kind": kind}
    node.update(extras)
    if e.get("definition"): node["definition"] = e["definition"]
    if e.get("multi_select"): node["multi_select"] = True
    yield node, origin
    for v in e.get("values", []):
        if not isinstance(v, dict):
            continue
        vn = {"node": "Value", "id": v["id"], "name": v["name"], "value": v.get("value", slug(v["name"]).lower())}
        if v.get("definition"): vn["definition"] = v["definition"]
        yield vn, origin
        m = {"edge": "member", "from": e["id"], "to": v["id"]}
        if v.get("rank") is not None: m["props"] = {"rank": v["rank"]}
        yield m, origin


def mapping_lines(nid, maps, origin):
    for m in maps or []:
        yield {"edge": m.get("match", "exactMatch"), "from": nid, "to": f'{m["system"]}:{m["code"]}',
               "props": {"display": m.get("display", "")}}, origin


def convert_class(spec, origin):
    c = spec["center"]; cid = spec["id"]
    node = {"node": "FindingClass", "id": cid, "name": c["name"], "entity_type": c.get("entity_type", "finding")}
    for k in ("definition", "synonyms", "version", "status", "status_date"):
        if spec.get(k) not in (None, "", []): node[k] = spec[k]
    yield node, origin
    for e in spec.get("elements", []):
        yield from element_lines(cid, e, origin)
    for s in spec.get("scope", []):
        yield {"node": "AnatomicLocation", "id": s["ref"], "name": s["name"]}, origin
        yield {"edge": "SCOPED_TO", "from": cid, "to": s["ref"],
               "props": {"kind": s.get("kind", "structure"), "strength": s.get("strength", "expected")}}, origin
    for r in spec.get("related", []):
        tid = stub_id(r["name"])
        note = r.get("note", "")
        ntype, et = NAME_TYPES.get(r["name"], (None, None))
        if ntype is None:
            ntype, et = ("Diagnosis", None) if note.startswith("diagnosis") else \
                        ("FindingClass", "assessment") if note.startswith("assessment") else ("FindingClass", "finding")
        stub = {"node": ntype, "id": tid, "name": r["name"]}
        if et: stub["entity_type"] = et
        yield stub, origin
        et_, f_, t_ = oriented(r["edge"], cid, tid)
        edge = {"edge": et_, "from": f_, "to": t_}
        if " - " in note: edge["props"] = {"note": note.split(" - ", 1)[1]}
        yield edge, origin
    for m in spec.get("metadata", []):
        for conc in concept_ids(m["type"], m["name"]):
            if conc.startswith(m["type"] + "-"):   # unresolved: keep a placeholder node so the edge has a target
                yield {"node": "Concept", "id": conc, "name": m["name"], "scheme": m["type"]}, origin
            edge = {"edge": m["edge"], "from": cid, "to": conc}
            if m.get("note"): edge["props"] = {"note": m["note"]}
            yield edge, origin
    yield from mapping_lines(cid, spec.get("mappings"), origin)


def convert_element(spec, origin):
    eid = spec["id"]
    kind, extras = kind_of(spec.get("kind"))
    node = {"node": "DataElement", "id": eid, "name": spec["name"], "kind": kind}
    node.update(extras)
    for k in ("definition", "synonyms", "version", "status", "status_date"):
        if spec.get(k) not in (None, "", []): node[k] = spec[k]
    vs = spec.get("value_set")
    if vs and vs.get("ordered"): node["ordered"] = True
    qn = spec.get("quantity")
    if qn:
        node["quantity_type"] = qn["type"]
        for k in ("units", "min", "max", "step", "method"):
            if qn.get(k) is not None: node[k] = qn[k]
    yield node, origin
    if vs:
        for v in vs["values"]:
            vn = {"node": "Value", "id": v["id"], "name": v["name"], "value": v.get("value", slug(v["name"]).lower())}
            if v.get("definition"): vn["definition"] = v["definition"]
            yield vn, origin
            m = {"edge": "member", "from": eid, "to": v["id"]}
            if v.get("rank") is not None: m["props"] = {"rank": v["rank"]}
            yield m, origin
            yield from mapping_lines(v["id"], v.get("codes"), origin)
    for b in spec.get("bound_by", []):
        bid = b.get("id") or stub_id(b["name"])
        ntype, et = NAME_TYPES.get(b["name"], ("FindingClass", "finding"))
        stub = {"node": ntype, "id": bid, "name": b["name"]}
        if et: stub["entity_type"] = et
        yield stub, origin
        yield {"edge": "HAS_ELEMENT", "from": bid, "to": eid}, origin
    yield from mapping_lines(eid, spec.get("mappings"), origin)


def convert_location(spec, origin):
    lid = spec["id"]
    node = {"node": "AnatomicLocation", "id": lid, "name": spec["name"]}
    for k in ("contained_by", "part_of", "owner"):
        if spec.get(k): node[k] = spec[k]
    yield node, origin
    for e in spec.get("elements", []):
        yield from element_lines(lid, e, origin)
    for c in spec.get("scoped_classes", []):
        cid = c.get("id") or stub_id(c["name"])
        et = c.get("entity_type", "finding")
        stub = {"node": "Diagnosis" if et == "diagnosis" else "FindingClass", "id": cid, "name": c["name"]}
        if et != "diagnosis": stub["entity_type"] = et
        yield stub, origin
        yield {"edge": "SCOPED_TO", "from": cid, "to": lid, "props": {"kind": "structure", "strength": "required"}}, origin
        if c.get("interpreted_from"):
            yield {"edge": "INTERPRETED_FROM", "from": cid, "to": c["interpreted_from"]}, origin
    yield from mapping_lines(lid, spec.get("mappings"), origin)


def convert_all(examples_dir):
    for path in sorted(p for p in glob.glob(os.path.join(examples_dir, "*.json")) if p.endswith((".neighborhood.json", ".element.json", ".location.json"))):
        spec = json.load(open(path, encoding="utf-8"))
        origin = "examples/" + os.path.basename(path)
        kind = spec.get("node")
        conv = convert_element if kind == "DataElement" else convert_location if kind == "AnatomicLocation" else convert_class
        yield from conv(spec, origin)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from graph import canonical_text
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")
    sys.stdout.write(canonical_text([o for o, _ in convert_all(d)]))
