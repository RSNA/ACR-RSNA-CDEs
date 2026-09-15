---
type: Review Record
title: The Knowledge Graph Viewer, 8 September 2026 — Review
description: What the single-page "CDE knowledge graph skeleton" viewer received on 8 September 2026 models and shows, where it deviates from the bundle's current model, what it raises that the bundle has not yet taken into account, and how the two could be harmonized. Claude's reading; the harmonization proposals are not decisions.
tags: [next-gen-schema, review, viewer, harmonization, assessment, measurement, scope, mappings]
status: draft
generated: { by: "claude-code/claude-fable-5.1", at: 2026-09-08 }
sources:
  - id: viewer
    resource: raw_sources/cde-knowledge-graph-view-v5.html
    title: "CDE knowledge graph skeleton", version 5, a self-contained HTML page (internal; kept out of the public repo)
    last_modified: 2026-09-08
  - id: exchange
    resource: /notes/review-exchange-2026-08-25-extract.md
    title: The 25 August exchange whose open questions the viewer carries as flags
  - id: memo
    resource: /notes/conditional-relationships-memo.md
    title: The memo whose identifier scheme the viewer shares
  - id: record
    resource: /docs/next-gen-schema/10-decision-record-2026-09-02.md
    title: The decision record the deviations are measured against
sanitization: The page carries no personal names. Its author is not stated in the file; the attribution below is an inference and is marked as one. Nothing is quoted beyond the page's own short interface labels and open-question flags.
---

# The Knowledge Graph Viewer, 8 September 2026

**Status:** Claude's review of a file the owner placed in `raw_sources/` on 2026-09-08. Read, run in a browser, and clicked through on the same day. Section 5 is proposals; none of it is decided.

## 1. What it is

A single HTML file, about 2,000 lines, with the RSNA and ACR marks, a browse and search list, and an object view. Everything is in one embedded JavaScript object of about 80 entries: the pulmonary nodule family (nodule, solid component, three differential diagnoses, Fleischner and Lung-RADS as assessments with full value sets), a thorax family (pleural effusion, consolidation, ground-glass opacity, atelectasis, mediastinal lymphadenopathy, pneumonia, pulmonary edema), the thyroid nodule with the five TI-RADS axes, the anatomy those need, and one terminology-mapping node per external code. It has editing affordances (add synonym, add mapping, add attribute, remove) that do nothing; it is a mock of an authoring and browsing surface, not a data store.

**Attribution (inferred).** The identifier prefixes (`FC-`, `DE-`, `AS-`, `MS-`, `AL-`, `V-`) match the [26 August memo](conditional-relationships-memo.md), and the open-question flags on the page restate the questions of the [25 August exchange](review-exchange-2026-08-25-extract.md). It reads as the external reviewer's working model. The file does not say so.

**What it covers that the bundle also covers:** pulmonary nodule, thyroid nodule, pleural effusion, presence, margin, attenuation (named composition), size (named mean diameter), Lung-RADS and Fleischner (stubs in our graph, full nodes there).

**What it does not cover at all:** the report plane (no Observations, no laterality, no sided anatomy), a finding taxonomy (no `SUBTYPE_OF` between findings anywhere), Grouping nodes, edge properties (no typicality, specificity, ids, or notes on any edge), causal or progression edges, and relationship types as objects.

## 2. Its model, in our terms

