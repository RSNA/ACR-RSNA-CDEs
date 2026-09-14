# -*- coding: utf-8 -*-
"""
Two more serialisations of the same content:

  graph/*.json     the definition graph in the node/edge shape the md files describe
  compiled/*.json  one resolved shape per FindingClass, references applied

The compiled form is what 00-stated-goals.md asks for: one concrete shape rather
than a general shape plus conditions an extractor has to evaluate. Conditional
content is resolved by emitting the defined subtypes as separate shapes.
"""
import json, os, datetime, collections
import snomed
import spec
from pathlib import Path
from radlex_index import anatomy_branch, descendants

TODAY = datetime.date.today().isoformat()
ROOT = Path(__file__).resolve().parent.parent
OUT = str(ROOT)


def vb(status="proposed", n=1):
    return {"number": n, "status": status, "created": TODAY, "published": None,
            "last_modified": TODAY, "contributors": [
                {"id": "PERSON-000001", "role": "author", "via": "alpha-generator"}]}


def sct(code, label, match):
    return {"system": "SNOMEDCT", "code": code, "source_label": label, "match": match,
            "source_version": "supplied", "version": vb("published")}


_RADLEX_LABELS = None
def binding(system, code, label, match="exactMatch"):
    global _RADLEX_LABELS
    if system == "RADLEX":
        if _RADLEX_LABELS is None:
            try:
                _ai = json.load(open(Path(__file__).with_name("anatomy.json"), encoding="utf-8"))
                _RADLEX_LABELS = {r: n.get("label") for r, n in _ai.get("classes", {}).items()}
            except Exception:
                _RADLEX_LABELS = {}
        label = _RADLEX_LABELS.get(code) or label
    b = {"system": system, "code": code, "source_label": label, "match": match,
         "source_version": spec.RADLEX_VERSION, "version": vb("published")}
    return b


_edge_seq = [0]


def E(edge, frm, to, props=None):
    """Create one addressable CDE-authored edge with its own version block."""
    _edge_seq[0] += 1
    return {"node": "Edge", "id": f"EDGE-{_edge_seq[0]:06d}",
            "edge": edge, "from": frm, "to": to, "props": props or {},
            "version": vb()}


def taxonomy_target_set(anat, root_rid, include_root=False, include_descendants=True):
    """Resolve eligible concepts from one native RadLex taxonomy root."""
    out = set()
    if include_descendants:
        out.update(descendants(anat, root_rid, include_root=include_root))
    elif include_root:
        out.add(root_rid)
    return sorted(out)


def refinement_target_set(anat, rule):
    """Resolve exact and taxonomy-defined targets without coupling them to predicates."""
    out = set(rule.get("allowed_targets", []))
    root = rule.get("target_root")
    if root:
        out.update(taxonomy_target_set(
            anat, root,
            include_root=rule.get("include_root", False),
            include_descendants=rule.get("include_descendants", True)))
    return sorted(out)


