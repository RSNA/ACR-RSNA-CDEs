---
type: Exploration
title: Diagram alternatives, round 1 (open brief, two alternatives): claude-b
description: Verbatim README written by the agent claude-code/claude-fable-5.1 (subagent B) for its diagram alternatives on 2026-09-02; kept as a record of the exploration, not as a specification.
tags: [next-gen-schema, exploration, diagrams, superseded]
status: deprecated
generated: { by: "claude-code/claude-fable-5.1 (subagent B)", at: 2026-09-02 }
sources:
  - id: brief
    resource: /docs/plans/2026-09-02-diagram-brief.md
    title: The brief this agent worked from
---

> **Exploration record.** This file is the agent's own README, unedited apart from this frontmatter block. The design it describes was reviewed on 2026-09-02 and is superseded by [09](../../../09-mat-and-tree.md); see [the review](../review.md) for what it contributed.

# claude-b: two alternatives for the constellation diagrams

Both alternatives are generated, not drawn: `alt1_sunburst.py` and `alt2_swimlanes.py`
read `docs/next-gen-schema/graph/core.jsonl` plus the family file and emit the SVGs here.
The only "view" input is the hub node id, the family file, and a title. Run
`python3 alt1_sunburst.py` or `python3 alt2_swimlanes.py` from this directory to regenerate.
`common.py` holds the loader, the text metrics, the palette, and the legend.

Files:

- `alt1-pleural-effusion.svg`, `alt1-pyelonephritis.svg` (1334 x 850, 1084 x 1118)
- `alt2-pleural-effusion.svg`, `alt2-pyelonephritis.svg` (1333 x 906, 1179 x 805)

Two conventions shared by both, because they answer the brief's items 3 and 4 regardless of layout:

- **Node kind without a legend.** Findings are upright text in blue boxes with square corners.
  Diagnoses are italic text in purple boxes with rounded corners. Groupings are a dashed slate frame
  that *contains* things and carries the words "reported only as absent". Anatomy is amber. Elements
  are small green text with a ring bullet inside the class that binds them. In grayscale the
  italic/upright and rounded/square pairs still separate diagnosis from finding.
- **Every relationship's properties live in exactly one place, attached to the line.** No label floats at a
  curve midpoint. Under fan-in this is the whole game, so each alternative solves it a different way
  (see below). Typicality and specificity are spelled out as words; the `expected` hint is the italic
  grey line under the verb.
- Presence is bound by every class and suppressed with a legend note. Scope is stated once for the
  hub ("scoped to kidney") and shown as a badge only on classes that deviate (perinephric fat stranding
  says "scope: perirenal space"; pleural thickening and the split pleura sign say "scope: pleura").
  Scope is inherited down SUBTYPE_OF when a class has no SCOPED_TO edge of its own.

## Alternative 1: radial taxonomy with port-anchored cards

**The idea.** The class under discussion is a disc at the centre. Its subtypes are the sectors of a ring
around it, and their subtypes are sectors of the next ring out, each centred in its parent's span: a
sunburst, so "a kind of" is read as "one ring further out, inside the parent's angle". The hub's
ancestors are concentric frames around the sunburst: pyelonephritis is a rounded purple frame around
acute pyelonephritis, and the renal abnormality grouping is the dashed frame around that. Every other
class is a card placed inside the innermost frame it belongs to, so the reader sees at a glance that
striated nephrogram is a renal abnormality but not a pyelonephritis, and that heart failure is neither.
Every typed relationship gets one text row on the card at its outer end, and the line for that
relationship ends on that row's port, so the label and the edge are one object. Cards are placed in
sectors by relationship kind: causes into the family on the west, manifestations, companions and
complications on the east, progression targets below.

**Against the ranked list.**

1. Subsumption reads as containment (frames) and as radial descent (rings). Empyema sits in the ring
   around pleural effusion even though it is purple and the effusion is blue; renal abscess is a card
   nested inside the renal lesion card. The grouping is the outermost frame with a dashed border, large
   and labelled, not a quiet node.
