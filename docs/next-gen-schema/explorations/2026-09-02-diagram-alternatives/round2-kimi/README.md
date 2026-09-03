---
type: Exploration
title: Diagram alternatives, round 2 (the mat and the tree, from the decisions document): kimi
description: Verbatim README written by the agent opencode/kimi-k3 for its diagram alternatives on 2026-09-02; kept as a record of the exploration, not as a specification.
tags: [next-gen-schema, exploration, diagrams, superseded]
status: deprecated
generated: { by: "opencode/kimi-k3", at: 2026-09-02 }
sources:
  - id: brief
    resource: /docs/plans/2026-09-02-diagram-brief.md
    title: The brief this agent worked from
---

> **Exploration record.** This file is the agent's own README, unedited apart from this frontmatter block. The design it describes was reviewed on 2026-09-02 and is superseded by [09](../../../09-mat-and-tree.md); see [the review](../review.md) for what it contributed.

# The mat and the tree — kimi

Implements `docs/plans/2026-09-02-mat-and-tree-decisions.md`. One generator,
`render_mat_tree.py`, loads the canonical graph through
`docs/next-gen-schema/tools/graph.py` (`load_graph()`) and takes exactly a hub id and
a title as the view:

```
python3 render_mat_tree.py mat  RDE2_000502 "Pleural effusion"      > mat-pleural-effusion.svg
python3 render_mat_tree.py mat  RDE2_000801 "Acute pyelonephritis"  > mat-acute-pyelonephritis.svg
python3 render_mat_tree.py tree RDE2_000516 "Pleural abnormality"   > tree-pleural-abnormality.svg
python3 render_mat_tree.py tree RDE2_000814 "Renal abnormality"     > tree-renal-abnormality.svg
```

All four outputs were rasterized headlessly and inspected; the mat's hover detail was
exercised in a browser (the `.mdetail` group flips to `display:inline` on
`.mini:hover`).

## The mat — layout algorithm

The context object is the mat: a single card with the fixed zone stack from §2.3 —
title band, anatomy line, text, attribute table, containers, mappings, stat row — each
zone drawn even when empty ("no anatomic scope", "—" cells). Containers are computed in
the fixed §2.5 order and empty ones vanish. Inside a container, rows are one mini-card
plus its edge properties (typicality, specificity, `expected`, note) set beside the
card; edge ids are never shown. A container whose edges carry no properties at all
(currently only "kinds of" / "a kind of") switches to a three-across grid to save
height. Mini-card faces are exactly name + kind + own id; the hover detail is a CSS
rule inside the SVG (`<style>.mdetail{display:none} .mini:hover
.mdetail{display:inline}</style>`), and mini-card groups are painted bottom-up in
document order so a revealed detail always overlays the rows below it. The hover detail
carries the definition (truncated to four lines), the mappings, the stat row, and the
node's own one-hop connection lines, excluding the hub. On GitHub the minimal faces are
what render, per §2.4.

The `required` property is ignored everywhere; presence is an ordinary row in the
attribute table, values elliptical after three entries (§2.7). The attribute table
shows each element's id, kind (with `multi-select` / `ordered` folded into the kind
column), and values or quantity (range, UCUM units, truncated method). Mappings always
carry their preferred term, close matches are prefixed `close: `, and the stat row
shows concept names verbatim (see deviation 1).

## The tree — layout algorithm

A tidy top-down tree: DFS over `SUBTYPE_OF` (children in canonical id order), leaves
assigned sequential slots, parents centered over their children; boxes distinguish
kind by shape *and* color (rounded = finding, chamfered = diagnosis, dashed =
grouping). Is-a connectors are orthogonal elbows: parent bottom-center, down to a bus
near the child row, across, down into child top-center.

Relationship edges are routed through **gap channels**: the horizontal band between
two adjacent box rows is divided into a stack of 9px channels above the tree's elbow
bus, and each edge gets exactly one horizontal run in its own channel. Up-tree edges
exit the source's side edge (per-gutter risers shared across rows so no two verticals
share an x) and enter the target's bottom edge; down-tree and same-row edges exit the
source's bottom edge and enter the target's top or bottom edge; `OCCURS_WITH` is
dashed, headless, and enters the target's top edge from the gap above it. Every label
sits on its own edge's channel run at the **target end** of the run — the one place
where runs in the same gap are guaranteed to be spread apart — with the edge-type word
omitted when every edge in the gap is the same type (color carries it, per the
legend). Arrowheads use `markerUnits="userSpaceOnUse"` with `orient="auto"` on final
segments that are always axis-aligned, so every head points exactly along its line —
the failure the owner called out in the old renderer cannot recur.

## Deviations from the decisions document

1. **§2.9 (stat-row codes):** the document asks for RadLex RIDs on modality/region
   concepts and provisional owned codes for the others, but the graph still holds
   `Scheme-slug` placeholder concept nodes and the lookup table does not exist yet. Per
   the task instruction, stat cells show the concept **names** (`CT US XR`, `chest`,
   `idiopathic`); no codes are invented for them.
2. **§2.8 (element-level codes):** the graph carries no mappings on DataElement nodes
   (only per-value codes, which the decision excludes). The attribute table therefore
   shows element ids but no external codes; the wiring (`mappings()`) renders them the
   moment they exist.
3. **§2.3 zone 5 wording:** "connections" on a mini-card face appear only inside the
   hover detail (the face stays minimal per §2.4); the zone is otherwise the container
   stack on the context object, as specified.
4. **Ghost boxes (§3):** implemented intent is documented but not exercised — neither
   family has a second parent, so the code paths for it (side slots on all four edges)
   exist but produce no ghost box in these two pictures.
5. **Tree width:** the renal tree is ~1580px wide, past the 1000–1300 comfort range of
   the superseded brief; the decisions document sets no width constraint for trees and
   the tidy layout prefers breadth over re-flowing the hierarchy. If width matters, the
   honest fix is smaller boxes, not wrapping the tree.
6. **`expected` rendering on the mat:** shown as `expect: <element>: <value>` pairs
   verbatim from the graph rather than the mockup's compressed phrasing, because the
   keys are element names and dropping them would misattribute the hint.
