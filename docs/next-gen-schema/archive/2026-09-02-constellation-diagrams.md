---
type: Archived Design
title: The Constellation Diagrams (retired)
description: The column-and-curve constellation renderer of 1 to 2 September 2026, what it drew, why it was retired the same day, and where its ideas went.
tags: [next-gen-schema, archive, diagrams, superseded]
status: deprecated
generated: { by: "claude-code/claude-fable-5.1", at: 2026-09-03 }
sources:
  - id: record
    resource: /docs/next-gen-schema/10-decision-record-2026-09-02.md
    title: The decisions that retired it
  - id: spec
    resource: /docs/next-gen-schema/09-mat-and-tree.md
    title: What replaced it
---

# The Constellation Diagrams (retired)

**Status:** Deprecated. Nothing here is current. The renderer was never committed; this page is the record.

## What it was

A "constellation" was a hand-listed set of nodes laid out in columns by role (diagnoses, findings, anatomy; or causes, the family, companions), with every typed relationship drawn as a labelled cubic curve between chips. Same-column subtypes were drawn as indented trees with elbow connectors; same-column non-subtype edges looped out the free side of the column. Edge labels carried the edge type, typicality, and specificity, placed at the curve midpoint with a slot mechanism to stagger collisions. The renderer, `render_constellation.py`, also produced an automatic three-column neighborhood (points here, the node, points to) for every node page on the site. View files listed node ids per column.

Two constellations were drawn: acute pyelonephritis (diagnosis tree and the findings it manifests as) and pleural effusion (causes, the finding with its subtypes, companions).

## Why it was retired

Judged against what the pictures were for, they failed in five places, which the owner's review then confirmed (D1 to D3 in the record):

- Labels stacked at curve midpoints, so under fan-in a reader could not tell which typicality belonged to which cause.
- The `expected` hints were omitted for space.
- The anatomy and the kidney length binding, the very thing the pyelonephritis example was built to show, were dropped when the anatomy column was removed to reduce clutter.
- Elements were invisible, and on node pages they shared a column with relationship targets.
- The arrowheads, drawn as markers oriented to the path's end tangent, sat at an angle to their curves.

## Where the ideas went

The role columns became the containers of the mat; the indented subtype tree became the tree; the edge label became the edge box; and the automatic neighborhood became the mat rendered for every node. The idea of a labelled curve went nowhere and should not come back (D8).
