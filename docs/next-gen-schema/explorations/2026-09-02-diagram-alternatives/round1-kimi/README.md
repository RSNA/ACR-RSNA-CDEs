---
type: Exploration
title: Diagram alternatives, round 1 (open brief, two alternatives): kimi
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

# Constellation diagram alternatives — kimi

Two designs, both produced by working generators from the canonical graph files
(`docs/next-gen-schema/graph/*.jsonl` via `tools/graph.py load_graph()`), so the
"generated, not drawn" constraint is demonstrated rather than asserted:

```
python3 gen_alt1.py pleural-effusion > alt1-pleural-effusion.svg
python3 gen_alt1.py pyelonephritis  > alt1-pyelonephritis.svg
python3 gen_alt2.py pleural-effusion > alt2-pleural-effusion.svg
python3 gen_alt2.py pyelonephritis  > alt2-pyelonephritis.svg
```

The view (which nodes, in what order) is a small explicit block at the top of each
render function; everything else — rows, slots, band widths, note placement — is
computed from the graph. Both were rasterized and visually inspected headlessly before
delivery.

---

## Alt 1 — "Flow": band width = typicality, specificity glyph at the arrowhead

`alt1-pleural-effusion.svg`, `alt1-pyelonephritis.svg`

**Idea.** The diagram is a Sankey-flavored flow. Causal and manifestation relationships
are *bands*, not lines: width encodes typicality on a fixed scale (obligate 13 px →
occasional 4.5 px), and specificity is a shape sitting just behind the arrowhead
(◆ pathognomonic, ▲ highly suggestive, ● suggestive, ○ none asserted). Every band label
is a single word (the typicality) placed at the **source end** of its band, which kills
the current renderer's worst failure — labels stacking at curve midpoints under fan-in.
The `expected` hints are not on the band at all; they ride inside the cause chip as an
italic `expect:` line, where attachment is unambiguous by construction. Subsumption is
never a band: the taxonomy descends from the grouping node (a loud dashed
"negative-only" band, fixing the "grouping nodes too quiet" failure) through the anchor
to its subtypes as trunk-and-branch connectors. Co-occurrence is a thin dashed gray line
with no arrowhead and no width — visibly not causation. Progression is a teal chevron
arrow routed in the tree's own gutter.

**Against the ranked list:**

1. *Taxonomy.* Trunk-and-branch descent from the grouping band; renal abscess sits
   indented under renal lesion (finding) as a diagnosis chip, making the
   label-crossing explicit. Subsumption shares no visual channel with any other edge
   type.
2. *Typed relationships.* Width + arrowhead glyph + source-end label means five
   converging causes still read unambiguously: each band's word label sits next to its
   own cause chip, and the expected hint is inside that chip. Manifestation,
   causation, progression, co-occurrence are color- *and* shape-distinct (band vs
   chevron vs dashed hairline).
3. *Direction and kind.* Direction is the arrowhead; node kinds keep the existing
   palette plus a kind word on every chip; the grouping node is a dashed banner.
4. *Bindings.* Anchor card lists elements in green; finding chips carry green element
   pills; renal enlargement carries its `INTERPRETED_FROM` binding citation as a green
   pill (`RDE2_000830 · kidney HAS_ELEMENT length`).
5. *Anatomic scope.* Amber scope line under each finding; perinephric fat stranding's
   `perirenal space` is bolded and flagged `← differs from the family`.

**Layout algorithm.** Fixed columns (causes | anchor + subtype tree | related findings;
resp. diagnosis tree | findings). Causes are stacked by (typicality rank desc, name);
band slots on the anchor's edge are assigned in source order so the fan-in is planar.
Subtypes follow view order with a tree guide. Any relation that cannot route through
the gutter without crossing chips (acute → renal abscess) detours through the free
channel at the diagram's edge, with a full `source → target` label on the straight run.
Arrowheads use `markerUnits="userSpaceOnUse"` so marker size never scales with band
width. All geometry derives from node counts and the view spec; no solver, no
randomness.

**Gives up.** The bands are decorative weight, not quantitative flow — width steps are
ordinal, not proportional to anything clinical. Long-range detours (the abscess cause
band) travel far from the conversation. And the label vocabulary is minimal by design:
a reader must learn the width scale and four glyphs from the legend once.

---

## Alt 2 — "Annotated outline": the taxonomy as a document, relationships as margin notes

`alt2-pleural-effusion.svg`, `alt2-pyelonephritis.svg`

**Idea.** The diagram reads like a page from a structured textbook, which is the genre
the committee already knows how to argue with. The left two-thirds are a numbered,
indented outline of the subtype tree — one row per class, hairline separators, kind
pills (FINDING / DIAGNOSIS / GROUPING), green `binds:` element tags, amber `scope:`
tags. Indentation *is* subsumption; `SUBTYPE_OF` never produces anything else. The
right margin holds one numbered note per typed relationship, vertically aligned with
its source row and tied to it by a short leader: a colored verb chip (CAUSES /
MANIFESTS AS / PROGRESSES TO / OCCURS WITH), the target name, a five-bar meter for
typicality, a shape glyph for specificity, and the `expected`/`note` properties as
italic lines. Target rows carry back-reference pills (`◂ n9 n11–n14`), so a
relationship is traceable in both directions and **no line ever crosses the outline** —
fan-in is a stack of notes, each anchored to its own row, each carrying its own meter.

**Against the ranked list:**

1. *Taxonomy.* The strongest possible reading of "containment or descent": an actual
   indented document tree with guides, from the grouping node down. Empyema under
   pleural effusion and renal abscess under renal lesion are just indentation — the
   finding/diagnosis label crossing is visible as a pill-color change, not a different
   structure.
2. *Typed relationships.* Each note is unambiguously attached: numbered disc at the
   source row, target named in the note, back-reference at the target row. Typicality
   is a bar meter (legible in grayscale); specificity is a glyph plus words. The four
   edge kinds have distinct colors, chip words, and arrow symbols (→ vs ↔).
3. *Direction and kind.* Kind is a labeled pill on every row; direction is the note's
   verb and arrow, with source/target fixed by position.
4. *Bindings.* Inline `binds:` tags on every row; the anchor's full element set and
   value list get sub-rows; `INTERPRETED_FROM` is a green sub-line under renal
   enlargement.
5. *Anatomic scope.* Amber scope pill per row; scope that differs from the family's
   grouping-node scope is bolded (`scope: perirenal space`).

**Layout algorithm.** DFS preorder over the subtype forest (children in canonical id
order) assigns rows and depths; nodes reachable only by non-subsumption edges fall into
a second section, non-tree cause sources into a third — all three partitions computed
from the graph, not the view. Notes are numbered in (source-row, edge type,
target-row) order, placed at their source row, and pushed down on collision; leaders
elbow only when pushed. Elements inline when they fit the row measure, sub-row
otherwise. Everything is deterministic text measurement.

**Gives up.** It is tall (the taxonomy is one row per node by design, so 30 nodes means
30+ rows) and the spatial argument is weaker: you cannot see the constellation's shape
at a glance the way Alt 1's bands show it. Relationships to nodes outside the outline
(none in these two families, but possible in general) would need a convention not yet
invented. And the two-way referencing asks the reader to learn the `n#` / `◂ n#`
idiom once.
