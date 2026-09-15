# -*- coding: utf-8 -*-
"""Build small, source-faithful HermiT fixtures.

The shipped ontology continues to import the complete configured RadLex release.
These fixtures exist only so CI/tests can reason within practical runtime limits.
They remove the full import and embed the exact native RadLex axioms exercised by
our regression probes. No synthetic anatomy relationship is permitted.
"""
from pathlib import Path
from rdflib import Graph, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL
from radlex_config import RADLEX_NS, RADLEX_ONTOLOGY_IRI
from radlex_index import load_index

ROOT=Path(__file__).resolve().parent.parent
ALPHA=ROOT/'radcde-alpha.ttl'
PROBES=ROOT/'radcde-probes.ttl'
OUT=ROOT/'rdfxml'

# Exact native assertions needed by the anatomy fidelity probes. They are kept
# under their exact source predicates. No application traversal family is created.
RELATIONSHIPS = [
    ('RID205','Part_Of','RID204'),
    ('RID205','Contained_In','RID431'),
]

def restriction(g, s, pred, target):
    r=BNode(); g.add((r,RDF.type,OWL.Restriction)); g.add((r,OWL.onProperty,URIRef(pred)))
    g.add((r,OWL.someValuesFrom,URIRef(RADLEX_NS+target))); g.add((URIRef(RADLEX_NS+s),RDFS.subClassOf,r))

def add_radlex_subset(g, include_native_probe_axioms):
    ai=load_index()
    # Declare every RadLex RID already referenced by the generated CDE/probe graph.
    refs=set()
    for s,p,o in list(g):
        for term in (s,o):
            if isinstance(term,URIRef) and str(term).startswith(RADLEX_NS+'RID'):
                refs.add(str(term).rsplit('/',1)[-1])
    for rid in refs:
        if rid not in ai['classes']:
            raise AssertionError(f'fixture references unknown RadLex class {rid}')
        g.add((URIRef(ai['classes'][rid]['iri']),RDF.type,OWL.Class))

    # Declare only the exact native object properties exercised by the fixture,
    # preserving their source declarations without expanding a hierarchy into an
    # application traversal policy.
    wanted = {RADLEX_NS + pname for _, pname, _ in RELATIONSHIPS}
    for iri in sorted(wanted):
        pd = ai['object_properties'].get(iri)
        if not pd:
            raise AssertionError(f'fixture references unknown RadLex property {iri}')
        g.add((URIRef(iri), RDF.type, OWL.ObjectProperty))
        for parent in pd.get('subPropertyOf', []):
            g.add((URIRef(iri), RDFS.subPropertyOf, URIRef(parent)))
        for inverse in pd.get('inverseOf', []):
            g.add((URIRef(iri), OWL.inverseOf, URIRef(inverse)))

    if not include_native_probe_axioms:
        return
    rel={(e['from'],e['predicate'],e['to']) for e in ai['relationships']}
    for child,pname,parent in RELATIONSHIPS:
        pred=RADLEX_NS+pname
        if (child,pred,parent) not in rel: raise AssertionError(f'native RadLex assertion missing: {child} {pname} {parent}')
        restriction(g,child,pred,parent)


def base(with_probes=False):
    g=Graph().parse(ALPHA,format='turtle')
    alpha=URIRef('https://radelement.org/ng/radcde-alpha')
    g.remove((alpha,OWL.imports,URIRef(RADLEX_ONTOLOGY_IRI)))
    if with_probes:
        pg=Graph().parse(PROBES,format='turtle')
        for t in pg: g.add(t)
        probe_ont=URIRef('https://radelement.org/ng/radcde-probes')
        g.remove((probe_ont,OWL.imports,alpha))
    add_radlex_subset(g, include_native_probe_axioms=with_probes)
    return g

def main():
    OUT.mkdir(exist_ok=True)
    a=base(False); p=base(True)
    a.serialize(OUT/'radcde-reasoner-alpha.rdf',format='xml')
    p.serialize(OUT/'radcde-reasoner-probes.rdf',format='xml')
    print('alpha fixture triples:',len(a))
    print('probe fixture triples:',len(p))

if __name__=='__main__': main()
