---
type: Gap Log
title: Anatomic Locations Gaps and Node Requests
description: Specific gaps found in the anatomic locations data during analysis for the CDE schema redesign, and the running list of specific node requests to carry to the RadLex anatomy track, recorded so the main documents do not go stale as they close.
tags: [next-gen-schema, anatomy, radlex, gaps, node-requests]
status: draft
generated: { by: ["human:talkasab", "claude-code/claude-fable-5.1", "codex/gpt-6"], at: 2026-09-15 }
sources:
  - id: scope-discussion
    resource: /docs/plans/2026-09-14-structural-decision-agenda.md
    title: Tissue-type and structure-type scope families to develop, 15 September 2026, S50
  - id: data
    resource: "https://raw.githubusercontent.com/openimagingdata/findingmodel/854d1f55d3ed039c455fe8eaa9a2a2983dcefc32/notebooks/data/anatomic_locations_noembed.json"
    title: The anatomic locations data behind the published anatomic-locations package, pinned to the commit of 2026-03-02; checked 2026-09-13 and 2026-09-14
    author: "human:talkasab"
  - id: earlier
    resource: "https://raw.githubusercontent.com/talkasab/anatomiclocations.org/main/data/body_parts.json"
    title: AnatomicLocations.org body_parts.json, release 1.0.0-rc.1, the earlier file analyzed 2026-07-28 and 2026-08-19
    author: "human:talkasab"
  - id: axis
    resource: /docs/next-gen-schema/11-anatomy-axis.md
    title: The current-state summary of the anatomy axis
---

# Anatomic Locations Gaps and Node Requests

Gaps found in the anatomic locations data while checking whether the anatomy substrate can express what the CDE vocabulary needs ([11](./11-anatomy-axis.md)). The data is an overlay on RadLex and the basis of the RadLex anatomy axis going forward (decision record S37), so entries here are expected to close upstream; the date each was checked is recorded. The earlier entries were checked against AnatomicLocations.org `body_parts.json` 1.0.0-rc.1; from 2026-09-13 the reference is the pinned anatomic locations file of the `anatomic-locations` package (2,926 nodes).

## Gaps

| Gap | Checked | Status |
|---|---|---|
| No is-a / type relation over locations | 2026-09-13 | **Open; the major shortcoming.** A first layer can be derived from RadLex 4.3's own is-a hierarchy, which covers all 1,910 plain-id nodes (to-do item 11) |
| Structure-type nodes absent: `tendon`, `muscle`, `artery`, `ligament`, `lymph node`, and the rest | 2026-09-13 | Open. RadLex has the concepts (artery RID478, vein RID1008, tendon RID6067, muscle organ RID13196, bone organ RID13197, joint RID6122, nerve RID13189, lymph node RID13296, ligament organ RID6071, cartilage organ RID28456, anatomical space RID13217); the package defines a structure-type field but the data leaves it empty |
| `pleural space` absent | 2026-09-13 | **Closed**: present as RID1363 with sided forms `RID1363_RID5824` and `RID1363_RID5825` |
| `pericardial space` / `pericardial sac` absent (only `pericardium`) | 2026-09-14 | Open |
| `subarachnoid space` absent | 2026-09-14 | Open |
| `lung parenchyma` absent | 2026-09-14 | Open; raised by the reviewer on 8 September. RadLex has only the generic `parenchyma` (RID5978) |
| `perirenal space` (RID434) and its sided forms (RID32986, RID32987) absent | 2026-09-14 | Open; the pyelonephritis example takes them from RadLex directly |
| Compound ids for sided variants RadLex lacks (1,016 nodes, such as `RID1363_RID5825`) | 2026-09-14 | Expected to close when the RadLex track mints real ids (S37) |
| External-code coverage is uneven | 2026-09-14 | Open. SNOMED CT on 1,782 of 2,926; 608 nodes carry no codes at all |
| `lung` is contained by `pleural space` | 2026-09-14 | Noted; anatomically odd, and any check that walks containment from a lung location will pass through it |

## Scope-family work identified 15 September (S50)

Develop tissue-type scope (pulmonary parenchyma, hepatic parenchyma, subcutaneous fat) alongside structure-type scope (solid organs, vessels with artery/vein subtypes, muscles, tendons, ligaments). The structural gap is an agreed way to connect these specifiers to the anatomic location hierarchy; see [11 §5](11-anatomy-axis.md#5-anatomy-scope-specifiers-two-families-s50).

This is a discussion requirement, not a new data audit. Coverage of the newly named candidates has not been checked in this pass: do not label hepatic parenchyma, subcutaneous fat, or every candidate structure type as absent. Add specific node requests when the gap is established; keep the existing checked requests below intact. The assistant's proposed connection alternatives remain exploratory.

## Node requests

The running list of specific "we need this node" changes, kept as the owner asked on 13 September, to be carried to the RadLex anatomy track regardless of the wider discussion. Add to it as examples are built.

| Request | Needed by | Raised |
|---|---|---|
| `lung parenchyma`, contained by and part of `lung` | consolidation, ground-glass opacity (the reviewer's classes) | 2026-09-08, reviewer |
| `perirenal space` with left and right forms | the pyelonephritis example | 2026-09-14 |
| `pericardial space` | pericardial effusion, a likely early example | 2026-07-28 |
| `subarachnoid space` | subarachnoid hemorrhage | 2026-07-28 |
| Real RadLex ids for the compound sided variants | every sided Observation; S12 | 2026-09-13 |
| An is-a relation and structure-type nodes | scope of the form "applies to tendons", "muscle, not otherwise specified" | 2026-08-19, restated 2026-09-13 as the top priority |

## Notes

**Structure types.** The node schema is `_id`, `description`, `region`, `containedByRef`, `partOfRef`, `hasPartsRefs`, `containsRefs`, `leftRef`, `rightRef`, `unsidedRef`, `codes`, `snomedId`, `synonyms`, `definition`, `sexSpecific`: no type relation. Specific structures are organised by where they sit, not what they are. Until an is-a relation lands, scope guidance of the form "applies to tendons" ([01 §2](./01-what-the-vocabulary-must-express.md)) cannot be stated against the data; the derived overlay of to-do item 11 is the interim.

**Potential spaces.** `pleural space` is now first-class with sided forms; `peritoneal cavity` and `retroperitoneum` are present; pericardial and subarachnoid spaces are not.