2. Five causes into pleural effusion are five cards in the west column, each with its own row
   ("may cause pleural effusion · frequent" then "bilateral, right greater than left; fluid attenuation:
   simple"), each with its own spoke into the disc. Nothing stacks. Manifestation rows read from the
   finding's side ("manifestation of empyema · frequent · highly suggestive"), so a finding that is a
   sign of two things (pleural thickening) carries two rows and two ports. Progression is a dashed teal
   arc with a chip between adjacent sectors, or a dashed teal spoke to a card; occurrence is a dotted
   grey line with no arrowhead.
3. Kinds by shape, colour, and type style; direction by arrowhead and by the verb on the row.
4. Elements are listed inside the hub disc and inside each card. The renal enlargement card has a row
   "interpreted from kidney length" whose spoke ends on the "length · binding RDE2_000830" row of the
   kidney card, the one anatomy card the view needs.
5. Scope badge on deviating cards only.

**Layout algorithm.**

1. *Partition.* From the hub: ancestors (via SUBTYPE_OF, within the family) become frames, nearest
   innermost; the hub and its descendants become the sunburst; every other class becomes a card whose
   level is the innermost frame it descends from (0 = outside all frames). A card nests inside another
   card when its SUBTYPE_OF parent is a card. An INTERPRETED_FROM edge adds an anatomy card for the
   binding's owner with one row per binding cited.
2. *Rows.* Each typed edge gets one row on the card farther from the hub (the source for
   INTERPRETED_FROM). Row text is verb + far node name + typicality + specificity; detail line is the
   `expected` hint or the note.
3. *Sunburst angles.* Ring 1 shares 360° minus openings reserved for the hub's own spokes (west for
   incoming edges, east for outgoing, south for progression; width 10° per spoke). Children are sorted
   by "pull" (count of outgoing external edges minus incoming), progression pairs made adjacent, split
   between the north and south arcs, and given angular shares proportional to leaf count, capped at
   100° and pushed toward the side they pull to. Deeper rings recurse inside the parent's span.
4. *Sides.* A card's side is a vote over its rows: cause into the family = west, progression from the
   hub = south, everything else = east; cards tied only to other cards inherit their partner's side.
   Its ordering key is the mean angle of its partners.
5. *Placement, innermost level outward.* Per side and level, cards are stacked with uniform gaps,
   centred on the hub axis, ordered by that key. A column that sits between the hub's opening and an
   outer column is shifted clear of the opening; cards in the outer column that connect to the
   sunburst are pushed above or below the inner column's band. After each level the frame rectangle
   is the bounding box plus padding, and the next level's columns start outside it.
6. *Spokes.* Each sector spreads its spokes evenly along its outer arc, ordered by target angle; the
   hub spreads its spokes across the reserved opening. A spoke is a cubic curve leaving radially and
   arriving horizontally at the row's port if the angular gap is small; otherwise it runs out to a
   "ring road" (concentric circle, one radius per such spoke), arcs to the target's angle, and curves
   in. Spokes arriving from above or below a card enter its top or bottom edge and continue as a leader
   down the card's left margin to the row, so the row is still unambiguous.
7. Title, frames, sectors, arcs, spokes, disc, cards, legend; bounding box sets the viewBox.

**What it gives up.** It is not a reading-order diagram: a radiologist reads it from the centre outward,
not left to right, and the causes column is a list without the causes' own structure. Sector labels are
squeezed for long names ("malignant pleural effusion" is three lines), so it will not scale past about
eight subtypes per ring without growing the ring. Long spokes that ride the ring road (malignant
pleural effusion to nodular pleural thickening) are traceable but not pretty. The hub disc, not the
diagnosis, is the visual centre for pleural effusion, which is correct for that family but means the
pyelonephritis picture centres on *acute* pyelonephritis with chronic below it rather than on the
pyelonephritis tree as a whole. And it spends height: the pyelonephritis picture is 1118 px tall.

## Alternative 2: role swimlanes, nested boxes, one track per wire

**The idea.** Four vertical lanes, present only when populated, in the order a radiologist reasons:
CAUSES (clinical diagnoses that only point at the family), THE FAMILY (the hub with its taxonomy as
boxes inside boxes), FINDINGS & COMPANIONS (what the family looks like and what it brings), ANATOMY &
BINDINGS (only when a class interprets a measurement). Subtypes are stacked inside their parent's box,
so the six kinds of pleural effusion are six purple boxes inside the blue effusion box, and
emphysematous pyelonephritis is a box inside acute inside pyelonephritis. The grouping is a dashed band
across the family lane and the top of the findings lane, so its members are the things inside the band.
Every wire is orthogonal, leaves its source at its own port on the right edge, carries its label in the
channel right beside that port, turns on its own vertical track, and enters its target at its own port
on the left edge. Labels are all left of all tracks, so a wire may cross another wire but never a label.

