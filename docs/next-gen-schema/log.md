# Log

Change history for the next-gen schema bundle, newest first. Decisions are recorded in [10](10-decision-record-2026-09-02.md); this log records what changed in the bundle and when.

## 2026-09-15

**Housekeeping** (Claude): publishing process written into the tools playbook and the handoff's site item updated; the checker's denylist sweep extended to `docs/plans/` and the root glossary after two plan files were found carrying a participant's name (renamed and sanitized); the agreed terms added to `CONTEXT.md`; the commit-and-merge path written as `docs/plans/2026-09-15-commit-and-merge-path.md`.

- Added tissue-type and structure-type anatomy scope families; their connections to the location hierarchy remain open (S50).
- Corrected the agenda's open-question list: existing Measurement and Observation behavior is stated as background; OWL mapping, export metadata, and verification are deferred implementation work (S51). The meeting agenda is revised without changing the schema or demos.
- Recorded the ordinary-chat question preference in the handoff and working agenda.
- Republished the corrected meeting agenda at its existing public URL; only the agenda HTML changed, with anonymous access and content equality verified.

## 2026-09-14

**Clarification** S49 distinguishes historical prototype instructions and owner working positions from unsettled integration proposals. The comparison now treats inheritance, finding/diagnosis types, and components as discussion items, explains the OWL meaning question, and suggests incremental export improvements for the alpha. No implementation or published artifacts changed.

**Decision** S48 specifies any-match scope lists by default and support for explicit all-match combinations. Recorded as an acceptance criterion for the implementation foundation, not a verified current defect; implementation is unchanged.

**Decision** S47 defines missing modality constraints as no information, not pan-modality applicability. The agenda and structural documentation now distinguish omission from explicit applicability; implementation is unchanged.

**Clarification** S46 makes a categorizing DataElement and a taxonomy alternative representations of the same distinction, not simultaneous ones. The structural discussion question that combined them has been withdrawn; implementation and examples are unchanged.

**Decision** S45 distinguishes modality constraints on findings, individual descriptor bindings, and descriptors themselves. Intrinsic descriptor limits are not overridable defaults; omission semantics remain open. Documentation only.

**Discussion idea** added: multi-component measurements, with component representation and the relationship to derivation left open. This is not a proposal or model decision; no implementation changes.

**Proposal** S44 puts default selection cardinality on DataElement with possible binding-edge adjustment. Adjustment rules remain open for discussion; no implementation changes.

**Decision** S43 permits direct AnatomicLocation bindings to DataElements and Measurements, without requiring a FindingClass to describe normal anatomy. Documentation updated; implementation and example artifacts are unchanged.

**Decision** S42 allows a FindingClass–DataElement binding to restrict permitted values to a subset while retaining the shared element and its full value set. Documentation updated; no implementation or example artifacts changed.

**Decisions** S40–S41 make AssessmentScheme a separate definition type with links to multiple ordinary DataElements, rather than one flattened category list or distinct assessment-specific descriptors. Binding details remain open; no implementation or example artifacts changed.

**Decision** S39 distinguishes Measurements from DataElements, explicitly allows ordered or unordered value sets, and makes measurement method optional and unspecified by default. Requirements and structural documentation reflect the decision; example artifacts are unchanged.

