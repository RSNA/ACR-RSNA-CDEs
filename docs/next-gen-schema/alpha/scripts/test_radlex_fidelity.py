# -*- coding: utf-8 -*-
"""Regression gate for direct-RadLex anatomy fidelity."""
from pathlib import Path
import json, tempfile, os
from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDFS

from radlex_config import RADLEX_NS, RADLEX_ONTOLOGY_IRI, RADLEX_VERSION
from radlex_index import load_index, anatomy_branch
import build_anatomy
from build_json import refinement_target_set

ROOT = Path(__file__).resolve().parent.parent
RDFS_SUBCLASS = str(RDFS.subClassOf)
FORBIDDEN = (
    "LOCAL_ANATOMY", "LOCAL_ANATOMY_EDGES", "radcde-anatomy",
    "https://radelement.org/ng/anatomy/", "generalPartOf", "regionalPartOf",
    "constitutionalPartOf", "cde:partOf", "cde:containedIn",
)


def fail(msg):
    raise AssertionError(msg)


def main():
    ai = load_index()
    graph = json.loads((ROOT / "graph" / "definition-graph.json").read_text())
    ttl_path = ROOT / "radcde-alpha.ttl"
    ttl_text = ttl_path.read_text()
    owl = Graph().parse(ttl_path, format="turtle")

    if (URIRef("https://radelement.org/ng/radcde-alpha"), OWL.imports,
            URIRef(RADLEX_ONTOLOGY_IRI)) not in owl:
        fail("alpha does not directly owl:import configured RadLex ontology")

    # Generated CDE ontology may reference RadLex objects but must not assert facts ON them.
    bad_subjects = [s for s,_,_ in owl if str(s).startswith(RADLEX_NS)]
    if bad_subjects:
        fail(f"generated CDE OWL asserts {len(bad_subjects)} triples with RadLex subjects")

    for term in FORBIDDEN:
        if term in ttl_text:
            fail(f"forbidden anatomy construct present in alpha OWL: {term}")

    als = [n for n in graph["nodes"] if n.get("node") == "AnatomicLocation"]
    branch = anatomy_branch(ai)
    anatomy_ids = {n["id"] for n in als}
    for n in als:
        rid=n["id"]
        if not rid.startswith("RID") or rid not in branch:
            fail(f"non-native anatomy identity: {rid}")
        if n.get("iri") != ai["classes"][rid]["iri"]:
            fail(f"IRI drift for {rid}")

    # The canonical CDE definition graph contains native anatomy references, not
    # a copied RadLex subgraph. Native anatomy-to-anatomy assertions and RadLex
    # property metadata belong to anatomy.json / RadLex.owl.
    native_graph_edges = [
        e for e in graph["edges"]
        if e["from"] in anatomy_ids and e["to"] in anatomy_ids
    ]
    if native_graph_edges:
        fail(f"canonical definition graph contains {len(native_graph_edges)} copied native anatomy edges")
    if "radlex_object_properties" in graph:
        fail("canonical definition graph duplicates RadLex object-property metadata")

    referenced = set()
    for e in graph["edges"]:
        if e["from"] in anatomy_ids or e["to"] in anatomy_ids:
            if e["from"] in anatomy_ids:
                referenced.add(e["from"])
            if e["to"] in anatomy_ids:
                referenced.add(e["to"])
    for r in [n for n in graph["nodes"] if n.get("node") == "AnatomicRefinementRule"]:
        if r.get("scope"):
            referenced.add(r["scope"])
        referenced.update(r.get("allowed_targets", []))
        tc = r.get("target_constraint") or {}
        if tc.get("root"):
            referenced.add(tc["root"])
    if anatomy_ids != referenced:
        fail(f"canonical anatomy-node set is not exactly the explicitly referenced RID set: "
             f"nodes={len(anatomy_ids)}, references={len(referenced)}")

    # Native facts and property declarations are verified against the RadLex-derived
    # index, where they now belong.
    prop_iris = set(ai["object_properties"])
    kidney_part = ("RID205", RADLEX_NS + "Part_Of", "RID204")
    kidney_contained = ("RID205", RADLEX_NS + "Contained_In", "RID431")
    indexed_native = {(e["from"], e["predicate"], e["to"]) for e in ai["relationships"]}
    if kidney_part not in indexed_native:
        fail("native kidney Part_Of urinary tract fact is missing from anatomy index")
    if kidney_contained not in indexed_native:
        fail("native kidney Contained_In retroperitoneum fact is missing from anatomy index")
    if ("RID205", RADLEX_NS + "Part_Of", "RID431") in indexed_native:
        fail("Contained_In was incorrectly substituted with Part_Of for kidney")
    regional = ("RID1016", RADLEX_NS + "Regional_Part_Of", "RID1014")
    constitutional = ("RID1016", RADLEX_NS + "Constitutional_Part_Of", "RID39952")
    if regional not in indexed_native or constitutional not in indexed_native:
        fail("Regional_Part_Of / Constitutional_Part_Of distinction regression fixture is missing")
    if ("RID1016", RADLEX_NS + "Regional_Part_Of", "RID39952") in indexed_native:
        fail("Constitutional_Part_Of was substituted with Regional_Part_Of")

    # Refinement rules must not encode a property-chain scope policy.
    if "refinementKind" in ttl_text or "propertyChainAxiom" in ttl_text:
        fail("unsupported refinementKind or implicit scope property-chain semantics remain in OWL")
    rules = [n for n in graph["nodes"] if n.get("node") == "AnatomicRefinementRule"]
    pulmonary = next((r for r in rules if r.get("id") == "ARR-000001"), None)
    if pulmonary is None:
        fail("pulmonary-nodule anatomic refinement rule ARR-000001 is missing")
    if pulmonary.get("allowed_predicates"):
        fail("pulmonary-nodule rule contains an unauthored native RadLex predicate")
    if pulmonary.get("traversal") is not None:
        fail("pulmonary-nodule rule contains unauthored traversal behavior")
    tc = pulmonary.get("target_constraint") or {}
    if tc.get("root") != "RID34694" or tc.get("include_root") is not False or tc.get("include_descendants") is not True:
        fail(f"pulmonary-nodule target taxonomy constraint drift: {tc}")

    # Target selection supports exact RIDs, taxonomy-defined sets, or both.
    exact_only = refinement_target_set(ai, {"allowed_targets": ["RID205"]})
    if exact_only != ["RID205"]:
        fail(f"exact-target-only refinement resolution failed: {exact_only}")
    combined = refinement_target_set(ai, {
        "allowed_targets": ["RID205"], "target_root": "RID34694",
        "include_root": False, "include_descendants": True})
    if "RID205" not in combined or len(combined) != 8:
        fail(f"combined exact/taxonomy refinement resolution failed: {combined}")

    # Every semantic relationship indexed must originate from a declared RadLex property.
    bad_preds = {r["predicate"] for r in ai["relationships"] if r["predicate"] not in prop_iris}
    if bad_preds:
        fail(f"undeclared relationship predicates: {sorted(bad_preds)[:5]}")
    if ai["stats"]["unindexed_restrictions"]:
        fail(f"unindexed restrictions: {ai['stats']['unindexed_restrictions']}")
    if ai["stats"]["unresolved_rids"]:
        fail(f"unresolved RadLex RIDs: {ai['stats']['unresolved_rids']}")

    # Full native anatomy fidelity is an index/source concern. The canonical
    # definition graph intentionally does not materialize those assertions.

    # Future-version regression: an unknown native property, its subproperty and inverse,
    # plus direct and restriction assertions must be discovered without code changes.
    rdf = f'''<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
 xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:r="{RADLEX_NS}">
 <owl:ObjectProperty rdf:about="{RADLEX_NS}Future_Rel">
  <rdfs:subPropertyOf rdf:resource="{RADLEX_NS}Part_Of"/>
  <owl:inverseOf rdf:resource="{RADLEX_NS}Has_Future_Rel"/>
 </owl:ObjectProperty>
 <owl:ObjectProperty rdf:about="{RADLEX_NS}Has_Future_Rel"/>
 <owl:Class rdf:about="{RADLEX_NS}RID900001"><rdfs:label xml:lang="en">future child</rdfs:label>
  <rdfs:subClassOf rdf:resource="{RADLEX_NS}RID3"/>
  <rdfs:subClassOf><owl:Restriction><owl:onProperty rdf:resource="{RADLEX_NS}Future_Rel"/>
   <owl:someValuesFrom rdf:resource="{RADLEX_NS}RID900002"/></owl:Restriction></rdfs:subClassOf>
 </owl:Class>
 <owl:Class rdf:about="{RADLEX_NS}RID900002"><rdfs:label xml:lang="en">future parent</rdfs:label>
  <rdfs:subClassOf rdf:resource="{RADLEX_NS}RID3"/></owl:Class>
 <rdf:Description rdf:about="{RADLEX_NS}RID900001"><r:Future_Rel rdf:resource="{RADLEX_NS}RID900002"/></rdf:Description>
 <owl:Class rdf:about="{RADLEX_NS}RID3"><rdfs:label xml:lang="en">anatomical entity</rdfs:label></owl:Class>
</rdf:RDF>'''
    with tempfile.NamedTemporaryFile("w", suffix=".owl", delete=False) as f:
        f.write(rdf); temp=f.name
    try:
        future = build_anatomy.build(temp)
    finally:
        os.unlink(temp)
    p = RADLEX_NS + "Future_Rel"
    if p not in future["object_properties"]:
        fail("future property was not discovered")
    pd = future["object_properties"][p]
    if RADLEX_NS + "Part_Of" not in pd.get("subPropertyOf", []):
        fail("future property subPropertyOf declaration was not preserved")
    if RADLEX_NS + "Has_Future_Rel" not in pd.get("inverseOf", []):
        fail("future property inverseOf declaration was not preserved")
    rel = [r for r in future["relationships"] if r["predicate"] == p]
    if len(rel) != 1 or set(rel[0]["forms"]) != {"direct", "restriction:someValuesFrom"}:
        fail(f"future relationship source forms not preserved: {rel}")

    print("PASS RadLex fidelity regression checks")
    print("configured version:", RADLEX_VERSION)
    print("RID classes:", f"{ai['stats']['classes']:,}")
    print("object properties:", ai['stats']['object_properties'])
    print("native semantic relationships:", f"{ai['stats']['relationships']:,}")
    print("native relationship source expressions:", f"{ai['stats']['relationship_source_expressions']:,}")
    print("RadLex anatomy branch:", f"{len(branch):,}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
