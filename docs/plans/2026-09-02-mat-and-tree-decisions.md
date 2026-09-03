# Decisions: the mat and the tree

**Written:** 2026-09-02, from a working conversation between the owner and Claude. **Status:** superseded as a record by `docs/next-gen-schema/10-decision-record-2026-09-02.md`, which sorts the same decisions by structure, display, and content with stricter provenance marks; kept as the working document Codex and Kimi built from. Built the same day in `docs/next-gen-schema/tools/render_cards.py` after two agent attempts (Codex, Kimi) were reviewed; Kimi's served as the guide. Amendments from that review are marked **[amended]** below.

Every decision below is tagged with where it came from. **[owner]** means the owner stated it. **[proposed, accepted]** means Claude proposed it and the owner accepted it explicitly. **[default]** means Claude proposed it, the owner did not object when asked, and it stands until someone objects. Where the owner corrected an earlier proposal, the correction is what is recorded.

This supersedes the constellation design in `docs/next-gen-schema/tools/render_constellation.py` and the diagram brief of the same date for everything below.

## 1. What is being built

Two pictures, and they split cleanly. **[proposed, accepted]**

- **The mat** is the view of one object (the *context object*), one hop out. It replaces the site's per-node neighborhood diagram and the two constellation diagrams in 08. The old constellation renderer is deleted, not kept. **[owner: "this is the basic architecture of the node neighborhood, replacing everything that's done that before"]**
- **The tree** is the zoomed-out is-a view of a finding or diagnosis family: boxes and connectors. **[owner]** It carries relationship edges too, with labels, done well. **[owner: "I think that CAN be done well. Try it."]**

Both remain deterministic SVG generated from the canonical graph (`docs/next-gen-schema/graph/*.jsonl`, loaded through `tools/graph.py`) plus at most a small view file, byte-checked by the bundle checker, usable inline in HTML and as a static image on GitHub. **[default]** No interactivity in this step; the card faces are designed with fixed zones so a canvas could reuse them later. **[owner: the card metaphor is "how the picture should feel", not an editor]**

## 2. The mat

### 2.1 The mat is the context object

The page is about one object. That object is the mat, drawn in full. Everything else is brought onto the mat as a card, and the cards sit in shaded or dotted containers whose label is the relationship to the context object. **[owner: "the mat is the CONTEXT of what we're looking at, and then we bring in the connected objects and have some dotted/shaded container that says how they're associated to the CONTEXT OBJECT this display is about"]**

The mat reaches one hop. A card brought onto the mat may carry its own connections to third parties as lines on its face, but those third parties do not get cards. **[proposed, accepted: "That's the right idea"]**

### 2.2 Cards feel like cards

Contained things are cards being assembled on a canvas, not points in space. Each card has its important information directly on it, or quickly available without clicking. **[owner]**

### 2.3 Every card has the same frame

Zones in fixed positions, like the printed frame of a trading card. An empty zone is still drawn. **[owner: "It's NOT OK for them to be loosey-goosey."]**

Reading top to bottom:

1. **Title line.** Name at left; kind and the object's own id at right. Base ids are shown for everything. **[owner]**
2. **Anatomy line.** The anatomic location the object is scoped to, as its RID with its preferred term, and the scope kind and strength. An anatomic location carries one id, the RID, and nothing else; do not show a RadLex code alongside an anatomic location, the RID is the RadLex code. **[owner]**
3. **Text.** Definition; synonyms.
4. **Attributes.** The context object gets a table: element, its id, kind, and its values or quantity with units and method. **[owner: "the table-like thing"]** Mini-cards do not get the table.
5. **Connections.** On the context object these are the containers (§2.5). On a mini-card, lines on the face for its own edges to third parties, one hop and no further.
6. **Mappings.** External codes, last. A code is never shown without its preferred term. Never. **[owner]** Mappings to other ontologies do not go in the title bar; they were given too much prominence in an earlier draft. **[owner]**
7. **Stat row.** Seven fixed cells, always the bottom of the card: modality, body region, subspecialty **[amended: subspecialty had been dropped in error]**, sex specificity, age profile, expected time course, etiology. "—" when unset. **[owner: "Put the stats as the consistent bottom row."]**

