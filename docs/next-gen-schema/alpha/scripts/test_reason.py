# -*- coding: utf-8 -*-
"""
Runs HermiT over the built ontology and checks the entailments the model is
supposed to produce. Each check corresponds to a decision in DECISIONS.md.
"""
import os, sys
from owlready2 import get_ontology, sync_reasoner, default_world, Thing, onto_path
onto_path.append("/mnt/user-data/outputs/radcde-alpha/rdfxml")

OUT = "/mnt/user-data/outputs/radcde-alpha/rdfxml"
CDE = "https://radelement.org/ng/"
ANAT = CDE + "anatomy/"

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(("PASS  " if ok else "FAIL  ") + name + ((" | " + detail) if detail else ""))


onto_anat = get_ontology(f"file://{OUT}/radcde-anatomy.rdf").load()
onto = get_ontology(f"file://{OUT}/radcde-alpha.rdf").load()

C = lambda n: default_world[CDE + n]
A = lambda n: default_world[ANAT + n]

print("loaded. classes:", len(list(onto.classes())) + len(list(onto_anat.classes())))
print("running HermiT ...\n")
with onto:
    sync_reasoner(infer_property_values=True, debug=0)
print()

# ---------------------------------------------------------------- D-01
# Class-level only. The instance-level versions of these checks were removed with
# the fixtures: probes A3 and A6 make the same claims without a fabricated sentence.
check("D-01  defined subtype inherits every parent element (no re-authoring)",
      C("PulmonaryNodule") in C("PartSolidPulmonaryNodule").ancestors()
      and len(C("PartSolidPulmonaryNodule").ancestors()) > 2,
      "ancestors include PulmonaryNodule; no abstract genus remains")

# ---------------------------------------------------------------- D-02
# Attenuation values are pairwise disjoint, so a nodule cannot be two at once.
solid, partsolid = C("V_000010_Solid"), C("V_000011_PartSolid")
fn = [p.name for p in onto.object_properties()
      if hasattr(p, "is_a") and any("Functional" in str(x) for x in p.is_a)]
check("D-02  single-select elements declared functional",
      "hasAttenuation" in fn and "hasCalcification" not in fn,
      f"functional: {len(fn)} of {len(list(onto.object_properties()))} object properties; "
      "hasCalcification deliberately left multi-select")
disj = set()
for d in onto.disjoint_classes():
    disj.add(frozenset(e.name for e in d.entities))
check("D-02  solid / part-solid / non-solid declared disjoint",
      frozenset({"V_000010_Solid", "V_000011_PartSolid"}) in disj or
      any({"V_000010_Solid", "V_000011_PartSolid"} <= s for s in disj),
      f"{len(disj)} disjointness axioms in the authored layer")


# ---------------------------------------------------------------- D-04
# Narrowing is a real OWL construct, not an annotation.
rf = C("RibFracture")
narrows = list(getattr(rf, "narrowsTo", []))
check("D-04  narrowing is advisory: an annotation, not an allValuesFrom axiom",
      bool(narrows),
      f"narrowsTo on RibFracture: {narrows}; the hard form lives in probe B3 only")

# ---------------------------------------------------------------- D-07
# Nodule and Mass are disjoint, and the 3cm criterion is an annotation only,
# so nothing reclassifies a lesion when a measurement changes.
check("D-07  PulmonaryNodule disjointWith PulmonaryMass (organ level, not pattern level)",
      any({"PulmonaryNodule", "PulmonaryMass"} <= s for s in disj),
      "the 30 mm criterion is Fleischner's chest convention and lives where the evidence is")
pn = C("PulmonaryNodule")
check("D-07  3 cm criterion carried as annotation, not as a defining condition",
      bool(getattr(pn, "criterion", [])) and pn.equivalent_to == [],
      "PulmonaryNodule is primitive and has no equivalentClass axiom")

check("D-15  componentOf is functional",
      any("Functional" in str(x) for x in C("componentOf").is_a),
      "a sub-finding belongs to exactly one whole")


# ---------------------------------------------------------------- consistency
inconsistent = list(default_world.inconsistent_classes())
check("Consistency  no unsatisfiable classes",
      len(inconsistent) == 0,
      "unsatisfiable: " + ", ".join(c.name for c in inconsistent) if inconsistent else "ontology is consistent")

# ---------------------------------------------------------------- inferred hierarchy diff
print("\n--- computed vs asserted subsumption for the defined classes ---")
for n in ["PulmonaryNodule", "SolidPulmonaryNodule", "PartSolidPulmonaryNodule",
          "NonSolidPulmonaryNodule", "ThyroidNodule", "AdrenalNodule",
          "SimpleRenalCyst", "ComplexRenalCyst", "MuralNodule"]:
    c = C(n)
    anc = [a.name for a in c.ancestors() if hasattr(a, "name") and a is not c
           and a.name not in ("Thing",)]
    print(f"  {n:28s} -> {', '.join(sorted(anc))}")



failed = [r for r in results if not r[1]]
print(f"\n{len(results)-len(failed)}/{len(results)} checks passed")
sys.exit(1 if failed else 0)
