---
type: Playbook
title: Next Steps and Open Threads
description: Handoff for whoever picks this up with a clean context - where to start, what exists, what is waiting on the owner, the queue in order, what is half-baked, and which decisions belong to the committee, RadLex, or IHE.
tags: [next-gen-schema, handoff, next-steps]
status: draft
generated: { by: ["human:talkasab", "claude-code/claude-fable-5.1"], at: 2026-09-04 }
sources:
  - id: baseline
    resource: /docs/next-gen-schema/00-current-understanding.md
    title: Current understanding
    author: "human:talkasab"
  - id: record
    resource: /docs/next-gen-schema/10-decision-record-2026-09-02.md
    title: The decision record; every open default below is numbered there
    author: "human:talkasab"
  - id: log
    resource: /docs/next-gen-schema/log.md
    title: What changed when; the dated narrative this handoff no longer carries
---

# Next Steps and Open Threads

Rewritten 2026-09-04 as a current-state handoff. History is in [`log.md`](log.md); decisions and who made them are in [10](./10-decision-record-2026-09-02.md). Run `python3 docs/check_bundle.py` from the repo root before every commit; the owner approves each commit.

## 1. Start here

Read in this order, then build the site and click around it.

1. [00](./00-current-understanding.md) for what is settled and the open issues list (§8).
2. [10](./10-decision-record-2026-09-02.md) for every decision since, marked as the owner's or Claude's. Do not treat a CLAUDE DEFAULT as settled.
3. [09](./09-mat-and-tree.md) for how the pictures work, [08](./08-worked-examples.md) for the examples and which of their facts are unverified.
4. [`graph/README.md`](graph/README.md) for the canonical form, [`tools/README.md`](tools/README.md) for the scripts and how to look at the pictures.

```
python3 docs/next-gen-schema/tools/graph.py check
python3 docs/check_bundle.py
uv run docs/next-gen-schema/tools/build_site.py      # then open site/index.html
```

Plans in `docs/plans/` are working artifacts, not bundle documents; the completed ones are marked so. A separate list of incidental documentation issues is in [`docs/plans/2026-09-03-doc-cleanup-plan.md`](../plans/2026-09-03-doc-cleanup-plan.md); do those in a batch, not as a side effect of other work.

## 2. What exists

- **The canonical graph** in `graph/*.jsonl`: relationship types, shared elements, anatomy, a concept lookup table with RadLex ids and provisional codes, and two worked families. Validated and normalized by `tools/graph.py`; the six older interim specs are converted in at load time.
- **Three pictures**, all generated: the mat (one object, one hop out), the tree (an is-a outline), and the report picture (one report in two planes). Committed copies under `diagrams/` are byte-checked.
- **The site**, gitignored, built on demand: a mat on every finding, diagnosis, and grouping page with hover detail; tree pages with a click layer; every document and note rendered.
- **Two worked examples** as graph files with report samples, and one report-plane example; their clinical values are Claude's and unreviewed (10 §C).
- **The documents**: 00 to 10, `log.md`, `archive/` for superseded material, `explorations/` for the diagram alternatives.

## 3. Waiting on the owner

Only the owner can do these, and they gate the rest.

- **Review the invented clinical content.** Every typicality and specificity on the two mats, every `expected` hint in the hover, the subtype trees, and the exact-versus-close code choices (10 C2 to C8). A pass over the pleural effusion and acute pyelonephritis mats marking what is wrong turns 10 §C from unreviewed to reviewed.
- **Rule on four structural defaults** that shape the graph: scope and context propagating down subtypes at render time (S13); non-imaging causes as elementless Diagnosis nodes (S14); whether the `expected` property stays in the graph at all (S15); whether the causal pair takes typicality (S18, and [07 §7](./07-relationship-family.md) question 2).
- **Report-plane follow-ups** from the 2026-09-03 example: a certainty vocabulary for `confidence` (S26 carries the phrase verbatim for now); the observation-space relationship type list, including the provisional `SUPPORTS` and `ASSOCIATED_WITH` (S24, S25); how compound severity phrases such as "mild-to-moderate" map to the ordered values (S23).
- **[07 §7](./07-relationship-family.md) questions 1, 3, 4, and 5**: association strength on `OCCURS_WITH`; `typicality: excluded` on a `MAY_MANIFEST_AS` edge; the conditionality fork; whether relation types carry mappings to their prior-art counterparts.
- **The ten-exemplar-sets request** and the workflow push from the [20 August call](../../notes/working-group-call-2026-08-20-extract.md) remain outstanding.