| Viewer | Ours | Same, or different |
|---|---|---|
| eight node types: finding, diagnosis, assessment, measurement, element, value, anatomy, concept | FindingClass (with `entity_type`), Diagnosis, Grouping, DataElement (with `kind`), Value, AnatomicLocation, Concept, RelationshipType | **Assessment and Measurement are node types there, an `entity_type` and a `kind` here.** No Grouping there. |
| typed id prefixes (`FC-000001`, `MS-000001`, `AL-000001`, `V-000012`) | one `RDE2_` space, type in the graph ([00 Issue E](../docs/next-gen-schema/00-current-understanding.md)) | different; ours is a settled direction, theirs is the memo's lag |
| anatomy has its own `AL-` id and maps to a RadLex concept node marked `primary` | the RID *is* the id (10 S12, OWNER) | **conflict** |
| `HAS_DATA_ELEMENT`, derived at display time into `HAS_MEASUREMENT` when the target is a measurement | `HAS_ELEMENT` | naming only |
| `HAS_VALUE` | `member` | naming only |
| `MAY_REPRESENT` (finding to diagnosis), `MAY_BE_REPRESENTED_BY` (diagnosis to finding) | `MAY_MANIFEST_AS` with inverse `MAY_REPRESENT` | same pair, opposite assertion direction |
| `OCCURS_WITH`, footnoted "says nothing about cause or sequence" | `OCCURS_WITH`, SNOMED wording ([07 §2](../docs/next-gen-schema/07-relationship-family.md)) | same |
| `MAY_HAVE_COMPONENT` from pulmonary nodule to solid component, flagged "Component vs subtype not settled" | the same edge with a prose note, and the same open fork ([07 §7](../docs/next-gen-schema/07-relationship-family.md) question 4) | same open question, both sides |
| `ASSESSED_BY`; the "screening" and "incidental" selector is a tag **on the assessment node** ("Applies when"), flagged "Which scheme applies is still being worked out" | a note on the edge; the owner ruled the selector comes from the exam object ([exchange §5](review-exchange-2026-08-25-extract.md)) | a third position; ours is the owner's |
| `MAPPED_TO` a concept node carrying `system`, code, `match` (exact, narrow, broad, close), `sourceVersion`, `primary` | `exactMatch` or `closeMatch` edge to `SYSTEM:code` with `display` | **theirs is richer:** four SKOS match kinds, a source version per mapping, a primary flag |
| anatomy edges `PART_OF` and `IS_A`, both used | `SUBTYPE_OF` reused for the sided is-a (10 S27, CLAUDE DEFAULT); no part-of edges yet | different names; theirs matches RadLex's own relations |
| scope on the node: `{loc, kind: specific or region or class, strength: required or expected or unconstrained}` | `SCOPED_TO` edge with `kind` (structure and so on) and `strength` | same three kinds under different names ([00 Issue H](../docs/next-gen-schema/00-current-understanding.md)); theirs spells out the match rule per kind |
| **scope on data elements** (composition and margin scoped to lung; short axis to mediastinal lymph node; the TI-RADS axes to the thyroid) | `SCOPED_TO` domain is FindingClass, Diagnosis, Grouping; the [exchange §4](review-exchange-2026-08-25-extract.md) answer to widen it to DataElement is not yet applied | **theirs implements an owner answer we have not applied** |
| **modality on elements and findings as a display filter** (`mods`); the object view has a modality radio bar that hides attributes not declared for the chosen modality, flagged "Modality mechanism not fully defined" | `SEEN_ON` on classes only | new |
| `version`, `status` (draft, proposed, published, retired), `date` on every node; browse filters by status; `uses` counts ("used in 214") | version and status on spec nodes; nothing on most graph nodes; binders listed on element dossiers | theirs keeps a minimal lifecycle in the semantic layer, which [00 Issue J](../docs/next-gen-schema/00-current-understanding.md) leaves open |
| local anatomy with provenance: `source: local`, `sourceStatus: pending_request`, `request: RADLEX-1187` (lung parenchyma) | `owner` free text on the node and the [04 gap log](../docs/next-gen-schema/04-anatomy-gaps.md) | theirs is structured |
| open questions as `openNotes` on nodes and values and `open` on groups, rendered as amber dashed flags in place | open questions in documents (07 §7, 06 §3) | theirs puts the question where the reader meets the object |
| three columns: "wider context" (edges into the focus), the focus with an anatomic-scope card, "detail" (edges out of the focus); tiles expand in place; edges read as sentences ("FINDINGCLASS pulmonary nodule *records* DATA ELEMENT presence") with the edge code above; a breadcrumb chain of context bands when drilling from finding to element to value; a Diagnosis is always a root | the mat: one context object, containers by relationship, no wires, hover detail ([09](../docs/next-gen-schema/09-mat-and-tree.md)) | different organizing axis: direction of the edge there, kind of relationship here |

## 3. Where it deviates, and whose decision stands

Listed from most to least consequential for the model.