**Against the ranked list.**

1. Nested boxes are containment, full stop. The band is large and named. Empyema inside pleural
   effusion and renal abscess inside renal lesion cross the finding/diagnosis colour boundary exactly
   where the model does.
2. Fan-in of five causes: five ports on the hub's left edge, five wires, five labels each sitting
   beside its own source card on the left. Fan-out from acute pyelonephritis: five ports on its right
   edge stacked in the header, each label on its own horizontal run. Progression between siblings is a
   thick dashed teal vertical arrow in the gap between adjacent boxes with the verb beside it.
   Occurrence is a dotted grey wire with no arrowhead.
3. As above.
4. Elements listed inside each box. The anatomy lane appears only for pyelonephritis, holding the
   kidney with its "length · binding RDE2_000830" row and the "interpreted from" wire from renal
   enlargement.
5. Scope badge on deviating cards only.

**Layout algorithm.**

1. *Lanes.* Classes whose only edges are outgoing MAY_CAUSE into the family go to CAUSES. The hub,
   its non-grouping ancestors, and all their descendants go to THE FAMILY. Owners of cited bindings go
   to ANATOMY. Everything else goes to FINDINGS. Empty lanes are dropped.
2. *Boxes.* A box is header (name, kind, scope badge, elements, binding rows) plus its children stacked
   below with a fixed indent. Children are ordered so a MAY_PROGRESS_TO source sits directly above its
   target, then by out-degree, then name. The header is tall enough for its out-ports (one label
   height each) and in-ports (12 px each).
3. *Ports.* Out-ports on the right edge in semantic order (manifestation, occurrence, cause,
   progression, interpretation), in-ports on the left edge ordered by source y. Edges from a
   right lane to a left lane are reversed on the canvas and drawn with the arrow at the left.
4. *Channels.* Channel width = 12 + widest label in that channel + 12 + 9 px per track + 10. Label
   width is capped by wrapping at 176 px, two lines for the verb line and two for the detail.
5. *Vertical placement.* The family root box is placed first. Findings-lane boxes are placed by
   barycentre of their partners' port y, members of the band first, then non-members below the band.
   Causes and anatomy boxes likewise, pushed down only as needed to avoid overlap.
6. *Tracks.* Per channel, edges are sorted by descending source y and given the leftmost track whose
   occupied y-intervals do not overlap theirs; that ordering makes any order-preserving pair of wires
   cross-free and leaves exactly one crossing per pair that must cross.
7. Band rectangle from the family lane's left edge to the findings lane's right edge, from the top to
   the last member; then boxes, wires, labels, legend.

**What it gives up.** Height is spent on port stacks: a box with five outgoing relationships has a
header five labels tall even when its own text is one line, which is why acute pyelonephritis has empty
space inside it. Long wires (pleural effusion down to compressive atelectasis, chronic pyelonephritis
across to scarring) are traced by following a vertical track, which is easy but not instant, and wires
do cross each other where the barycentre order cannot avoid it. The band forces non-member findings
(atelectasis, mediastinal shift, split pleura sign) below the family's full height, leaving a gap in the
findings lane for pleural effusion. Lanes are by role rather than strictly by node kind, so a clinical
diagnosis and an imaging diagnosis are in different lanes and rely on colour and italics, not position,
to say they are the same kind of thing. And the sector grouping of relationships is by lane only: the
reader distinguishes cause from manifestation wires by colour, arrowhead, and the verb, not by where
they arrive.

## Known rough edges in the mockups

- Text widths are estimated from a character table, not measured; a few lines sit within 4 px of a
  box edge. A real generator would measure with a font library or leave a wider margin.
- Alternative 1 has no collision check between a ring-road spoke and a card in the bottom row; the two
  examples never trigger it. A generator should reserve the road radii as an exclusion zone.
- External mappings (RadLex, SNOMED CT) and modality/etiology concepts are omitted from both.
