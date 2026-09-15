# Plan: the part-solid pulmonary nodule with a solid component

**Written:** 2026-09-08 by Claude, from the bundle as it stands and the [viewer review](../../notes/viewer-review-2026-09-08.md) of the same day. **Status:** proposed; nothing below is done. **Executor:** to be assigned by the owner. **Owner approves each commit; do not commit.** Queue item 1 of [06 §4](../next-gen-schema/06-next-steps.md).

## Goal

Define the `solid component` class that the pulmonary nodule spec references but never defines, bind its size, and write a two-Observation report end to end, so that three things become visible in pictures a radiologist can argue with:

1. **The sub-finding pattern of [03 §5](../next-gen-schema/03-draft-structures.md).** One report sentence produces two Observations, the nodule and its solid component, each with its own size, joined by a report-level `HAS_COMPONENT` edge that points to no vocabulary relationship (10 S22).
2. **The subtype-versus-condition fork of the [25 August exchange](../../notes/review-exchange-2026-08-25-extract.md) §2**, built the owner's way (a subtype carries the component relation) with the other way written out beside it on the same example, so the owner and the reviewer can compare on one page instead of in the abstract.
3. **Scope satisfied by part-of, not only is-a.** The nodule is reported in the upper lobe of the right lung. A lobe is not a kind of lung; it is part of one. The report validator today walks only `SUBTYPE_OF` (10 S20); this example makes it walk part-of as well, which [01 §2.2](../next-gen-schema/01-what-the-vocabulary-must-express.md) already promised.

The sentence:

> There is a 14 mm part-solid nodule in the right upper lobe with a 6 mm solid component.

## What blocks it

Checked against [06 §3](../next-gen-schema/06-next-steps.md) (waiting on the owner):

- **07 §7 question 4, the conditionality fork.** This is the only §3 item that touches the example, and it does not block building it: the owner's counter-proposal is on record in the exchange ("When deciding between attribute and subtype, if the distinction would affect the relationships, then use a subtype") and was applied once already (acute and chronic pyelonephritis, [08 §2](../next-gen-schema/08-worked-examples.md)). It does block *closing* the question. The example is built to force that ruling, not to presume it.
- **The observation-space relationship type list (S24, S25).** `HAS_COMPONENT` joins the provisional list. Not blocking; the list is provisional by decision.
- **S13 is withdrawn (2026-09-09).** The owner ruled that `SUBTYPE_OF` propagates nothing and every node asserts its own scope and context; the mat shows no "inherited" language. Each new subtype therefore carries its own `SCOPED_TO` and context edges.
- Nothing else in §3 (S14, S15, S18, the certainty vocabulary, compound severity, the ten-exemplar sets) touches this item.

## Decisions to record in 10 before applying (proposed marks)

**Ruled 2026-09-09 (10 S30, OWNER):** four classes, composition part of the identity, no composition element on any of them, and the component of a part-solid nodule exists by definition while its description in a report is optional. That supersedes the proposed S30 and S32 rows below and the Phase 1 family list; Phase 1 gains `solid pulmonary nodule` (RID50151) and `ground-glass pulmonary nodule` (RID50153, RadLex "non-solid pulmonary nodule"), the `attenuation` element leaves the pulmonary nodule spec, and 03 §6.1's sample and the source-review note's "attenuation" wording are updated to "composition". **Ruled 2026-09-13 (10 S33, OWNER):** one `HAS_COMPONENT` relationship (inverse `COMPONENT_OF`) carrying a minimum and maximum count from the container's side; an optional component-of scope on the component class, checked by classification like anatomic scope. That supersedes the proposed S31 row below: `part-solid pulmonary nodule HAS_COMPONENT solid component` with count 1 to 1, and `solid component` carries component-of scope `part-solid pulmonary nodule`. No marker goes on the component class. The rest of this table still awaits rulings.

Copy these into `10-decision-record-2026-09-02.md`, numbered after the current last row of each section, each citing this plan. The marks are Claude's proposals for how to mark them; the owner may re-mark.

