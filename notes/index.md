# Provenance

* [Notes — Provenance](SOURCES.md) - Provenance for the notes directory — upstream URLs for the fetched OIFM copies and extraction records for the sanitized committee and working-group material.

# Sanitized Committee Extracts

Raw committee material is kept out of the public repository (gitignored `raw_sources/`); these extracts preserve the substantive content with participants' identifying details removed.

* [Proposed Schema Changes Deck — Extract](proposed-schema-changes-deck-extract.md) - Complete text extraction of the 22-slide schema-changes deck presented to the RSNA-ACR CDE Committee at SIIM, 12 June 2026.
* [SIIM Meeting Minutes — Extract](siim-meeting-extract.md) - Sanitized extract of the SIIM committee meeting minutes — nomenclature debate, decoupled graph structure, attribute types, anatomic location, relationships, metadata, and action items.
* [Committee Meeting Notes — Extract](committee-notes-extract.md) - Sanitized extract of RSNA/ACR CDE Committee schema discussion notes — source of the Finding Class / Data Element / Value terminology and the draft reusable-element list.
* [CDE Schema Recommendations — Part II](schema-recommendations-part2.md) - The initial written proposal for iterating the schema forward — templates set aside, findings/attributes decoupled, explicit relationships, expanded metadata, location guidance, governance separated, and quantity types.

# Working Group, August 2026

Material from the working sessions that followed the analysis bundle being pushed to `next-gen-2026`. The call summary and the email thread are sanitized; the memo is a verbatim copy of an external contributor's document.

* [Working Group Call, 20 August 2026 — Extract](working-group-call-2026-08-20-extract.md) - Sanitized extract of the 20 August 2026 schema working-group call, covering prototyping on a relational store before the graph, edge properties versus nodes, compositional versus associative edges, and the agreement to separate Diagnosis from Finding.
* [Schema Review Exchange, 25 August 2026 — Extract](review-exchange-2026-08-25-extract.md) - Sanitized extract of the 25 August 2026 email exchange on the next-generation schema, covering the Diagnosis node and its relationship types, conditional relationships versus subtype classes, bilaterality, anatomic scope for scored slots, and how study indication selects an assessment.
* [Conditional Relationships — Engineering Memo](conditional-relationships-memo.md) - An engineering comparison of two ways to express a relationship that applies only under a condition, a condition property on the edge or explicit subtype classes, with the recommendation and the reasoning that tips it. Copy of the memo circulated 26 August 2026.


# Standards Extracts

* [Profile of the Hood Finding Taxonomies](hood-taxonomies-profile-2026-09-01.md) - What the six per-modality finding taxonomies by Michael Hood contain and how they are shaped, measured on 2026-09-01 from the 2026-08-15 export - row counts, typing, hierarchy depth, the recurring name patterns, and the structural facts the vocabulary work draws on.
* [Source Review of Nodule Content](source-review-2026-08-20.md) - Findings from checking the pulmonary-nodule and thyroid-nodule example content against Radiopaedia, Radiology Assistant, and Wikipedia on 2026-08-20, including foundational content those pages suggest the vocabulary should capture.
* [IHE IDR Phase II — Extract](ihe-idr-extract.md) - What the IHE Imaging Diagnostic Report (IDR) Phase II public-comment draft says about encoding findings as FHIR Observations — the grammar this vocabulary must fit — read directly from the supplement.

# Research and Discussion

* [Ontology Background Research and Follow-up Questions](ontology-background-research-2026-09-04.md) - Primary-source background and proposed worked examples for target identity, assertion context, negation, formal semantics, terminology mappings, and diagnostic reasoning in the next-generation CDE vocabulary.

# OIFM Reference Copies

Copies of public Open Imaging Finding Model documents, retrieved 2026-07-29; edit the upstream source, not these.

* [Finding Models: Overview](oifm-overview.md) - OIFM overview of finding models — why they exist, what they contain, and modelling guidance. Copy of the upstream document.
* [FindingModel Source Schema v2 Draft](oifm-schema-v2-draft.md) - Proposed OIFM source-format and supporting file schemas for FindingModel authoring. Copy of the upstream gist.
* [Finding Model Structured Metadata Fields](oifm-metadata-fields.md) - Reference for the structured metadata fields on FindingModelBase and FindingModelFull. Copy of the upstream gist.
