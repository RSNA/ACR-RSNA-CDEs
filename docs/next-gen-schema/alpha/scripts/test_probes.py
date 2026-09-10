import sys
from owlready2 import get_ontology, sync_reasoner, default_world, onto_path
onto_path.append("/mnt/user-data/outputs/radcde-alpha/rdfxml")
onto = get_ontology("file:///mnt/user-data/outputs/radcde-alpha/rdfxml/radcde-probes.rdf").load()
PROBE="https://radelement.org/ng/probe/"; CDE="https://radelement.org/ng/"
print("running HermiT over alpha + anatomy + probes ...")
with onto: sync_reasoner(debug=0)
bad = {c.name for c in default_world.inconsistent_classes()}
print()
EXPECT_A=["A1_NoduleInRightUpperLobe","A2_NoduleInSuperiorSegmentRLL","A3_PartSolidByAttenuation","A4_NoduleInLocalSubpleuralRegion","A5_NoduleInThyroidLobe","A6_CystWithMuralNodule"]
EXPECT_B=["B1_SolidAndPartSolid","B2_NoduleThatIsAMass","B3_RibFractureWithChronicAcuity","B4_FindingThatIsAlsoADiagnosis","B6_SimpleCystWithMuralNodule"]
ok=0; tot=0
for n in EXPECT_A:
    c=default_world[PROBE+n]; tot+=1
    anc=sorted({a.name for a in c.ancestors() if hasattr(a,'name') and a is not c and a.name not in("Thing","DefinitionEntity")})
    sat = n not in bad
    good = sat and len([a for a in anc if a not in ("FindingClass","Lesion")])>0
    ok+=good
    print(f"{'PASS' if good else 'FAIL'}  A {n:42s} -> {', '.join(anc) if sat else 'UNSATISFIABLE'}")
for n in EXPECT_B:
    c=default_world[PROBE+n]; tot+=1
    good = n in bad; ok+=good
    print(f"{'PASS' if good else 'FAIL'}  B {n:42s} -> {'unsatisfiable (caught)' if good else 'SATISFIABLE - constraint not enforced'}")
n="B5_ThyroidNoduleInLung"; tot+=1
good = n not in bad; ok+=good
print(f"{'PASS' if good else 'FAIL'}  B {n:42s} -> {'satisfiable, as expected (negative control)' if good else 'unexpectedly unsatisfiable'}")
print(f"\n{ok}/{tot} probes behaved as designed")

print()
for n,exp in [("C1_NoduleProgressingToMass",True),("C2_IdentityPreservingProgression",False),("C3_ProgressionWithinOneClass",True)]:
    sat = n not in bad
    print(f"{'PASS' if sat==exp else 'FAIL'}  C {n:38s} -> {'satisfiable' if sat else 'UNSATISFIABLE'} (expected {'satisfiable' if exp else 'unsatisfiable'})")

n="D1_FindingClassWithNoAnatomicAnchor"; sat = n not in bad
print(f"{'PASS' if sat else 'FAIL'}  D {n:38s} -> {'satisfiable, as expected (governance flag, not an axiom)' if sat else 'unexpectedly unsatisfiable'}")

print()
E = default_world[PROBE+"E1_ScopeDoesNotTravelAlongContainedIn"]
E2 = default_world[PROBE+"E2_ScopedToAbdomen"]
E3 = default_world[PROBE+"E3_ScopeTravelsAlongLocalGapFill"]
E4 = default_world[PROBE+"E4_ScopedToLung"]
t = E2 not in E.ancestors()
print(f"{'PASS' if t else 'FAIL'}  E E1: kidney scope does NOT reach abdomen (containedIn not chased)")
t2 = E4 in E3.ancestors()
print(f"{'PASS' if t2 else 'FAIL'}  E E3: lung-parenchyma scope DOES reach lung (gap-fill edge holds)")
for n, want_sat in [("E5_MultiSelectAllowsTwoValues",True),("E6_SingleSelectOnAcuity",False),
                    ("E7_AtelectasisAxesAreIndependent",True)]:
    sat = n not in bad
    print(f"{'PASS' if sat==want_sat else 'FAIL'}  E {n:40s} -> {'satisfiable' if sat else 'unsatisfiable'}")
n="E8_PartSolidWithItsSolidComponent"; sat = n not in bad
print(f"{'PASS' if sat else 'FAIL'}  E {n:40s} -> {'satisfiable: two entities resolve it' if sat else 'UNSATISFIABLE'}")
n="E9_BothValuesStatedResolveToTheSubtype"
c=default_world[PROBE+n]
anc={a.name for a in c.ancestors() if hasattr(a,'name')}
t = n not in bad and "PartSolidPulmonaryNodule" in anc
print(f"{'PASS' if t else 'FAIL'}  E {n:40s} -> {'classifies as PartSolidPulmonaryNodule' if t else sorted(anc)}")
n="E10_NoCalcificationPlusAPattern"; sat = n not in bad
print(f"{'PASS' if not sat else 'FAIL'}  E {n:40s} -> {'unsatisfiable: none excludes the siblings' if not sat else 'SATISFIABLE, exclusion not enforced'}")