| # | Decision | Proposed mark and source |
|---|---|---|
| S30 | `part-solid pulmonary nodule` is a `SUBTYPE_OF pulmonary nodule` and carries the component relation; the parent class does not. | **OWNER-derived** from exchange §2: "define multiple finding classes for the family: pulmonary nodule with sub-finding classes solid pulmonary nodule, part-solid pulmonary nodule, and so on. HAS_COMPONENT is then required on the part-solid class and absent from the others." The fork (07 Q4) stays open; this applies the owner's stated side. |
| S31 | A definition-space relationship type `HAS_COMPONENT` (inverse `COMPONENT_OF`), FindingClass to FindingClass, compositional: the target is a constitutive sub-part of every instance of the source. `MAY_HAVE_COMPONENT` is kept for the genuinely optional case, as its definition already says, and is now unused. | **OWNER-derived** from the same exchange §2 passage and "a MAY_HAVE_COMPONENT relationship type does make sense, but only where the component is genuinely optional in all cases, with nothing gating it." The name being the same word as the report-plane relation is a **CLAUDE DEFAULT**: the two planes already have separate vocabularies (S21, S25). |
| S32 | `attenuation` stays bound on `pulmonary nodule` with its three values. The part-solid subtype does not bind it; its attenuation is entailed by class membership. Only the part-solid subtype is created now; solid and ground-glass subtypes wait until a relationship needs them. | **CLAUDE DEFAULT.** The alternative (three subtypes, attenuation removed) is written out in 08 for the owner. This is the memo's "the same fact lives in two places" objection made visible on purpose. |
| S33 | `solid component` binds `size (mean diameter)`, `margin`, and a new element `position within nodule` (central, eccentric). It does not bind `presence`: its existence is entailed by the parent class, and a `presence: absent` on it would be the nonsense assertion the reviewer warned about. | **CLAUDE DEFAULT** for the no-presence rule; the three attributes are content taken from the reviewer's viewer as a draft (C18). |
| S34 | `solid component` is `SCOPED_TO lung` (structure, required), like the nodule. | **CLAUDE DEFAULT.** |
| S35 | Anatomy gains `PART_OF` (inverse `HAS_PART`) edges: `upper lobe of right lung PART_OF right lung`. `right lung SUBTYPE_OF lung` follows S20 and S27. Scope is satisfied when walking any mix of `PART_OF` and `SUBTYPE_OF` upward from the Observation's location reaches a scope target. | **CLAUDE DEFAULT**, implementing 01 §2.2's containment walk; `PART_OF` chosen over a contained-by edge because the lobe case is the same in both hierarchies and the name matches RadLex and the reviewer's viewer (viewer review §5.3). The contained-by hierarchy is added when a case needs it. |
| S36 | A report file may carry one `{"context": [ids]}` line naming definition-space classes to draw that are not Observation subjects (the acute pyelonephritis card in the existing picture; the parent `pulmonary nodule` here). | **CLAUDE DEFAULT**, extending S28. It keeps the pyelonephritis picture byte-identical instead of deriving the extra card by a rule. |
| D34 | A quantitative value on an Observation card is drawn as number and unit; a quantitative element box in the definition plane shows quantity type, units, and range instead of a value list. | **CLAUDE DEFAULT.** |
| D35 | The mat's container order gains "has component" and "component of" immediately before "may have component" and "may be component of". The committed mat for this family is the part-solid nodule's. | **CLAUDE DEFAULT**, extending D24. |
| C18 | All content values: the sentence; 14 mm and 6 mm; the right upper lobe; the definitions of the subtype, the component, and `position within nodule`; the choice of `margin` and `position within nodule` for the component (from the viewer's draft); every code match. | **CLAUDE INVENTION**, illustrative and unreviewed, like C12 and C16. The codes themselves are looked up (below). |
| C19 | RadLex codes for the family, looked up with `molu` on 2026-09-08: `part-solid pulmonary nodule` RID50152; `solid pulmonary nodule` RID50151; `non-solid pulmonary nodule` RID50153; `solid component of part-solid pulmonary nodule` RID50154; `right lung` RID1302; `upper lobe of right lung` RID1303. RID50155 `average diameter` as a candidate exact match for size (mean diameter), replacing the close match to RID13432 `diameter`, **to be verified by the executor** before use. | Looked up; match choices **CLAUDE**. |
| C20 | `SUBTYPE_OF nodule` is removed from the pulmonary nodule spec: "nodules in general" is not a class (S5, S6). The `STUB-nodule` node disappears with it. | Applies **OWNER** S5 and S6; the removal itself is Claude's housekeeping. |

## Coordination

- Everything runs from the repository root. Graph files are hand-edited JSONL followed by `python3 docs/next-gen-schema/tools/graph.py normalize`. `python3 docs/check_bundle.py` must end with 0 errors before reporting done.
- The pulmonary nodule class itself stays in `examples/pulmonary-nodule.neighborhood.json` until queue item 3 migrates the six interim specs. Everything new goes in a graph file. The loader gives a graph-file node priority over a spec-converted node with the same id (`graph.py`, `prio=2` over `prio=1`), so defining `RDE2_000130` fully in the graph overrides the bare stub the spec converter emits; check the `NAME_IDS` entry in `spec_to_graph.py` still resolves the spec's reference and remove the spec's `related` entry for the component (it moves to the subtype) so no duplicate edge is stated.
- Screenshots: `playwright-cli` cannot run here; use the no-sandbox Node script in [`tools/README.md`](../next-gen-schema/tools/README.md). Write renders under `.preview/part-solid-nodule/` (gitignored). Leave `final-mat.png` and `final-report.png`.
- Code lookups: `cd /home/talkasab/med-ontology-lookup && uv run --env-file=.env molu search "<term>" -o RADLEX,SNOMEDCT -n 6 -f json`. Never write a code that was not returned by a lookup; never show a code without its preferred term.
- Do not edit `render_cards.py` beyond the container list, and do not change the committed pyelonephritis or effusion pictures unless a renderer change forces it; if it does, regenerate them and say so in the report.

## Phase 0: the record

- [ ] `10-decision-record-2026-09-02.md`: the rows above, with this plan in `sources`. Update the frontmatter `description`.
- [ ] `log.md`: a 2026-09-08 entry for the work, to be completed as phases land.

## Phase 1: the graph

Files: `graph/core.jsonl` (relationship types, anatomy, the new element), new `graph/pulmonary-nodule.jsonl` (the family), `examples/pulmonary-nodule.neighborhood.json` (two removals).

- [ ] **Relationship types** in `core.jsonl`: `HAS_COMPONENT` (inverse `COMPONENT_OF`, domain and range FindingClass, props `id`, `note`, definition per S31, formal name `has_part` is *not* claimed; note the distinction from anatomy part-of); `PART_OF` (inverse `HAS_PART`, domain and range AnatomicLocation, props none, definition: containment and functional part-of coincide for this edge; the contained-by hierarchy is not modeled yet). Amend the `MAY_HAVE_COMPONENT` definition to point at `HAS_COMPONENT` for the constitutive case.
- [ ] **Anatomy** in `core.jsonl`: `RID1302 right lung` (`side: right`, `unsided: RID1301`, `SUBTYPE_OF RID1301`); `RID1303 upper lobe of right lung` (`PART_OF RID1302`). Add `RID1301 lung` explicitly if only the spec converter currently supplies it. Confirm both lobes and both lungs exist in AnatomicLocations.org `body_parts.json`; if either is absent, record it in [04](../next-gen-schema/04-anatomy-gaps.md). The left lung and its lobes are not needed (D32 spirit: only what the report touches).
- [ ] **Element** in `core.jsonl`: `position within nodule`, id `RDE2_000133`, categorical, values `.0 central`, `.1 eccentric`, with definitions; look up a RadLex or SNOMED code and leave it unmapped with a note if none is exact.
- [ ] **Family** in `graph/pulmonary-nodule.jsonl`:
  - `RDE2_000132 part-solid pulmonary nodule`, FindingClass, `entity_type: finding`, definition ("A pulmonary nodule with both ground-glass and solid components"), `exactMatch RADLEX:RID50152`, `SUBTYPE_OF RDE2_000123`, `HAS_ELEMENT` presence `RDE2_000001`, size `RDE2_000014`, margin `RDE2_000031`. With its own `SCOPED_TO RID1301` (structure, required) and its own context edges (the same modality, region, subspecialty, sex, age, time course, and etiology concepts as the parent), since nothing propagates down `SUBTYPE_OF` (owner ruling of 2026-09-09; S13 withdrawn). The same for the solid and ground-glass subtypes.
  - `RDE2_000130 solid component`, FindingClass, `entity_type: finding`, full definition, `exactMatch RADLEX:RID50154`, `SCOPED_TO RID1301` (structure, required), `HAS_ELEMENT` size `RDE2_000014`, margin `RDE2_000031`, position `RDE2_000133`. Context edges: `SEEN_ON` CT only (RID10321); region, subspecialty, sex, age as for the nodule.
  - `HAS_COMPONENT` from `RDE2_000132` to `RDE2_000130`, id `RDE2_000901` (the id [03 §5](../next-gen-schema/03-draft-structures.md) already cites; confirm unused).
- [ ] **Spec edits** to `pulmonary-nodule.neighborhood.json`: remove the `nodule` and `solid component` entries from `related`. Consider (and record if done) changing the SNOMED CT 427359005 match from `exactMatch` to `closeMatch` with a note that it is narrower, per viewer review §3.9. Regenerate `diagrams/fc-neighborhood.svg`.
- [ ] `graph.py normalize && graph.py check`: 0 errors, no `STUB-nodule` in the dump.

## Phase 2: the ground truth

New file `examples/part-solid-nodule.report.jsonl`. Compute every span; `quote` must equal `text[start:end]`.

```jsonl
{"report":"rep-2","text":"There is a 14 mm part-solid nodule in the right upper lobe with a 6 mm solid component."}
{"context":["RDE2_000123"]}
{"observation":"obs-1","subject":"RDE2_000132","location":"RID1303","values":{"RDE2_000001":"present","RDE2_000014":{"value":14,"unit":"mm"}},"quote":"14 mm part-solid nodule in the right upper lobe","span":[…]}
{"observation":"obs-2","subject":"RDE2_000130","location":"RID1303","values":{"RDE2_000014":{"value":6,"unit":"mm"}},"quote":"6 mm solid component","span":[…]}
{"relation":"HAS_COMPONENT","from":"obs-1","to":"obs-2","quote":"with a"}
```

Rules: the component's Observation is located where the nodule is, in the lobe; it carries no presence (S33); the nodule Observation points at the subtype, because the radiologist said "part-solid" (C14's principle, the assertion is as specific as the radiologist made it, no more).

