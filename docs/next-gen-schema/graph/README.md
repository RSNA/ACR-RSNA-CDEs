---
type: Reference
title: The Canonical Graph
description: The canonical JSON Lines form of the vocabulary - files, line shapes, ordering rules, identifier blocks, and the commands that validate, normalize, and dump it.
tags: [next-gen-schema, graph, canonical-form, reference]
status: draft
generated: { by: "claude-code/claude-fable-5.1", at: 2026-09-02 }
---

# The canonical graph

This directory holds the vocabulary as the canonical form of [03 §6.2](../03-draft-structures.md): JSON Lines, one object per line, nodes before edges, deterministic order. These files are what the site, the constellation diagrams, and the validator read. They are authored by hand (or by a script) and then normalized.

```
python3 docs/next-gen-schema/tools/graph.py check       # validate and report drift from canonical order
python3 docs/next-gen-schema/tools/graph.py normalize   # rewrite every file in canonical order
python3 docs/next-gen-schema/tools/graph.py dump        # the merged graph, including the converted example specs
```

The six interim specs under [`../examples/`](../examples/) are converted into graph lines at load time by `tools/spec_to_graph.py`, so the merged graph covers everything; the specs remain the source for the dossier diagrams until the renderer reads the graph ([06 §4](../06-next-steps.md)).

## Files

| File | Holds |
|---|---|
| `core.jsonl` | the relationship types, shared data elements not defined by a spec (change from prior, size (qualitative), distribution, length), the anatomy nodes the examples use, the kidney bindings, and placeholder concept nodes |
| `pyelonephritis.jsonl` | the acute pyelonephritis constellation ([08](../08-worked-examples.md)) |
| `pleural-effusion.jsonl` | the pleural effusion family and its causes ([08](../08-worked-examples.md)) |
| `concepts.jsonl` | the context concept lookup table: RadLex nodes (with `RID` ids) for modality, body region, and subspecialty; provisional owned nodes (`RDE2_0010xx` to `0014xx`) for etiology, sex specificity, age profile, and time course, seeded from the OIFM lists. Each carries `aliases` the spec converter resolves (`CT`, `chest`, `neoplastic : benign`) |

## Line shapes

A node: `{"node": "<Type>", "id": "...", "name": "...", ...scalars}`. Types: `FindingClass` (with `entity_type`), `Diagnosis`, `Grouping`, `DataElement`, `Value`, `AnatomicLocation`, `Concept` (with `scheme`), `RelationshipType`. Node properties are scalars or lists of scalars; `synonyms` is a list of `{term, type}`.

An edge: `{"edge": "<TYPE>", "from": "<id>", "to": "<id>", "id": "<optional reified id>", "props": {...}}`. Every edge type must be declared as a `RelationshipType` node, which records its inverse, symmetry, formal name, domain and range, and the properties it may carry. `exactMatch` and `closeMatch` target an external code written `SYSTEM:code` and carry the source term in `props.display`. `INTERPRETED_FROM` targets a binding, that is the `id` of a `HAS_ELEMENT` edge.

## Order

Nodes sorted by `id`; then edges sorted by `(edge, from, to, id)`; keys sorted within each object; compact separators; UTF-8 with no escaping. `graph.py normalize` produces exactly this and the bundle checker fails if a file drifts from it, so a diff on these files is always a semantic diff.

## Adding a node

Write the node and its edges into the family's file, look up its codes under the policy of [03 §2.1](../03-draft-structures.md) (mechanics in [`tools/README.md`](../tools/README.md)), point context edges at entries in `concepts.jsonl`, run `graph.py normalize`, regenerate any committed diagram the node appears in, and run the bundle checker.

## Identifiers

All owned nodes and reified edges share the `RDE2_NNNNNN` space. No registry exists yet ([06 §4](../06-next-steps.md)); the validator rejects duplicates across files, which is the interim registry. Blocks used so far, all invented for the examples:

| Range | Used for |
|---|---|
| `RDE2_0000xx` | shared elements and the bindings that carry ids (`000830` kidney length, `000831` bile duct caliber) |
| `RDE2_0001xx` | pulmonary and thyroid nodule classes and their inline elements |
| `RDE2_0005xx` | the pleural effusion family, its elements, subtypes, and causes |
| `RDE2_0006xx`, `0007xx` | classes named by the earlier specs |
| `RDE2_0008xx` | the pyelonephritis family |
| `RDE2_0009xx` | reified relationships |
| `RDE2_0010xx` to `0014xx` | provisional context concepts (etiology, sex, age, time course duration and modifiers) |

Anatomy nodes keep their RadLex `RID` ids, and so do the modality, region, and subspecialty concepts. A `Scheme-slug` id only appears when a spec names a concept the lookup table lacks; the validator treats it as a placeholder to resolve. Stubs that a spec only names carry `STUB-` ids and are meant to be replaced.

Sided anatomy records retain `side` and `unsided` properties for convenient display and lookup, while explicit `SUBTYPE_OF` edges carry the graph semantics. The two forms are deliberately redundant.
