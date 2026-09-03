---
type: Exploration
title: Diagram alternatives, round 1 (open brief, two alternatives): claude-a
description: Verbatim README written by the agent claude-code/claude-fable-5.1 (subagent A) for its diagram alternatives on 2026-09-02; kept as a record of the exploration, not as a specification.
tags: [next-gen-schema, exploration, diagrams, superseded]
status: deprecated
generated: { by: "claude-code/claude-fable-5.1 (subagent A)", at: 2026-09-02 }
sources:
  - id: brief
    resource: /docs/plans/2026-09-02-diagram-brief.md
    title: The brief this agent worked from
---

> **Exploration record.** This file is the agent's own README, unedited apart from this frontmatter block. The design it describes was reviewed on 2026-09-02 and is superseded by [09](../../../09-mat-and-tree.md); see [the review](../review.md) for what it contributed.

# Constellation diagram alternatives: claude-a

Two designs, both generated from the canonical graph files by the scripts in this directory. Nothing here is hand-drawn: each SVG is `render_*.py` applied to a view file that lists which node ids to include and in what order. Re-run `./build.sh` to regenerate; `PNG=/some/dir ./build.sh` also rasterizes.

| File | What |
|---|---|
| `alt1-pleural-effusion.svg`, `alt1-pyelonephritis.svg` | Alternative 1, nested containment |
| `alt2-pleural-effusion.svg`, `alt2-pyelonephritis.svg` | Alternative 2, relationship matrix |
| `render_nested.py`, `render_matrix.py` | the generators (import `graph.py` from `docs/next-gen-schema/tools`, read-only) |
| `views/*.json` | the view files: title, aria text, and the node ids |
| `build.sh` | regenerate, parse-check, optionally rasterize |

Both designs share four decisions that answer the known failures of the current renderer:

- **Edges carry no text.** Every property of a relationship (typicality, specificity, `expected`, note) is written as text in a fixed place that belongs to exactly one edge: a line inside a node card in alternative 1, a cell in alternative 2. Nothing can stack at a curve midpoint because nothing sits on a curve.
- **Elements and scope are on the class.** Data elements are green chips (alternative 1) or a green line (alternative 2) on the class that binds them; `presence` is stated once in the key rather than repeated on every class. Anatomic scope is an amber tag that appears only where it differs from the enclosing or parent class, so in pyelonephritis exactly one tag appears in the family, on perinephric fat stranding, which is the fact the brief wants seen. `INTERPRETED_FROM` resolves the binding id and is written as an element-like line, `interpreted from length bound to kidney`.
- **Node kind without a legend.** Finding, diagnosis, grouping keep the existing colors (blue, purple, slate) and gain shape: findings have square corners, diagnoses rounded corners, grouping nodes a dashed outline, and every node prints its kind word under its name. Elements are small green pills, anatomy amber tags. All of this survives grayscale.
- **Edge kind without a legend, in grayscale.** May-cause is a solid line with a filled head, may-manifest-as a solid line with a hollow head, may-progress-to a long dash with a filled head, occurs-with a dotted line with no head (it is symmetric). Colors are kept from the current renderer on top of that.

## Alternative 1: nested containment

### The idea

Subsumption is drawn as containment and nothing else: a subtype is a box inside its parent's box. The grouping node is the outermost dashed box; the pleural effusion finding is a solid box inside it; the six diagnosis subtypes are cards inside that. A purple card inside a blue box is the sentence "empyema is a kind of pleural effusion even though one is a diagnosis and the other a finding", said without an arrow. Typed relationships are the only arrows on the page, drawn between boxes. Their properties are written inside the card at the edge's *quieter* end, naming the other end, so the picture reads as prose from either side: the heart failure card says "may cause pleural effusion, frequent, expect location bilateral, right greater than left; fluid attenuation simple", and the split pleura sign card says "may represent empyema, frequent, highly suggestive". Causes stand in a column on the left, companions and manifestations in a column on the right, the family in the middle.

### Against the ranked list

