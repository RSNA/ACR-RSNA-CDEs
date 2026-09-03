# Plan: canonical graph, two constellation examples, and a browsable site

**Written:** 2026-09-02. **Status:** complete (2026-09-02); follow-ups are listed in [06 §0](../next-gen-schema/06-next-steps.md). **Owner approves each commit.**

## Goal

Turn the next-gen schema material into something a reader can click through: every node of the vocabulary as a page, every edge a link, the two new worked examples (acute pyelonephritis, pleural effusion) drawn as constellation diagrams, and the analysis documents and notes published alongside. Do it from a canonical graph so the site is generated, not hand-written, which also delivers the canonical form that [03 §6.2](../next-gen-schema/03-draft-structures.md) specified but nothing yet reads or writes.

## Decisions taken to get moving

These were open at the start; the defaults below are recorded so they can be reversed deliberately.

1. **Site generator is Python, not Astro.** The Astro/Starlight site under `astro-docs/` has no installed modules, is pinned to old versions, and deploys only from the `styleguide` branch. A dependency-light Python generator alongside `render_neighborhood.py` and `check_bundle.py` keeps one toolchain. Output goes to `site/`, gitignored, built on demand; publishing to GitHub Pages is a later step.
2. **Canonical form is JSON Lines** in `docs/next-gen-schema/graph/*.jsonl`, exactly the shape of [03 §6.2](../next-gen-schema/03-draft-structures.md): one object per line, nodes before edges, nodes sorted by id, edges by (type, from, to), keys sorted. A normalizer enforces the sorting and the bundle checker verifies byte-exactness.
3. **Existing examples stay in their spec files.** A converter turns the six `examples/*.json` specs into graph lines at build time so the site covers everything. Migrating the dossier renderer to read the graph is deferred.
4. **Non-imaging causes are Diagnosis nodes with no elements**, carrying only a name, a definition, and mappings. The alternative (edges targeting SNOMED codes directly) breaks the rule that edges point at nodes.
5. **Grouping is a node type**, used only for the negative-only nodes (`renal abnormality`, `pleural abnormality`). Positively reportable underspecified classes (`renal lesion`) are ordinary FindingClasses.
6. **`SUBTYPE_OF` is one taxonomy, unrestricted by finding versus diagnosis**, tested by "can you say X without Y". Owner's decision on 2026-09-02; the edits to 07 follow.
7. **Patterns (lesion, mass, process, abnormality) are not in the graph.** They become an authoring-guide section and a checker rule.
8. **Context metadata** (modality, region, etiology) stays minimal in the new examples, pending the resource the owner said he would provide ([06 §1](../next-gen-schema/06-next-steps.md)). Etiology and modality concept nodes are placeholders.

## Phases

### Phase 1: plan and format
- [x] This document.
- [x] `graph/README.md`: the line format, node types, edge property conventions, id allocation.
- [x] `tools/graph.py`: load, merge, validate (unique ids, edges resolve, relationship types declared), normalize.

### Phase 2: the two examples as graph files
- [x] `graph/core.jsonl`: relationship types, shared elements (presence, size, severity, change from prior), concept nodes.
- [x] `graph/pyelonephritis.jsonl`: the constellation from the sketch (diagnosis with subtypes, five manifesting findings with typicality and specificity, renal abscess as a caused diagnosis under renal lesion, progression to chronic, kidney length binding interpreted as enlargement).
- [x] `graph/pleural-effusion.jsonl`: one finding node with its elements, diagnosis subtypes (empyema, hemothorax, chylothorax, malignant, hepatic hydrothorax, parapneumonic), causal edges from clinical diagnoses with typicality and target hints, companions.
- [x] Codes looked up through molu; RadLex gaps recorded.
- [x] Report-plane samples for both.

### Phase 3: diagrams
- [x] `tools/render_constellation.py`: reads the merged graph plus a small view spec (which nodes, which columns), emits a deterministic SVG with nodes linked by id.
- [x] Two view specs and two SVGs under `examples/` and `diagrams/`.
- [x] `check_bundle.py` learns the second renderer and checks graph normalization.

### Phase 4: site
- [x] `tools/build_site.py` (PEP 723 script, deps: markdown): node pages, edge catalog, per-type indexes, example pages with the constellation SVG, docs and notes rendered from markdown with links rewritten, diagrams copied, a search box over node names.
- [x] `site/` in `.gitignore`; build instructions in `graph/README.md` and the bundle index.

### Phase 5: documents
- [x] `08-worked-examples.md`: the two examples, what each exercises, what broke, and the 2026-09-02 decisions (unrestricted subtyping, confidence in the report plane, no binding inheritance, patterns as authoring guide, grouping node type).
- [x] Amend 07 §1 domain column and §2 (subsumption test); 03 §2 (`INTERPRETED_FROM` domain widened to FindingClass); 01 §5 third column for diagnosis.
- [x] Update 06 next steps, bundle index, root index; run `python3 docs/check_bundle.py`.
- [x] Mark this plan complete.

## Phase 6, added 2026-09-02: mat and tree

- [x] Decisions recorded in [`2026-09-02-mat-and-tree-decisions.md`](2026-09-02-mat-and-tree-decisions.md); two agent attempts reviewed under `.preview/mat-attempts/`.
- [x] `tools/render_cards.py`: the mat and the tree; `render_constellation.py` and its views and diagrams deleted.
- [x] Graph: `required` removed everywhere; `graph/concepts.jsonl` lookup table with RadLex ids and provisional owned codes; element-level codes; subspecialty, sex, age, and course edges on the two families.
- [x] Four committed diagrams under the byte-exact check; 08 re-pointed.
- [x] Site: node pages carry the mat, family pages carry the tree with the interactive layer (click for relationships and a fuller card; hover for the detail card).

## Phase 7, added 2026-09-03: documentation

- [x] 09 (display specification) and 10 (decision record with provenance) added to the bundle; 08 retitled to the worked examples with its decisions moved to 10.
- [x] `archive/` and `explorations/` created with indexes; the constellation design archived; both rounds of alternatives kept verbatim with frontmatter.
- [x] `log.md` added at the bundle root; checker extended to subdirectories and reserved files.
- [x] Incidental issues collected in [`2026-09-03-doc-cleanup-plan.md`](2026-09-03-doc-cleanup-plan.md).

## Out of scope

Publishing to GitHub Pages; migrating the dossier renderer to the graph; the context-metadata edges of 06 §1; the prose pass of 06 §2.
