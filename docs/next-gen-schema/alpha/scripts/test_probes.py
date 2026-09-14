# -*- coding: utf-8 -*-
"""HermiT regression over reduced alpha + probe fixture."""
from pathlib import Path
from owlready2 import get_ontology, sync_reasoner, default_world

ROOT = Path(__file__).resolve().parent.parent
onto = get_ontology((ROOT / 'rdfxml' / 'radcde-reasoner-probes.rdf').as_uri()).load()
P = 'https://radelement.org/ng/probe/'
with onto:
    sync_reasoner(debug=0)
bad = {c.name for c in default_world.inconsistent_classes()}


def cls(n):
    return default_world[P + n]


def anc(n):
    return {a.name for a in cls(n).ancestors() if hasattr(a, 'name')}


passes = 0
total = 0


def report(ok, label, detail=''):
    global passes, total
    total += 1
    passes += bool(ok)
    print(('PASS' if ok else 'FAIL'), label, ('-> ' + detail if detail else ''))


A = ['A3_PartSolidByAttenuation', 'A6_CystWithMuralNodule']
B = ['B1_SolidAndPartSolid', 'B2_NoduleThatIsAMass', 'B3_RibFractureWithChronicAcuity',
     'B4_FindingThatIsAlsoADiagnosis', 'B6_SimpleCystWithMuralNodule']
for n in A:
    report(n not in bad and len(anc(n) - {'Thing', 'DefinitionEntity', 'FindingClass', 'Lesion'}) > 0,
           'A ' + n)
for n in B:
    report(n in bad, 'B ' + n)
report('B5_ThyroidNoduleInLung' not in bad, 'B B5_ThyroidNoduleInLung',
       'negative control remains satisfiable')

report('D1_FindingClassWithNoAnatomicAnchor' not in bad,
       'D D1 governance-only anchor check')

# Native anatomy facts are exercised under their exact predicates. These checks
# deliberately make no CDE traversal claim.
for n in ['E1_KidneyPartOfUrinaryTract', 'E2_KidneyContainedInRetroperitoneum']:
    report(n not in bad, 'E ' + n, 'exact native predicate remains satisfiable')

for n, want in [('E5_MultiSelectAllowsTwoValues', True),
                ('E6_SingleSelectOnAcuity', False),
                ('E7_AtelectasisAxesAreIndependent', True)]:
    sat = n not in bad
    report(sat == want, 'E ' + n, 'satisfiable' if sat else 'unsatisfiable')

report('E8_PartSolidWithItsSolidComponent' not in bad,
       'E E8_PartSolidWithItsSolidComponent')
report('PartSolidPulmonaryNodule' in anc('E9_BothValuesStatedResolveToTheSubtype'),
       'E E9 classifies as PartSolidPulmonaryNodule')
report('E10_NoCalcificationPlusAPattern' in bad,
       'E E10 none excludes sibling patterns')
report('E11_EpiduralCannotBeCrescentic' in bad,
       'E E11 epidural fixed biconvex excludes crescentic')
report('E12_SubduralCannotBeBiconvex' in bad,
       'E E12 subdural fixed crescentic excludes biconvex')

print(f'\n{passes}/{total} probes passed')
raise SystemExit(0 if passes == total else 1)