### 2.4 Mini-cards are minimal

A card brought onto the mat shows its name, kind, and own id, and nothing else on its face. **[owner: "TOO much detail on the mini-cards ... maybe almost just the code and the name"]** Where an object lives (its anatomy) is a fact about that object and belongs on its own mat, not beside its mini-card in a container. **[owner: "How does the fact that some of the findings are in the kidney and some not matter for showing them in the 'manifests as' box?"]**

Hover detail: in the site's inline SVG, pointing at a mini-card reveals a more detailed mini-card, not the full mat: definition, mappings, stat row, and its own connection lines. **[owner]** On GitHub, where hover does not exist, the picture stands on the minimal face.

### 2.5 Containers

A container is one relationship read from the context object's side. **[amended]** An edge carrying typicality or specificity draws as a dotted *edge box* around the mini-card, with only those two values, in gray, riding the bottom border; nothing else goes on an edge, since no edge bears more weight than that. The `expected` hints and notes live in the hover detail only. **[owner]** Edge ids are **not** shown on the mat. **[owner: "we don't need the edge ids on the neighborhood mat"]**

Order, fixed; empty containers vanish: **[default, "OK for a first pass"]**

1. a kind of (the parents, including the grouping node)
2. kinds of (the subtypes)
3. manifests as
4. may be caused by
5. may cause
6. progresses to
7. progresses from
8. occurs with
9. assessed by

"Located in" is not a container; it is the anatomy line on the face.

### 2.6 No wires on the mat

Containment and containers replace edges. The mat has no wires and no arrowheads. **[proposed, accepted]**

### 2.7 Attributes, presence, and "required"

There is no such thing as a required element. The `required` property on `HAS_ELEMENT` edges is to be removed from the graph, the example specs, 03 §2, and every renderer; the "every card binds presence" legend note goes with it. **[owner: "THERE IS NO SUCH THING AS A REQUIRED ELEMENT"]** Presence is an ordinary row in the attribute table.

On the context object's attribute table, be elliptical where the values are obvious; the full list of presence choices need not be spelled out. **[owner]**

### 2.8 Codes: how far down

Show codes as far down the chain as makes sense, which is about one level: a code for the element "presence", not codes for each of its values. **[owner]** RadLex and SNOMED CT on classes; LOINC where an element has one; close matches marked as close; always with the term. **[default]**

### 2.9 Context nodes (the stat row's sources)

Modality, body region, and subspecialty are RadLex concepts and get their RIDs, looked up now. Etiology, sex specificity, age profile, and time course get our own provisional codes now, seeded from the OIFM lists, documented as a lookup table in the graph until official versions exist. **[owner: "Might as well start the lookup table."]**

## 3. The tree

**[amended after review]** The tree is an *outline* of mini-cards, not a family tree of boxes and wires: one mini-card per row, indented by subsumption, rooted at the grouping node, nothing else drawn statically. **[owner: "much more like an expanding outline of the mini-cards than a literal family tree"]** Relationships are not drawn on the static tree. On the site, hovering or clicking a card pops a more detailed card and lights up the cards in the visible tree it has relationships with, with the relationship named. **[owner]** This is the one place JavaScript enters; the committed SVG is the fully expanded outline.

The earlier requirement that labelled relationship edges be drawn on the tree was tried by both agents and withdrawn on review. Neither result worked for the owner. Arrowheads, if used, must be aligned with the line they terminate; the earlier renderer's markers sat at an angle to their curves and that is unacceptable. **[owner: "the arrow heads aren't aligned with the arrow lines"]**

## 3.1 Propagation of scope and context

**[default, taken during the build]** `SCOPED_TO` and the seven context edge types propagate down `SUBTYPE_OF` at render time when a node has none of its own, shown in gray with "inherited from" naming the ancestor. The graph stays explicit. This is not element inheritance, which remains excluded. Reversible by asserting the edges on each subtype and deleting the rule.

## 3.2 Density

**[owner]** Layout must be tight: base font 13 px, mini-cards three across, one-line stat cells. Both agent attempts inflated the frame and shrank the type; that is the failure mode to avoid.

