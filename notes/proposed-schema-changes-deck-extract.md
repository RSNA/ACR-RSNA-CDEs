---
type: Presentation Extract
title: Proposed Schema Changes Deck — Extract
description: Complete text extraction of the 22-slide schema-changes deck presented to the RSNA-ACR CDE Committee at SIIM, 12 June 2026.
tags: [committee, presentation, siim, next-gen-schema]
status: stable
generated: { by: claude-code/claude-sonnet-5, at: 2026-07-31 }
sources:
  - resource: raw_sources/RSNA-ACR_CDE_Committee_schema_changes_proposed_2026-06-12.pdf
    title: RSNA-ACR CDE Committee schema-changes deck, 12 June 2026 (internal; kept out of the public repo)
sanitization: No participants are named in the slide content; meeting logistics (per-topic agenda times, facilitation notes, future-meeting scheduling) omitted as non-substantive. All 22 slides extracted (pypdf); the extraction is complete.
---

# Proposed Schema Changes Deck — Extract

## Goal

- **Overall objective:** scale up and modernize radiology common data elements creation and publication.
- **Meeting agenda:** review the proposed schema updates and finalize the recommendations.

## Agenda Topics Covered

Templates & Nomenclature; Structure; Attribute Definitions; Location; Relationships; Metadata (Entity Type, Synonyms, Clinical Context, Coding); Governance, History and Activities.

## Nomenclature

Terminology for this discussion — "Findings" and "Attributes" — was to be finalized later. The understanding of the semantic layer has evolved: giving each part of the schema a more specific name, aligned more closely with how established standards describe the same ideas, makes the model easier to author, review, and build on as it grows.

| Old term | New term | Meaning |
|---|---|---|
| Sets | Findings | An imaging observation |
| Elements | Attributes | A property of a finding |

## Templates: an Organizing Layer

The template is a high-level layer that sits above findings. It helps set clearer boundaries and apply shared expectations, such as conditional rules and inherited requirements, which keeps the structure coherent. At this stage it is an organizing concept rather than a fully defined schema object.

Illustrative structure:

- **Template** — shared scope, conditional rules, inheritance
  - **Finding A** — Attributes: X, Y, Z
  - **Finding B** — Attributes: Z, W, Q

The deck's focus was the semantic layer the template sits on top of: which attributes each finding carries, and how the same attribute (like "Z") can be standardized and reused across findings.

## Structure

### Current State

- **Tight Coupling Limits Reuse:** findings and attributes are closely linked, reducing flexibility and preventing reuse across different contexts.
- **Duplication and Inconsistency:** because a high-use attribute can be defined in several findings, keeping those definitions aligned takes ongoing attention, and differences can creep in over time.
- **Challenges in Schema Evolution:** modifying attributes requires multiple updates, increasing risk of breaking changes over time.
- **Constraints on Tool Development:** with attributes tied to individual findings, validation and visualization tools tend to handle each finding separately, increasing special-case handling.

### Proposed

- **Modular and Scalable Design:** decoupling findings from attributes makes the model more modular and lets a high-use attribute be defined once and reused rather than repeated, with scalability in mind.
- **Reusable Shared Attributes:** common attributes such as presence, change, and grading scales are explicitly defined once for consistent interpretation and reuse.
- **Simplified Tooling and Analytics:** predictable, shared attributes let one set of validation and analytics tools work across many findings.
- **Supports Future Growth:** new findings and attributes can be added by composing with existing pieces, with little disruption to what is already in place. A well-defined shared attribute should rarely require updates; reusing existing attributes cuts significant redundant work in the authoring and reviewing process.

### Structural Shift Summary

| Current | Proposed |
|---|---|
| Each element owns its attribute definition | Independent findings and attributes |
| Concept duplication | Attributes as linkable, reusable concepts |
| Manual alignment enforcement | Consistently aligned definitions |
| Multiple AI signals | Predictable for AI |

Question posed: "Which one is the authoritative representation for asserting presence?" Answer: the committee-approved standard is the default authoritative representation — this eliminates ambiguity, enforces consistency, saves time, and reduces cognitive burden. Attributes are linked to (via `has_attribute`), not owned by, the finding — versus the current state where each attribute "lives" in the element.

## Attribute Definitions

### Current State

- **One Object, Two Roles, Three Forms:** a single element object (attribute) takes one of three forms, set by a type property — a value set (pick list), an integer, or a float. The value set is the qualitative case; integer and float are the two quantitative forms. Changing the type reshapes the same object.
- **Qualitative Attributes:** an attribute that draws from a defined answer set is well understood and works as intended.
- **Fixed Unit and Interoperability Challenges:** on the quantitative side, units are fixed in the definition (for example, millimeters), which makes it harder to reuse a measurement across systems or requires extra logic to convert between units.

### Proposed

