# Plan: one sentence of a report, drawn in two planes

**Written:** 2026-09-03 by Claude, from the owner's answers in the working session. **Status:** complete 2026-09-03. **Executor:** the Codex agent. **Owner approves each commit; do not commit.**

## Goal

Take one sentence of a radiology report and show, as ground truth in JSON Lines and as a generated picture, how the report's Observation objects form their own small graph and how each of them points into the definitions graph (finding classes, diagnoses, data elements, anatomic locations). The picture must make two things visible without argument:

1. **Laterality.** The vocabulary scopes pyelonephritis, hydronephrosis, and renal abscess to `kidney` (RID205). A specific observation is in a specific kidney, `left kidney` (RID29663). Because left kidney IS A kidney, the observation satisfies the scope. The same holds for perinephric stranding in the left perirenal space under the perirenal space.
2. **Two planes, two relationships.** In definition space the committee wrote, once, `acute pyelonephritis MAY_MANIFEST_AS striated nephrogram` (a standing potential). In observation space the radiologist writes "consistent with", which is an act: putting *these* observations together as *this* diagnosis. That is a different relationship, in a different space, between different objects. The report edge carries **no pointer** to the vocabulary relationship. The two structures are drawn so that the reader sees them correspond.

The sentence:

> Left kidney demonstrated striated nephrogram, mild hydronephrosis, and perinephric stranding, consistent with pyelonephritis. No associated abscess.

## Owner decisions taken in this session (copy these into 10 verbatim)

These are the owner's words. They go into `10-decision-record-2026-09-02.md` as new **OWNER** rows, numbered after the current last row in each section. Each row cites this plan as its source. Quotations must be copied exactly.

| Decision | Owner's words | Section |
|---|---|---|
| The deliverable is a drawing, a section in the worked examples, and a site page. | "I think we need a drawing, a new section in the worked examples, AND the site page." | D |
| Layout: report text at the top, faint arrows to the observations below, clear interactions within observation space, then clear interactions to the definitions at the bottom. | "I would have said report TEXT on top, with faint arrows to relevant Observations below, with clear interactions WITHIN Observation space and then clear interactions to the definitions at the bottom." | D |
| An Observation carries: what it is (the FindingClass or Diagnosis it points to); where it is (the anatomic location it points to); a compact table of data element to value pairs, each element a pointer; a quote of the report text it is drawn from; pointers to other Observations. | "Observation should have: What it is--that is, the FindingClass it points to; WHERE it is--what anatomic location it points to; A COMPACT table of data element -> value pairs (with pointers to the data elements); A quote of the snippet of report text it's drawn from; Pointers to relevant OTHER Observation objects" | S |
| Laterality: classes are scoped to the unsided organ; a specific observation is in the sided organ; the sided organ IS A the unsided organ, which satisfies the scope. Kidney, left kidney, and right kidney must all be present and related this way. | "Pyelonephritis, renal abscess, etc, all go in 'kidney, NOS'. A SPECIFIC OBSERVATION is obviously in a SPECIFIC kidney--'left kidney' in this case. Since 'left kidney' IS A 'kidney, NOS', it satisfies the location requirement. This is EXACTLY the kind of issue I hope this diagram can help clear up." and "We must include kidney, left kidney, and right kidney, and they must be related as I have said." | S |
| "Consistent with" is an observation-space relationship, distinct from the definition-space potential. | "'Consistent with' is radiologist-talk for 'I'm putting THESE findings together as THIS diagnosis.' It's NOT the same relationship that the abstract ideas of 'pyelonephritis' and 'striated nephrogram' have in DEFINITION space--it's a DIFFERENT relationship in Observation space." | S |
| The report edge carries no pointer to the vocabulary relationship it parallels. The correspondence should be visible from the structures. | "I don't think we need that, though I HOPE the structures in the two spaces might suggest that." | S |
| The observation points at the diagnosis the radiologist named, not a more specific one. | "What the radiologist SAYS is 'pyelonephritis'. It's not our job to make their assertion more specific than they make it themselves, in spite of how obvious it is." | C |
| Perinephric stranding is in the left perirenal space. | "Yes, perinephric stranding is in the LEFT perirenal space." | C |
| Severity is an element with standard values minimal, mild, moderate, severe. | "Definitely create a severity element with standard values 'minimal', 'mild', 'moderate', and 'severe'. We can argue about 'mild-to-moderate', etc., later." | S |
| The absent abscess relates to the diagnosis observation by ASSOCIATED_WITH, not a negated edge. | "I agree, but I think the edge would be 'ASSOCIATED_WITH'--doesn't need to be negated." | S |
| The example is JSON Lines ground truth and the picture is generated from it, so that several agents can render the same truth. | "Yes, let's make sure we have JSON lines so we agree on ground truth, and generate diagrams from a consistent ground truth. That way we can do the thing of having multiple agents take a crack at it." | D |
| All content values are hypothetical. | "Nah, no one thinks this is real yet--this is all understood as a hypothetical exercise to see how the framework works." | C |

