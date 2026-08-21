---
type: Analysis
title: "Next-Generation CDE Schema: Current Understanding"
description: Referenced baseline for the CDE schema redesign — scope, terms, the assumed grammar, what the committee has decided, requirements evidence, prior art, and open issues.
tags: [next-gen-schema, cde, analysis]
status: draft
generated: { by: ["human:talkasab", "claude-code/claude-fable-5"], at: 2026-08-19 }
sources:
  - id: siim-minutes
    resource: /notes/siim-meeting-extract.md
    title: SIIM committee meeting minutes (extract)
    author: team:rsna-acr-cde-committee
    last_modified: 2026-06-12
  - id: committee-notes
    resource: /notes/committee-notes-extract.md
    title: Committee meeting notes (extract)
    author: team:rsna-acr-cde-committee
  - id: deck
    resource: /notes/proposed-schema-changes-deck-extract.md
    title: Proposed schema changes deck (extract)
    author: team:rsna-acr-cde-committee
    last_modified: 2026-06-12
  - id: recommendations-2
    resource: /notes/schema-recommendations-part2.md
    title: "CDE schema recommendations, Part II (extract)"
    author: "human:talkasab"
  - id: current-schema
    resource: /cde.schema.json
    title: Current CDE schema (requirements evidence)
    author: team:rsna-acr-cde-committee
  - id: sample-set
    resource: /SampleDES.cdes.json
    title: Worked example set against the current schema
    author: team:rsna-acr-cde-committee
  - id: authoring-conventions
    resource: /astro-docs/src/content/docs/reference/
    title: Published authoring conventions (set, element, valueset)
    author: team:rsna-acr-cde-committee
  - id: oifm-overview
    resource: /notes/oifm-overview.md
    title: OIFM definitions and modelling guidance
    author: "human:talkasab"
    last_modified: 2026-07-29
  - id: anatomiclocations
    resource: "https://github.com/talkasab/anatomiclocations.org"
    title: AnatomicLocations.org, data/body_parts.json release 1.0.0-rc.1 (ISC)
    author: "human:talkasab"
  - id: published-corpus
    resource: "https://radelement.org"
    title: Published CDE corpus and public API
    author: team:rsna-acr-cde-committee
---

# Next-Generation CDE Schema: Current Understanding

**Status:** Draft for discussion — not an approved design
**Date:** 2026-08-19
**Branch:** `next-gen-2026`
**Purpose:** Establish a shared, referenced baseline: what we are building, what has already been decided, what the existing corpus tells us must be expressible, what prior art exists, and what remains genuinely open. This is a statement of the *starting position*, not a proposal.

> **Companion document:** [01-what-the-vocabulary-must-express.md](./01-what-the-vocabulary-must-express.md) works out what the vocabulary has to be able to express — anatomic scope guidance, the breadth of what gets reported on, measurement versus interpretation, and what `entity_type` is really recording. It postdates this document and settles several issues here; see [01 §6](./01-what-the-vocabulary-must-express.md).

---

## 1. What we are actually building

The goal is to represent radiology results as data structures rather than unstructured text. The committee's stated objective is to "scale up and modernize radiology common data elements creation and publication" ([SIIM deck, slide 2](../../notes/proposed-schema-changes-deck-extract.md)). The existing RSNA/ACR Common Data Element model is the incumbent, with a published corpus, a public API, and vendor consumers at [radelement.org](https://radelement.org).

### 1.1 Vocabulary, not grammar

This project defines the **vocabulary** of radiology results: the terms available for saying what was seen, how it is characterized, and how those terms relate to one another. It does not define the **grammar** — how an individual result is assembled from those terms.

The committee has already drawn this line twice. The [SIIM minutes](../../notes/siim-meeting-extract.md) record the consensus that "validation and template constraints are out of scope for the semantic schema, focusing instead on defining possible attributes and relationships." The [initial proposal](../../notes/schema-recommendations-part2.md) set templates aside — "along with a method of representing them in report text" — as a separate concern to be layered in later.

### 1.2 Terms used here

| Term | Meaning |
|---|---|
| **FindingClass** | A term naming a kind of finding that can be reported. Replaces what the current schema calls a *set*. |
| **DataElement** | A term naming a characteristic that can be recorded about a finding, together with the values it permits. Replaces *element*. |
| **Value** | A permitted answer to a DataElement. |
| **AnatomicLocation** | A place, identified by a RadLex ID and drawn from AnatomicLocations.org (§2.6). |
| **Anatomic scope guidance** | A statement on a FindingClass about which AnatomicLocations are congruent with it. Guidance about a value space, not a location in its own right. |
| **Relationship type** | A named, typed edge — available between FindingClasses, and available to the grammar between Observations. |
| **Observation** | A single reported result in an actual report. Belongs to the grammar (§1.3), not to this project. |

### 1.3 The grammar: IHE IDR

