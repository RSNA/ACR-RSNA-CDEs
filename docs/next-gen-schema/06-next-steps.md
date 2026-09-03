---
type: Playbook
title: Next Steps and Open Threads
description: Handoff for whoever picks this up with a clean context - what is queued, what is half-baked, what placeholders are lying around, and which decisions belong to the committee, RadLex, or IHE.
tags: [next-gen-schema, handoff, next-steps]
status: draft
generated: { by: ["human:talkasab", "claude-code/claude-fable-5"], at: 2026-08-21 }
sources:
  - id: baseline
    resource: /docs/next-gen-schema/00-current-understanding.md
    title: Current understanding
    author: "human:talkasab"
  - id: structures
    resource: /docs/next-gen-schema/03-draft-structures.md
    title: Draft structures
    author: "human:talkasab"
---

# Next Steps and Open Threads

## 0. Update, 2026-09-02

The canonical graph now exists ([`graph/`](graph/README.md)), with two constellation examples ([08](./08-worked-examples.md)), a validator (`tools/graph.py check`, run by the bundle checker), a mat and tree renderer (`tools/render_cards.py`, which replaced the constellation renderer the same day after review), and a site builder (`uv run docs/next-gen-schema/tools/build_site.py`, output in gitignored `site/`). Plan and status: [`docs/plans/2026-09-02-graph-and-site.md`](../plans/2026-09-02-graph-and-site.md). Decisions taken that day are in [10](./10-decision-record-2026-09-02.md), marked by provenance; the display grammar is [09](./09-mat-and-tree.md). New open items from it:

- **Authoring-guide page for patterns** (lesion, mass, process, abnormality, variant, postsurgical change, applied at a location) and a checker rule that flags a class named `<organ> lesion` departing from the pattern. Nothing in the graph ([10 S6](./10-decision-record-2026-09-02.md)).
- **Non-imaging causes as elementless Diagnosis nodes** was taken as a working default so the effusion example could be written; reversible.
- **The `expected` property on causal edges** is a proposal; decide whether it stays loose text keyed by element name or becomes structured.
- **Migrate the six interim specs** into `graph/` and make `render_neighborhood.py` read the graph, then delete `spec_to_graph.py`.
- **Publish `site/`** (GitHub Pages workflow) once the owner wants it public; the bundle checker does not build the site.
- **RadLex proposals surfaced**: striated nephrogram, perinephric fat stranding, chylothorax; and `pleural space` (RID1363) for AnatomicLocations.org.

Written 2026-08-21, right after the first commit (`a53aa62`). Read [00](./00-current-understanding.md) first for what is settled; this document is only what is *not* finished. Run `python3 docs/check_bundle.py` from the repo root before every commit; the owner approves each commit.

## 1. Immediate: context metadata as real edges to RadLex nodes

The example specs carry modality, subspecialty, body region, etiology, sex, age, and time course as free-text `name`/`type`/`note` strings ([03 §10](./03-draft-structures.md)). They must become edges to real nodes, **RadLex's node wherever RadLex has one** (modality, subspecialty, body region), with the DICOM and SNOMED mappings proposed upstream to RadLex rather than kept here, and `RDE2_` nodes only where RadLex has nothing (probably etiology, age stage, sex specificity, time course), seeded from OIFM's lists in [`notes/oifm-metadata-fields.md`](../../notes/oifm-metadata-fields.md). The owner said he would provide a resource ("a present") before this starts; wait for it.

To check first, against the 4.3 OWL ([`05`](./05-radlex-baseline.md) describes how): whether RadLex's modality and subspecialty branches cover OIFM's lists, and whether RadLex carries any DICOM mappings at all (the `ExternalRefID` census saw none). Then: spec format, renderer, canonical-form sample, and the [03 §2](./03-draft-structures.md) edge table all change; the `(?) missing Etiology value` chip on the thyroid example becomes a proposed node.

## 2. Prose pass

The documents are full of em-dashes (about 338 across the eight prose files; `00` has 102, `03` has 90), which the owner objects to. Each needs a real rewrite (comma, colon, period, or restructure), not a substitution. The `humanizer` skill targets this and the related tells. Do it file by file and re-run the checker after each.

## 3. Examples queue, in order

Each case was chosen to break something specific ([03 §10](./03-draft-structures.md) has the one-line versions):

1. **Kidney** as a location dossier: bindings on unsided `RID205` inherited by `RID29663`/`RID29662` across the laterality triad. Proves inheritance works before relying on it.
2. **Artery** as a structure-type binding (`artery HAS_ELEMENT diameter`). **Blocked** on the is-a relation landing in AnatomicLocations.org ([04](./04-anatomy-gaps.md)).
3. **Part-solid nodule with a solid component**: the `solid component` FindingClass (`RDE2_000130`) is referenced but not defined; define it, bind its size, and write the two-Observation report sample end to end.
4. ~~**Acute pyelonephritis**~~ Done 2026-09-02 as a graph file ([08 §2](./08-worked-examples.md)); pleural effusion done alongside it ([08 §3](./08-worked-examples.md)).
5. **Lung cancer staging**: the stage as an assessment with T, N, M as component assessments, each `INTERPRETED_FROM` specific finding bindings and never restating their values.
6. **Upper abdominal abnormality**: negation propagation over `SUBTYPE_OF`; the test case for [00 Issue A](./00-current-understanding.md) and the closed-world assumption.

