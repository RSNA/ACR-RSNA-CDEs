---
type: Meeting Notes
title: SIIM Meeting Minutes — Extract
description: Sanitized extract of the SIIM committee meeting minutes — nomenclature debate, decoupled graph structure, attribute types, anatomic location, relationships, metadata, and action items.
tags: [committee, meeting-notes, siim, next-gen-schema]
status: stable
generated: { by: claude-code/claude-sonnet-5, at: 2026-07-31 }
sources:
  - resource: raw_sources/siim_meeting_minutes.txt
    title: SIIM committee meeting minutes (internal; kept out of the public repo)
sanitization: Names of participants other than the repo owner (Tarik Alkasab) removed or replaced with role descriptions; future-meeting scheduling omitted.
---

# SIIM Meeting Minutes — Extract

## Templates and Nomenclature

**Naming Conventions and Terminology Alignment:** Debated terminology for schema components, considering options like "element," "attribute," "data element," "finding," and "observation type," with the goal of balancing clinical meaning, engineering alignment, and branding.

- **Element vs. Attribute vs. Data Element:** Discussed whether to retain the term "element" for atomic schema components or adopt "attribute" or "data element." Some favored keeping "element" for branding; others noted that "attribute" is more descriptive and aligns with informatics standards.
- **Finding vs. Observation Type:** Debate over using "finding" or "observation type" for higher-level schema objects. Some preferred "observation type" for its flexibility and alignment with standards like FHIR; others noted potential confusion with existing clinical report sections.

Consensus: provide explicit definitions for chosen terms to avoid confusion, especially given overlapping terminology in related standards and clinical practice.

## Structure

**Proposed:** decoupling findings and attributes so that each becomes an individual object, allowing findings to link to shared attribute definitions rather than embedding attributes within findings. This is intended to improve reusability and reduce duplication — previously, attributes were closely tied to specific findings, leading to inconsistency and manual effort in maintaining definitions.

- **Tooling and Reusability Challenges:** The current schema's close coupling of findings and attributes, combined with limited tooling, led to inconsistent attribute definitions and hindered reusability. Although the schema was designed for reusable elements, the lack of supporting tools resulted in variations and bloat, as users did not consistently follow guidelines.
- **Graph Model Adoption:** The proposed schema moves toward a graph model, where findings point to canonical attribute objects. This is expected to facilitate faster scaling and easier maintenance, as shared attributes can be centrally defined and referenced by multiple findings, reducing cognitive load and manual cross-checking.
- **Implications for Authoring Tools:** Adopting this model will require more sophisticated authoring tools capable of managing relationships and preventing issues like cyclic structures. The graph needs to be checked for cycles to avoid complexity in AI tooling and term resolution.

## Attribute Definitions

Discussed redefining attributes into qualitative (categorical) and quantitative (measurement) types, aiming to standardize measurement definitions and improve interoperability across findings.

- **Attribute Types and Structure:** Proposed splitting attributes into qualitative (pick lists or categorical options) and quantitative (measurements with units) types. This separation allows for clearer definitions and supports standardized measurement concepts, such as length, volume, and count, with predefined allowable units.
- **Units:** Units are embedded in the observation value and must be compatible with the attribute definition. The schema will specify allowable units for each quantitative attribute, supporting flexibility while maintaining consistency.
- **Practical challenges:** variability in how measurements are described (e.g., plane of measurement for lymph nodes). The schema will allow for optional specification of measurement context, such as plane or axis, to accommodate real-world variability.
- **Ordinal and categorical attributes:** Distinguishing between ordinal and non-ordinal categorical attributes matters because it affects how data can be analyzed and interpreted. The schema will capture whether a choice attribute is ordinal to support downstream use cases.

## Location

Elevating anatomic location to a top-level concept in the schema, with explicit linkage to standard ontologies like RadLex to improve consistency and support advanced use cases.

