---
type: Exploration
title: Diagram alternatives, round 2 (the mat and the tree, from the decisions document): codex
description: Verbatim README written by the agent codex/gpt-5.6-sol for its diagram alternatives on 2026-09-02; kept as a record of the exploration, not as a specification.
tags: [next-gen-schema, exploration, diagrams, superseded]
status: deprecated
generated: { by: "codex/gpt-5.6-sol", at: 2026-09-02 }
sources:
  - id: brief
    resource: /docs/plans/2026-09-02-diagram-brief.md
    title: The brief this agent worked from
---

> **Exploration record.** This file is the agent's own README, unedited apart from this frontmatter block. The design it describes was reviewed on 2026-09-02 and is superseded by [09](../../../09-mat-and-tree.md); see [the review](../review.md) for what it contributed.

# Codex MAT and TREE generator

`render_mat_tree.py` generates the two decided diagram forms directly from the merged canonical graph returned by `docs/next-gen-schema/tools/graph.py:load_graph`. The only semantic view inputs are a hub/root node id and an optional title; output path and renderer mode are CLI mechanics, not view data. No graph file, supplemental view file, or hand-authored node list is used.

## Usage

Generate the four requested pictures beside the script:

```sh
python render_mat_tree.py all
```

Generate one picture:

```sh
python render_mat_tree.py mat RDE2_000502 --title "Pleural effusion" -o mat.svg
python render_mat_tree.py tree RDE2_000516 --title "Pleural abnormality" -o tree.svg
```

## MAT layout algorithm

The MAT uses a fixed 1280 × 1820 context-card frame for every hub. Its seven zones always occupy the same coordinates and retain their borders even when empty: title, anatomy, text, attributes, connections, mappings, and the six-cell stat row at the bottom.

1. Read the hub node and only its direct edges. Nothing is inherited from a parent class.
2. Render the title line as preferred name at left and node kind plus base id at right.
3. Render each direct `SCOPED_TO` edge on the anatomy line as `RID “preferred term” · kind · strength`. The strength belongs to the scope edge; it is unrelated to element requirement.
4. Render definition and synonyms in the text zone.
5. Sort direct `HAS_ELEMENT` edges by element id and place them into five fixed attribute rows. The generator never reads or renders `HAS_ELEMENT.props.required`; presence is formatted identically to every other element. Categorical values are abbreviated where obvious, while quantitative rows include units/range and a bounded method summary.
6. Gather one-hop neighbors in the decided container order: A KIND OF, KINDS OF, MANIFESTS AS, MAY BE CAUSED BY, MAY CAUSE, PROGRESSES TO, PROGRESSES FROM, OCCURS WITH, ASSESSED BY. Empty containers vanish; populated containers are stably sorted by preferred source/target name and id. Large/property-heavy containers span both columns, while small containers are packed into the shorter of two columns. Every row contains a minimal fixed-frame mini-card and its edge properties beside—not on—the face. The MAT contains no relationship wires or arrowheads and never displays relationship ids.
7. Render only mappings that have both a code and the graph’s preferred display term; close matches are marked `close`. Codes are never emitted bare.
8. Populate the fixed stat cells from direct `SEEN_ON`, `IN_REGION`, `SEX`, `AGE_APPLICABILITY`, `TIME_COURSE`, and `HAS_ETIOLOGY` edges. Concept placeholders contribute their names exactly as requested; unset cells show `—`.
9. Add transparent hover targets after all visible content so they paint above the MAT when active. Inline SVG CSS reveals a bounded detail card containing the mini-card’s definition, mappings, six-cell stat row, and up to three of its own one-hop relationship lines. With no hover support, including GitHub image rendering, only the minimal face remains visible.

The identical frame intentionally leaves more white space in the acute-pyelonephritis MAT: empty fixed zones are part of the agreed card grammar rather than an opportunity to collapse the layout.

## TREE layout algorithm

The TREE is data-height and fixed-width at 1280 px.

1. Starting at the root, repeatedly follow incoming `SUBTYPE_OF` edges to collect every descendant.
2. Choose a deterministic primary parent by shortest root depth and then id. Additional parents are supported as repeated dashed ghost boxes beside the affected child.
3. Sort primary children by id. Compute leaf slots across the available width, place leaves at slot centers, and center each parent over the span of its first and last child.
4. Place depth layers at fixed vertical intervals. Draw hierarchy connectors behind the boxes as parent stems, horizontal sibling buses, and child stems; all taxonomy segments are orthogonal and unarrowed.
5. Distinguish Grouping, FindingClass, and Diagnosis boxes by redundant fill, border, corner shape, kind label, and base id. Long names wrap while kind and id use separate fixed metadata lines.
6. Select non-taxonomic relationships whose source and target are both descendants. Sort them by relationship family, preferred endpoint names, and edge id.
7. Draw each relationship on its own horizontal track below the hierarchy, with repeated typed endpoint references and one centered label box containing the relationship name and properties. This is still an edge view, but the dedicated track means fan-in can never separate a label from its edge. Directed edges use `markerUnits="userSpaceOnUse"` and terminate on a horizontal segment, so arrowheads align exactly; symmetric `OCCURS_WITH` uses endpoint circles and a dashed line instead of implying direction.

Canonical relationship ids are retained only as hidden `data-edge` attributes in the TREE for auditability; visible TREE labels contain semantics and properties, not implementation identifiers.

## Decisions and deviations

There are no intentional semantic deviations from `2026-09-02-mat-and-tree-decisions.md` or the task instructions.

Two layout choices resolve details that document left open:

- TREE relationship edges use dedicated tracks beneath the taxonomy and repeat minimal endpoint references. Drawing them directly across hierarchy boxes recreated the rejected label/route ambiguity; the track is the smallest deterministic form that keeps an edge visually drawn, labelled, and unambiguous under fan-in.
- TREE relationships are limited to edges whose endpoints both belong to the rooted descendant family. External one-hop neighbors remain the MAT’s responsibility; otherwise the TREE would cease to be the decided zoomed-out is-a family view.

The graph currently contains placeholder Concept nodes rather than the future RadLex/provisional lookup codes discussed in the decisions. Per the task instruction, the generator shows their preferred names in the stat row and does not invent codes absent from the canonical graph.

## Outputs

- `mat-pleural-effusion.svg` — hub `RDE2_000502`
- `mat-acute-pyelonephritis.svg` — hub `RDE2_000801`
- `tree-pleural-abnormality.svg` — root `RDE2_000516`
- `tree-renal-abnormality.svg` — root `RDE2_000814`

## Verification record

- Python compilation and XML parsing pass.
- Both MATs pass source audits for one-hop container membership, minimal mini-card faces, preferred-term mappings, fixed stat cells, absence of visible edge ids, and complete disregard of element `required` properties.
- The pleural TREE contains all 10 rooted nodes and four internal relationship edges; the renal TREE contains all 14 rooted nodes and eight internal relationship edges. Their canonical relationship-id sets match the generated hidden `data-edge` sets exactly.
- Every arrow marker uses user-space units and every directed relationship track ends horizontally.
- Regenerating all four files produces byte-identical SHA-256 hashes.
- All four final SVGs were rasterized after generation and inspected at 80% scale. No text clips its container, no boxes overlap, hierarchy elbows meet their boxes, every relationship label is isolated on its own track, and arrowheads align with their terminal lines.
- A separate image-review process was attempted in the foreground but produced no output and was terminated after a bounded wait; it made no edits. Direct raster inspection and the automated audits above are the completion gate.

Status: complete. No files under `docs/`, no graph files, and no repository history were modified.