Sources to draft from: the corresponding OIFM models (treated as drafts, [00 §5.1](./00-current-understanding.md)), and the verified findings in [`notes/source-review-2026-08-20.md`](../../notes/source-review-2026-08-20.md).

## 4. Half-baked in the model

- **Binding identity.** Resolved 2026-09-02: bindings that must be cited carry `RDE2_` ids (`RDE2_000830` kidney length, `RDE2_000831` bile duct caliber) and `INTERPRETED_FROM` targets the id ([08 §2](./08-worked-examples.md)). The `RID199/HAS_ELEMENT/RDE2_000090` path form in [03 §9](./03-draft-structures.md) is superseded.
- **Canonical form syntax.** JSON Lines is now implemented in [`graph/`](graph/README.md) with the sorting rules enforced by `tools/graph.py`; the choice among JSONL, Turtle, and OWL functional syntax ([00 Issue D](./00-current-understanding.md)) remains open but there is now something to convert from. The review-form generator does not exist; the site's node pages are the nearest thing.
- **Spec format is interim.** The renderer reads bespoke `*.neighborhood.json` / `*.element.json` / `*.location.json` files. Once the canonical form exists the renderer should read that and the specs disappear.
- **Identifiers are made up.** Every `RDE2_` id in the examples was invented on the spot (`RDE2_000123`, `RDE2_000130`, `RDE2_000502`, `RDE2_000900`, and so on) with no registry; collisions are likely as examples grow. Even a checked-in `ids.tsv` would do until real minting exists. The canonical samples in `03` §6 still use the older `FC-`/`DE-` placeholders (14 occurrences) and should move to `RDE2_`.
- **Illustrative binders.** The `severity` and `size (mean diameter)` element dossiers list binders (lymph node, liver lesion, spinal canal stenosis, pulmonary edema, hydronephrosis) that are not defined classes. Replace them as real classes appear.
- **Value definitions are paraphrases.** The TI-RADS descriptor definitions and the pulmonary attenuation/margin definitions in the thyroid and pulmonary specs are summaries of the sources, not committee-grade wording.
- **Dossier header** does not yet show `version`/`current_status` for DataElements and locations consistently, and element dossiers are not generated for elements defined inline in a class.
- **Binding strength on `rdfs:range`** (FHIR's required/extensible/preferred) and whether multi-select elements bind differently: both marked open in [03 §2](./03-draft-structures.md).

## 5. Decisions that belong to others

**Committee** ([00 §8](./00-current-understanding.md) has the full issues list):
- Issue A: does `is-a` carry inference, and is the negation sweep's closed-world assumption a declared property of a class?
- Issue B: OWL classes versus SKOS-style individuals (punning is the likely escape).
- Issue E remainder: whether the `RDE2_` space is partitioned for distributed minting, and what the URI base is (needs the RadElement operators).
- Presence as the set's own value or as its first child (IDR asks; [`notes/ihe-idr-extract.md` §8](../../notes/ihe-idr-extract.md)).
- The normal-structure proposal ([01 §3.1](./01-what-the-vocabulary-must-express.md)) is the owner's; it still needs to be worked through with others.

**RadLex / AnatomicLocations.org**:
- The is-a relation and the structure-type nodes (tendon, muscle, artery) in progress upstream ([04](./04-anatomy-gaps.md)); the missing potential spaces (pleural, pericardial, subarachnoid).
- DICOM and SNOMED mappings on modality and other concept nodes (§1 above).
- Still unverified against the OWL: the relation axioms and the imaging-observation branch ([00 §2.4](./00-current-understanding.md)).

**IHE** (the seven items in [`notes/ihe-idr-extract.md` §8](../../notes/ihe-idr-extract.md)), above all: our default that every report assertion, diagnoses included, is an `Observation`; causal relationships, which FHIR Core lacks; and typed, citable relationships for `expresses`.

## 6. Repository housekeeping

- `astro-docs/src/content/docs/reference/{set,element,valueset}.md`, `build_schemas.py`, and the generated schema filenames still use the old set/element vocabulary and have not been touched ([00 §6](./00-current-understanding.md)).
- `docs/check_bundle.py` should become a pre-commit hook once the workflow settles.
- A Dependabot alert exists on the repository (almost certainly `astro-docs/` dependencies); unrelated to this work.
- The raw committee material lives in gitignored `raw_sources/`, alongside `raw_sources/denylist.txt` which the checker uses for the name sweep. Neither is in git; do not re-add them.
