---
type: Meeting Notes
title: Committee Meeting Notes — Extract
description: Sanitized extract of RSNA/ACR CDE Committee schema discussion notes — source of the Finding Class / Data Element / Value terminology and the draft reusable-element list.
tags: [committee, meeting-notes, next-gen-schema]
status: stable
generated: { by: claude-code/claude-sonnet-5, at: 2026-07-31 }
sources:
  - resource: raw_sources/committee_meeting_notes.txt
    title: RSNA/ACR CDE Committee schema discussion notes (internal; kept out of the public repo)
sanitization: Names of participants other than the repo owner (Tarik Alkasab) removed or replaced with role descriptions; meeting logistics omitted.
---

# Committee Meeting Notes — Extract

## Schema Discussion

Action item: start documenting rules of thumb for when to define a new reusable data element and its attributes (existing guidelines from a committee member's prior work could inform this).

Discussed the challenge of defining clear boundaries between different levels of the schema, particularly around concepts like ground glass opacity, and how to handle reusable data elements across different contexts.

### Reusable Data Elements

General principle: assume any data element could be reusable; make the case for data elements that are *not* reusable. Look for commonality of values, and commonality of instructions used to determine values.

Examples of common reusable elements:

- Presence
- Change from prior
- Size (1D — long axis)
- Size (1D — short axis)
- Size (2D)
- Size (3D)
- Size (Volume)
- Size (qualitative)
- Laterality
- Location (anatomic)
- Location (spatial)
- Location (relative location within a structure)
- Color (CT — density — qualitative)
- Color (CT — density — quantitative, Hounsfield units)
- Color (MRI — signal intensity)
- Color (Radiograph — density)
- Color (US — echogenicity)
- Color (Nuclear Medicine)

### Terminology

Discussion moved away from using "observation" due to potential conflicts with FHIR modeling, settling instead on "finding class" for the top level, while retaining "data elements" for attributes and "values" for specific measurements like presence/absence.

Naming Convention & Terminology Alignment (explicit definitions needed):

- **Set → Finding Class** — The subject of an imaging finding (e.g., pulmonary nodule)
- **Elements → Data Elements** — The attributes that make up a finding class (e.g., size, shape, opacity, presence)
- **Value → Value** — The potential descriptors of a data element (e.g., 3 mm; spherical/spiculated; solid/semi-solid; present/absent/indeterminate/unknown)

Other points raised:

- Diverse entity types (e.g., findings, diagnoses, measurement sets)
- Confidence levels: definite/probable/possible
- Associated metadata (subspecialty, etiologies, demographics, time courses) to provide foundational context for each definition

### Edge Cases and Modeling Feedback

Action item: collect and send examples of edge cases or situations where the proposed structure does not fit, to ensure these are accounted for before finalizing the schema.

### Schema Smoke Test and Validation

Action item: conduct a "smoke test" of the new schema by creating definitions using the schema and ensuring they can be used to characterize specific kinds of observations in medical record language.

### Other Topics Noted for Future Work

Governance, lifecycle management, and detailed modeling guidelines, ensuring comprehensive documentation and stakeholder alignment.

## Action Items

- Documentation: start documenting rules of thumb for when to define a new reusable data element and its attributes.
- Schema draft: produce a new schema draft (co-authored effort involving Tarik).
