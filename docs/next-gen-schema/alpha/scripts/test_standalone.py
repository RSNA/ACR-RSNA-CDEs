"""Verifies the merged single-file build reasons identically to the modular pair.

Checks class-level entailments and the probe outcomes. No instances: the fixtures
were removed because their representations were authored rather than derived, and
the probes make the same claims without inventing a sentence.
"""
import sys
from owlready2 import get_ontology, sync_reasoner, default_world
D = "/mnt/user-data/outputs/radcde-alpha/standalone"
CDE = "https://radelement.org/ng/"
PROBE = CDE + "probe/"
onto = get_ontology(f"file://{D}/radcde-standalone-probes.owl").load()
print("loaded standalone (no imports). classes:", len(list(onto.classes())))
with onto:
    sync_reasoner(debug=0)
bad = {c.name for c in default_world.inconsistent_classes()}

ok = 0
c = default_world[CDE + "PartSolidPulmonaryNodule"]
anc = {a.name for a in c.ancestors() if hasattr(a, "name")}
t = "PulmonaryNodule" in anc
print(("PASS" if t else "FAIL"), "- defined subtypes classify in the merged file")
ok += t

exp_red = {"B1_SolidAndPartSolid", "B2_NoduleThatIsAMass", "B3_RibFractureWithChronicAcuity",
           "B4_FindingThatIsAlsoADiagnosis", "B6_SimpleCystWithMuralNodule",
           "C2_IdentityPreservingProgression"}
red = {n for n in bad if n[0] in "BC"}
t = red == exp_red
print(("PASS" if t else "FAIL"), f"- probes under owl:Nothing: {sorted(red)}")
ok += t

t = "B5_ThyroidNoduleInLung" not in bad and "D1_FindingClassWithNoAnatomicAnchor" not in bad
print(("PASS" if t else "FAIL"), "- negative controls stay satisfiable")
ok += t
print(f"\n{ok}/3 standalone checks passed")
sys.exit(0 if ok == 3 else 1)
