# -*- coding: utf-8 -*-
"""Generate RADLEX-SHAPE.md from the native RadLex index."""
import json, collections, datetime
from pathlib import Path
from radlex_config import RADLEX_VERSION
from radlex_index import anatomy_branch

ROOT=Path(__file__).resolve().parent.parent
RDFS_SUBCLASS="http://www.w3.org/2000/01/rdf-schema#subClassOf"

def short(iri):
    return iri.rsplit('/',1)[-1].rsplit('#',1)[-1]

def main():
    ai=json.load(open(Path(__file__).with_name('anatomy.json'), encoding='utf-8'))
    branch=anatomy_branch(ai)
    rel=[r for r in ai['relationships'] if r['from'] in branch and r['to'] in branch]
    counts=collections.Counter(r['predicate'] for r in rel)
    L=[]; w=L.append
    w('# Native RadLex anatomy shape')
    w('')
    w(f'Generated on {datetime.date.today().isoformat()} from configured RadLex {RADLEX_VERSION}. Do not hand-edit.')
    w('')
    w('This document describes the imported RadLex side of the model. These are native RadLex classes and predicates, not CDE-defined relationships. Predicate identity is preserved exactly. `rdfs:subPropertyOf` and `owl:inverseOf` are ontology metadata and do not, by themselves, authorize an application to substitute predicates or recursively traverse them.')
    w('')
    w('## Anatomy branch')
    w('')
    w(f'- Native RadLex classes: **{len(ai["classes"]):,}**')
    w(f'- RID3 anatomical-entity branch: **{len(branch):,}**')
    w(f'- Native object properties declared by RadLex: **{len(ai["object_properties"]):,}**')
    w(f'- Native semantic relationships in the full index: **{len(ai["relationships"]):,}**')
    w(f'- Distinct native predicates used between RID3 anatomy concepts: **{len(counts):,}**')
    w('')
    w('## Native object properties')
    w('')
    w('| Property | Anatomy assertions | subPropertyOf | inverseOf | Domain | Range | OWL characteristics |')
    w('|---|---:|---|---|---|---|---|')
    for iri,p in sorted(ai['object_properties'].items(), key=lambda kv:(short(kv[0]).lower(),kv[0])):
        w('| `%s` | %d | %s | %s | %s | %s | %s |' % (
            iri, counts.get(iri,0),
            ', '.join('`'+x+'`' for x in p.get('subPropertyOf',[])) or '—',
            ', '.join('`'+x+'`' for x in p.get('inverseOf',[])) or '—',
            ', '.join('`'+x+'`' for x in p.get('domain',[])) or '—',
            ', '.join('`'+x+'`' for x in p.get('range',[])) or '—',
            ', '.join(p.get('characteristics',[])) or '—'))
    w('')
    w('## Canonical-graph representation')
    w('')
    w('The canonical CDE definition graph materializes only native RID anatomy concepts explicitly referenced by CDE definitions. Full native taxonomy edges, object-property assertions, and object-property declarations remain in `scripts/anatomy.json` and the untouched RadLex source. Consumers that need RadLex context join against that index rather than relying on a copied RadLex subgraph.')
    w('')
    w('No CDE `PART_OF`, `ANATOMY_RELATION`, `Contained_In` proxy, or other flattened anatomy predicate is created.')
    (ROOT/'RADLEX-SHAPE.md').write_text('\n'.join(L)+'\n', encoding='utf-8')
    print(f'RADLEX-SHAPE.md written: {len(L)} lines')

if __name__=='__main__': main()
