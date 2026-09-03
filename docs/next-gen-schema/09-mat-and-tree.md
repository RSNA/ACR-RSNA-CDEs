---
type: Draft Specification
title: The Mat and the Tree
description: The current display grammar for the vocabulary's two generated pictures - the mat (one context object, one hop out, cards in relationship containers, no wires) and the tree (an is-a outline of mini-cards) - with the card frame, containers, edge boxes, codes policy, density rules, hover and click layers, and the tooling that renders them.
tags: [next-gen-schema, display, diagrams, mat, tree, cards, renderer]
status: draft
generated: { by: ["human:talkasab", "claude-code/claude-fable-5.1"], at: 2026-09-03 }
sources:
  - id: decisions
    resource: /docs/next-gen-schema/10-decision-record-2026-09-02.md
    title: The decision record every rule here cites by number
    author: "human:talkasab"
  - id: renderer
    resource: /docs/next-gen-schema/tools/render_cards.py
    title: The renderer that implements this specification
  - id: explorations
    resource: /docs/next-gen-schema/explorations/2026-09-02-diagram-alternatives/review.md
    title: The alternatives tried before this design, and what each contributed
---

# The Mat and the Tree

**Status:** Draft, implemented. This is the current state of how the vocabulary is drawn. It is a *display* specification: it says nothing about what the vocabulary is (that is [03](./03-draft-structures.md) and [07](./07-relationship-family.md)) or about the facts in any example (that is [08](./08-worked-examples.md)). Every rule cites its decision in [10](./10-decision-record-2026-09-02.md), where the owner's decisions are marked apart from Claude's proposals and defaults.

## 1. Two pictures

There are two generated pictures, and they split cleanly (D7):

- **The mat** is the view of one object, the *context object*, one hop out. It is what a node's page on the site shows, and what a worked example shows when the context object is the family's hub.
- **The tree** is the zoomed-out is-a view of a family: an outline of mini-cards, indented by subsumption, rooted at a grouping node.

Both are deterministic SVG generated from the canonical graph ([graph README](graph/README.md)) by `tools/render_cards.py`, driven by a view file that names only the kind and the hub. Committed copies live under `diagrams/` and are byte-checked by the bundle checker. The site regenerates them for every node at build time (D26).

## 2. The mat

### 2.1 The mat is the context object

The page is about one object. That object is drawn in full. Everything connected to it is brought onto the mat as a card, and the cards sit in dotted containers whose label is the relationship to the context object (D5). The mat reaches one hop: a card's own connections to third parties are available on hover, but the third parties do not get cards (D6). The picture should feel like cards assembled on a canvas, with each card's important information on its face or one hover away (D4).

### 2.2 Mini-cards

A card brought onto the mat shows its name, its kind, and its own id, and nothing else on its face (D16). Where the object lives is a fact about that object, shown on its own mat and in its hover detail, never beside its mini-card in a container (D23). Mini-cards tile three across.

```
┌ empyema                        ┐
│ DIAGNOSIS · RDE2_000510        │
└────────────────────────────────┘
```

### 2.3 The context object's frame

Every card of every kind has the same zones in the same places, like the printed frame of a trading card; an empty zone is still drawn (D15). Top to bottom:

```
╔══ pleural effusion ═══════════════════════════════ FINDING · RDE2_000502 ═╗   1 title: name; kind · own id
║ ⌂ RID1363 “pleural space” · structure                                     ║   2 anatomy: RID with term, scope kind
║ Fluid within the pleural space beyond the physiologic few millilitres.    ║   3 text: definition, synonyms
║ synonyms: pleural fluid · hydrothorax                                     ║
║ ATTRIBUTES                                                                ║   4 attributes: the table
║  element               id           kind          values / quantity       ║
║  presence              RDE2_000001  categorical   present · possible · …  ║
║                                     SNOMED CT 386397008 “Presence”        ║
║  fluid attenuation     RDE2_000504  quantitative  [hnsf'U] · -20 to 100 · ║
║ ░ A KIND OF ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ║   5 containers (§2.4)
║ ░ KINDS OF ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ║
║ ░ MAY BE CAUSED BY ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ║
║ RadLex RID34539 “pleural effusion” · SNOMED CT 60046008 “Pleural effusion”║   6 mappings
╠══════════╤═════════╤══════════════╤═════════╤═════════╤═════════╤═════════╣   7 stat row
║ MODALITY │ REGION  │ SUBSPECIALTY │ SEX     │ AGE     │ COURSE  │ ETIOLOGY║
╚══════════╧═════════╧══════════════╧═════════╧═════════╧═════════╧═════════╝
```