def build():
    anat = json.load(open(Path(__file__).with_name("anatomy.json"), encoding="utf-8"))
    nodes, edges = [], []

    # ---- anatomy references
    # AnatomicLocation is a CDE graph role over native RadLex classes. The
    # canonical definition graph materializes only RIDs explicitly referenced by
    # CDE-authored definitions. Full native RadLex taxonomy, relationships, and
    # property metadata remain in anatomy.json and RadLex.owl.
    branch = anatomy_branch(anat)
    al_by_key = {}

    def require_anatomy(rid):
        if rid not in branch:
            raise ValueError(f"{rid} is referenced as anatomy but is not in the native RadLex RID3 anatomy branch")
        if rid not in al_by_key:
            nd = anat["classes"][rid]
            n = {"node": "AnatomicLocation", "id": rid, "iri": nd["iri"],
                 "name": nd.get("label") or rid,
                 "definition": nd.get("definition"), "source": "RADLEX",
                 "synonyms": ([{"term": t, "type": "synonym"} for t in nd.get("synonyms", [])] +
                              [{"term": t, "type": "acronym"} for t in nd.get("acronyms", [])]),
                 "bindings": [binding("RADLEX", rid, nd.get("label") or rid, "exactMatch")],
                 "version": vb("published")}
            if nd.get("unsanctioned"):
                n["unsanctioned_terms"] = nd["unsanctioned"]
            if nd.get("source"):
                n["concept_source"] = nd["source"]
            nodes.append(n)
            al_by_key[rid] = rid
        return rid

    # ---- data elements and values
    de_index = {}
    for de in spec.DATA_ELEMENTS:
        de_index[de["id"]] = de
        n = {"node": "DataElement", "id": de["id"], "name": de["name"],
             "definition": de["definition"],
             "select_cardinality": "multi" if de.get("multi_select") else "single",
             "synonyms": [{"term": t, "type": ty} for t, ty in de.get("synonyms", [])],
             "bindings": ([binding("RADLEX", de["radlex"], de["name"], "closeMatch")]
                          if de.get("radlex") else []),
             "version": vb()}
        nodes.append(n)
        ordered = all(v[4] is not None for v in de["values"])
        for rid in de.get("scoped_to", []):
            edges.append(E("SCOPED_TO", de["id"], require_anatomy(rid),
                           {"kind": "region", "strength": "required"}))
        for mcode in de.get("modality", []):
            edges.append(E("SEEN_ON", de["id"], mcode, {}))
        for vid, vname, vrid, vdef, vrank in de["values"]:
            vn = {"node": "Value", "id": vid, "name": vname, "value": vname,
                  "definition": vdef, "synonyms": [],
                  "bindings": (([binding("RADLEX", vrid,
                                         spec.LOOSE_VALUE_MATCHES[vid][2]
                                         if vid in spec.LOOSE_VALUE_MATCHES else vname,
                                         spec.LOOSE_VALUE_MATCHES[vid][1]
                                         if vid in spec.LOOSE_VALUE_MATCHES else "exactMatch")]
                                if vrid else [])
                               + ([sct(*snomed.VALUES[vid])] if vid in snomed.VALUES else [])),
                  "version": vb()}
            nodes.append(vn)
            props = {"rank": vrank} if ordered else {}
            if de.get("exclusive_none") == vid:
                props["exclusive"] = True
                props["exclusive_note"] = ("selecting this excludes every other value of "
                                           "this element")
            edges.append(E("HAS_VALUE", de["id"], vid, props))

    # ---- measurements
    for ms in spec.MEASUREMENTS:
        nodes.append({"node": "Measurement", "id": ms["id"], "name": ms["name"],
                      "definition": ms["definition"], "quantity_kind": ms["quantity_kind"],
                      "permitted_units": ms["permitted_units"], "method": ms["method"],
                      "synonyms": [], "bindings": [], "version": vb()})
        for c in ms.get("components", []):
            edges.append(E("HAS_MEASUREMENT_COMPONENT", ms["id"], c, {}))
        for d in ms.get("derived_from", []):
            edges.append(E("DERIVED_FROM_MEASUREMENT", ms["id"], d, {}))
        # A descriptor of a normal structure may carry its own anatomic scope
        # without belonging to a FindingClass.
        if ms.get("scoped_to_anatomy"):
            edges.append(E("SCOPED_TO", ms["id"], require_anatomy(ms["scope_target"]),
                           {"kind": "class", "strength": "required"}))

    # ---- assessment schemes
    as_index = {}
    for a in spec.ASSESSMENT_SCHEMES:
        as_index[a["id"]] = a
        nodes.append({"node": "AssessmentScheme", "id": a["id"], "name": a["name"],
                      "issuing_authority": a["authority"], "scheme_version": a["scheme_version"],
                      "scheme_scope": a["scope"],
                      "categories": [{"name": c[0], "rank": c[2],
                                      "bindings": ([binding("RADLEX", c[1], c[0])] if c[1] else [])}
                                     for c in a["categories"]],
                      "bindings": ([binding("RADLEX", a["radlex"], a["name"], "exactMatch")]
                                   if a.get("radlex") else []),
                      "version": vb()})

    for eid, cls, name, rid, defn in spec.ETIOLOGIES:
        nodes.append({"node": "Etiology", "id": eid, "name": name, "definition": defn,
                      "bindings": (([binding("RADLEX", rid, name, "closeMatch")]
                                    if rid else [])
                                   + ([sct(*snomed.ETIOLOGY[eid])] if eid in snomed.ETIOLOGY else [])),
                      "version": vb()})

    for mid, code, label, rid in spec.MODALITIES:
        nodes.append({"node": "Modality", "id": mid, "name": code, "definition": label,
                      "bindings": ([binding("RADLEX", rid, label, "exactMatch")]
                                   + ([sct(*snomed.MODALITY[mid])] if mid in snomed.MODALITY else [])),
                      "version": vb("published")})
    for sid, short, label in spec.SUBSPECIALTIES:
        nodes.append({"node": "Subspecialty", "id": sid, "name": short, "definition": label,
                      "bindings": [], "version": vb("published")})

    # ---- findings
    fc_id = {f["cls"]: f["id"] for f in spec.FINDING_CLASSES}
    dx_id = {d["cls"]: d["id"] for d in spec.DIAGNOSES}

    def al(x):
        return require_anatomy(x)

    for fc in spec.FINDING_CLASSES:
        n = {"node": "FindingClass", "id": fc["id"], "name": fc["name"],
             "definition": fc["definition"],
             "defined_concept": bool(fc.get("defined")),
             "synonyms": [{"term": t, "type": ty,
                           "scope": (fc.get("synonym_scope") or {}).get(t, "exact")}
                          for t, ty in fc.get("synonyms", [])],
             "bindings": (([binding("RADLEX", fc["radlex"], fc["name"],
                                    fc.get("match", "exactMatch"))]
                           if fc.get("radlex") else [])
                          + ([sct(*snomed.FINDINGS[fc["name"]])]
                             if fc["name"] in snomed.FINDINGS else [])),
             "version": vb()}
        if fc.get("criterion"):
            n["criterion"] = fc["criterion"]
        if fc.get("radlex_composition"):
            comp = fc["radlex_composition"]
            base = comp.get("base")
            n["radlex_composition"] = {
                "base": ({"code": base[0], "label": base[1]} if base else None),
                "modifiers": [{"code": c, "label": l} for c, l in comp.get("modifiers", [])],
            }
        if fc.get("component"):
            n["component"] = True
        nodes.append(n)

        if fc.get("parent"):
            edges.append(E("SUBTYPE_OF", fc["id"], fc_id[fc["parent"]],
                       {"inheritance": "strict"}))
        eff_el, eff_ms, eff_mod = spec.expand(fc)
        for deid in eff_el:
            props = {}
            if deid in (fc.get("narrow") or {}):
                props["narrow"] = fc["narrow"][deid]
                if deid in (fc.get("narrow_note") or {}):
                    props["note"] = fc["narrow_note"][deid]
            if deid in (fc.get("modality_scoped") or {}):
                props["modality"] = fc["modality_scoped"][deid]
            edges.append(E("HAS_DATA_ELEMENT", fc["id"], deid, props))
        for deid, allowed in (fc.get("narrow") or {}).items():
            if deid not in eff_el:
                props = {"narrow": allowed}
                if deid in (fc.get("narrow_note") or {}):
                    props["note"] = fc["narrow_note"][deid]
                if deid in (fc.get("modality_scoped") or {}):
                    props["modality"] = fc["modality_scoped"][deid]
                e = E("HAS_DATA_ELEMENT", fc["id"], deid, props)
                e["_inherited_from"] = fc.get("parent")
                edges.append(e)
        for msid in eff_ms:
            edges.append(E("HAS_MEASUREMENT", fc["id"], msid, {}))
        for asid in fc.get("assessed_by", []):
            edges.append(E("ASSESSED_BY", fc["id"], asid, {}))
        for m in eff_mod:
            edges.append(E("SEEN_ON", fc["id"], m,
                       {}))
        for s in fc.get("in_subspecialty", []):
            edges.append(E("IN_SUBSPECIALTY", fc["id"], s,
                       {}))
        # Symmetric: stored once. A consumer walking edges out of the target must read
        # the flag and traverse backwards; two stored edges would mean two ids for one
        # assertion, and retiring one would leave the other standing.
        for target in fc.get("occurs_with", []):
            edges.append(E("OCCURS_WITH", fc["id"], fc_id[target], {"symmetric": True}))
        for cname, strength in fc.get("components", []):
            edges.append(E("HAS_COMPONENT", fc["id"], fc_id[cname],
                       {"strength": strength, "direction": "required_on_whole"}))
        if fc.get("component_of"):
            edges.append(E("COMPONENT_OF", fc["id"], fc_id[fc["component_of"]],
                           {"direction": "necessary_on_component"}))
        for prop, vid in fc.get("fixed", []):
            edges.append(E("HAS_VALUE_CONSTRAINT", fc["id"], vid,
                           {"element": prop, "defining": False,
                            "note": fc.get("fixed_note", "fixed by the authored class model, not offered as an element")}))
        for prop, target in fc.get("differentia", []):
            if prop.startswith("scopedTo"):
                edges.append(E("SCOPED_TO", fc["id"], al(target),
                               {"kind": "region", "strength": "required", "defining": True}))
            else:
                edges.append(E("HAS_VALUE_CONSTRAINT", fc["id"], target,
                       {"element": prop, "defining": True}))
        for rule in fc.get("anatomic_refinement_rules", []):
            rid = rule["id"]
            scope = require_anatomy(rule["scope"])
            allowed_predicates = list(rule.get("allowed_predicates", []))
            allowed_targets = [require_anatomy(r) for r in rule.get("allowed_targets", [])]
            target_root = rule.get("target_root")
            if target_root:
                target_root = require_anatomy(target_root)
            if not allowed_targets and not target_root:
                raise ValueError(f"{rid} must define exact targets, a taxonomy target set, or both")
            for predicate in allowed_predicates:
                if predicate not in anat.get("object_properties", {}):
                    raise ValueError(f"{rid} references unknown native RadLex predicate {predicate}")
            target_constraint = None
            if target_root:
                target_constraint = {
                    "type": "radlex_taxonomy", "root": target_root,
                    "include_root": bool(rule.get("include_root", False)),
                    "include_descendants": bool(rule.get("include_descendants", True))
                }
            rn = {
                "node": "AnatomicRefinementRule", "id": rid,
                "name": f"{fc['name']} anatomic refinement rule",
                "scope": scope,
                "allowed_predicates": allowed_predicates,
                "allowed_targets": allowed_targets,
                "target_constraint": target_constraint,
                "traversal": rule.get("traversal"),
                "version": vb()
            }
            nodes.append(rn)
            edges.append(E("HAS_ANATOMIC_REFINEMENT_RULE", fc["id"], rid, {}))
            edges.append(E("REFINES_SCOPE", rid, scope, {}))
            for target in allowed_targets:
                edges.append(E("ALLOWED_ANATOMIC_TARGET", rid, target, {}))
            if target_constraint:
                edges.append(E("TARGET_TAXONOMY_ROOT", rid, target_root,
                               {"include_root": target_constraint["include_root"],
                                "include_descendants": target_constraint["include_descendants"]}))
        for sc in fc.get("scoped_to", []):
            rid, kind, strength = sc[0], sc[1], sc[2]
            edges.append(E("SCOPED_TO", fc["id"], al(rid),
                       {"kind": kind, "strength": strength}))

    for cls, rid, kind, strength in spec.SCOPE_ASSERTIONS:
        edges.append(E("SCOPED_TO", fc_id[cls], al(rid),
                       {"kind": kind, "strength": strength}))

    dx_id_map = {d["cls"]: d["id"] for d in spec.DIAGNOSES}
    for dx in spec.DIAGNOSES:
        n = {"node": "Diagnosis", "id": dx["id"], "name": dx["name"],
             "definition": dx["definition"],
             "synonyms": [{"term": t, "type": ty} for t, ty in dx.get("synonyms", [])],
             "bindings": (([binding("RADLEX", dx["radlex"], dx.get("source_label", dx["name"]),
                                    dx.get("match", "exactMatch"))]
                           if dx.get("radlex") else [])
                          + ([sct(*snomed.DIAGNOSES[dx["name"]])]
                             if dx["name"] in snomed.DIAGNOSES else [])),
             "version": vb()}
        if dx.get("synonym_only_hit"):
            n["radlex_binding_found_via"] = "synonym"
        if dx.get("radlex_composition"):
            comp = dx["radlex_composition"]
            base = comp.get("base")
            n["radlex_composition"] = {
                "base": ({"code": base[0], "label": base[1]} if base else None),
                "modifiers": [{"code": c, "label": l} for c, l in comp.get("modifiers", [])],
            }
        if dx.get("no_imaging_elements"):
            n["no_imaging_elements"] = True
        nodes.append(n)

        # evidential: the diagnosis can show itself as the target
        for target, typicality, specificity in dx.get("manifests_as", []):
            tid = fc_id.get(target) or dx_id_map.get(target)
            edges.append(E("MAY_MANIFEST_AS", dx["id"], tid,
                           {"typicality": typicality, "specificity": specificity,
                            "reading": "evidential", "inference_bearing": False}))
        # causal: the source can produce the target as a distinct second entity
        for target, typicality in dx.get("causes", []):
            tid = fc_id.get(target) or dx_id_map.get(target)
            edges.append(E("MAY_CAUSE", dx["id"], tid, {"typicality": typicality}))
        for target in dx.get("progresses_to", []):
            edges.append(E("MAY_PROGRESS_TO", dx["id"], dx_id_map[target], {}))
        for target in dx.get("occurs_with", []):
            edges.append(E("OCCURS_WITH", dx["id"], dx_id_map[target], {"symmetric": True}))
        for et in dx.get("etiology", []):
            edges.append(E("HAS_ETIOLOGY", dx["id"], et, {}))
        for sc in dx.get("scoped_to", []):
            rid, kind, strength = sc[0], sc[1], sc[2]
            edges.append(E("SCOPED_TO", dx["id"], require_anatomy(rid),
                           {"kind": kind, "strength": strength}))
        for deid in dx.get("elements", []):
            edges.append(E("HAS_DATA_ELEMENT", dx["id"], deid,
                       {}))
        for asid in dx.get("assessed_by", []):
            edges.append(E("ASSESSED_BY", dx["id"], asid,
                       {}))

    return nodes, edges, de_index, as_index


