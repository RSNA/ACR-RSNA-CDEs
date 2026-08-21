---
type: Proposal
title: CDE Schema Recommendations — Part II
description: The initial written proposal for iterating the schema forward — templates set aside, findings/attributes decoupled, explicit relationships, expanded metadata, location guidance, governance separated, and quantity types.
tags: [proposal, next-gen-schema, cde]
status: stable
generated: { by: claude-code/claude-sonnet-5, at: 2026-07-31 }
sources:
  - resource: raw_sources/first_ideas.txt
    title: "CDE schema recommendations — Part II (draft notes; kept out of the public repo)"
    author: "human:talkasab"
sanitization: Names of participants other than the author removed or replaced with role descriptions; email framing and scheduling stripped.
---

# CDE Schema Recommendations — Part II — Extract

A note on scope: this draft omits the versioning piece. The tentative direction is that every new version of a node becomes a new node, with versions connected by a shared ID — other committee members may have refinements to this idea.

## Templates

Templates — groups of findings/measurements, etc. — along with a method of representing them in report text, are being set aside as a separate concern which may be layered in later. This is where information about validity and conditional requirements could eventually live. For example, information about how, if a particular feature is mentioned, certain other attributes are required, or that certain choices are mutually incompatible.

## Nomenclature

Terminology needs to be clearer. "Element" and "set" are so abstract as to be essentially meaningless. Provisionally, the top-level objects (formerly "sets") are proposed to be named "findings," and their constituent parts (formerly "elements") referred to as "attributes." The terms need to convey at least that much context — making it immediately clear that these are data models for things seen in imaging exams.

For reference: what are currently called "sets" correspond to "findings," and what are currently called "elements" correspond to "attributes."

## Structure

The new structure requires that findings and attributes be completely decoupled from one another. An attribute does not belong inherently to a specific finding — any given attribute can be used across multiple findings. As part of this, a number of canonical attributes should be defined: presence, change from prior, standard measurement types, and standard grading scales (mild/moderate/severe and the like).

## Relationships

The schema needs to explicitly express relationships between findings themselves — not just that an attribute belongs to a finding, but that different findings are related to one another. Examples include: a finding caused by another finding, findings commonly seen together, findings that are components of other findings, sub-type-of relationships, and groupings. Relationships are not inherent properties of the findings themselves, but rather separate many-to-many relationships between finding nodes.

## Metadata

There is opportunity to greatly expand the metadata associated with finding definitions. This can improve discoverability of entries in the repository, and be used to identify those relevant to a specific situation.

- **Entity type:** whether what's being described is literally a finding as opposed to a diagnosis, a measurement, a rating, a sub-component, etc.
- **Synonyms** at all levels — true equivalent-meaning terms for a given finding, attribute, or attribute value.
- Body region
- Etiologies
- Age groups
- Sex specificity
- Keep the RSNA subspecialty codes
- Keep the imaging modality codes
- More relationships with external ontologies should also be supported. Currently the schema is limited to SNOMED, RadLex, LOINC, and ACR Common — any coded ontology should be referrable.

## Location

Each finding definition should have the opportunity to express what kinds of anatomic locations are expected for that finding or diagnosis. This could be as broad as a body region (e.g., the abdomen), a structure type (e.g., arteries), or as specific as a named body structure (e.g., anterior cruciate ligament).

There probably is no need for attributes specifically intended to represent the location of a finding. In FHIR representations, for example, the body structure element is already built into the Observation resource, and the definitions don't need their own location attributes. However, they can provide guidance as to what anatomic locations would be congruent with the finding being defined.

## Governance and History

The current schema is encumbered with a lot of governance, versioning, and history overhead. Items related to history, provenance, governance status, and decisions should be explicitly separated out. This would probably take the form of a separate event log capturing creation, editing, and approval events in the lifecycle of a definition. This is also the place to record information about AI contributions to authoring, as well as subsequent human review and approval.

## Numerical Attributes

Currently, numerical attributes convey specific units — an over-specification. Instead, a common set of quantity types should be defined — count, length, volume, radiodensity, etc. — reflecting what physical property is actually being expressed by the number. These quantity types would then imply standard sets of units. If it's a length, it might be in centimeters or millimeters. If it's a volume, it could be in cubic millimeters, milliliters, or cubic centimeters, and so on.