Claude defaults in this plan, to be marked **CLAUDE DEFAULT** in 10: the edge name `SUPPORTS` for "consistent with"; the `confidence` field carrying the radiologist's phrase verbatim ("consistent with") rather than a mapped certainty value; `SUBTYPE_OF` reused as the is-a edge for anatomy; the report line shapes in §2 below; the picture's layout details beyond the owner's sentence.

## Coordination

- The Kimi agent is concurrently editing `tools/render_cards.py`, `tools/build_site.py`, `09-mat-and-tree.md`, and the two `diagrams/tree-*.svg`. **Do not edit those four until Phase 5.** Put the new renderer in its own file. Before Phase 5, run `git status` and read `.preview/briefs/tree-relationship-boxes.REPORT.md`; if it does not exist yet, stop at the end of Phase 4 and report.
- Everything runs from the repo root, `/home/talkasab/ACR-RSNA-CDEs`. Graph files are hand-edited JSONL followed by `python3 docs/next-gen-schema/tools/graph.py normalize`. `python3 docs/check_bundle.py` must end with 0 errors before you report done.
- Screenshots: `playwright-cli` cannot run here. Use a Node script that requires `/home/linuxbrew/.linuxbrew/lib/node_modules/@playwright/cli/node_modules/playwright` and launches `chromium.launch({chromiumSandbox:false})`. Write renders under `.preview/report-plane/` (gitignored). To view an SVG, open it via `file://` and screenshot with `fullPage: true`.
- RadLex lookups: `cd /home/talkasab/med-ontology-lookup && uv run --env-file=.env molu search "left perirenal space" -o RADLEX -f json`.

## Phase 1: the graph

Files: `docs/next-gen-schema/graph/core.jsonl` (anatomy, shared elements), `docs/next-gen-schema/graph/pyelonephritis.jsonl`.

- [x] **Anatomy is-a.** Add `{"edge":"SUBTYPE_OF","from":"RID29663","to":"RID205"}` and the same for `RID29662`. Widen the `SUBTYPE_OF` RelationshipType's `domain` string to include `AnatomicLocation` and add a sentence to its `definition`: sided anatomic locations are subtypes of the unsided location. Keep the existing `side` and `unsided` properties on the nodes; they are now redundant with the edge but harmless. Note the redundancy in the graph README.
- [x] **Perirenal space, sided.** Look up the RadLex ids for left and right perirenal space with molu. If RadLex has them, add both nodes with their RIDs, `side`, `unsided: "RID434"`, and `SUBTYPE_OF RID434` edges. If RadLex lacks one or both, add them with `STUB-left-perirenal-space` style ids per the README's stub rule and record the gap in `04-anatomy-gaps.md` and in 10 as content.
- [x] **Severity.** The graph has `HAS_ELEMENT` edges to `RDE2_000077` but the node comes from `examples/severity.element.json` through the spec converter. Edit that spec: values become minimal, mild, moderate, severe, ordered, ranks 1 to 4, ids `RDE2_000077.0` to `.3` reassigned in that order. Regenerate `diagrams/de-severity.svg` with `python3 docs/next-gen-schema/tools/render_neighborhood.py docs/next-gen-schema/examples/severity.element.json > docs/next-gen-schema/diagrams/de-severity.svg`. Check that nothing else in `graph/*.jsonl` or the docs cites `RDE2_000077.N` ids by grep.
- [x] `python3 docs/next-gen-schema/tools/graph.py normalize && python3 docs/next-gen-schema/tools/graph.py check` reports 0 errors.

## Phase 2: the ground truth

File: `docs/next-gen-schema/examples/pyelonephritis.report.jsonl`, rewritten. Line shapes, in this order:

```jsonl
{"report":"rep-1","text":"Left kidney demonstrated striated nephrogram, mild hydronephrosis, and perinephric stranding, consistent with pyelonephritis. No associated abscess."}
{"observation":"obs-1","subject":"RDE2_000802","location":"RID29663","values":{"RDE2_000001":"present"},"quote":"striated nephrogram","span":[25,44]}
{"observation":"obs-2","subject":"RDE2_000808","location":"RID29663","values":{"RDE2_000001":"present","RDE2_000077":"mild"},"quote":"mild hydronephrosis","span":[46,65]}
{"observation":"obs-3","subject":"RDE2_000803","location":"<left perirenal space id>","values":{"RDE2_000001":"present"},"quote":"perinephric stranding","span":[71,92]}
{"observation":"obs-4","subject":"RDE2_000800","location":"RID29663","values":{"RDE2_000001":"present"},"confidence":"consistent with","quote":"consistent with pyelonephritis","span":[94,124]}
{"observation":"obs-5","subject":"RDE2_000809","location":"RID29663","values":{"RDE2_000001":"absent"},"quote":"No associated abscess","span":[126,147]}
{"relation":"SUPPORTS","from":"obs-1","to":"obs-4","quote":"consistent with"}
{"relation":"SUPPORTS","from":"obs-2","to":"obs-4","quote":"consistent with"}
{"relation":"SUPPORTS","from":"obs-3","to":"obs-4","quote":"consistent with"}
{"relation":"ASSOCIATED_WITH","from":"obs-5","to":"obs-4","quote":"associated"}
```

Rules:

- `span` is `[start, end)` character offsets into the report text; compute them, do not trust the numbers above. `quote` must equal `text[start:end]`.
- No `expresses` field anywhere. Remove it from `examples/pleural-effusion.report.jsonl` too, and give that file a `report` line and quotes and spans if you can write a plausible two-sentence report for it; otherwise leave it with the pointer removed and add a `note` line saying it predates the text-anchored form.
- The subject of obs-4 is `pyelonephritis` (RDE2_000800), not acute. The renal enlargement and kidney-length observations of the old sample are dropped; they are not in the sentence.
- Old `INTERPRETATION_OF` and `REPRESENTS` relation lines are gone.

Document the line shapes in `03-draft-structures.md §5` (replace the `expresses` paragraph: the report edge does not cite the vocabulary relationship; the two planes correspond by structure, and the reader is expected to see it), listing the observation fields the owner specified and the two observation-space relationship types `SUPPORTS` and `ASSOCIATED_WITH`, marked as provisional names.

## Phase 3: the validator and the renderer

New file: `docs/next-gen-schema/tools/render_report.py`. Usage: `render_report.py examples/pyelonephritis.report.jsonl > diagrams/report-pyelonephritis.svg`. Import `load_graph` from `graph.py` and the `Cards` helpers, `txt`, `esc`, `wrap`, and the colour constants from `render_cards.py` (import only; do not edit that file).

**Validate before drawing**, and fail with a message on: a subject that is not a FindingClass or Diagnosis; a location that is not an AnatomicLocation; a value element not bound to the subject by `HAS_ELEMENT` (own bindings only, no inheritance, per 10 S3); a categorical value not in the element's value set; a location that does not satisfy the subject's scope, where "satisfies" means the location equals a `SCOPED_TO` target (own or inherited down `SUBTYPE_OF`, the 09 §4 rule) or reaches one by walking `SUBTYPE_OF` upward from the location; a quote that does not equal the span; a relation whose ends are not observations in the file.

**Draw**, deterministic SVG, width 1100 like the other pictures, same fonts and accent colours as `render_cards.py`:

1. **Band 1, the report text.** The sentence wrapped at the top, each observation's span underlined in its observation's colour with a small `obs-N` tag beneath it.
2. **Band 2, observation space.** One card per observation in reading order, left to right. Card face, top to bottom: `obs-N` and the subject's name with kind and id (pointer to the class); `⌂` location name and id (pointer to the location); the element table, one row per value, element name, id, value (pointer to the element); the quote in italics; `confidence` if present. Faint gray lines from each span in band 1 straight down to its card. Observation-space relations drawn as **labelled arcs above the cards**, in a band between the text and the cards, with the relation name on the arc; the three SUPPORTS arcs converge on obs-4, the ASSOCIATED_WITH arc goes from obs-5 to obs-4.
3. **Band 3, definition space.** Below the observations, a horizontal rule and the label DEFINITIONS. Three rows:
   - **Classes**: a mini-card for each subject, placed under its observation, plus `acute pyelonephritis` under `pyelonephritis` with a `SUBTYPE_OF` guide line, because the vocabulary relationships are stated on acute. The definition-space relationships among these cards, `MAY_MANIFEST_AS` from acute to the three findings, `OCCURS_WITH` to hydronephrosis if present, `MAY_CAUSE` to renal abscess, drawn as labelled arcs **below** the class cards, mirroring the observation arcs above. Typicality and specificity in gray on the arc label, the mat's edge-box style.
   - **Anatomy**, left half: mini-cards for kidney, left kidney, right kidney, perirenal space, left perirenal space, right perirenal space, laid out as two small trees with `SUBTYPE_OF` guide lines (sided under unsided). `SCOPED_TO` lines from each class card to kidney or perirenal space.
   - **Elements**, right half: mini-cards for presence and severity, with their value lists in small type. `HAS_ELEMENT` lines from each class card to its elements.
4. **Pointers** from observation cards into band 3: subject to class card (short, vertical); location to the sided anatomy card; each value row to its element. Route location and element pointers orthogonally through a gutter at the left edge (anatomy) and right edge (elements) of the picture, staggered a few pixels apart, so they do not cross the class row. Pointer colour is the target type's accent at low opacity. Where the location pointer lands on `left kidney` and the scope line lands on `kidney`, the picture is making the laterality point; make the is-a guide line between those two cards slightly heavier than the others.
5. No hover layer is required in the committed SVG. If cheap, add the same `:has()` hover detail the mat uses for the class cards.

Iterate with screenshots at least twice: legibility, no overlaps, arcs not colliding with the text band, gutters not crossing cards. Leave `.preview/report-plane/final.png`.

- [x] `tools/render_report.py`
- [x] `diagrams/report-pyelonephritis.svg`, committed output
- [x] `docs/check_bundle.py`: add the pair `"examples/pyelonephritis.report.jsonl": (tool_r, "diagrams/report-pyelonephritis.svg")` to `spec_map` with a `tool_r` for the new renderer, so the diagram is byte-checked.

## Phase 4: the documents

- [x] `08-worked-examples.md`: new section `## 4. One sentence, two planes` before "What the two examples share" (renumber the later sections and any cross-references to them). Embed the picture. Explain the five observations, the laterality satisfaction, and the two relationships, using the owner's framing from the decisions above. Every value is hypothetical; say so once.
- [x] `03-draft-structures.md §5`: as in Phase 2.
- [x] `10-decision-record-2026-09-02.md`: the OWNER rows and CLAUDE DEFAULT rows from the table above. Update the frontmatter `description` and add this session to `sources` (`https://claude.ai/code/session_01C8QzRRzsPNZWS85s6evk9J`).
- [x] `09-mat-and-tree.md`: **wait for Phase 5**; Kimi is editing it. Then add a short section `## 7. The report picture` before the tooling table, and a row in the tooling table.
- [x] `graph/README.md`: the anatomy is-a note and the new file row if any.
- [x] `04-anatomy-gaps.md`: only if the perirenal lookup found gaps.
- [x] `06-next-steps.md §3`: mark the kidney laterality item done by this example, and add the follow-ups: certainty vocabulary for `confidence`; the observation-space relationship type list; "mild-to-moderate" and other compound severities.
- [x] `log.md`: a 2026-09-03 entry for this work.
- [x] `index.md`: no change unless a new document was added.

## Phase 5: the site (after Kimi's report exists)

- [x] `tools/build_site.py`: an examples page `examples/pyelonephritis-report.html` that shows the picture and, below it, the JSON Lines file verbatim, with the intro sentence from the owner's layout decision. Link it from the examples index and from the pyelonephritis node page. Remove the old `REPORTS` mapping that pasted the report file under the mats, or keep it if it still reads well; say which.
- [x] `uv run docs/next-gen-schema/tools/build_site.py` succeeds; screenshot the new page.

## Done means

`python3 docs/check_bundle.py` ends with 0 errors; `git status` shows only intended files; `.preview/report-plane/final.png` postdates the last edit; and a report at `.preview/briefs/report-plane.REPORT.md` lists every file touched, the RadLex lookup result, every validator rule implemented, anything skipped, and a suggested commit message in the owner's format (one-line summary, three or four bullets for an outside reader). Then reply in the terminal with only the path of that report.
