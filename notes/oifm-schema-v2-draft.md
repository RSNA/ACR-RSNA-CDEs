---
type: Reference
title: FindingModel Source Schema v2 Draft
description: Proposed OIFM source-format and supporting file schemas for FindingModel authoring. Copy of the upstream gist.
resource: "https://gist.github.com/talkasab/8648a8887e4ee6ce381375485bc280c7"
tags: [oifm, reference, schema]
status: stable
retrieved: 2026-07-29
---

# FindingModel Source Schema v2 Draft

**Status:** Draft for review
**Date:** 2026-04-20
**Scope:** Proposed source-format and related file schemas for FindingModel authoring

## Purpose

This document describes the proposed updated schema for FindingModel source files and the closely related supporting file types that make the source format work:

- source FindingModel files
- canonical attribute definition files
- hydrated/resolved FindingModel output
- relationship-type registry
- quantity-kind registry
- per-model history sidecars

This is a proposed authoring schema, not an implementation-complete contract yet. It reflects the current agreed direction in `tasks/finding-model-schema-v2-migration-plan.md`.

## Core Concepts

### Source model vs hydrated model

- A **source model** is the authored `.fm.json` file stored in the corpus.
- A **hydrated model** is the fully resolved model after canonical attribute references have been expanded.
- Hydrated attributes should look like the current concrete attribute shape already used by `FindingModelFull`.
- Runtime APIs and indexing should operate on hydrated models, not raw source models with unresolved canonical references.

### Canonical attribute reuse

- Shared standard attributes such as `presence` and `change from prior` should be defined once in separate canonical attribute files.
- A source model may refer to a canonical attribute instead of redefining it inline.
- A canonical reference may override:
  - the attribute `description`
  - choice-value descriptions via `value_descriptions`
- Canonical references do **not** allow structural overrides in v2.

### Relationship authorship

- Source `.fm.json` files store only the relationship assertions authored on that model.
- Authors should not manually maintain both sides of inverse pairs.
- Tooling derives inverse or symmetric relationship views using the relationship registry.

### Identifier rules

- Source model files use OIFM-based filenames: `<OIFM_ID>.fm.json`
- Canonical attribute files use OIFMA-based filenames: `<OIFMA_ID>.attribute.json`
- Canonical attributes and model-local instantiated attributes use the same OIFMA format, but they must never share the same value.

## File Layout

Expected corpus layout:

```text
models/
  OIFM_OIDM_000100.fm.json
  OIFM_OIDM_000100.history.jsonl
  OIFM_OIDM_000110.fm.json
attributes/
  OIFMA_OIDM_000001.attribute.json
  OIFMA_OIDM_000002.attribute.json
registries/
  relationship_types.json
  quantity_kinds.json
```

## 1. Source FindingModel File

### Top-level shape

```json
{
  "schema_version": "2.0",
  "oifm_id": "OIFM_OIDM_000100",
  "name": "pulmonary embolism",
  "description": "Pulmonary embolism is the occlusion of a pulmonary artery or one of its branches.",
  "synonyms": ["PE"],
  "tags": ["vascular", "thoracic"],
  "references": [
    {
      "url": "https://radiopaedia.org/articles/pulmonary-embolism",
      "title": "Pulmonary embolism",
      "description": "General overview and imaging features"
    }
  ],
  "lifecycle": {
    "status": "active"
  },
  "related_models": [
    {
      "relationship_type": "occurs_with",
      "oifm_id": "OIFM_OIDM_000321",
      "display": "right heart strain"
    }
  ],
  "attributes": [
    {
      "canonical_oifma_id": "OIFMA_OIDM_000001",
      "canonical_version": "1.0.0",
      "oifma_id": "OIFMA_OIDM_100001",
      "description": "Presence or absence of pulmonary embolism",
      "value_descriptions": {
        "absent": "Pulmonary embolism is absent",
        "present": "Pulmonary embolism is present",
        "indeterminate": "Presence of pulmonary embolism cannot be determined",
        "unknown": "Presence of pulmonary embolism is unknown"
      }
    },
    {
      "canonical_oifma_id": "OIFMA_OIDM_000002",
      "canonical_version": "1.0.0",
      "oifma_id": "OIFMA_OIDM_100002",
      "description": "Whether and how a pulmonary embolism has changed over time",
      "value_descriptions": {
        "unchanged": "Pulmonary embolism is unchanged",
        "stable": "Pulmonary embolism is stable",
        "new": "Pulmonary embolism is new",
        "resolved": "Pulmonary embolism seen on a prior exam has resolved",
        "increased": "Pulmonary embolism has increased",
        "decreased": "Pulmonary embolism has decreased"
      }
    },
    {
      "oifma_id": "OIFMA_OIDM_100003",
      "name": "embolus size",
      "type": "numeric",
      "description": "Estimated maximal size of the pulmonary embolus.",
      "synonyms": ["clot size"],
      "minimum": 0,
      "maximum": 999,
      "quantity_kind": "length",
      "common_units": ["mm", "cm"]
    }
  ]
}
```