## 4. Queue, in order

Each item says what it breaks or proves. Take them in order unless the owner reorders.

1. **Part-solid pulmonary nodule with a solid component.** The `solid component` class (`RDE2_000130`) is referenced but not defined; define it, bind its size, and write the two-Observation report end to end. It exercises `MAY_HAVE_COMPONENT`, the sub-finding report pattern of [03 §5](./03-draft-structures.md), and the subtype-versus-condition question of the [25 August exchange](../../notes/review-exchange-2026-08-25-extract.md), the most contested structural issue still open. Third mat, and the first where the report picture matters as much as the class picture.
2. **Patterns as an authoring guide and a lint rule** (10 S5 to S7). A page saying what a lesion, mass, process, and abnormality class looks like at a location, which elements it binds, and which relationship shape it carries; and a checker rule that flags a class named `<organ> lesion` departing from it. Nothing in the graph.
3. **Migrate the six interim specs into `graph/`**, make `render_neighborhood.py` read the graph, delete `spec_to_graph.py`. The dossier pictures then come from the same source as everything else.
4. **Upper abdominal abnormality**: negation propagation over `SUBTYPE_OF`; the test case for [00 Issue A](./00-current-understanding.md) and the closed-world assumption, now that grouping nodes bind presence (S29).
5. **Lung cancer staging**: the stage as an assessment with T, N, and M as component assessments, each `INTERPRETED_FROM` specific finding bindings and never restating their values. Nested assessments and reified binding targets at scale.
6. **Artery as a structure-type binding** (`artery HAS_ELEMENT diameter`). **Blocked** on the is-a relation landing in AnatomicLocations.org ([04](./04-anatomy-gaps.md)).
7. **The review form** of [03 §6.1](./03-draft-structures.md) does not exist. Kimi's annotated outline ([explorations](explorations/2026-09-02-diagram-alternatives/review.md)) is the nearest seed: an indented taxonomy with relationships as margin notes, generated from the graph, for committee redlining.
8. **Publish `site/`** through a GitHub Pages workflow once the owner wants it public; the checker does not build the site. Decide first whether `astro-docs/` is retired or becomes its home.
9. **The prose pass.** Em-dashes across the prose documents; the owner objects to them. Real rewrites, not substitutions, file by file, checker after each.
10. **Context metadata upstream.** The modality, region, and subspecialty concepts now carry RadLex ids; the DICOM and SNOMED mappings on those nodes are still to be proposed to RadLex rather than kept here, and the provisional etiology, sex, age, and time-course codes need official versions.

Sources to draft examples from: the corresponding OIFM models, treated as drafts ([00 §5.1](./00-current-understanding.md)); the verified nodule content in [`notes/source-review-2026-08-20.md`](../../notes/source-review-2026-08-20.md); the Hood taxonomies as test material ([profile](../../notes/hood-taxonomies-profile-2026-09-01.md)); and the [ontology background research note](../../notes/ontology-background-research-2026-09-04.md) of 2026-09-04, which records source facts and follow-up questions without changing the model.

## 5. Half-baked in the model