- [ ] Document the `context` line and the quantitative value shape in [03 §5](../next-gen-schema/03-draft-structures.md); update its sub-finding sample so the vocabulary line reads `HAS_COMPONENT` from `RDE2_000132` and the report lines match this file.

## Phase 3: the validator and the renderers

`tools/render_report.py`, generalized; the pyelonephritis picture must still render byte-identical (the checker enforces it) unless a change is deliberate and reported.

- [ ] **Validation**: a quantitative value must be `{"value": number, "unit": string}` with the unit in the element's `quantity.units` and the value within `min` and `max`; a location satisfies scope when a walk over `SUBTYPE_OF` and `PART_OF` upward reaches a scope target asserted on the subject itself (`Cards.scope` now returns own edges only); a `context` id must be a FindingClass, Diagnosis, or Grouping; a relation type is any uppercase name (the list is provisional), drawn with a style table keyed by name and a neutral fallback.
- [ ] **Observation cards**: format quantitative values as `14 mm`.
- [ ] **Definition plane**: draw the subject classes plus the `context` classes; draw every family edge among the drawn classes (`SUBTYPE_OF` as a guide line with its label, `HAS_COMPONENT`, `MAY_MANIFEST_AS`, `OCCURS_WITH`, `MAY_CAUSE`) with typicality and specificity in gray where present; remove the hard-coded acute pyelonephritis and pyelonephritis ids. Element boxes for every element that appears in a value: categorical boxes list values as now, quantitative boxes show type, units, and range (D34). Anatomy trees may be more than one level deep and may mix `PART_OF` and `SUBTYPE_OF` guide lines; label the edge kind on the line; make the path from the Observation's location to the scope target the heavier one, as the left kidney is now.
- [ ] `tools/render_cards.py`: only the container list (D35).
- [ ] `examples/part-solid-pulmonary-nodule.mat.json` (`{"kind":"mat","hub":"RDE2_000132"}`); `diagrams/mat-part-solid-pulmonary-nodule.svg`; `diagrams/report-part-solid-nodule.svg`.
- [ ] `docs/check_bundle.py`: add both pairs to `spec_map`.
- [ ] `tools/build_site.py`: the report page is generated from a list of report files rather than the one hard-coded pyelonephritis path; both report pages link from the examples index and from their subject node pages.
- [ ] Iterate with screenshots at least twice; the report picture must show, without a caption, that the two Observations share a location, that the location reaches `lung` by part-of then is-a, and that `pulmonary nodule` (context) carries no component edge while its subtype does.