### Top-level fields

| Field | Type | Required | Notes |
|---|---|---:|---|
| `schema_version` | string | yes | Must be `"2.0"` for v2 source files |
| `oifm_id` | string | yes | OIFM-format identifier |
| `name` | string | yes | Canonical finding-model name |
| `description` | string | yes | Textbook-style description of the finding |
| `synonyms` | list[string] | no | Model-level alternate names |
| `tags` | list[string] | no | Existing tag concept retained |
| `references` | list[`WebReference`] | no | Model-level references only in v2 |
| `lifecycle` | object | no | Active/deprecated metadata |
| `related_models` | list[`RelatedModelRef`] | no | Authored relationship assertions |
| `attributes` | list[`AttributeSource`] | yes | Inline attributes or canonical references |

### Lifecycle object

```json
{
  "status": "deprecated",
  "deprecated_reason": "Split into acute and chronic variants",
  "replaced_by_oifm_id": "OIFM_OIDM_000110",
  "deprecated_at": "2026-04-20"
}
```

| Field | Type | Required | Notes |
|---|---|---:|---|
| `status` | string | yes | `active` or `deprecated` |
| `deprecated_reason` | string | no | Optional explanation |
| `replaced_by_oifm_id` | string | no | Must target an existing OIFM model |
| `deprecated_at` | string | no | ISO date string |

### Related model reference

```json
{
  "relationship_type": "type_of",
  "oifm_id": "OIFM_OIDM_000100",
  "display": "pulmonary embolism"
}
```

| Field | Type | Required | Notes |
|---|---|---:|---|
| `relationship_type` | string | yes | Must exist in relationship registry |
| `oifm_id` | string | yes | Existing target model |
| `display` | string | yes | Human-readable label for target |

## 2. Attribute Source Variants

The `attributes` array contains a structural union. No explicit `kind` field is required.

- If an object contains `canonical_oifma_id`, it is a canonical attribute reference.
- Otherwise it is an inline attribute and must contain `type`.

### 2.1 Canonical attribute reference

```json
{
  "canonical_oifma_id": "OIFMA_OIDM_000001",
  "canonical_version": "1.0.0",
  "oifma_id": "OIFMA_OIDM_100001",
  "description": "Presence or absence of pulmonary embolism",
  "value_descriptions": {
    "absent": "Pulmonary embolism is absent",
    "present": "Pulmonary embolism is present",
    "indeterminate": "Presence of pulmonary embolism cannot be determined",
    "unknown": "Presence of pulmonary embolism is unknown"
  }
}
```

| Field | Type | Required | Notes |
|---|---|---:|---|
| `canonical_oifma_id` | string | yes | OIFMA-format ID of canonical attribute definition |
| `canonical_version` | string | yes | Version of canonical definition being referenced |
| `oifma_id` | string | yes | Local instantiated attribute ID on this model |
| `description` | string | no | Overrides canonical attribute description |
| `value_descriptions` | object | no | Map of canonical choice-value name → replacement description |