1. **Taxonomy.** Containment, at any depth, across the finding/diagnosis line. The grouping node is the loudest thing on the page because it is the biggest, and it says `grouping · negative-only`.
2. **Typed relationships with their properties attached.** Each edge's properties are written inside exactly one card, the endpoint with fewer typed edges (tie goes to the source). Under the fan-in of seven causes on pleural effusion, every cause card carries its own typicality and its own `expected` hint, and the arrows only have to say *where* they go. Progression is a short vertical dashed arrow between adjacent cards; occurs-with is a dotted line with no head; manifestation has a hollow head; causation a filled one.
3. **Kind and direction.** Shape, color, and the printed kind word per node; arrowheads per edge type. Boxes and cards are the same visual vocabulary at different sizes.
4. **What a class binds.** Green chips in the box or card header, listing the elements the class binds beyond those already shown on an enclosing box. The interpretation-of-a-binding case is a green chip reading `≈ interpreted from length bound to kidney`.
5. **Anatomic scope.** An amber tag on a box is inherited by everything inside it, so a tag only appears where the scope changes. Pleural abnormality is `in pleura`, pleural effusion inside it is `in pleural space`, pleural thickening inside it has no tag because it is also in pleura.

### The layout algorithm

Input: the merged graph, and a view file naming node ids in display order. All decisions below are functions of that input, so the output is deterministic.

1. **Tree.** Take the `SUBTYPE_OF` edges among the view's nodes; each node's parent is the first such target. Nodes with no parent are roots.
2. **Regions.** A root that is a grouping node or has children is *center*. A childless root whose only typed edges are outgoing `MAY_CAUSE` is a *cause* (left column). Every other root is a *companion* (right column).
3. **Containers.** For each container, decide **stack** or **lanes**: count the children whose subtree receives a flow edge (`MAY_CAUSE`, `MAY_MANIFEST_AS`, `OCCURS_WITH`) from a sibling's subtree. Two or more receivers, and the container has two lanes, senders left and receivers right, each lane a vertical stack. Otherwise it is a single vertical stack. Renal abnormality gets lanes (the pyelonephritis tree sends to seven findings); pleural abnormality gets a stack (only pleural thickening receives). Progression is deliberately excluded from this count so that acute and chronic pyelonephritis stack vertically with a short arrow between them.
4. **Order within a stack.** View order, except that a `MAY_PROGRESS_TO` target is moved to sit directly under its source.
5. **Widths, bottom-up.** A card is 300 wide. A container is as wide as its widest child (or its two lanes plus the lane gap) plus padding plus a *channel* strip on the right, 9 px per edge routed through it (step 7). Cards inherit the width of their stack.
6. **Heights, bottom-up.** A card's height is its title, kind line, element chip rows, and annotation lines at the card's width; a container adds its children and the gaps between them (wider where a vertical arrow runs).
7. **Edge routes**, one of four, decided from structure alone:
   - to or from a side-column card: a cubic curve between the facing sides;
   - between the two lanes of a lanes container: a cubic curve, left to right;
   - between adjacent children of a stack: a straight vertical arrow;
   - anything else inside the family: an orthogonal route that leaves the source to the right, drops down the channel in the right padding of the lowest common ancestor container, and enters the target from the right. That is how empyema reaches pleural thickening and malignant effusion reaches nodular thickening without crossing any card.
8. **Anchors.** Edges sharing a side of a node are spread along a band (the header band for a container, the full side for a card), ordered by the other endpoint's y, so the five causes land on five distinct points of the pleural effusion header.
9. **Side columns.** Each cause or companion card is placed at the mean y of what it connects to, then cards are pushed down in that order until none overlap.
10. **Annotations.** For every typed edge, write its properties into the endpoint with the lower typed-edge count (tie: the source) using the relationship's name at the source or its inverse name at the target, from the `RelationshipType` node. Wrap to the card width.

Scaling: the stack grows downward, the lanes grow outward; 30 nodes is three or four containers with ten cards each, which is a tall page but not a wide one. Deeper taxonomies (five levels) would shrink cards by 24 px per level and need the base width raised.

### What it gives up