- **Identifiers are made up.** Every `RDE2_` id was invented on the spot with no registry; the validator's uniqueness check across `graph/` is the interim registry. The canonical samples in [03 §6.2](./03-draft-structures.md) still show `FC-`/`DE-` placeholders and a `required` property; regenerate them from `graph.py dump`.
- **Canonical form syntax.** JSON Lines is implemented; the choice among JSONL, Turtle, and OWL functional syntax ([00 Issue D](./00-current-understanding.md)) remains open, but there is now something to convert from.
- **The `expected` property** on causal edges is loose text keyed by element name (S15). If it stays, decide whether it becomes structured.
- **Propagation of scope and context** is a render-time rule (S13); if the owner prefers explicit assertion on every subtype, the renderer rule goes and the graph gains edges.
- **`SUBTYPE_OF` reused as the anatomy is-a edge** (S27) is a convenience that should be confirmed or replaced with the upstream relation when AnatomicLocations.org ships one.
- **Illustrative binders** on the `severity` and `size (mean diameter)` dossiers name classes that do not exist (lymph node, liver lesion, spinal canal stenosis, pulmonary edema). Replace them as real classes appear.
- **Value definitions are paraphrases** in the thyroid and pulmonary specs, not committee-grade wording.
- **Binding strength on `rdfs:range`** and whether multi-select elements bind differently: both open in [03 §2](./03-draft-structures.md).
- **RadLex gaps surfaced** and not yet proposed upstream: striated nephrogram, perinephric fat stranding, chylothorax; `pleural space` (RID1363) for AnatomicLocations.org.

## 6. Decisions that belong to others

**Committee** ([00 §8](./00-current-understanding.md) has the full issues list):
- Issue A: does `is-a` carry inference, and is the negation sweep's closed-world assumption a property of the Grouping node type (10 S8)?
- Issue B: OWL classes versus SKOS-style individuals (punning is the likely escape).
- Issue E remainder: whether the `RDE2_` space is partitioned for distributed minting, and what the URI base is (needs the RadElement operators).
- Presence as the set's own value or as its first child (IDR asks; [`notes/ihe-idr-extract.md` §8](../../notes/ihe-idr-extract.md)).
- The normal-structure proposal ([01 §3.1](./01-what-the-vocabulary-must-express.md)) is the owner's; it still needs to be worked through with others.
- Whether two node types, Finding and Diagnosis, are still warranted now that only relationship sourcing separates them ([07](./07-relationship-family.md) framing; a Claude observation).

**RadLex / AnatomicLocations.org**:
- The is-a relation and the structure-type nodes (tendon, muscle, artery) in progress upstream ([04](./04-anatomy-gaps.md)); the missing potential spaces (pleural, pericardial, subarachnoid).
- DICOM and SNOMED mappings on modality and other concept nodes (§4 item 10).
- Still unverified against the OWL: the imaging-observation branch ([00 §2.4](./00-current-understanding.md)); the relation axioms were verified 2026-09-01 ([07 §6](./07-relationship-family.md)).

**IHE** (the seven items in [`notes/ihe-idr-extract.md` §8](../../notes/ihe-idr-extract.md)), above all: our default that every report assertion, diagnoses included, is an `Observation`; causal relationships, which FHIR Core lacks; and typed observation-space relationships, now that report edges no longer cite vocabulary relationships (S22).

## 7. Repository housekeeping

- `astro-docs/` and `build_schemas.py` still use the old set/element vocabulary and have not been touched ([00 §6](./00-current-understanding.md)); two Pages workflows exist and one is dead.
- `docs/check_bundle.py` should become a pre-commit hook once the workflow settles.
- A Dependabot alert exists on the repository, almost certainly `astro-docs/` dependencies; unrelated to this work.
- The raw committee material lives in gitignored `raw_sources/`, alongside `raw_sources/denylist.txt` which the checker uses for the name sweep. Neither is in git; do not re-add them.
- The gitignored `.preview/` directory holds the agents' working copies of the diagram alternatives; the kept copies are under `explorations/`. It can be deleted.