1. **No finding taxonomy, and the taxonomy is our spine.** Nothing there is a subtype of anything; the attenuation element's three values map to the RadLex concepts `solid pulmonary nodule` (RID50151), `part-solid pulmonary nodule` (RID50152), and `non-solid pulmonary nodule` (RID50153), which RadLex models as kinds of nodule. That is the attribute side of the subtype-versus-condition fork made concrete: RadLex already has the subtypes, and the viewer binds them as values. Our side is 10 S1 (OWNER, one taxonomy) and the owner's counter-proposal in [exchange §2](review-exchange-2026-08-25-extract.md). The fork itself is still open (07 Q4), and the viewer's flag says so too.
2. **Assessment and Measurement as node types.** The viewer flags its own choice ("Assessment as its own node type is untested"). Ours is an `entity_type` value and a `kind` value, and [06 §6](../docs/next-gen-schema/06-next-steps.md) already asks the committee whether even Finding and Diagnosis both survive. A measurement node there is a data element with units, a `predefined` flag ("conventions controlled by committee"), and no value set; nothing in it needs a separate type except the display label. Assessments there carry `authority` and `scheme` (a year), which our FindingClass does not.
3. **Anatomy ids.** `AL-` ids with a `primary` RadLex mapping versus the RID as the id. 10 S12 is the owner's and stands. The viewer's local node (lung parenchyma, RadLex has only the generic `parenchyma`, RID5978) shows the case that needs a provisional id and a tracked upstream request; we handle that with `STUB-` ids and the 04 gap log, less formally.
4. **Diagnosis as a root.** The viewer never shows a diagnosis in another object's context and reads findings "in the context of" a diagnosis. That is a reading order, not a taxonomy, but it is the finding-under-diagnosis ranking the owner rejected in S1 ("you don't seem to get how interchangeably radiologists use these").
5. **Representation where we say causation.** Pleural effusion there "may represent" lung cancer, pneumonia, and pulmonary edema; here heart failure, pneumonia, and the rest `MAY_CAUSE` the effusion. The viewer has no causal edge, so every diagnosis-finding link is evidential. [07 §2](../docs/next-gen-schema/07-relationship-family.md) keeps the two apart with a test; the viewer would fail it for pneumonia (an effusion is a complication, not pneumonia showing itself).
6. **Nothing on edges.** The reviewer wrote on 25 August that edge properties were the direction she would argue for; the viewer has none. No conflict, only lag.
7. **Where the assessment selector lives.** On the assessment node there; the owner put it on the exam object in the instance layer. The viewer's own flag concedes it is unresolved.
8. **Presence has four values there** (present, absent, indeterminate, unknown, each with RadLex and SNOMED codes) **and five here** (with `possible`). The viewer's definition text reads like the published RDE wording. Content, not structure; worth a look at where `possible` came from.
9. **Mapping quality.** The viewer marks SNOMED CT 427359005 "Solitary nodule of lung" as a *narrow* match for pulmonary nodule; our spec has it as `exactMatch`. The viewer is right, and our two-valued match vocabulary cannot say so.

## 4. New things to take into account

Things the viewer raises that the bundle has no answer to yet.

- **Element-level scope** (`composition` and `margin` bounded by lung, `short axis` by mediastinal lymph node). The owner already said yes to this ([exchange §4](review-exchange-2026-08-25-extract.md)); the `SCOPED_TO` domain in `graph/core.jsonl` still excludes DataElement. Note the viewer's own difficulty: `margin` is reused by four classes yet scoped to lung.
- **Modality applicability below the class.** Which attributes apply under which modality (attenuation under CT only; margin under CT and MR). Ours has `SEEN_ON` on the class and nothing on bindings or elements. Whether this belongs on the element, on the binding, or in the template layer is a real question; the viewer's filter is a good demonstration of why someone wants it.
- **Value-level conditions and co-occurring values**, flagged on Lung-RADS: 4X can only follow a category 3 or 4 assessment and the category it escalated from is lost; S is a modifier that rides on another category (2S, 4BS). These are the same shape as the RDES329 value-level condition in the [exchange appendix](review-exchange-2026-08-25-extract.md), and neither the condition-on-edge nor the subtype answer addresses them.
- **Derived and composite measurements**: volume by segmentation versus volume computed from diameters ("not the same measurement; whether they are one object or two is not yet defined"); size in three axes as one measurement holding three values; Lung-RADS pairing each diameter threshold with a volume threshold ("alternative measurements or one criterion in two encodings"). Ours decided multi-component quantities ([00 §8 Decided](../docs/next-gen-schema/00-current-understanding.md)) and has `INTERPRETED_FROM` for classes, but no derived-measurement mechanism; IDR's "Computed Property" is the grammar-side counterpart.
- **Source version on every mapping** (RadLex 4.3; SNOMED CT US Edition 2026-03-22) and a `primary` terminology per node. We record neither.
- **A structured upstream-request record** on a locally held anatomy node.
- **Open questions carried on the objects themselves**, shown in place. Governance metadata in the semantic layer, which the committee said to move out (00 §4 topic 6), but as a review aid it is effective.
- **A solid component with three attributes**: mean diameter, margin, and a new element, *position within nodule* (central, eccentric). Our spec gives it a size only.
- **Full Lung-RADS and Fleischner value sets with codes** (RadLex RID50134 to RID50141 and RID50710; SNOMED CT 1204653000 to 1204659001 for the Fleischner recommendations) and the thyroid `TI-RADS` categories (RID50503 to RID50508). Ours has stubs. Every code is a claim to verify with `molu` before use, not a fact.
- **Better codes than ours in two places**: RadLex RID50155 "average diameter" as an exact match for size (mean diameter), where we have a close match to RID13432 "diameter"; and RID39409 "composition" for attenuation. Also RID50154 "solid component of part-solid pulmonary nodule", which our own lookup confirmed on 2026-09-08.

