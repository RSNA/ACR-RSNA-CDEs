# Alpha Examples Ontology Documentation Generator

This directory is named `alpha examples`.

The generated Markdown files are human-readable inspection views of the canonical alpha model. Their presentation intentionally preserves the original alpha-example format, including subtype grouping, diagnosis connections, scopes, relationship sections, value constraints, measurements, modalities, subspecialties, and compact DataElement usage tables.

## Source

The generator reads the canonical graph at:

```text
graph/definition-graph.json
```

It also reads:

```text
scripts/anatomy.json
```

for RadLex taxonomy membership used by explicitly authored anatomic refinement rules.

The examples do not independently infer anatomy relationships from RadLex. `AVAILABLE_LOCATION_REFINEMENTS` is emitted only when an explicit `AnatomicRefinementRule` permits the target concept set.

## Requirements

Python 3 is required. The generator uses only the Python standard library.

## Run

From the `alpha examples` directory:

```bash
python3 generate_ontology_docs.py
```

## Generated files

The script creates or replaces these files in the same directory:

```text
findingclass_relationships_scope_and_diagnosis.md
diagnosis_relationships_and_scope.md
dataelement_concepts.md
```

The generator derives the documents fresh from the canonical graph each time. It does not patch a previous Markdown version.

### FindingClass document

Includes:

- FindingClass scope
- explicitly permitted location refinements
- subtype grouping and indentation
- Diagnosis connections, including inherited connections
- symmetric `OCCURS_WITH` representation when declared symmetric by the graph
- `HAS_COMPONENT` and `COMPONENT_OF`
- measurements
- DataElements
- fixed DataElement value constraints
- assessment schemes
- modality through `SEEN_ON`
- subspecialty information

Anatomic refinement is intentionally explicit. Predicate selection, target selection, and traversal behavior are separate controls. A scoped anatomy alone does not authorize generation of narrower locations.

### Diagnosis document

Includes:

- scope
- etiology
- `MAY_MANIFEST_AS`
- `MAY_CAUSE`
- `MAY_PROGRESS_TO`
- assessment relationships
- DataElements associated directly with the Diagnosis
- scope of connected FindingClasses

### DataElement document

Includes:

- DataElement values
- explicit DataElement scope if present
- compact `USED_BY` table separating Diagnoses from FindingClasses

## Validation

After generation, the script prints counts for FindingClasses, Diagnoses, and DataElements. It also reports DataElements with no detected value list so that unexpected model changes are visible during review.