- **Location as a Top-Level Concept:** Anatomic location should not be treated as a simple attribute but as a fundamental property of observations, with each observation object pointing to a standard anatomic location from an ontology such as RadLex.
- **Ontology and Hierarchy Integration:** Linking findings to hierarchical anatomy ontologies allows for anatomical guidance and reduces duplication. For example, a generic lymph node observation can be linked to specific anatomical locations without creating separate findings for each body part.
- **Practical Use Cases and Vendor Needs:** Explicit anatomical anchoring supports vendor requirements for structured reporting and facilitates parsing and template creation. The schema will provide cues for viable anatomical choices without predefining exhaustive lists.
- **Mapping to External Standards:** Mappings to SNOMED and other standards will be maintained at the RadLex level, ensuring interoperability and supporting both input and output coding requirements.

## Relationships

Explored introducing explicit relationships between findings and attributes, moving beyond a flat structure to support hierarchies, subtypes, and complex modeling scenarios.

- **From Flat to Structured Relationships:** The current schema's flat structure was identified as insufficient for representing complex relationships. The proposed model introduces explicit links between findings and attributes, as well as between findings themselves, to capture sub-findings, components, and hierarchical relationships.
- **Handling Subtypes and Inheritance:** Discussed the need for guidance on when to create specific subtypes versus using generic findings with location attributes. Consensus: subtypes should be defined independently, without automatic inheritance of attributes, to avoid conflicts and maintain clarity.
- **Managing Hierarchies and Edge Cases:** Concern raised about managing multiple levels of hierarchy, attribute conflicts, and the distinction between "where" and "what" in anatomical labeling. The schema will provide rules of thumb and modeling guidelines to address these complexities.
- **Cardinality and Validation Scope:** Questions about enforcing cardinality (e.g., number of locations per finding) were discussed, with the consensus that validation and template constraints are out of scope for the semantic schema, which will focus instead on defining possible attributes and relationships.

## Metadata (Entity Type, Synonyms, Clinical Context, Coding)

Discussed enhancements to metadata, including synonym support for improved discoverability, expanded coding standards, and the separation of governance and lifecycle management from the semantic schema.

- **Synonym Support for Discoverability:** The schema will introduce synonym support at multiple levels, allowing different terms (e.g., "laterality" and "side") to be recognized as equivalent, thereby improving concept reuse and searchability.
- **Expansion of Coding Standards:** Plans to expand beyond the current limited set of ontologies, incorporating additional industry standards to enhance interoperability and coverage.
- **Separation of Governance and Lifecycle:** Governance and versioning information, currently embedded in the schema, will be moved to a separate schema. This will include activity logs, provenance, and approval tracking, streamlining the semantic layer and simplifying authoring.
- **Entity Types and Additional Metadata:** Support for different entity types (e.g., findings, diagnoses, measurement sets) and metadata such as subspecialty, possible etiologies, demographics, and time courses — providing foundational context for each definition — will need to be finalized in a committee meeting.

## Governance, History and Activities

Consensus: provide explicit definitions for chosen terms to avoid confusion, especially given overlapping terminology in related standards and clinical practice.

**Planned Outputs and Next Steps:** Agreed to document the outcomes of the meeting in a white paper and to continue refining schema details, with further discussions planned for governance, lifecycle, and modeling guidelines.

## Future Discussions

Further meetings will address unresolved topics such as governance, lifecycle management, and detailed modeling guidelines, ensuring comprehensive documentation and stakeholder alignment.

**White paper development:** Proposed producing one or more white papers to summarize the new direction on CDEs, targeting both technical and clinical audiences, and highlighting the schema's relevance for AI and interoperability.

## Action Items

- Create a new schema draft for review.
- Schema Smoke Test and Validation: conduct a "smoke test" of the new schema by creating definitions using the schema and ensuring they can be used to characterize specific kinds of observations in medical record language.
- Edge cases and modeling feedback: collect and send examples of edge cases or situations where the proposed structure does not fit, to ensure these are accounted for before finalizing the schema.
- Documentation: start documenting rules of thumb for when to define a new finding versus using attributes.
- Prepare two separate white papers: one for a technical audience (e.g., JIM) and one for a clinical audience (e.g., JACR), outlining the new direction for CDEs and their implications.
