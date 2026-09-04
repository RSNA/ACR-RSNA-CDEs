---
type: Exploration Record
title: Diagram Alternatives, 2 September 2026: Review
description: What the eight round-one alternatives and the two round-two attempts showed, how each measured against the brief and then against the decisions, and which ideas survived into the mat and the tree.
tags: [next-gen-schema, exploration, diagrams, review, superseded]
status: deprecated
generated: { by: "claude-code/claude-fable-5.1", at: 2026-09-03 }
sources:
  - id: brief
    resource: /docs/plans/2026-09-02-diagram-brief.md
    title: The round-one brief (superseded)
  - id: decisions-plan
    resource: /docs/plans/2026-09-02-mat-and-tree-decisions.md
    title: The round-two brief, the decisions document as first written (superseded by 10)
  - id: record
    resource: /docs/next-gen-schema/10-decision-record-2026-09-02.md
    title: The decision record that supersedes both briefs
---

# Diagram Alternatives, 2 September 2026: Review

**Status:** Deprecated. Kept as a record of the exploration. The design that came out of it is [09](../../09-mat-and-tree.md). Each agent's own README and SVGs are in the sibling directories, unedited apart from a frontmatter block.

## Round one: eight alternatives to an open brief

Four agents were given the same brief[^brief] and asked for two genuinely different designs each, seeded with different starting directions so the eight would not converge. All eight are kept.

| Directory | Design | What it showed |
|---|---|---|
| `round1-claude-a` | Nested containment | Subsumption as a box inside a box, so empyema sits purple inside the blue pleural effusion box and the grouping node is the largest thing on the page. Edge properties written inside the card at the edge's quieter end. Ranked first against the brief; the direct ancestor of the mat. |
| `round1-claude-a` | Relationship matrix | Rows as the indented taxonomy, columns as targets, Harvey balls for typicality and diamonds for specificity. Unambiguous and trivially deterministic; no picture of the graph. |
| `round1-claude-b` | Radial sunburst | Hub as a disc, subtypes as sectors, port-anchored cards around. Striking; the ring labels were already cramped at six subtypes. |
| `round1-claude-b` | Swimlanes with per-wire ports | Every wire with its own port and its own label at the source, so fan-in never stacked labels; an anatomy lane with the kidney binding and the interpreted-from wire. Ranked second; contributed the anatomy-on-the-face idea by contrast. |
| `round1-codex` | Taxonomy spine and ledger | A clean top-down tree, then one row per relationship. A document more than a diagram; the most legible taxonomy of the eight. |
| `round1-codex` | Containment and source cards | Containment for the taxonomy, then one card per source. Clear cards with no path between them. |
| `round1-kimi` | Flow with band width | Band thickness as typicality and an arrowhead glyph as specificity; the one new visual encoding in the set, hard to read as an ordinal scale. |
| `round1-kimi` | Annotated outline | The taxonomy as an indented document with relationships as numbered margin notes. Not a diagram; the closest thing to the review form of 03 §6.1, and the seed of the tree-as-outline. |

Four things all eight converged on independently, which were then taken as settled: subsumption drawn as containment or indentation rather than as arrows; no property ever placed on a curve; presence suppressed with a legend note (later made moot by S9, no required elements); scope stated once and badged only where it deviates (later dropped, D23).

The owner's review: nested containment was definitely the direction; anatomy had to be shown; the arrows and arrowheads were unacceptable because the heads were not aligned with the lines; the annotated outline was powerful; and the whole thing should feel like a deck of finding, anatomy, and attribute cards being assembled on a table.

## Round two: the mat and the tree, from a decisions document

The conversation that followed produced a decisions document[^decisions-plan]; Codex and Kimi were each asked to build both pictures from it, with density unspecified.

| Directory | Result | What it showed |
|---|---|---|
| `round2-codex` | Mat and tree | Followed the frame faithfully; padded everything, with fixed-height empty attribute rows and a dead band before the mappings. Its tree declined the labelled-edge requirement and produced a ledger instead. Its hover detail was the richer of the two. |
| `round2-kimi` | Mat and tree | Tighter, with elliptical attributes and dashed containers; the guide for the final renderer. Its tree drew labelled orthogonal relationship wires on a box-and-connector hierarchy, which was what had been asked for and which the owner then rejected in favour of an outline of mini-cards. |

Both exposed the same two graph gaps rather than rendering faults: acute pyelonephritis had no anatomy and an empty stat row because those edges sat on its parent (which led to the propagation rule, S13), and no element-level codes existed yet (C8).

The owner's review of round two: the mats were the right direction but the layout had to be drastically tightened and the type was too small; edge properties should be a dotted box under the linked card carrying only typicality and specificity; subspecialty was missing; and neither tree worked, the tree should be an expanding outline of the mini-cards with relationships appearing on hover or click. Those became D9, D19, D20, D21, and D22.

## What the exploration taught about briefing agents

Process knowledge, kept here because this is the record of the process; the reusable form is in [`tools/README.md`](../../tools/README.md).

- A prose brief with a ranked list produced eight designs that were easy to compare but hard to steer; a decision record with numbered, owner-marked rules produced two mats that were structurally right on the first try. Brief with the record.
- "No overlaps" as the success criterion was met by both round-two agents in the same way: inflate every frame and shrink the type. Density has to be stated in numbers (type sizes, card heights, cards per row), or it will be traded away.
- Both round-two attempts exposed gaps in the graph rather than faults in rendering (missing scope and context on subtypes, no element-level codes). Expect a rendering round to be partly a data round.
- Codex declined the one requirement it judged unsolvable (labelled edges on the tree) and documented why; Kimi attempted it and the owner rejected the result. Both outcomes were useful, and the requirement was withdrawn. Ask for the attempt anyway.
- Agents that rasterized and looked at their own output fixed real defects before delivery; the one that did not needed a review round for the same defects.
- Keep each agent in its own gitignored directory and forbid edits under `docs/`; merging is the reviewer's job.

## What survived

From claude-a: containment, the edge's facts written at one end. From claude-b: nothing drawn, but its anatomy lane made the case that anatomy belongs on the face instead. From Kimi's annotated outline and Kimi's round-two mat: the shape of the tree and the density of the final mat. From Codex round two: the hover detail's contents. From the owner: everything in the D section of the decision record.

[^brief]: The round-one brief, now superseded, is kept under `docs/plans/`.
[^decisions-plan]: The round-two decisions document, now superseded by [10](../../10-decision-record-2026-09-02.md), is kept under `docs/plans/` as a working artifact.