## 4. Where things live

Two mats (acute pyelonephritis, pleural effusion) and two trees (renal abnormality, pleural abnormality) committed under `docs/next-gen-schema/diagrams/` and byte-checked; per-node mats generated at site build and not committed. **[default]**

## 5. Reference mockups

The context object's frame, as agreed (mini-cards are the same frame minus zones 3 to 5):

```
╔══ pleural effusion ═══════════════════════════ FINDING · RDE2_000502 ══╗
║ ⌂ pleural space RID1363 "pleural space"               structure · required║   (scope strength, not element requirement)
║ Fluid within the pleural space beyond the physiologic few millilitres.  ║
║ synonyms: pleural fluid · hydrothorax                                   ║
║ ATTRIBUTES                                                              ║
║ ┌ element ──────────┬ id ───────┬ kind ────────┬ values / quantity ────┐ ║
║ │ presence          │ RDE2_000001│ categorical │ present · absent · … │ ║
║ │ change from prior │ RDE2_000002│ categorical │ new · increased · …  │ ║
║ │ size (qualitative)│ RDE2_000013│ ordered     │ trace … large        │ ║
║ │ fluid attenuation │ RDE2_000504│ quantitative│ HU · ROI method      │ ║
║ │ internal complexity RDE2_000505│ multi-select│ septations · …       │ ║
║ └───────────────────┴───────────┴─────────────┴──────────────────────┘ ║
║ ░ A KIND OF ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ║
║ ░ ┌ pleural abnormality   GROUPING · RDE2_000516 ┐                     ░ ║
║ ░ └───────────────────────────────────────────────┘                     ░ ║
║ ░ KINDS OF ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ║
║ ░ ┌ empyema      DIAGNOSIS · RDE2_000510 ┐ ┌ hemothorax  DIAGNOSIS · RDE2_000511 ┐ ║
║ ░ └───────────────────────────────────────┘ └─────────────────────────────────────┘ ║
║ ░ … four more                                                                   ░ ║
║ ░ MAY BE CAUSED BY ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ║
║ ░ ┌ heart failure  DIAGNOSIS · RDE2_000520 ┐  frequent · expect bilateral, R > L; ░ ║
║ ░ └─────────────────────────────────────────┘  simple fluid                      ░ ║
║ ░ ┌ pneumonia      DIAGNOSIS · RDE2_000522 ┐  frequent · expect ipsilateral;     ░ ║
║ ░ └─────────────────────────────────────────┘  small to moderate                 ░ ║
║ ░ MAY CAUSE ░░░░░░░░░░░░░░░░░░░░░░  ░ OCCURS WITH ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ║
║ ░ compressive atelectasis · frequent ░ pleural thickening  FINDING · RDE2_000532 ░ ║
║ RID34539 "pleural effusion" · SNOMED 60046008 "Pleural effusion"                ║
╠══════════╤══════════╤══════════╤══════════╤══════════╤══════════════════════════╣
║ MODALITY │ REGION   │ SEX      │ AGE      │ COURSE   │ ETIOLOGY                 ║
║ CT US XR │ chest    │ neutral  │ all      │ —        │ idiopathic               ║
╚══════════╧══════════╧══════════╧══════════╧══════════╧══════════════════════════╝
```

## 6. What was tried and rejected, for the record

- Columns of chips with labelled bezier curves (the current renderer): labels stack under fan-in, arrowheads misaligned, anatomy and bindings omitted. **[owner: "the arrows and arrowheads look terrible"]**
- A morphology "form" axis and upper-level lesion/mass/process classes: not clinically meaningful as nodes; patterns are an authoring guide, not graph content. **[owner]**
- Mini-cards carrying definition, anatomy, mappings, and stat rows on the mat: too much detail. **[owner]**
- Anatomy as a lane of location cards wired to classes, or as an outer container: replaced by the anatomy line on every card's face. **[owner: the location IS the anatomy of the finding]**
- Codes in the title bar. **[owner]**
- A second visual axis for anatomic-scope deviations inside containers. **[owner]**