### 2.2 Inline choice attribute

```json
{
  "oifma_id": "OIFMA_OIDM_100010",
  "name": "location",
  "type": "choice",
  "description": "Anatomic location of the embolus.",
  "synonyms": ["embolus location"],
  "max_selected": 3,
  "values": [
    {
      "name": "main pulmonary artery",
      "description": "Embolus is located in the main pulmonary artery.",
      "synonyms": ["main PA"]
    },
    {
      "name": "lobar artery",
      "description": "Embolus is located in a lobar pulmonary artery."
    },
    {
      "name": "segmental artery",
      "description": "Embolus is located in a segmental pulmonary artery."
    }
  ]
}
```

| Field | Type | Required | Notes |
|---|---|---:|---|
| `oifma_id` | string | yes | Local attribute ID |
| `name` | string | yes | Attribute name |
| `type` | string | yes | Must be `"choice"` |
| `description` | string | no | Attribute description |
| `synonyms` | list[string] | no | Attribute-level synonyms |
| `max_selected` | integer | no | Defaults to 1 if omitted |
| `values` | list[`ChoiceValueSource`] | yes | At least two values |

### 2.3 Inline numeric attribute

```json
{
  "oifma_id": "OIFMA_OIDM_100003",
  "name": "embolus size",
  "type": "numeric",
  "description": "Estimated maximal size of the pulmonary embolus.",
  "synonyms": ["clot size"],
  "minimum": 0,
  "maximum": 999,
  "quantity_kind": "length",
  "common_units": ["mm", "cm"]
}
```

| Field | Type | Required | Notes |
|---|---|---:|---|
| `oifma_id` | string | yes | Local attribute ID |
| `name` | string | yes | Attribute name |
| `type` | string | yes | Must be `"numeric"` |
| `description` | string | no | Attribute description |
| `synonyms` | list[string] | no | Attribute-level synonyms |
| `minimum` | number | no | Lower bound |
| `maximum` | number | no | Upper bound |
| `quantity_kind` | string | yes | Must exist in quantity-kind registry |
| `common_units` | list[string] | no | Suggested common units such as `["mm", "cm"]` |

### 2.4 Choice value source

```json
{
  "name": "absent",
  "description": "Pulmonary embolism is absent",
  "synonyms": ["not present"]
}
```

| Field | Type | Required | Notes |
|---|---|---:|---|
| `name` | string | yes | Stable canonical value name when used in canonical attributes |
| `description` | string | no | Human-readable meaning |
| `synonyms` | list[string] | no | Optional alternate names |

## 3. Canonical Attribute File

Canonical attribute definitions are versioned, reusable templates for standard attributes.

```json
{
  "schema_version": "2.0",
  "oifma_id": "OIFMA_OIDM_000001",
  "version": "1.0.0",
  "name": "presence",
  "type": "choice",
  "description": "Presence or absence of finding",
  "synonyms": ["presence/absence"],
  "values": [
    {
      "name": "absent",
      "description": "Finding is absent",
      "synonyms": ["not present"]
    },
    {
      "name": "present",
      "description": "Finding is present",
      "synonyms": ["seen"]
    },
    {
      "name": "indeterminate",
      "description": "Presence of finding cannot be determined"
    },
    {
      "name": "unknown",
      "description": "Presence of finding is unknown"
    }
  ]
}
```

| Field | Type | Required | Notes |
|---|---|---:|---|
| `schema_version` | string | yes | Must be `"2.0"` |
| `oifma_id` | string | yes | Canonical attribute ID |
| `version` | string | yes | Canonical definition version |
| `name` | string | yes | Canonical attribute name |
| `type` | string | yes | Usually `"choice"` initially |
| `description` | string | no | Default canonical description |
| `synonyms` | list[string] | no | Canonical attribute synonyms |
| `values` | list[`ChoiceValueSource`] | yes for `choice` | Default choice-value structure |
| `references` | list[`WebReference`] | no | Allowed on canonical attribute definitions |