**Analysis** added of [the reviewer's alpha structure](12-alpha-structural-comparison.md), using her implementation approach as the foundation: definition semantics, anatomy, components, identifiers, and JSON/OWL contracts. Clinical-content and mat-presentation work are tracked separately; the implementation direction is recorded as S38.

**Creation** of [11 The Anatomy Axis, Current State](11-anatomy-axis.md), a one-page summary for anyone working on anatomy. **Rewrite** of [04](04-anatomy-gaps.md) against the pinned anatomic locations file (2,926 nodes): pleural space closed, lung parenchyma, perirenal space, and the compound sided ids added, and a running node request list started as the owner asked on 13 September. **Extract** added of the [13 September exchange](../../notes/review-exchange-2026-09-13-extract.md). **Update** to 00 §2.6 and 06 §6 pointing at the new substrate; decisions S30 to S37 recorded in 10 during the week.

## 2026-09-10

**Extract** added of the [8 September email exchange](../../notes/review-exchange-2026-09-08-extract.md) with the reviewer: a cystic lesion with a mural nodule as a second component case, the FindingClass-versus-DataElement boundary, how the definitions are consumed, and RadLex anatomy gaps; its open items are listed at the end and carried on the working to-do list.

## 2026-09-09

**Update** extending the correction below to every subtype: the six pleural effusion subtypes and the chronic, emphysematous, and xanthogranulomatous pyelonephritis nodes now assert their own scope, modality, region, subspecialty, sex, and age edges (10 C18), so their mats and hover cards show context again without any propagation. The four committed mats and trees regenerated. The owner's words recorded verbatim on 10 S13.

**Correction** to subtype semantics and the mat renderer: `SUBTYPE_OF` no longer supplies scope or context from a parent, and no mat or hover card labels anything as inherited. Acute pyelonephritis now carries explicit scope, modality, region, subspecialty, sex, age, course, and etiology assertions, preserving the displayed context without implying OOP-style inheritance. Added focused regression coverage.

## 2026-09-08

**Review** of the single-page knowledge-graph viewer placed in `raw_sources/` on this date, written up as [a note](../../notes/viewer-review-2026-09-08.md): its model in our terms, nine deviations, the new questions it raises, and twelve harmonization proposals, none decided. Pointers added in 06 §3 and §4. The plan for queue item 1, the part-solid nodule, is in `docs/plans/2026-09-08-part-solid-nodule.md`; nothing in the graph or the pictures changed.

## 2026-09-04

**Update** to 06: rewritten as a current-state handoff (start here, what exists, waiting on the owner, the queue in order, half-baked, decisions that belong to others, housekeeping); the dated narrative it carried is in this log.

**Research** added [ontology background and follow-up questions](../../notes/ontology-background-research-2026-09-04.md), connecting primary standards to proposed examples for target identity, assertion context, negation, formal semantics, mappings, and diagnostic reasoning. Recommendations remain separate from model decisions.

**Update** integrating knowledge that had only lived in the working session: the Hood taxonomy profile as a note with a `SOURCES.md` entry; the code-lookup policy folded into 03 §2.1 and an "adding a node" step in the graph README; the purpose of the pictures at the top of 09; the observation that only relationship sourcing now separates Diagnosis from FindingClass, in 03 §1 and 07; a pointer from 07's open question 2 to 10 S18. Process and tooling kept apart in a new [`tools/README.md`](tools/README.md) and a lessons section in the exploration review.

## 2026-09-03

**Report plane, second round.** Added “Right kidney is unremarkable” as an absent renal-abnormality Observation, bound presence to both negative-only Grouping nodes, restricted anatomy in the report picture to referenced locations and scope paths, and made every observation- and definition-space relationship visibly land with source dots and target arrowheads.

**Report plane example.** Added a text-anchored JSON Lines report and a generated two-plane picture for one pyelonephritis sentence. The example shows five report Observations, observation-space relationships, pointers into definition classes, anatomy, and elements, and sided anatomy satisfying unsided scope through explicit `SUBTYPE_OF` edges. Added the report validator/renderer, four-value severity scale, sided perirenal-space nodes, worked-example explanation, and generated-site page.

**Restructure** for the mat-and-tree work. Added [09 The Mat and the Tree](09-mat-and-tree.md) as the display specification and [10 Decision Record](10-decision-record-2026-09-02.md) with every decision marked by provenance and sorted into structure, display, and content. Retitled 08 to [Two Worked Examples](08-worked-examples.md) and moved its decisions section into 10. Created `archive/` for superseded material and `explorations/` for the two rounds of diagram alternatives, both with their own indexes. Extended the bundle checker to subdirectories and to treat `log.md` as reserved. A separate cleanup plan for incidental documentation issues is in `docs/plans/2026-09-03-doc-cleanup-plan.md`.

## 2026-09-02

**Creation** of the mat and the tree. `tools/render_cards.py` replaced `tools/render_constellation.py` (deleted with its view files and diagrams) after two rounds of agent alternatives were reviewed. Four committed diagrams: two mats, two trees. The site's node pages carry the mat with hover detail; tree pages add a click layer.

**Update** to the graph. `required` removed from every `HAS_ELEMENT` edge, spec, and renderer. `graph/concepts.jsonl` added: RadLex ids for modality, region, and subspecialty; provisional codes for etiology, sex, age, and time course. Element-level external codes added. Subspecialty, sex, age, and time-course edges added to the two example families. Placeholder concept ids replaced throughout.

**Creation** of the canonical graph (`graph/*.jsonl`), the loader and validator (`tools/graph.py`), the spec converter (`tools/spec_to_graph.py`), the two worked examples as graph files with report-plane samples, and the site builder (`tools/build_site.py`). Added 08 and amended 01, 03, 06, 07 for the decisions of the day.

## 2026-09-01

**Creation** of [07 The Finding and Diagnosis Relationship Family](07-relationship-family.md).

## 2026-08-21

**Creation** of the bundle: 00 to 06, the object-dossier renderer and specs, and `docs/check_bundle.py`.
