# Alpha Examples Ontology Documentation Generator

This directory is expected to be named `alpha examples`.

Keep the Turtle ontology file and `generate_ontology_docs.py` in the same directory.

## Requirements

Python 3 and `rdflib` are required.

Install `rdflib` if needed:

```bash
python3 -m pip install rdflib
```

## Directory layout

Example:

```text
alpha examples/
├── alpha-turtle.ttl
├── generate_ontology_docs.py
└── README.md
```

## Run

From the `alpha examples` directory:

```bash
python3 generate_ontology_docs.py
```

If no filename is supplied, the script automatically uses the most recently modified `.ttl` file in the same directory.

You can also specify the Turtle file explicitly:

```bash
python3 generate_ontology_docs.py "alpha-turtle.ttl"
```

## Generated files

The script creates or replaces these files in the same directory:

```text
findingclass_relationships_scope_and_diagnosis.md
diagnosis_relationships_and_scope.md
dataelement_concepts.md
```

The generator derives the documents fresh from the Turtle file each time. It does not patch a previous Markdown version.

### FindingClass document

Includes:

- FindingClass scope
- constrained available location refinements
- subtype grouping and indentation
- Diagnosis connections
- symmetric `OCCURS_WITH` representation when declared symmetric by the ontology
- `COMPONENT_OF`
- measurements
- DataElements
- modality through `SEEN_ON`
- subspecialty information

Location refinement is intentionally conservative. Anatomical containment alone is not treated as proof that a structure is a valid authoring location. The generator includes named specialization, explicit regional subdivisions, and regional/lobar/segmental anatomy rather than every `partOf` descendant.

### Diagnosis document

Includes:

- scope
- etiology
- `MAY_MANIFEST_AS`
- `MAY_CAUSE`
- `MAY_PROGRESS_TO`
- assessment relationships
- DataElements associated directly with the Diagnosis

### DataElement document

Includes:

- DataElement values
- explicit DataElement scope if one is present in the ontology
- compact `USED_BY` table separating Diagnoses from FindingClasses

## Validation

After generation, the script prints counts for FindingClasses, Diagnoses, and DataElements.

It also prints warnings when an expected ontology structure changes in a way that may require reviewing the generator, such as:

- no FindingClasses, Diagnoses, or DataElements being detected
- `occursWith` existing but no longer being declared symmetric
- a DataElement having no detected value list

Review any warning before treating the generated Markdown as current documentation.