# --------------------------------------------------------------------------
def compile_findings(nodes, edges, de_index, as_index, anat):
    """Resolve every reference into one flat shape per FindingClass.

    Inheritance is applied: a defined subtype carries everything its ancestors
    carry, so a consumer reads one shape and evaluates nothing.
    """
    byid = {n["id"]: n for n in nodes}

    def nm_of(i):
        return byid[i]["name"] if i in byid else i

    def code_of(i):
        for b in byid.get(i, {}).get("bindings", []):
            if b["system"] == "RADLEX":
                return b["code"]
        return None

    out_edges = collections.defaultdict(list)
    for e in edges:
        out_edges[e["from"]].append(e)

    parent = {e["from"]: e["to"] for e in edges if e["edge"] == "SUBTYPE_OF"}

    def chain(fid):
        c, seen = [fid], set()
        while c[-1] in parent and c[-1] not in seen:
            seen.add(c[-1])
            c.append(parent[c[-1]])
        return c

    compiled = []
    for n in nodes:
        if n["node"] != "FindingClass":
            continue
        anc = chain(n["id"])
        elements, measurements, schemes, scopes = {}, {}, [], []
        refinement_rules = []
        modalities, subspecialties, components, represents = [], [], [], []
        caused_by, occurs_with, component_of, fixed_values = [], [], [], []
        narrowings = {}
        for fid in reversed(anc):                      # ancestors first
            for e in out_edges[fid]:
                if e["edge"] == "HAS_DATA_ELEMENT":
                    if "narrow" in e["props"]:
                        narrowings[e["to"]] = e["props"]["narrow"]
                    elements[e["to"]] = dict(
                        element_id=e["to"], inherited_from=(None if fid == n["id"] else fid),
                        modality=e["props"].get("modality"))
                elif e["edge"] == "HAS_MEASUREMENT":
                    measurements[e["to"]] = dict(
                        inherited_from=None if fid == n["id"] else fid,
)
                elif e["edge"] == "ASSESSED_BY":
                    schemes.append(e["to"])
                elif e["edge"] == "SEEN_ON":
                    modalities.append(e["to"])
                elif e["edge"] == "IN_SUBSPECIALTY":
                    subspecialties.append(e["to"])
                elif e["edge"] == "HAS_COMPONENT":
                    components.append(dict(finding=e["to"], strength=e["props"].get("strength")))
                elif e["edge"] == "SCOPED_TO":
                    scopes.append(dict(location=e["to"], **e["props"]))
                elif e["edge"] == "HAS_ANATOMIC_REFINEMENT_RULE":
                    rule_node = next(x for x in nodes if x.get("id") == e["to"])
                    tc = rule_node.get("target_constraint")
                    permitted = set(rule_node.get("allowed_targets", []))
                    if tc:
                        permitted.update(taxonomy_target_set(
                            anat, tc["root"], tc.get("include_root", False),
                            tc.get("include_descendants", True)))
                    refinement_rules.append({
                        "id": rule_node["id"],
                        "scope": rule_node["scope"],
                        "allowed_predicates": rule_node.get("allowed_predicates", []),
                        "allowed_targets": rule_node.get("allowed_targets", []),
                        "target_constraint": tc,
                        "traversal": rule_node.get("traversal"),
                        "permitted_targets": [
                            {"code": code_of(r), "name": nm_of(r), "id": r}
                            for r in sorted(permitted, key=nm_of)
                        ]
                    })
                elif e["edge"] == "OCCURS_WITH":
                    occurs_with.append(e["to"])
                elif e["edge"] == "COMPONENT_OF":
                    component_of.append(e["to"])
                elif e["edge"] == "HAS_VALUE_CONSTRAINT":
                    fixed_values.append(dict(value_id=e["to"],
                                             element=e["props"].get("element"),
                                             defining=e["props"].get("defining", False)))
                elif e["edge"] in ("MAY_REPRESENT", "MAY_MANIFEST_AS"):
                    represents.append(e["to"])

        for e in edges:
            if e["edge"] in ("MAY_BE_REPRESENTED_BY", "MAY_MANIFEST_AS") and e["to"] in anc:
                represents.append(e["from"])
            if e["edge"] == "MAY_CAUSE" and e["to"] in anc:
                caused_by.append(e["from"])
            if e["edge"] == "OCCURS_WITH" and e["to"] in anc:
                occurs_with.append(e["from"])

        shape = dict(
            finding_id=n["id"], name=n["name"], definition=n["definition"],
            subtype_of=parent.get(n["id"]),
            defined_concept=n.get("defined_concept", False),
            bindings=n.get("bindings", []), synonyms=n.get("synonyms", []),
            anatomic_scope=[dict(s, name=nm_of(s["location"])) for s in scopes],
            anatomic_refinement_rules=refinement_rules,
            seen_on=sorted(set(modalities)),
            subspecialty=sorted(set(subspecialties)),
            elements=[], measurements=[], assessment_schemes=[],
            components=components,
            may_represent=sorted(set(represents)),
            may_be_caused_by=sorted(set(caused_by)),
            occurs_with=sorted(set(occurs_with)),
            component_of=(component_of[0] if component_of else None),
            component=bool(n.get("component")),
            fixed_values=fixed_values,
            source_definition=n.get("source_definition"),
            concept_source=n.get("concept_source"),
            version=n["version"])
        if n.get("criterion"):
            shape["criterion"] = n["criterion"]
        if n.get("radlex_composition"):
            shape["radlex_composition"] = n["radlex_composition"]

        # A non-defining fixed value is part of the class semantics but is not
        # presented as an author-selectable DataElement. Suppress it here even
        # when the element is inherited from an ancestor.
        fixed_props = {
            fv["element"] for fv in fixed_values
            if not fv.get("defining", False) and fv.get("element")
        }
        fixed_element_ids = {
            eid for eid, de in de_index.items()
            if de.get("prop") in fixed_props
        }

        for eid, meta in elements.items():
            if eid in fixed_element_ids:
                continue
            de = de_index[eid]
            allowed = narrowings.get(eid)
            vals = [v for v in de["values"] if allowed is None or v[0] in allowed]
            ordered = all(v[4] is not None for v in de["values"])
            shape["elements"].append(dict(
                element_id=eid, name=de["name"], definition=de["definition"],
                select_cardinality="multi" if de.get("multi_select") else "single",
                narrowed=allowed is not None,
                modality_restricted_to=meta["modality"],
                inherited_from=meta["inherited_from"],
                permitted_values=[dict(
                    value_id=v[0], name=v[1], definition=v[3],
                    rank=(v[4] if ordered else None),
                    **({"exclusive": True,
                        "exclusive_note": "selecting this excludes every other value of "
                                          "this element"}
                       if de.get("exclusive_none") == v[0] else {}),
                    bindings=([binding("RADLEX", v[2], v[1])] if v[2] else []))
                    for v in vals]))
        for mid, meta in measurements.items():
            ms = next(m for m in spec.MEASUREMENTS if m["id"] == mid)
            shape["measurements"].append(dict(
                measurement_id=mid, name=ms["name"], definition=ms["definition"],
                quantity_kind=ms["quantity_kind"], permitted_units=ms["permitted_units"],
                method=ms["method"], inherited_from=meta["inherited_from"],
                components=ms.get("components", [])))
        for sid in sorted(set(schemes)):
            a = as_index[sid]
            shape["assessment_schemes"].append(dict(
                scheme_id=sid, name=a["name"], issuing_authority=a["authority"],
                scheme_version=a["scheme_version"], scope=a["scope"],
                categories=[dict(name=c[0], rank=c[2]) for c in a["categories"]]))
        compiled.append(shape)
    return compiled