- **Two Separate Attribute Objects:** the compound "element" type separates into two objects — a qualitative attribute and a quantitative attribute — each modeled for what it carries.
  - **Qualitative Attribute:** functionally unchanged, a pick list allowing one or more values.
  - **Quantitative Attribute:** captures measurement using quantity types such as length (one dimension), length x depth x width (three dimensions), volume, or count, instead of fixed units — bringing the former integer and float forms together into one standardized reusable model. The unit follows a shared standardized convention rather than being set in each definition.
- **Future-Proof and Automation Ready:** separating quantity from units keeps the schema adaptable, easier to maintain, and aligned with AI and automation workflows.

### New Object: Quantitative Attribute

| Current | Proposed |
|---|---|
| Element object takes multiple forms | Qualitative attribute concept functionally unchanged |
| Measurements redefined in each element | New reusable standardized measurements |
| No standard enforcement mechanism | Shared conventions |
| Accuracy burden on author/reviewer | — |
| Fixed units | Unit guidance, not fixed |

Example: a single-dimension measurement is one value in a single unit type. Length is the typical case — diameter, radius, and distance are all lengths (measured in mm or cm), so each uses the same model.

## (Anatomic) Location

### Current State

- Body part is optional on both the set and the element, and the two are not linked.
- In practice, authors capture location by adding a free-form value-set element (Location, Position, Orientation, even Type), whose values are ungrounded, allowing variation from finding to finding. This does not automatically mean values are incorrect, but the way they are expressed can vary significantly.
- No central control exists to prevent a mix of anatomic regions, directions and axes, and distribution.
- With nothing anchoring body part, element, and values together, location is hard to query reliably.

### Proposed

- **Location as an Anchor:** (Anatomic) Location takes a more prominent role as an anchor property that can support inherited conditional rules and structural accuracy enforcement.
- **Clear Boundaries for Spatial Location:** clearer boundaries let spatial location (planes and axes in relation to landmarks) be represented on its own.
- **Standardized Location Hierarchies:** defining anatomic location hierarchies, grounded to a shared vocabulary (for example, abdomen or arteries), improves consistency and supports precise querying.
- **Coding Mapping:** RadLex; SNOMED.

### Anchored Anatomic Locations Summary

- **Current:** body part is optional, free-text, and unlinked, so locations are entered ad hoc with no shared structure.
- **Proposed:** body part bound to a mapped terminology (RadLex) is used as an anchor that suggests standardized locations; the author selects clinically applicable options.

## Relationships

### Current State

- **Implicit Relationship Modeling:** the structure is flat — relationships between findings are signaled by naming rather than defined explicitly. Since they are inferred rather than stated, they are harder to use for analytics.
- **Integration Across Systems:** different systems represent relationships differently, so integrating them tends to rely on custom logic.

### Proposed

- **Explicit Many-to-Many Relationships:** relationships between findings are defined explicitly, capturing causal links, co-occurrence, subtypes, and groupings.
- **Richer Semantic Reasoning:** with locations and relationships stated explicitly, the model supports clearer reasoning, decision support, and more accurate analytics.
- **Built for AI:** explicit relationships in a schema give AI the structure it relies on and let accuracy be validated through the model rather than left to inference.

### Explicit Relationships Summary

- **Current:** in a "flat" structure, all elements sit side-by-side. Relationships between elements exist only in the name (e.g., "element X presence," "element X side"). Elements are redefined repeatedly because they rely on the name to signal their relationship.
- **Proposed:** structure makes relationships explicit and unlocks reusability — e.g., a standardized presence attribute linked to Finding X, the same standardized presence attribute linked to Finding Y, via an explicit `has_attribute` relationship. Grouping relationships allow findings to be defined only once, with context (other associated findings) determining diagnosis-leaning concepts.

## Metadata

### Current State

- **Synonym Support:** none — this limits discoverability and prevents alignment of equivalent terms across different systems.
- **Limited Coding Integration:** supports coding standards like SNOMED, RadLex, and LOINC, but they are integrated unevenly, impacting data interoperability.
- **Governance and Versioning Challenges:** governance info embedded in schema artifacts complicates versioning, auditing, and large-scale integration efforts.

### Proposed

- **Coherent Metadata Framework:** the model organizes metadata into a consistent framework supporting entity typing and synonyms for term alignment; synonyms are crucial for discoverability and reuse.
- **Clinical Context Descriptors:** descriptors capture clinical factors like body region, etiology, and demographics to enrich metadata meaning.
- **Expanded Coding Mappings:** support for additional industry-standard coding mappings for comprehensive interoperability.
- **Governance and Lifecycle Management as an Independent Schema:** this no longer lives in the semantic layer.

## Governance

- **Governance and Lifecycle Management:** a separate schema allows governance and the semantic layer to evolve separately, decreasing friction.
- **Event-sourced governance** to manage history, approvals, and AI contributions.
- Goal: ensure transparency and traceability.