### Initial seeded canonicals

- `OIFMA_OIDM_000001` → `presence`
- `OIFMA_OIDM_000002` → `change from prior`

## 4. Hydrated/Resolved Model

Hydration resolves canonical references into normal concrete attributes. The hydrated shape should look like the current model shape, adjusted for the agreed v2 field changes:

- no canonical reference objects remain
- no `required` field
- numeric attributes use `quantity_kind` and optional `common_units`
- choice values receive `value_code`s derived from the local `oifma_id`

### Example hydrated attribute

Source canonical ref:

```json
{
  "canonical_oifma_id": "OIFMA_OIDM_000001",
  "canonical_version": "1.0.0",
  "oifma_id": "OIFMA_OIDM_100001",
  "description": "Presence or absence of pulmonary embolism",
  "value_descriptions": {
    "absent": "Pulmonary embolism is absent",
    "present": "Pulmonary embolism is present",
    "indeterminate": "Presence of pulmonary embolism cannot be determined",
    "unknown": "Presence of pulmonary embolism is unknown"
  }
}
```

Hydrated output:

```json
{
  "oifma_id": "OIFMA_OIDM_100001",
  "name": "presence",
  "type": "choice",
  "description": "Presence or absence of pulmonary embolism",
  "synonyms": ["presence/absence"],
  "values": [
    {
      "value_code": "OIFMA_OIDM_100001.0",
      "name": "absent",
      "description": "Pulmonary embolism is absent",
      "synonyms": ["not present"]
    },
    {
      "value_code": "OIFMA_OIDM_100001.1",
      "name": "present",
      "description": "Pulmonary embolism is present",
      "synonyms": ["seen"]
    },
    {
      "value_code": "OIFMA_OIDM_100001.2",
      "name": "indeterminate",
      "description": "Presence of pulmonary embolism cannot be determined"
    },
    {
      "value_code": "OIFMA_OIDM_100001.3",
      "name": "unknown",
      "description": "Presence of pulmonary embolism is unknown"
    }
  ],
  "max_selected": 1
}
```

### Hydration rules

1. Load the source model.
2. For each canonical reference, load the canonical attribute by `canonical_oifma_id` and `canonical_version`.
3. Copy the canonical structure into a new concrete attribute.
4. Inject the local `oifma_id`.
5. Replace the attribute description if the ref contains `description`.
6. Replace per-value descriptions for any names present in `value_descriptions`.
7. Generate `value_code`s from the local `oifma_id`.
8. Emit a standard concrete attribute object for runtime/indexing.

## 5. Relationship Behavior

### Relationship registry semantics

Relationship types are defined in a checked-in registry and each type declares whether it is:

- inverse-backed
- symmetric
- one-way

Examples:

- `type_of` ↔ `has_subtype`
- `causes` ↔ `caused_by`
- `evolves_to` ↔ `evolves_from`
- `occurs_with` is symmetric

### Authored vs effective relationship view

Authored source edge:

```json
{
  "oifm_id": "OIFM_OIDM_000110",
  "name": "subsegmental pulmonary embolism",
  "related_models": [
    {
      "relationship_type": "type_of",
      "oifm_id": "OIFM_OIDM_000100",
      "display": "pulmonary embolism"
    }
  ]
}
```

Effective derived inverse view on the target model:

```json
{
  "oifm_id": "OIFM_OIDM_000100",
  "name": "pulmonary embolism",
  "related_models_effective": [
    {
      "relationship_type": "has_subtype",
      "oifm_id": "OIFM_OIDM_000110",
      "display": "subsegmental pulmonary embolism"
    }
  ]
}
```

### Validation rules for relationships