## 5. How to harmonize (proposals)

Claude's proposals for the owner to accept, reject, or take to the reviewer. Nothing here is applied.

1. **Trivial name alignment, do it in one pass.** `HAS_ELEMENT` and `HAS_DATA_ELEMENT`; `member` and `HAS_VALUE`; the assertion direction of the manifestation pair. Pick one name each and say so in [07 §1](../docs/next-gen-schema/07-relationship-family.md) and in a mapping table the reviewer can read.
2. **Scope kinds: one table, two vocabularies.** Their `specific`, `region`, `class` are our named structure, region, and structure type. Adopt one set of names, and adopt the viewer's habit of stating, per kind, which anatomy relation the match walks (part-of for structure and region, is-a for structure type) and what each strength does (required rejects, expected flags, unconstrained does nothing). That belongs in [01 §2](../docs/next-gen-schema/01-what-the-vocabulary-must-express.md) as structure and in the hover detail as display.
3. **Anatomy edges: take `PART_OF` and `IS_A` as the names now.** S27 reused `SUBTYPE_OF` for the sided is-a as a Claude default; the viewer uses the names RadLex and AnatomicLocations.org use. The part-solid nodule example needs a part-of walk anyway (a lobe is part of a lung, not a kind of lung), so this is the moment. Keep `SUBTYPE_OF` for the finding taxonomy only.
4. **Widen `SCOPED_TO` to DataElement**, as the owner already answered. Then decide whether element scope means "this element only makes sense at this anatomy" (the viewer) or is the same thing as the normal-structure binding of [03 §9](../docs/next-gen-schema/03-draft-structures.md) seen from the other end. They are not the same, and the viewer's `margin` case shows the first reading misfires on shared elements.
5. **Mappings: adopt the four SKOS match kinds and a source version.** Change `closeMatch` to the pair `broadMatch` and `narrowMatch` where the direction is known, keep `closeMatch` for the rest, and put `sourceVersion` in the edge props. Re-examine the SNOMED match on pulmonary nodule. Cheap, and it removes a real inaccuracy.
6. **Assessment and Measurement: put the node-type question to the committee alongside the Finding-versus-Diagnosis question** in [06 §6](../docs/next-gen-schema/06-next-steps.md), with the viewer's `authority` and `scheme` properties and the `predefined` flag as the concrete things a separate type would carry. Do not split now; the mat and tree are indifferent to the answer.
7. **The assessment selector stays off the vocabulary** (owner, exchange §5). Tell the reviewer the viewer's "Applies when" tag is the thing the owner moved to the exam object.
8. **Causation.** The reviewer's viewer needs `MAY_CAUSE` before its pleural effusion can agree with ours; send [07 §2](../docs/next-gen-schema/07-relationship-family.md) with the test.
9. **Ids.** Ours are the settled direction (00 Issue E). Ask the reviewer to move the viewer to `RDE2_` and to the RID-as-id rule for anatomy (S12), and take from the viewer the structured `request` record for a local anatomy node into our stub convention.
10. **Open-question flags on objects.** Worth trying on the site as display: a `note` already exists on nodes and edges; an `open` property rendered as a flag in the hover detail would cost little. Display decision for the owner.
11. **Modality on bindings.** Raise as a structure question in 06 §3 rather than adopt: the viewer's own flag says the mechanism is undefined.
12. **Content to take as drafts**, the way OIFM models are taken ([00 §5.1](../docs/next-gen-schema/00-current-understanding.md)): the solid component's three attributes; the Lung-RADS, Fleischner, and TI-RADS value sets with their codes, verified first; RID50155 and RID39409; the viewer's presence definition wording, checked against the published RDE.

## 6. What this changes for the queue

Queue item 1 in [06 §4](../docs/next-gen-schema/06-next-steps.md) (the part-solid nodule) now has the RadLex subtype and component concepts to bind, the viewer's draft of the solid component's attributes, and a reason to add part-of anatomy edges; the plan for it is [`docs/plans/2026-09-08-part-solid-nodule.md`](../docs/plans/2026-09-08-part-solid-nodule.md). Queue item 5 (staging) and the assessment stubs gain a value-set source. Proposals 1 to 5 and 9 are cheap and could be a small batch of their own; 6, 10, and 11 are decisions.

## 7. How it was reviewed

The file was read in full, served from `raw_sources/` on a loopback port, opened with headless Chromium (the no-sandbox Node script of [`tools/README.md`](../docs/next-gen-schema/tools/README.md)), and the object views for the pulmonary nodule, solid component, lung, presence, composition, and the assessments were captured under the gitignored `.preview/viewer-review/`. Code lookups for the nodule subtypes and the component were made with `molu` on 2026-09-08; the viewer's other codes were not verified.
