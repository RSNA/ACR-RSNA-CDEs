---
type: Exploration
title: Diagram alternatives, round 1 (open brief, two alternatives): codex
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

# Codex constellation alternatives

These mockups use the real pleural-effusion nodes and edges from `graph/core.jsonl` and `graph/pleural-effusion.jsonl`, with shared presence and severity details resolved from their canonical example specifications. Both views deliberately omit mappings and broad context edges (`exactMatch`, `closeMatch`, `HAS_ETIOLOGY`, `IN_REGION`, and `SEEN_ON`) so the committee’s attention stays on the brief’s ranked questions. Colors retain the existing vocabulary’s broad node-family language, but shape, border, label, and line pattern also carry meaning so color is not the only cue.

## Alternative 1 — taxonomy spine + relationship ledger

`alt1-pleural-effusion.svg` follows a radiologist’s reading order: establish what the class is, inspect what it binds and where it applies, then read causes and other clinical relationships. Taxonomy is a thick, unarrowed descent tree in its own dominant panel; every other relationship occupies a dedicated horizontal row with source, direction, type, properties, and target, eliminating shared routes and midpoint labels. The design treats edge labels as a ledger rather than annotations floating over a conventional node-link graph.

### Ranked criteria

1. **Taxonomy:** `pleural abnormality` is visually forceful and explicitly negative-only. Pleural effusion and pleural thickening descend from it, six diagnosis capsules descend from the finding box, and nodular pleural thickening descends from pleural thickening; the shape transition makes the finding/diagnosis crossing unmistakable.
2. **Typed relationships:** all seven incoming clinical cause edges, the two outgoing causal edges, three manifestation edges, progression, and co-occurrence have separate rows. Typicality, specificity, `expected`, and the large-effusion note are contained inside the row they qualify; color plus solid/dashed line grammar separates causal, evidential, temporal, and associative relationships.
3. **Direction and node kind:** arrows are used only for non-taxonomic relationships. Rectangles, capsules, dashed grouping boxes, green anatomy pills, amber element tabs, inline type labels, and the compact key distinguish kinds after one glance.
4. **Bindings:** the five direct pleural-effusion elements are shown as attached tabs, including required presence, amount as the note on qualitative size, quantitative fluid attenuation, and multi-select internal complexity. A callout makes the non-inheritance rule explicit: each diagnosis subtype separately binds required presence.
5. **Anatomic scope:** the anatomy panel contrasts pleural effusion → pleural space with the grouping and pleural-thickening branch → pleura, all marked required structure scopes.

### Deterministic layout algorithm

Build the selected taxonomy forest first, sort siblings by an optional view-order list and then stable node ID, and place it with a layered parent-above-child tree. Allocate one fixed-height band for bindings and anatomy. Group remaining selected edges by relationship family in configured reading order, sort within each group by source display name, target display name, and edge ID, then give every edge one fixed-height row with four fixed columns: source, type, properties, target. Width is fixed at 1280 px; height is computed from taxonomy depth, the largest binding/scope panel, and edge-row counts. The same algorithm accommodates pyelonephritis by rendering its two-family taxonomy first and placing manifestation, cause, progression, and co-occurrence edges in the ledgers below.

### What it gives up

The ledger is taller than a compact node-link figure, and repeated target chips trade a single canonical on-page node for unambiguous edge ownership. It emphasizes deliberate reading over “whole graph at once” gestalt; that is a favorable trade for fan-in, but less attractive for a family with many dozens of sparse edges.

## Alternative 2 — contained taxonomy + source-centered small multiples

`alt2-pleural-effusion.svg` makes subsumption literal: more specific classes sit inside their parents, including diagnosis capsules inside the pleural-effusion finding and nodular pleural thickening inside pleural thickening. Below the taxonomy, every causal source receives its own compact card; behavior and evidence cards then collect the outgoing relationships of pleural effusion, parapneumonic effusion, empyema, and malignant pleural effusion. The repeated target chips are explicit references to the same canonical nodes, not duplicate classes.

### Ranked criteria

1. **Taxonomy:** a large dashed `pleural abnormality` grouping contains both primary finding branches. The six diagnosis subtypes are literally contained by pleural effusion, so the cross-label taxonomy is the first visual argument rather than an inference from arrows.
2. **Typed relationships:** one source per cause card keeps each typicality and `expected` bundle local. Empyema’s two manifestation rows visibly pair typicality with specificity; separate cards and border grammars distinguish progression, co-occurrence, manifestation, and causation.
3. **Direction and node kind:** relationship names include direction inside every card, while node kind is encoded redundantly by shape, color, and inline uppercase metadata. Because routes never leave a card, there are no crossings to decode.
4. **Bindings:** a focus card shows all five pleural-effusion bindings and required presence, with a direct statement that the six subtype presence bindings are separate. A companion summary preserves the remaining displayed findings’ presence, severity, and distribution bindings without letting element detail overwhelm the relationship cards.
5. **Anatomic scope:** a paired scope card contrasts the pleural space target for pleural effusion with the pleura target for the grouping and thickening findings.

### Deterministic layout algorithm

Construct a nested enclosure for each selected taxonomy root, compute child sizes bottom-up from label width and descendant count, and arrange siblings in a stable near-square grid by view order then node ID. For non-taxonomic edges, group by source node, sort each source’s edges by configured relationship-family order and then target ID, and render the group as a fixed-width card whose height is derived from its relationship rows. Pack cards into four equal columns using stable row-major order; a view file may pin clinically important sources before the stable fallback. Binding and scope cards use the same fixed-column chip packing. For pyelonephritis, the two taxonomy families become sibling enclosures and each diagnosis card lists its manifestations, complications, progression, or companion relationship.

### What it gives up

Small multiples duplicate node references and do not provide a single continuous route from every source to one central hub. Comparing all seven causes requires scanning cards rather than following convergent lines, and enclosure sizing is more complex for very deep or highly unbalanced taxonomies. In return, card-local properties remain robust from 10 to roughly 30 nodes and survive narrow embedding better than long labeled routes.

## Review record

- XML parsing and 1280 × 1600 view boxes validated for both SVGs.
- Both SVGs were rasterized and inspected at 1024 × 1280 output scale; the taxonomy hierarchy, relationship labels, qualifiers, bindings, and anatomy scopes remain legible without clipping or overlap.
- A separate image review found no catastrophic defects. Verified fixes increased the dashed `OCCURS_WITH` contrast, enlarged footer metadata, connected the nodular-thickening branch fully, relaxed long diagnosis labels, and wrapped the densest `expected` hint.
- Relationship audit confirmed all 14 focus edges represented in each design: seven incoming causes, two outgoing causes, three manifestations, one progression, and one co-occurrence edge. Taxonomy audit confirmed all nine selected `SUBTYPE_OF` edges.

Status: complete. Documentation reviewed against the final SVGs; no `docs/`, changelog, or development-log files were modified because the design brief confines this alternative to the preview directory.