- Every target `oifm_id` must exist.
- Every `relationship_type` must exist in the relationship registry.
- Source files should not be required to duplicate inverse edges manually.
- Build and runtime layers should expose the full effective relationship view derived from authored edges and registry semantics.

## 6. Registry Files

### 6.1 Relationship type registry

```json
[
  {
    "name": "type_of",
    "inverse_name": "has_subtype",
    "symmetric": false
  },
  {
    "name": "has_subtype",
    "inverse_name": "type_of",
    "symmetric": false
  },
  {
    "name": "occurs_with",
    "inverse_name": null,
    "symmetric": true
  },
  {
    "name": "causes",
    "inverse_name": "caused_by",
    "symmetric": false
  },
  {
    "name": "caused_by",
    "inverse_name": "causes",
    "symmetric": false
  },
  {
    "name": "evolves_to",
    "inverse_name": "evolves_from",
    "symmetric": false
  },
  {
    "name": "evolves_from",
    "inverse_name": "evolves_to",
    "symmetric": false
  }
]
```

### 6.2 Quantity-kind registry

```json
[
  "length",
  "area",
  "volume",
  "count",
  "ratio",
  "percentage",
  "radiodensity",
  "time",
  "angle",
  "mass",
  "score",
  "other"
]
```

## 7. Per-Model History Sidecar

Each source model may have a sidecar named `<OIFM_ID>.history.jsonl` stored next to the model file.

Each line is one JSON object:

```json
{
  "event_id": "evt_000001",
  "timestamp": "2026-04-20T15:32:10Z",
  "action": "migrate_schema",
  "actor_kind": "ai",
  "actor_id": "codex",
  "actor_display": "Codex",
  "source_system": "findingmodel-maintenance",
  "source_tool": "fm-schema-migrate",
  "source_model": "gpt-5.4",
  "summary": "Migrated source model from legacy schema to source schema v2",
  "target_schema_version": "2.0",
  "model_hash": "sha256:abc123..."
}
```

| Field | Type | Required | Notes |
|---|---|---:|---|
| `event_id` | string | yes | Stable event identifier |
| `timestamp` | string | yes | ISO 8601 timestamp |
| `action` | string | yes | `create`, `edit`, `review`, `approve`, `deprecate`, `migrate_schema` |
| `actor_kind` | string | yes | e.g. `human`, `ai`, `system` |
| `actor_id` | string | yes | Stable actor identifier |
| `actor_display` | string | yes | Human-readable actor name |
| `source_system` | string | yes | Producing system |
| `source_tool` | string | no | Optional tool name |
| `source_model` | string | no | Optional AI model or software version |
| `summary` | string | yes | Human-readable description of event |
| `target_schema_version` | string | yes | Schema version after event |
| `model_hash` | string | yes | Hash of reviewed/produced model content |

## 8. Explicit v2 Removals and Changes from Current Shape

Compared with the current concrete model shape in the repo:

- remove `required`
- replace numeric `unit` with `quantity_kind` and optional `common_units`
- add `synonyms` to attributes and choice values
- add model-level `references`
- add `lifecycle`
- add `related_models`
- allow canonical attribute references in source models
- keep hydrated output close to the current concrete model structure

## 9. Open Implementation Notes

These decisions are intentionally left at implementation-policy level rather than fixed schema detail:

- Whether runtime APIs expose both `related_models` and `related_models_effective`, or only the effective view
- Whether `deprecated_at` is date-only or full datetime
- Whether registry files live under `registries/`, `schema/`, or another dedicated folder
- Whether canonical attribute files eventually support numeric canonicals, not just choice attributes
- Whether canonical attribute definitions should themselves carry index codes in v2

## 10. Review Checklist

Reviewers should specifically look for:

- fields that are missing from the proposed source contract
- whether `description` and `value_descriptions` are sufficient override points
- whether model-level-only `references` is enough for v2
- whether relationship derivation rules are clear enough
- whether `quantity_kind` and `common_units` are the right numeric split
- whether hydrated output is close enough to current code expectations to ease migration