if __name__ == "__main__":
    os.makedirs(f"{OUT}/graph", exist_ok=True)
    os.makedirs(f"{OUT}/compiled", exist_ok=True)
    nodes, edges, de_index, as_index = build()
    anat = json.load(open(Path(__file__).with_name("anatomy.json"), encoding="utf-8"))

    by_type = collections.Counter(n["node"] for n in nodes)
    by_edge = collections.Counter(e["edge"] for e in edges)

    json.dump({"nodes": nodes, "edges": edges,
               "stats": {"nodes_by_type": dict(by_type), "edges_by_type": dict(by_edge),
                         "total_nodes": len(nodes), "total_edges": len(edges)}},
              open(f"{OUT}/graph/definition-graph.json", "w"), indent=1)

    compiled = compile_findings(nodes, edges, de_index, as_index, anat)
    for c in compiled:
        json.dump(c, open(f"{OUT}/compiled/{c['finding_id']}-{c['name'].replace(' ', '-')}.json", "w"),
                  indent=1)
    json.dump(compiled, open(f"{OUT}/compiled/_all-findings.json", "w"), indent=1)

    comp = {f["cls"] for f in spec.FINDING_CLASSES if f.get("component")}
    standalone = [c for c in compiled if c["name"] not in
                  {f["name"] for f in spec.FINDING_CLASSES if f.get("component")}]
    components = [c for c in compiled if c not in standalone]
    json.dump({
        "value_set": "finding-classes",
        "description": ("Every FindingClass is anatomically anchored and may be emitted as an "
                        "answer, except components, which are reached only through "
                        "HAS_COMPONENT."),
        "source_version": spec.RADLEX_VERSION,
        "standalone": [{"finding_id": c["finding_id"], "name": c["name"]} for c in standalone],
        "component_only": [{"finding_id": c["finding_id"], "name": c["name"]}
                           for c in components],

        "counts": {"standalone": len(standalone), "component_only": len(components)},
    }, open(f"{OUT}/compiled/_value-set-findings.json", "w"), indent=1)

    lint_out = spec.lint()
    json.dump({"rules": spec.AUTHORING_LINT, "findings": lint_out, "clean": not lint_out,
               "note": "Authoring checks. Advisory: none is enforced by a reasoner and none "
                       "constrains what an author may write."},
              open(f"{OUT}/compiled/_authoring-lint.json", "w"), indent=1)
    print(f"\nvalue set: {len(standalone)} standalone, {len(components)} component-only")
    print(f"authoring guidance: {len(spec.PATTERNS)} patterns declared; none serialized into the graph or compiled FindingClasses")
    print(f"authoring lint: {'clean' if not lint_out else str(len(lint_out)) + ' findings'}")

    # duplication cost of the no-value-sharing rule
    from collections import defaultdict
    by_name = defaultdict(list)
    for n in nodes:
        if n["node"] == "Value":
            by_name[n["name"].lower()].append(n["id"])
    dupes = {k: v for k, v in by_name.items() if len(v) > 1}

    print("nodes by type:", dict(by_type))
    print("edges by type:", dict(by_edge))
    print(f"\ncompiled shapes: {len(compiled)}")
    for c in sorted(compiled, key=lambda x: -len(x["elements"])):
        inh = sum(1 for e in c["elements"] if e["inherited_from"] or False)
        print(f"  {c['name']:42s} elements={len(c['elements']):2d} "
              f"(inherited {inh}) values="
              f"{sum(len(e['permitted_values']) for e in c['elements']):3d} "
              f"measurements={len(c['measurements'])}")
    print(f"\nvalue nodes: {by_type['Value']}; "
          f"duplicated labels under the no-sharing rule: {len(dupes)} -> "
          f"{ {k: len(v) for k, v in dupes.items()} }")
