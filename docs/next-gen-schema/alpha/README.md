# RadElement next-generation alpha

This repository contains the current alpha model, its generated definition graph and compiled FindingClass shapes, validation/evaluation scripts, reduced reasoner fixtures, and supporting documentation.

## Anatomy architecture

RadLex is the single source of truth for anatomy.

`AnatomicLocation` remains a CDE model node/role type, but the actual anatomy concepts occupying that role are native RadLex classes under `RID3` (`anatomical entity`). Their identity remains the native RID and IRI. The model does not create `AL-*` anatomy concepts, a parallel CDE anatomy hierarchy, or CDE replacements for RadLex anatomy predicates.

The generated CDE OWL imports the configured RadLex ontology directly. Native RadLex taxonomy, object-property hierarchy, inverses, and relationship predicates remain unchanged. `Contained_In`, `Part_Of`, `Regional_Part_Of`, `Member_Of`, `Branch_Of`, and the other native predicates remain distinct. Missing native relationships are reported as gaps rather than repaired locally.

`graph/definition-graph.json` contains CDE-authored semantics plus only the native RIDs explicitly referenced by those definitions. `scripts/anatomy.json` is the generated read-only index of the full native RadLex anatomy branch, taxonomy, relationships, and object-property metadata. Consumers needing broader anatomy context join against that index rather than copying RadLex into the CDE definition graph.

Anatomic refinement is represented by a first-class rule that separates four concerns: starting scope, permitted exact native RadLex predicates, eligible target concepts, and traversal behavior. A taxonomy-defined target set does not imply a predicate, and a permitted predicate does not imply recursion. The current pulmonary-nodule rule preserves the lobe-of-lung target set without fabricating a native relationship.

## Main artifacts

```text
radcde-alpha.ttl                 generated CDE ontology; imports RadLex directly
radcde-probes.ttl                deliberate reasoning probes
catalog-v001.xml                 local import resolution for Turtle workflow
rdfxml/radcde-alpha.rdf          RDF/XML serialization
rdfxml/radcde-probes.rdf         RDF/XML probes
rdfxml/catalog-v001.xml          local import resolution for RDF/XML workflow
rdfxml/radcde-reasoner-alpha.rdf reduced source-faithful HermiT alpha fixture
rdfxml/radcde-reasoner-probes.rdf reduced source-faithful HermiT probe fixture
graph/definition-graph.json      canonical CDE definition graph
compiled/*.json                  resolved FindingClass shapes
SHAPE.md                         generated CDE graph/shape documentation
RADLEX-SHAPE.md                  generated native RadLex anatomy/predicate documentation
MECHANISMS.md                    generated mechanism documentation
boundaries/                      node/edge boundary documents
```

The optional `standalone/radcde-standalone.ttl` artifact is a full single-file merge of the generated CDE ontology and configured RadLex release. The modular ontology plus its direct RadLex import is authoritative. The standalone builder writes through temporary files and replaces the final Turtle atomically so an interrupted build does not leave a truncated artifact.

## RadLex source configuration

This alpha was built and verified against RadLex Release 4.3. Download the
matching release from RSNA's RadLex site, agreeing to their license there,
before configuring the build to use it.

The build discovers the bundled `references/**/RadLex.owl` by default. To point the build at another release without changing code:

```bash
export RADCDE_RADLEX_OWL=/path/to/RadLex.owl
```

`RADLEX_OWL` is accepted as a compatibility alias. Source version information is derived from the configured source path when possible.

## Rebuild

From `scripts/`:

```bash
python build_anatomy.py
python build_owl.py
python build_json.py
python evaluate_graph.py
python build_probes.py
python build_reasoner_fixture.py
python test_radlex_fidelity.py
python verify_codes.py
python build_shape.py
python build_radlex_shape.py
python build_mechanisms.py
python build_standalone.py
python test_standalone.py
cd "../alpha examples"
python generate_ontology_docs.py
cd ..
rm -f cde-node-boundaries.zip
zip cde-node-boundaries.zip boundaries/*.md
```

`build_anatomy.py` creates a read-only native RadLex index. It does not generate an anatomy ontology. The standalone file, generated example documents, and nested boundary ZIP are derived artifacts and should be refreshed when their sources change.

The current build contains 45 FindingClasses and 20 deliberate probe classes.

## Reasoner regression

The shipped alpha imports the complete configured RadLex ontology. Full HermiT classification of that entire world can be slow, so the regression suite uses reduced fixtures containing the unchanged generated CDE ontology plus only the exact native RadLex axioms exercised by the tests. Fixture construction verifies those native assertions against the configured RadLex index before serialization.

With Owlready2 available:

```bash
PYTHONPATH=/path/to/owlready2 python test_reason.py
PYTHONPATH=/path/to/owlready2 python test_probes.py
```

The reduced fixtures are testing infrastructure only. They do not replace the full RadLex import in the generated CDE ontology.

## Release gates

Before packaging, the expected checks are:

```bash
python test_radlex_fidelity.py
python verify_codes.py
python evaluate_graph.py
```

The fidelity gate fails if local anatomy identities or proxy CDE anatomy predicates appear, if the definition graph duplicates native RadLex relationship/property metadata, or if the RadLex-derived index loses native relationship types.

`verify_codes.py` checks strict RadLex bindings against the configured source's preferred labels, sanctioned synonyms, and acronyms. A CDE label may legitimately differ from the RadLex preferred label when it uses an accepted RadLex synonym; binding metadata still records the source preferred label.

## Visualizer

The visualizer consumes `graph/definition-graph.json` for CDE-authored semantics and `scripts/anatomy.json` for native RadLex display context. The canonical graph contains only native RID anatomy concepts explicitly referenced by CDE definitions. The visualizer may add native taxonomy ancestry and a limited relationship neighborhood from the RadLex index, but it must not create local anatomy concepts or rewrite predicate semantics.
