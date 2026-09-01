---
type: Meeting Notes
title: Working Group Call, 20 August 2026 — Extract
description: Sanitized extract of the 20 August 2026 schema working-group call, covering prototyping on a relational store before the graph, edge properties versus nodes, compositional versus associative edges, and the agreement to separate Diagnosis from Finding.
tags: [committee, meeting-notes, next-gen-schema, diagnosis, prototyping]
status: stable
generated: { by: "claude-code/claude-opus-5", at: 2026-08-31 }
sources:
  - id: recording-summary
    resource: raw_sources/working_group_call_2026-08-20.txt
    title: AI-generated recording summary of the call (internal; kept out of the public repo)
    author: process:meeting-recording-summarizer
    last_modified: 2026-08-20
sanitization: Participants other than the repo owner (Tarik Alkasab) are referred to by role. Scheduling, distribution boilerplate, and organizational affiliations removed.
---

# Working Group Call, 20 August 2026

**Participants.** Tarik Alkasab, the external reviewer drafting the model, and an engineering collaborator.

**Reliability caveat.** The source is an automatically generated summary of a recording, not minutes anyone reviewed. Treat the wording as approximate. Where a point below is restated in the email exchange that followed ([`review-exchange-2026-08-25-extract.md`](review-exchange-2026-08-25-extract.md)), that restatement is the better record and is cross-referenced.

---

## 1. Prototyping store, relational before graph

The reviewer proposed building the alpha against an **expanded relational model** rather than a graph store, to get something testable quickly, with the intent of moving to a full graph later. Tarik and the engineering collaborator agreed, on the condition that the relational design be deliberate enough that the later migration is smooth rather than a rewrite.

This is consistent with the architecture already recorded, which treats the query store as a derived view rather than the system of record ([`docs/next-gen-schema/00-current-understanding.md` §7.2](../docs/next-gen-schema/00-current-understanding.md)). What is new is that the *first* derived view will be relational, and that the alpha is being built against it.

## 2. Database options

- **DuckDB** for portability and ease of use during development. The engineering collaborator's existing codebase already interfaces with DuckDB and can export to SQLite or CSV.
- **Postgres** preferred by the reviewer on familiarity grounds.
- Agreed that DuckDB's accessibility suits the early stages. Consistent with the position that the store choice is low stakes because it is derived ([00 §7.2](../docs/next-gen-schema/00-current-understanding.md)).

## 3. Future-proofing the edge representation

The engineering collaborator argued for **decoupling edge properties from edge types**, so that the set of properties an edge can carry is not fixed by its type and can be extended as requirements land. The group agreed the initial relational design must not foreclose the later move to richer graph structures.

## 4. Findings, measurements, and diagnoses

### 4.1 Measurement representation

Tarik: radiology measurements are reported inconsistently in practice, so enforcing strict measurement standards in the model is impractical. Agreed to introduce a **taxonomy of measurement types** and to avoid over-specifying at this stage. This is the same position as the measurement and method separation already written up ([`01-what-the-vocabulary-must-express.md` §4](../docs/next-gen-schema/01-what-the-vocabulary-must-express.md)).

### 4.2 Edge properties versus nodes

The engineering collaborator's rule, which matches the test already recorded in [`03-draft-structures.md` §2.1](../docs/next-gen-schema/03-draft-structures.md): **reusable concepts such as location are nodes; descriptive attributes such as units of measure are edge properties.** The group added a second consideration on top of it: whether a property is needed for *search or traversal* as against merely for *description*. A property that must be queried or traversed pulls toward being a node.

### 4.3 Compositional versus associative edges

Raised by the reviewer as unresolved: how to distinguish **compositional** edges (sub-findings, components) from **associative** ones (co-occurrence). The group agreed explicit rules and worked examples are needed, because the distinction determines both the structure and how the existing published corpus migrates into it. No rule was settled on the call; the reviewer took the action to draft one.

### 4.4 Diagnosis and finding as separate node types

The longest thread on the call. The reviewer and the engineering collaborator both argued for **separate node types** for Diagnosis and Finding, to avoid semantic confusion. Tarik acknowledged the boundary is genuinely blurry in clinical practice but agreed the ontology needs a clear delineation.

**This supersedes what is currently written up.** The analysis documents model `diagnosis` as a *value of `entity_type`* on a single `FindingClass` node type ([01 §5](../docs/next-gen-schema/01-what-the-vocabulary-must-express.md)), on the reasoning that the same term is used in both roles depending on context. The call agreed on separate node types instead. Tarik confirmed and expanded on this in the email exchange that followed ([exchange §1](review-exchange-2026-08-25-extract.md)).

### 4.5 Worked clinical examples

**Acute pyelonephritis** and **COVID-19** were used to illustrate the problem. Agreement that a diagnosis is a node linked to multiple findings, each carrying its own properties, and that the ontology has to support both compositional and associative relationships between them. Acute pyelonephritis is already queued as example 6 ([03 §10](../docs/next-gen-schema/03-draft-structures.md)); COVID-19 was the case that drove the earlier diagnosis question ([`02-review-questions.md` Q4](../docs/next-gen-schema/02-review-questions.md)).

---

## 5. Action items

| Owner | Item | Status |
|---|---|---|
| Tarik Alkasab | Provide roughly **ten example findings or CDE sets** closest to the ideal structure, to focus modelling and avoid overgeneralizing | Outstanding |
| Tarik Alkasab | Commit and share the documentation and worked examples for review | Done, 21 August 2026 (`a53aa62`, `a0fb91d`) |
| Tarik Alkasab | Push the current iteration of the workflow and codebase for the engineering collaborator's review | Outstanding |
| The reviewer | Draft rules for when an edge is compositional as against associative, and circulate for feedback | In progress (§4.3) |
| The reviewer | Send directed questions needing clinical input | Done, 25 August 2026 ([exchange](review-exchange-2026-08-25-extract.md)) |

The ten-example request is the significant open one. It is a scoping instrument as much as a modelling one, and nothing in the repository answers it yet.