1. **Title line.** Name at left; kind and own id at right. Base ids are shown for everything (D10).
2. **Anatomy line.** The anatomic location the object is scoped to, as its RID with its preferred term, and the scope kind. An anatomic location carries one id, the RID; no RadLex code is shown beside it (S12). When the scope is inherited (§4) the line says so in gray.
3. **Text.** Definition, then synonyms, then any note.
4. **Attributes.** A table on the context object only: element, its id, kind, values or quantity with units, range, and method, and the element's own codes beneath (D14, D12). Values are elliptical: the first few and an ellipsis (D14). Presence is an ordinary row (S9).
5. **Containers.** §2.4.
6. **Mappings.** External codes, last, never in the title (D13); each with its term (D11).
7. **Stat row.** Seven fixed cells, always the bottom of the card: modality, region, subspecialty (D19), sex, age, course, etiology. Each value is the concept's preferred term with its id; "—" when unset; gray with "(inherited from …)" when propagated (§4) (D15).

### 2.4 Containers and edge boxes

A container is one relationship read from the context object's side. Order, fixed; empty containers vanish (D24):

1. a kind of · 2. kinds of · 3. manifests as · 4. may represent · 5. may be caused by · 6. may cause · 7. progresses to · 8. progresses from · 9. occurs with · 10. assessed by · 11. assesses · 12. may have component · 13. may be component of · 14. may be related to

"Located in" is not a container; it is the anatomy line.

An edge that carries typicality or specificity draws as an **edge box**: a dotted bounding box around the mini-card, with those two values, in gray, riding the bottom border (D9). Nothing else goes on an edge: no `expected` hints, no notes, no edge ids (D9, D18). Those are in the hover detail.

```
╭╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╮
╎ ┌ striated nephrogram   FINDING · RDE2_000802 ┐ ╎
╎ └─────────────────────────────────────────────┘ ╎
╰╌╌ frequent · highly suggestive ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╯
```

### 2.5 No wires

Containment and containers replace edges. The mat has no wires and no arrowheads (D8). The arrow problem of the earlier renderer (D3) is therefore not solved but removed.

### 2.6 Hover

Every mini-card has a hover detail: a more detailed mini-card, not the full mat (D17). It carries the definition, the anatomy line (own or inherited), synonyms, the attribute names, up to six of the card's own connections to third parties with their typicality and specificity, the mappings with terms, and a one-line stat summary. The reveal is CSS inside the SVG, so it works when the SVG is opened alone in a browser and when it is inline in a page; it does not work when the SVG is placed as an image (as on GitHub), where the minimal face has to stand on its own (D16, D26).

## 3. Codes

Codes appear everywhere a node appears, and a code is never shown without its preferred term (D11). They go about one level down: the class and the element carry codes; the element's values do not appear with codes on the mat (D12). Close matches are marked "(close)". Anatomic locations show their RID and nothing else (S12).

## 4. Propagation of scope and context

When a node has no `SCOPED_TO` edge or none of a context edge type, the renderer walks up `SUBTYPE_OF` to the nearest ancestor that has one and shows those values in gray as "inherited from" that ancestor. The graph itself stays explicit; nothing is stored. This is a rendering rule for scope and the seven context edge types only. It is not element inheritance, which does not exist (S3). This rule is a Claude default the owner has not reviewed (S13).

## 5. Density

The layout is tight: base type 13 px, titles 18 px, mini-cards 40 px tall and three across, one-line stat cells that grow only when a cell holds several values. Whitespace is not a way to avoid overlap (D20).

## 6. The tree

The tree is an outline of mini-cards: one mini-card per row, indented by subsumption, rooted at the grouping node, every descendant included, with thin guide lines from a parent's left edge to its children. Nothing else is drawn statically: no relationship edges, no labels (D21). Each row has the same hover detail as on the mat.

On the site, the tree page adds a click layer (D22): clicking a card lights up every card in the visible tree it has a relationship with, and opens a panel listing those relationships with their typicality and specificity, plus a fuller card with anatomy, mappings, and stats. Names in the panel are clickable to walk the tree. The committed SVG is the fully expanded outline with no relationships on it, which is what a static image can honestly carry (D26).

## 7. Tooling

| Piece | Where |
|---|---|
| Renderer | `tools/render_cards.py`; `mat` and `tree` subcommands, or a view file |
| View files | `examples/*.mat.json`, `examples/*.tree.json`: `{"kind", "hub"}` |
| Committed pictures | `diagrams/mat-*.svg`, `diagrams/tree-*.svg`, byte-checked by `docs/check_bundle.py` |
| Site | `tools/build_site.py` renders a mat for every finding, diagnosis, and grouping node, and a tree page with the click layer for every tree view |
| Object dossiers | `tools/render_neighborhood.py` and `examples/*.{neighborhood,element,location}.json`, the older single-node pictures, unchanged |

## 8. What this replaced

The column-and-curve constellation renderer of 1 to 2 September 2026 ([archive](archive/2026-09-02-constellation-diagrams.md)), and the two rounds of alternatives that led here ([explorations](explorations/2026-09-02-diagram-alternatives/index.md)).