## Phase 4: the documents

- [ ] `08-worked-examples.md`: new `## 4. The part-solid nodule and its component` before "One report, two planes" (renumber the later sections and their cross-references, including the `build_site.py` anchor to 08 §4). Content: the mat and the report picture embedded; what the example exercises; the three-way choice on attenuation (S32) written out as JSONL so the owner can compare: (a) as built, (b) three subtypes with attenuation removed, (c) the reviewer's condition on the edge from the memo, on this very edge; which of the memo's objections each one meets; the viewer's value-to-RadLex-subtype mapping as the attribute form of the same fork (viewer review §3.1); a provenance paragraph listing C18 to C20.
- [ ] `07-relationship-family.md`: `HAS_COMPONENT` row in §1 beside `MAY_HAVE_COMPONENT`, with the constitutive-versus-optional distinction; a sentence under §7 question 4 saying the example now exists and where.
- [ ] `03-draft-structures.md`: §2 edge table gains `HAS_COMPONENT` and `PART_OF`; §5 per Phase 2; §9's anatomy note mentions `PART_OF`.
- [ ] `09-mat-and-tree.md`: §2.4 container list; §7 gains the `context` line, quantitative rendering, and the mixed anatomy walk.
- [ ] `01-what-the-vocabulary-must-express.md` §2.2: one sentence that the report validator now walks part-of as promised.
- [ ] `graph/README.md`: the new file in the table, `RDE2_000132` and `000133` in the id block table, `PART_OF` beside the sided-anatomy note.
- [ ] `tools/README.md`: the two new render commands.
- [ ] `04-anatomy-gaps.md`: only if Phase 1 found a gap.
- [ ] `06-next-steps.md`: §4 item 1 marked done with pointers; §3 adds "rule on S30 to S36" under the structural defaults and notes that 07 Q4 now has a worked comparison to rule on; §5 drops the "solid component referenced but not defined" state.
- [ ] `log.md`: complete the 2026-09-08 entry.
- [ ] `index.md`: no change unless a document was added.

## Phase 5: the site and the report

- [ ] `uv run docs/next-gen-schema/tools/build_site.py` succeeds; screenshot the new mat page (hover on the solid component card showing) and the new report page.
- [ ] `.preview/briefs/part-solid-nodule.REPORT.md`: every file touched; every lookup made and what it returned; every validator rule added; which committed pictures changed and why; anything skipped; a suggested commit message in the owner's format (one-line summary, three or four bullets for an outside reader). Reply in the terminal with only the path of that report.

## Done means

`python3 docs/check_bundle.py` ends with 0 errors and no new warnings; `graph.py check` reports 0 errors; `git status` shows only intended files; the two final screenshots postdate the last edit; every new decision is in 10 with a mark; every new code has its preferred term beside it.

## Out of scope, deliberately

Lung-RADS and Fleischner as real classes with their value sets (the viewer offers a draft; queue item 5 territory); solid and ground-glass subtypes (S32); the left lung; the mat and tree changes the viewer review proposes (§5 items 2, 10); element-level scope and modality on bindings (viewer review §4); migrating the pulmonary nodule spec itself (queue item 3).