Not a deliverable, but necessary context: the vocabulary is shaped by what consumes it. The grammar is specified by **IHE** in the [Imaging Diagnostic Report (IDR) Phase II supplement](https://www.ihe.net/uploadedFiles/Documents/Radiology/IHE_RAD_Suppl_IDR_PhII_Rev1-2_PC_2026-03-04.pdf) (Rev. 1.2, public comment 4 March 2026), **read directly and extracted in [`notes/ihe-idr-extract.md`](../../notes/ihe-idr-extract.md)**. IDR profiles FHIR `Observation`: the target entity is a `BodyStructure` — anatomy in `.structure` (pre-coordinated except laterality), laterality as its own field, a pathologic entity in `.morphology` — and the property observed is `Observation.code`, its value in `Observation.value` with units. CDE Sets are encoded as a root observation whose `.code` is the set, with `.hasMember` to the element observations; IDR says explicitly that the associated observations "are expected to follow the specifications for the CDE Set on radelement.org."

In our terms, an **Observation** carries:

- a pointer to a **FindingClass** — *what* is being reported (IDR: `.morphology` on the target, or the root `.code` of a Finding Set) — **or, for the description of a normal structure, the AnatomicLocation itself as the target with no morphology** — a pattern IDR already specifies and works through in its Table B.3-1 ("Pancreatic duct · Diameter · 2 mm"), so [01 §3.1](./01-what-the-vocabulary-must-express.md) needs no grammar change
- a pointer to an **AnatomicLocation** — *where* it is (IDR: `.structure` + `.laterality`; our sided nodes map to that pair)
- a set of key/value pairs, each key a pointer to a **DataElement** and each value one that element permits
- relationships to other Observations in the same report — component, adjacency, causation, "may be related to," and so on

Two consequences are worth stating immediately, because the sources disagree about both. **Location is not an attribute**: it is a pointer sitting beside the FindingClass pointer, not one of the key/value pairs. And **relationships exist at two levels, and the levels are connected**: between Observations, which are claims about this patient on this exam, and between FindingClasses, which are general knowledge. "This effusion may be caused by this pneumonia" and "effusions may be caused by pneumonias" are different assertions — the vocabulary owns only the second — but the first is an *expression* of the second: the report-level relationship instantiates a potential the vocabulary states once. That has a structural consequence: a vocabulary-level relationship must have **identity of its own** (`pleural effusion MAY_BE_CAUSED_BY pneumonia` is a citable thing, `RDE2_000900`), so that a report edge can say which potential it expresses. See [03 §5](./03-draft-structures.md).

### 1.4 What the vocabulary must therefore supply

| Grammar slot | What this project must supply |
|---|---|
| the FindingClass pointer | the FindingClasses themselves, at a granularity still to be decided ([01 §2.4](./01-what-the-vocabulary-must-express.md)) |
| the AnatomicLocation pointer | per-class **anatomic scope guidance** — which locations are congruent with this kind of finding — and an anatomy vocabulary able to express that guidance (§2.6) |
| the DataElement/value pairs | DataElements, their value spaces, and which are appropriate to which FindingClass — **or to which AnatomicLocation**, for normal-structure descriptors ([03 §9](./03-draft-structures.md)) |
| inter-Observation relationships | the relationship *types* available to be instantiated |
| all of the above | metadata making the terms discoverable |

Explicitly **not** supplied: the Observation structure itself, serialization, cardinality and conditional-requirement rules, templates, or an instance store.

---

## 2. Framing decisions already taken

These are not open questions. They were settled in discussion and they constrain everything downstream.

### 2.1 This is a retrenchment, not an iteration

The new model is not a revision of `cde.schema.json`. The existing schema is retained as **evidence of requirements** — a record of what authors have needed to express over the life of the project — but its *structure* carries no authority and should not be preserved by default. Arguments of the form "this is really just formalizing something the current schema already allows" are to be avoided: they are seductive because they make the change easier to sell, and they invite the committee to treat the work as a patch.

### 2.2 The internal representation will be a graph

The authoritative internal representation is a knowledge graph, not a document tree. JSON becomes an *export format* for consumers, not the model. This follows directly from the committee's own language — the minutes describe the proposal as a move to "a graph model, where findings point to canonical attribute objects" ([minutes](../../notes/siim-meeting-extract.md), Structure).

### 2.3 We lean into ontology concepts

Subsumption, typed relations, ontology binding, and inference are in scope as first-class concerns rather than as things layered on afterwards.

### 2.4 Stay close to RadLex

RadLex is treated as the more formal ontology and we follow its lead. The working posture is to **keep in line with RadLex terms, relations, and modelling conventions as far as we practically can** — it currently lacks some of the content and structures this project needs, so divergence is sometimes unavoidable, but it should be deliberate rather than incidental.

This is somewhat more than "we bind anatomy to RadLex" (which is what [deck slides 15–16](../../notes/proposed-schema-changes-deck-extract.md) approved), and it colours design in several ways:

- **Identifier strategy should stay compatible.** Reuse RIDs where they exist; mint our own where they do not, in a form that could be reconciled later. See Issue E.
- **Minimise divergence.** Avoid inventing relations where RadLex already has a usable one; prefer extending its existing relation set.
- **Watch what we take on.** Every foreign dependency is one more thing that alignment has to accommodate.

**What is known about RadLex:**

- **The ontology is on GitHub.** [RSNA/RadLex](https://github.com/RSNA/RadLex) is the official source going forward; the 4.3 release captures what was last pushed to BioPortal, and that OWL file is now the authoritative artifact.
- **Published as OWL** — which settles our own formalism question; see Issue D.
- Actively governed, and freely licensed for commercial and non-commercial use. The *Playbook* ships twice yearly under joint Regenstrief/RSNA governance, but it is a separate artifact.
- **Where RadLex already has relevant imaging-observation terms, we refer to them.** Little conflict is expected in this space.
- An active **FHIR distribution** exists in HL7 Terminology, generated 2025-07-07.

> **Verification status.** Synonym handling and external references have now been checked directly against the 4.3 OWL — see [05-radlex-baseline.md](./05-radlex-baseline.md), including one finding that contradicts a committee assumption (SNOMED mapping is effectively absent from the OWL). The relation axioms and the imaging-observation branch remain to be examined the same way.

### 2.5 The RadLex anatomy hierarchy is a DAG

Pharynx belongs to both head and neck. AnatomicLocations.org (§2.6) deliberately imposes a strict containment tree over the same nodes, so for the traversals this project needs the DAG problem is already handled in the resource we would consume.

### 2.6 AnatomicLocations.org — the anatomy substrate

[AnatomicLocations.org](https://github.com/talkasab/anatomiclocations.org) began as an independent project that *used* RadLex — built outside it because RadLex lacked the location coverage and structure that imaging needed, but keyed to RadLex IDs throughout. **It is now a subproject of RadLex and is imminently becoming an identified collection within RadLex itself.** The nodes it minted locally ("synthetic" nodes without an existing RID) will receive RadLex RIDs and become first-class RadLex nodes. So "bind anatomy to RadLex" and "use AnatomicLocations.org" are converging on the same statement, and the dependency is on RadLex.

Source: [`data/body_parts.json`](https://raw.githubusercontent.com/talkasab/anatomiclocations.org/main/data/body_parts.json), release `1.0.0-rc.1`, ISC licence, with TypeScript and Python client libraries. Single 1.1 MB JSON file validated by a JSON Schema.

**Verified by direct analysis of the data file, 2026-07-28:**

| Property | Finding |
|---|---|
| Size | **2,890 nodes** — small enough to hold entirely in memory; consistent with §7.4 |
| Shape | **Strict rooted tree.** Single root `RID39569 whole body` (self-contained). Every node has exactly one `containedById`; no multi-parent entries anywhere. |
| Second hierarchy | `partOfId` on **990** nodes, differing from `containedById` in **946** of them |
| Laterality | `leftId`/`rightId` on **1,611** nodes; `unsidedId` on **1,584** |
| Sex specificity | **110** nodes |
| External codes | **2,282** nodes, 4,185 entries: SNOMED CT 1,732 (60%) · FMA 1,643 · UMLS 578 · MeSH 232 — a principal value-add over raw RadLex ([05 §2](./05-radlex-baseline.md)) |

**Two hierarchies, and the distinction is real.** `containedById` is *where a structure physically sits*; `partOfId` is *what functional structure it belongs to*. They are not redundant:

| Structure | Contained by | Part of |
|---|---|---|
| abdominal aorta | retroperitoneum | aorta |
| aortic arch | mediastinum | aorta |
| appendix | pelvis | colon |

The two traversals answer different questions, and anything that walks the hierarchy must say which it means. For *upper lobe of right lung*, containment yields `→ right lung → thorax → whole body` while part-of yields `→ right lung` and terminates.

**Scope guidance resolves by plain traversal** ([01 §2.2](./01-what-the-vocabulary-must-express.md)). Run against this data:

```
lung  →  thorax  →  whole body
toe   →  ankle   →  lower extremity  →  whole body
```

The paths diverge immediately, so a FindingClass scoped to `lung` rejects a toe location by plain ancestry walk.

**Laterality is carried by the location, not by a DataElement.** Left, right, and unsided variants are distinct nodes with explicit triad links. Accordingly **there will be no laterality DataElements.** Location itself is not a DataElement at all — it is the Observation's AnatomicLocation pointer (§1.3). Elements that express *more precise* location than the codes permit — position within a structure, relation to a landmark — may exist, defined where needed, but they are not canonical and never restate what the code already says. This supersedes *Laterality* on the [committee's draft reusable-element list](../../notes/committee-notes-extract.md).

**Known gaps are tracked separately.** The resource is being actively extended — notably with is-a relationships over locations and explicit incorporation of the RadLex nodes for structure types such as tendon, muscle, and artery. Specific gaps found in analysis are recorded in [`04-anatomy-gaps.md`](./04-anatomy-gaps.md) rather than here, so that this document does not go stale as they close.

### 2.7 Consequences

Three things follow immediately and are worth stating so they are not re-argued:

- **JSON Schema is disqualified as the primary artifact.** It answers one question — is this document well-formed? Every core requirement here is a cross-document, graph-shaped constraint (shared element identity across thousands of findings; transitive subsumption; value spaces constrained by an external anatomy ontology; acyclicity). JSON Schema cannot express any of them. This also explains an apparent contradiction in the minutes, which record both that cycle detection is needed *and* that validation is out of scope for the semantic schema: those are two different artifacts that do not currently exist separately.
- **A file-level "shared vs. copied element definition" question disappears.** In a graph, a shared element is one node with one identity. What survives is smaller: where a contextualized description ("Pulmonary embolism is absent") lives, which is a property of the binding edge (§6).
- **The governance mechanism is now at risk and must be designed for.** Today the committee approves changes as pull requests against JSON in git. A graph database cannot be diffed in a PR. See §7.3.

---

## 3. Requirements inventory: what the corpus tells us must be expressible

Derived from [`cde.schema.json`](../../cde.schema.json) and [`SampleDES.cdes.json`](../../SampleDES.cdes.json), deliberately stripped of the current schema's structure. These are durable needs; where they currently live is an artifact.

### 3.1 Identity and lifecycle

- **Stable, citable identifiers** for the top-level object, for properties, and for individual permitted values. Value identity is *derived* from element identity (`RDE<n>.<i>`, [line 501](../../cde.schema.json)) — **carried forward**: values keep derived ids (`RDE2_000001.0`, `.1`, …) and so belong to exactly one element.
- **Draft identifiers before assignment.** Authors need to work before an ID exists; the current schema accommodates this with a `TO_BE_DETERMINED<n>` pattern ([lines 24–28](../../cde.schema.json)). A real workflow requirement, easily overlooked.
- **Lifecycle status with history** — currently Proposed / Published / Retired with dates ([line 588](../../cde.schema.json)).
- **Versioning** ([line 556](../../cde.schema.json)).
- **An extension escape hatch.** Any property beginning with `$` is reserved for notations and extensions ([lines 9–14](../../cde.schema.json)) — evidence that consumers needed room the model did not give them.

### 3.2 Semantics and presentation, separately

- **A definition** — what the thing means ([line 170](../../cde.schema.json)).
- **A question** — how a user should be prompted for it ([line 174](../../cde.schema.json)). Distinct from the definition; a presentation concern. **Not carried into the vocabulary** — it belongs to the template/grammar layer ([03 §8](./03-draft-structures.md)).
- **A machine-facing value string** distinct from the human-readable value name, explicitly "intended to provide a human and/or machine readable string that could be used to calculate a score, identify a position on a decision tree" ([line 511](../../cde.schema.json)). Evidence that scoring systems and decision trees are real use cases.

### 3.3 Value spaces

- **Enumerated permitted values** with human-readable name and definition.
- **Selection cardinality** — minimum and maximum number of values selectable ([line 466](../../cde.schema.json)).
- **Numeric ranges** with minimum, maximum, step, and unit ([lines 386, 409](../../cde.schema.json)).

### 3.4 Clinical context

- **Anatomic location** at multiple levels ([line 351](../../cde.schema.json)).
- **Modality applicability** ([line 430](../../cde.schema.json)).
- **Subspecialty applicability** ([line 541](../../cde.schema.json)).

### 3.5 Evidence and provenance

- **External code bindings** at every level — top-level object, property, and individual value ([line 365](../../cde.schema.json)).
- **Exemplar images** at all three levels, with caption, dimensions, **rights**, and attribution ([line 263](../../cde.schema.json)). Implies a media and rights-management requirement.
- **Bibliographic references** with citation, DOI, and PubMed ID ([line 593](../../cde.schema.json)) — distinct from bare web links.
- **Contributors**, as both people (with ORCID, affiliation, and role) and organizations (with role) ([line 300](../../cde.schema.json)).

### 3.6 Requirements visible as leakage

The most useful evidence is what authors did when the schema gave them no home for something. The deck's own critique (slide 14) documents the clearest case: because anatomic location had no proper representation, authors expressed it as ad hoc value-set elements named "Location", "Position", "Orientation", and even "Type", with ungrounded values varying finding to finding. That is a requirement asserting itself through workarounds.

A systematic pass over the ~1000 published sets for similar patterns would be the single highest-value piece of evidence-gathering available to this project, and it does not depend on any design decision.

---

## 4. What the committee agreed (SIIM, 12 June 2026)

Six topics were presented as "Current State / Proposing" pairs and discussed for approval ([deck](../../notes/proposed-schema-changes-deck-extract.md); [minutes](../../notes/siim-meeting-extract.md)).

**1. Nomenclature.** "Set" and "element" are too abstract to convey that these model things seen on imaging exams. Renaming agreed in principle; the deck left the specific terms open, and they have since been settled as `FindingClass` and `DataElement` (§6).

**2. Structure — decoupling.** Findings and their properties become independent objects; a finding *links* to a shared property definition rather than owning one. Canonical shared properties (presence, change from prior, grading scales, standard measurements) are defined once. Explicitly framed as a graph model, with the acknowledgement that it "will require more sophisticated authoring tools capable of managing relationships and preventing issues like cyclic structures."

**3. Property definitions — qualitative vs. quantitative.** The polymorphic element splits in two. Qualitative is functionally unchanged. Quantitative replaces fixed units with a *quantity type* — single dimension, three dimensions, volume, count, attenuation — implying allowable units, with the unit itself recorded on the observation rather than the definition (deck slides 12–13). The minutes additionally flag that **ordinality** of categorical properties must be captured.

**4. Location.** Promoted from ordinary property to anchor. A finding's body part binds to RadLex; RadLex's `has_part` / `has_regional_part` relations then *suggest* a valid location value space from which the author selects clinically applicable options (deck slide 16, worked through with thyroid gland RID7578). Spatial location — planes and axes relative to landmarks — separated as its own concern. SNOMED mapping assumed to be maintained at the RadLex level — **an assumption the 4.3 OWL does not bear out; see [05 §2](./05-radlex-baseline.md)**.

**5. Relationships.** Explicit, typed, many-to-many edges: causal links, co-occurrence, subtypes, component-of, groupings. Two constraints recorded: subtypes are defined **independently, without automatic inheritance of attributes**, and cardinality/validation constraints are **out of scope** for the semantic schema.

**6. Metadata and governance.** Synonyms at multiple levels; entity type; clinical context descriptors; coding systems beyond the current four. Governance, versioning, provenance, approval, and AI-contribution records move **out of the semantic layer** into a separate event-sourced schema (deck slides 21–22; [first_ideas](../../notes/schema-recommendations-part2.md)).

### 4.1 Explicitly deferred

- **Templates.** An organizing layer *above* findings carrying shared scope, conditional rules, inherited requirements, and mutual exclusivity — "an organizing concept rather than a fully defined schema object" (deck slide 7).
- **Versioning.** Omitted deliberately: "I think we're moving toward every new version of our nodes being a new node, which are all connected by the shared ID" ([first_ideas](../../notes/schema-recommendations-part2.md)). A significant departure from today's mutable-node-with-auto-incrementing-version, still undecided.

---

## 5. Prior art

### 5.1 OIFM — a working implementation of substantially this design

The Open Imaging Finding Model work has independently built much of this and is roughly one iteration ahead. **OIFMs can be treated as drafts for this project's FindingClasses** — many will be brought over for committee review rather than authored from scratch.

- Definitions and modelling guidance: [`openimagingdata/findingmodels` prompts/overview.md](https://github.com/openimagingdata/findingmodels/blob/main/prompts/overview.md)
- Source-format schema draft (v2): [gist 8648a888…](https://gist.github.com/talkasab/8648a8887e4ee6ce381375485bc280c7)
- Metadata field reference: [gist 2d366555…](https://gist.github.com/talkasab/2d366555a8c371d8f2e2316f9d39d0e0)

| Topic | OIFM's answer |
|---|---|
| Decoupling | Canonical attribute files referenced from finding models; seeded with `presence` and `change from prior`. |
| Authored vs. published form | A **source** model (with unresolved references) is distinguished from a **hydrated** model (references expanded); runtime APIs operate on the hydrated form. |
| Quantitative properties | `quantity_kind` from a checked-in registry, plus optional `common_units`. |
| Relationships | A registry where each type declares whether it is inverse-backed (`type_of` ↔ `has_subtype`, `causes` ↔ `caused_by`) or symmetric (`occurs_with`); authors assert one side, tooling derives the rest. |
| Governance separation | Per-model `.history.jsonl` event sidecars with `actor_kind` (`human`/`ai`/`system`) and content hashes. |
| Metadata | Worked vocabularies for body regions, subspecialties, entity type, modalities, etiologies, sex specificity, age profile, expected time course. |
| Modelling guidance | `overview.md` is effectively the "when to define a new finding vs. use a property" guidance the committee assigned as an action item. |

**Caveat.** OIFM's file-based design makes choices that a graph makes differently — most notably copy-on-reference for shared attributes (§2.7). Bringing models over is a review step, not a bulk import.

---

## 6. Terminology — **decided**

**`FindingClass`** replaces what the current schema calls a *set*. **`DataElement`** replaces what it calls an *element*. A permitted answer to a data element remains a **value**.

This settles a question the earlier sources left open. For the record, they disagreed:

| Source | Top-level object | Property | Value |
|---|---|---|---|
| [first_ideas](../../notes/schema-recommendations-part2.md) and [deck slide 6](../../notes/proposed-schema-changes-deck-extract.md) | Finding | Attribute | — |
| [committee_meeting_notes](../../notes/committee-notes-extract.md) (later) | Finding Class | Data Element | Value |
| OIFM | Finding Model | Attribute | Value |

The deck marked its own choice provisional — "Nomenclature for this discussion: Findings and Attributes — **will be finalized later**" (slide 6) — and the decision has now gone the way the committee notes pointed: away from "observation" (avoiding collision with FHIR's `Observation` resource), and retaining "data element" to preserve RadElement / RDE branding.

**Consequence for the published documentation.** [`reference/set.md`](../../astro-docs/src/content/docs/reference/set.md), [`reference/element.md`](../../astro-docs/src/content/docs/reference/element.md), and [`reference/valueset.md`](../../astro-docs/src/content/docs/reference/valueset.md) encode the old vocabulary throughout and must be revised. So must [`build_schemas.py`](../../build_schemas.py) and the per-granularity schema filenames it generates.

**Two things still unnamed.** Nothing yet names the **instance** of a finding class — the actual observed nodule in an actual report — and the graph framing makes that layer unavoidable rather than optional. And nothing names the **binding** between a `FindingClass` and a `DataElement`, the edge the deck labels only as `has_attribute`; in a graph that edge is where contextual overrides, requiredness, and conditionality would live, so it needs a name.

---

## 7. Architecture sketch

Not decided. Recorded as the current working proposal so it can be argued with.

### 7.1 Layering

| Layer | Role |
|---|---|
| **Authoring** | Forms and tables for subject-matter experts. Existing RadElement authoring UI is already this shape (deck slide 13). Curators never see the formalism. |
| **Source of truth** | Deterministic text serialization in git. Preserves pull-request review and therefore the committee's existing governance mechanism. |
| **Query and reasoning** | A graph store, materialized from source by CI. A derived artifact, not a system of record. |
| **Publication** | Generated: JSON / JSON-LD for vendors, an OWL release alongside RadLex's, documentation for the site. |

### 7.2 Why the store is a derived view

Two consequences. The database choice becomes low-stakes and reversible — a derived store can be swapped without migration, which is why an architecture can be agreed before a product is chosen. And it resolves §7.3 rather than deferring it.

### 7.3 The governance problem

Today the committee approves changes as pull requests against JSON in git (see PR #62 in the log). A graph database cannot be diffed in a pull request, and "the committee approved this change" loses its concrete referent.

This is a solved problem for ontologies generally, and RadLex now does it itself: the ontology lives in git as OWL ([RSNA/RadLex](https://github.com/RSNA/RadLex)), is reviewed as diffs, and is released from there. Whatever store is chosen must round-trip to a canonical text form losslessly and stably.

### 7.4 Scale is not a constraint

Roughly a thousand published sets today; perhaps ten thousand finding classes at ambition. Tens of thousands of nodes. Performance should not be a selection criterion, and infrastructure sized for a larger problem should be resisted.

### 7.5 Two shapes stacked

The model is two shapes stacked. The **finding-class taxonomy and relationships** are ontology-shaped — hierarchical, subsumption-bearing, wanting a reasoner. The **element and value definitions** are data-model-shaped — reusable slots with types, cardinality, units, bounds. These pull toward different tooling, and it may be right to use different tools for each rather than forcing one to cover both.

---

## 8. Open issues

Ordered by dependency. Issues A and B constrain most of the rest.

**Issue A — Does `is-a` carry inference?** The minutes state that subtypes inherit nothing. But the motivating use case for groupings is explicitly inferential: modelling "upper abdomen unremarkable" as `upper abdominal abnormality / presence: absent` and having an application "do a sweep for its ancestors being negative" ([02 Q3](./02-review-questions.md)). That is only sound if `is-a` is genuine transitive subsumption. Likely requires separating a strict, acyclic, inference-safe subsumption relation from looser associative relations. Note also the closed-world assumption: the negation sweep is valid only if the hierarchy beneath a class is complete *and* the radiologist actually assessed all of it — which may need to be a declared property of a class rather than an emergent one.

**Issue B — Are finding classes classes or individuals?** As OWL classes, subsumption and reasoning work natively and we align with how SNOMED and RadLex model things, but governance metadata requires punning or annotation properties. As SKOS-style individuals, metadata is trivial but `is_a` becomes `skos:broader`, which has no inference semantics — surrendering exactly what Issue A wants. OWL 2 punning is the standard escape. To be decided deliberately.

**Issue C — What reasoning do we actually need, and who owns the formal layer?** No upper-ontology imports (§2.4). What remains is not *which* foundation to adopt but what inference the vocabulary must support, and who maintains the axioms once they exist. Constraint: content must remain workable for subject-matter experts, which means curators author against patterns or templates and never see the description logic — SNOMED's practice at scale, and the cost is a standing role to own the patterns.

| Need | What it requires |
|---|---|
| Negation propagation down the finding hierarchy | Our own `is_a`, transitively closed |
| Anatomic traversal (thyroid → lobes; lung ⊃ segment) | RadLex's partonomy and containment |
| Structure-type scope (tendons, arteries) | An is-a relation over locations — being added to AnatomicLocations.org (§2.6) |
| Finding / diagnosis disambiguation | Conceptual; axioms buy consistency checking |
| SNOMED, LOINC, RadLex interop | Mappings |

**Issue D — Formalism: OWL.** **Settled in principle by §2.4.** RadLex is published as OWL and the official source is now an OWL file in git; following suit is the alignment posture applied to the one decision where it matters most. What remains is mechanics: relationship assertions want provenance, approval status, and strength on the *edge*, which OWL expresses through annotation on reified axioms, named graphs, or RDF-star rather than natively. [RDF 1.2](https://www.w3.org/TR/rdf12-concepts/) reached Candidate Recommendation in April 2026; [SPARQL 1.2](https://www.w3.org/TR/sparql12-query/) remains a Working Draft. Named graphs work today and are the conservative option.

**Issue E — Identifiers and migration of the published corpus.** **Direction settled: a fresh `RDE2` namespace.** All node types — FindingClass, DataElement, Value — mint from one space, `RDE2_NNNNNN` (separator mandatory: bare `RDE2123` is ambiguous against legacy `RDE`-prefixed IDs), as local names under a URI base so the OWL export has IRIs from day one. Type lives in the graph, not the identifier, so an ID survives reclassification. Values are the one exception: their ids derive from their element (`RDE2_000001.0`, `.1`, …), continuing the legacy `RDE<n>.<i>` pattern, and their machine value is the slugified name. The ID names the *lineage*; version-nodes (per the every-version-a-new-node direction, §4.1) are addressed off it. Legacy RDE/RDES continuity becomes mapping edges (`skos:exactMatch` / `Replaced_by`), not an ID scheme. Still open: whether FindingClasses eventually also carry RIDs, and the migration mechanics for the live API and its vendor consumers. Two sub-questions belong to the committee rather than this document: whether the ID space is partitioned for distributed minting (OIFM's `{ORG}` segment exists for exactly this, relevant if OIFM models arrive with their contributors), and what the URI base is — `radelement.org/id/` implies infrastructure commitments the RadElement operators should sign off on. There is a live API and there are vendor consumers. When duplicate elements collapse into canonical ones, what happens to the losing RDE IDs? Are existing sets auto-migrated, hand-migrated, or frozen beside a new corpus? Identifiers likely need to become URIs. Should be settled before the model hardens.

**Issue F — OIFM: how the crossover works.** Largely settled in direction by §5.1 — OIFMs are drafts for FindingClasses and will be brought over for review. Open: whether that means a shared identity space and canonical element registry, or a crosswalk maintained as a first-class deliverable.

**Issue G — How much of the grammar must be pinned before the vocabulary is finishable?** The Observation structure is IHE's ([§1.3](#13-the-assumed-grammar)), not ours. But several arguments in the sources offload real work onto it — that findings need no location property because the Observation carries one; that units live on the observation; that confidence (definite/probable/possible, from the [committee notes](../../notes/committee-notes-extract.md)) is an instance concern. Each is sound only if the IDR profile actually provides it. **Checked against the supplement** ([`notes/ihe-idr-extract.md`](../../notes/ihe-idr-extract.md)): units live in `Observation.value` — confirmed; anatomy-as-target with no morphology — confirmed, so the normal-structure proposal needs no grammar change; hierarchical targets (part-solid nodule) — confirmed via `.hasMember`, though untyped. **Not provided by IDR:** a causal relationship between observations ("LATER — no etiology mechanism in FHIR Core"), so our report-level `MAY_BE_CAUSED_BY` must be raised with IHE; and a typed way for a report edge to cite the vocabulary relationship it expresses, which would be an extension. IDR also asks two questions of us — the coding-system identifier for RadElement codes, and whether CDE Sets may carry additional sub-observations — that this vocabulary must answer. **One deliberate divergence to keep open:** IDR routes positive diagnoses to FHIR `Condition`; it is not clear which radiology-report diagnoses should be Conditions at all, so **our working default is that every assertion in a report, diagnoses included, is an `Observation`**. The full list of items to take to IHE is in [`notes/ihe-idr-extract.md` §8](../../notes/ihe-idr-extract.md).

**Issue H — Anatomic scope guidance: what shape is it?** Location is a grammar-level pointer, not an attribute (§1.3), which dissolves the apparent contradiction between [first_ideas](../../notes/schema-recommendations-part2.md) and deck slide 19. What the vocabulary owes is per-class guidance, and the same source says it ranges over "a body region (e.g., the abdomen), a structure type (e.g., arteries), or … a named body structure." Only two of those are spatial. Open: whether the guidance records which kind it is, and how binding it is ([01 §2.3](./01-what-the-vocabulary-must-express.md)). Separately, the RadLex dependency has an unspecified maintenance cadence, gap-filling process, and fallback.

**Issue I — Versioning.** Deferred but entangled with everything: durable identity across versions, what constitutes a breaking change, whether consumers and canonical references pin versions, whether a retired value code may be reused. The direction recorded in [first_ideas](../../notes/schema-recommendations-part2.md) — every new version is a new node, connected by a shared ID — is a real departure from today's mutable node and still undecided.

**Issue J — Smaller open questions.** Index codes as open system URIs, distinguishing exact-match from broader/narrower. Where ordinal scales live, given they blur the qualitative/quantitative split. Whether to adopt an external quantity vocabulary (UCUM is already cited in the current schema; QUDT models quantity-kind → dimension → units). Event log central or per-node. What minimum lifecycle status must remain in the semantic layer for consumers.

### Decided

- **Multi-component measurements** — a quantity type with components, per deck slide 13.
- **Synonyms are typed** — abbreviation, lay term, eponym, deprecated, and so on — rather than a flat list.
- **Shared versus copied element definitions** — one node, one identity (§2.7).

---

## 9. Deliverables and context

From the [SIIM minutes](../../notes/siim-meeting-extract.md):

- **New schema draft** — assigned to the external reviewer; the [committee notes](../../notes/committee-notes-extract.md) list it as a joint reviewer/Tarik deliverable. How the drafts converge is unsettled.
- **Smoke test** — create definitions using the new model and confirm they characterize real observations in medical-record language (several committee members). Now doing double duty: it is also the cheapest way to settle Issues A and B, since modelling deliberately hard FindingClasses end to end produces those decisions as a byproduct. The strawman structures in [03-draft-structures.md](./03-draft-structures.md) exist to make that possible. Proposed cases: one plain (pulmonary nodule), one location-anchored (thyroid nodule), one grouping-with-negation-propagation (upper abdominal abnormality).
- **Edge cases** — examples where the structure does not fit, collected before finalizing (all).
- **Modelling guidance** — rules of thumb for when to define a new finding vs. use a property; an experienced committee author's existing guidelines named as a starting point. OIFM's `overview.md` already covers much of this ground.
- **Two white papers** — technical (e.g. JIM) and clinical (e.g. JACR).

**Immediate next step for this repository:** make the context metadata (modality, subspecialty, body region, etiology, sex, age, time course) real edges to real nodes instead of the free-text strings the example specs carry today: RadLex's own concept wherever it has one, with the DICOM and SNOMED mappings proposed to RadLex rather than kept here; `RDE2_` nodes only where RadLex has nothing ([03 §10](./03-draft-structures.md)).

Next committee meeting was set for 24 June 2026.

**Repository context.** Work is on `next-gen-2026`, currently identical to `master`. The published documentation site is in [`astro-docs/`](../../astro-docs); [`reference/set.md`](../../astro-docs/src/content/docs/reference/set.md), [`reference/element.md`](../../astro-docs/src/content/docs/reference/element.md), and [`reference/valueset.md`](../../astro-docs/src/content/docs/reference/valueset.md) encode the old naming and authoring conventions and must be revised for the `FindingClass` / `DataElement` rename (§6). [`build_schemas.py`](../../build_schemas.py) generates per-granularity validation schemas driving editor validation. The knowledge bundle itself is validated by [`docs/check_bundle.py`](../check_bundle.py) — frontmatter, links and section references, index coverage, diagram freshness, and a leak sweep; run `python3 docs/check_bundle.py` from the repo root before committing.

---

## 10. Source material

| Source | Location |
|---|---|
| Current schema (requirements evidence) | [`cde.schema.json`](../../cde.schema.json) |
| Worked example set | [`SampleDES.cdes.json`](../../SampleDES.cdes.json) |
| Published authoring conventions | [`astro-docs/src/content/docs/reference/`](../../astro-docs/src/content/docs/reference/) |
| Tarik's schema proposal, part II | [`notes/schema-recommendations-part2.md`](../../notes/schema-recommendations-part2.md) |
| Design questions raised in review (Apr–May 2026) | [`02-review-questions.md`](./02-review-questions.md) — distilled; originals not committed |
| SIIM committee meeting minutes (12 Jun 2026) | [`notes/siim-meeting-extract.md`](../../notes/siim-meeting-extract.md) |
| Committee meeting notes (terminology) | [`notes/committee-notes-extract.md`](../../notes/committee-notes-extract.md) |
| SIIM proposed-changes deck | [`notes/proposed-schema-changes-deck-extract.md`](../../notes/proposed-schema-changes-deck-extract.md) |
| OIFM definitions and modelling guidance | https://github.com/openimagingdata/findingmodels/blob/main/prompts/overview.md |
| OIFM source-format schema v2 draft | https://gist.github.com/talkasab/8648a8887e4ee6ce381375485bc280c7 |
| OIFM metadata field reference | https://gist.github.com/talkasab/2d366555a8c371d8f2e2316f9d39d0e0 |
| RDF 1.2 / SPARQL 1.2 status | https://www.w3.org/TR/rdf12-concepts/ · https://www.w3.org/TR/sparql12-query/ |
| Published corpus and API | https://radelement.org · https://radelement.org/about/docs |
| RadLex ontology (official OWL source) | https://github.com/RSNA/RadLex |
| AnatomicLocations.org | https://github.com/talkasab/anatomiclocations.org |
| IHE IDR Phase II supplement (the grammar) | https://www.ihe.net/uploadedFiles/Documents/Radiology/IHE_RAD_Suppl_IDR_PhII_Rev1-2_PC_2026-03-04.pdf |
