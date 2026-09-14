# -*- coding: utf-8 -*-
"""HermiT regression over the reduced source-faithful alpha fixture."""
from pathlib import Path
from owlready2 import get_ontology, sync_reasoner, default_world

ROOT=Path(__file__).resolve().parent.parent
FIX=ROOT/'rdfxml'/'radcde-reasoner-alpha.rdf'
CDE='https://radelement.org/ng/'
results=[]
def check(name,ok,detail=''):
    results.append((name,ok)); print(('PASS  ' if ok else 'FAIL  ')+name+((' | '+detail) if detail else ''))
onto=get_ontology(FIX.as_uri()).load()
C=lambda n: default_world[CDE+n]
with onto: sync_reasoner(infer_property_values=True,debug=0)
check('defined subtype inherits parent', C('PulmonaryNodule') in C('PartSolidPulmonaryNodule').ancestors())
fn=[p.name for p in onto.object_properties() if any('Functional' in str(x) for x in getattr(p,'is_a',[]))]
check('single-select properties functional','hasAttenuation' in fn and 'hasCalcification' not in fn)
disj=[{e.name for e in d.entities} for d in onto.disjoint_classes()]
check('value disjointness',any({'V_000010_Solid','V_000011_PartSolid'}<=s for s in disj))
check('narrowing remains advisory',bool(getattr(C('RibFracture'),'narrowsTo',[])))
check('PulmonaryNodule / PulmonaryMass disjoint',any({'PulmonaryNodule','PulmonaryMass'}<=s for s in disj))
check('3 cm criterion remains primitive',bool(getattr(C('PulmonaryNodule'),'criterion',[])) and not C('PulmonaryNodule').equivalent_to)
check('componentOf functional',any('Functional' in str(x) for x in C('componentOf').is_a))
bad=list(default_world.inconsistent_classes())
check('no unsatisfiable authored alpha classes',len(bad)==0, ', '.join(c.name for c in bad))
failed=sum(not x[1] for x in results); print(f'\n{len(results)-failed}/{len(results)} checks passed')
raise SystemExit(1 if failed else 0)