- **Multiple parents.** A node can be inside exactly one box. The graph allows several `SUBTYPE_OF` targets; this design takes the first and would need a ghost card for the second.
- **Edges into a nested card cross its parents' borders.** Cirrhosis's arrow crosses the grouping border and the pleural effusion border to reach hepatic hydrothorax. It lands unambiguously on the card, and the padding it crosses is empty, but a border crossing is still a thing the eye has to forgive.
- **Vertical space.** The pleural effusion box is as tall as six stacked cards. A family with fifteen subtypes would need the stack to fold into two columns, which the algorithm does not yet do.
- **Two sides of one fact.** An edge's properties are written at one end only. The reader standing at pleural effusion sees seven arrowheads and must look left to the cause cards for the typicalities. The arrows say where; the cards say what.

## Alternative 2: relationship matrix

### The idea

The family is a table. Rows are every class in the view, laid out as the taxonomy tree: indentation and a connector line are the subsumption, and because a row is just a row, a purple diagnosis sits under a blue finding under a dashed grouping without any special case. Columns are the classes that receive a typed edge, in the same order. A cell at (row, column) is the edge from the row class to the column class: a colored strip naming its kind, a Harvey ball for typicality, one to three diamonds for specificity, and the `expected` hint as text. Fan-in becomes a column: pleural effusion's seven causes are seven rows, each with its own cell, and the question "which typicality belongs to which cause" cannot be asked. The seven clinical causes sit in their own section at the bottom, under a rule that says they have no elements of their own.

### Against the ranked list

1. **Taxonomy.** The row header is the tree. The grouping node is the first row, dashed, labelled negative-only; the crossing of the finding/diagnosis line is a purple row indented under a blue one.
2. **Typed relationships with their properties attached.** A cell is one edge, and it is the only place that edge's properties can be. The kind is a colored strip with the word on it (causes, manifests as, progresses to, occurs with), typicality is a ball whose fill is the HPO bin, specificity is diamonds, `expected` is text. Direction is fixed by the table: row to column. Occurs-with is symmetric and is drawn in both cells.
3. **Kind and direction.** Rows and column headers carry the same color, shape, and kind word as alternative 1. Direction is the reading rule printed above the columns.
4. **What a class binds.** A green line under the row's name, with the same inheritance rule (elements already on an ancestor row are not repeated), and the same `interpreted from length bound to kidney` line.
5. **Anatomic scope.** The same amber tag, shown on a row only where its scope differs from its parent's.

### The layout algorithm

1. **Rows.** Build the tree as in alternative 1. Walk the family roots depth-first in view order, then the other imaging classes, then the causes; each group starts a labelled section.
2. **Columns.** Every node that is the target of a typed edge (both ends for symmetric types), in row order.
3. **Cells.** For each typed edge, a cell at (from, to); symmetric edges also at (to, from).
4. **Sizes.** Column width is fixed (104 px). Row height is the maximum of the header's lines (name, kind, wrapped element line) and the tallest cell in the row (strip, ball line, diamond line, wrapped hint). Column header height is the tallest wrapped name.
5. **Draw.** Alternating row stripes, column rules, the diagonal shaded where a class is both a row and a column, tree connectors from each parent row to each child row.

Scaling: rows are linear in node count and columns in the number of targets, which is usually about half the nodes; 30 nodes is roughly 30 rows by 15 columns, 1600 px wide, so past about 20 nodes the column set would need to be restricted to findings, with diagnosis-to-diagnosis edges (progression, causes of a subtype) folded into the row header as annotations.

### What it gives up

- **No picture of the graph.** Nothing points at anything; the reader assembles the constellation by scanning a row and then finding its column. A radiologist who thinks in arrows gets a spreadsheet.
- **Every target appears twice**, once as a row and once as a column, and the reader must match names across the two.
- **Sparsity.** Most cells are empty; the pleural effusion matrix has 15 filled cells in 180. The empty rows are honest (hemothorax has no relationships recorded), but they cost height.
- **Width grows with the number of targets**, not with the number of nodes, so a family with many companions gets wide faster than alternative 1 does.
- **Subtype-to-subtype edges live in the sea of cells** rather than next to the nodes: parapneumonic progresses to empyema is a lone cyan cell, findable but not obvious.

## Verification

Every SVG parses with `xml.dom.minidom` (run by `build.sh`). All four were rasterized with cairosvg at 1800 px wide and inspected: no label overlaps another label or a node, no edge crosses a card, all text fits its container. The pleural effusion diagrams are 1068 px (alternative 1) and 1300 px (alternative 2) wide; the pyelonephritis diagrams 818 px and 1300 px.
