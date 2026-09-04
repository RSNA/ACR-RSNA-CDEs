# Log

Change history for the next-gen schema bundle, newest first. Decisions are recorded in [10](10-decision-record-2026-09-02.md); this log records what changed in the bundle and when.

## 2026-09-04

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
