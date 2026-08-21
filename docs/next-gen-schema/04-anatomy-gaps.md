---
type: Gap Log
title: AnatomicLocations.org Gaps
description: Specific gaps found in the AnatomicLocations.org data during analysis for the CDE schema redesign, recorded so the main documents do not go stale as they close.
tags: [next-gen-schema, anatomy, radlex, gaps]
status: draft
generated: { by: ["human:talkasab", "claude-code/claude-fable-5"], at: 2026-08-19 }
sources:
  - id: anatomiclocations
    resource: "https://raw.githubusercontent.com/talkasab/anatomiclocations.org/main/data/body_parts.json"
    title: AnatomicLocations.org body_parts.json, release 1.0.0-rc.1 — analyzed 2026-07-28 and 2026-08-19
    author: "human:talkasab"
---

# AnatomicLocations.org Gaps

Gaps found in `body_parts.json` release `1.0.0-rc.1` while checking whether the anatomy substrate can express what the CDE vocabulary needs ([00 §2.6](./00-current-understanding.md)). AnatomicLocations.org is becoming a collection within RadLex and is being actively extended, so entries here are expected to close; the date each was checked is recorded.

| Gap | Checked | Status |
|---|---|---|
| No is-a / type relation over locations | 2026-08-19 | Being added upstream |
| Structure-type nodes absent: `tendon`, `muscle`, `artery`, `ligament`, `lymph node` | 2026-08-19 | RadLex nodes being incorporated upstream |
| `pleural space` absent (only `pleura`, the membrane) | 2026-07-28 | Open |
| `pericardial space` / `pericardial sac` absent (only `pericardium`) | 2026-07-28 | Open |
| `subarachnoid space` absent entirely | 2026-07-28 | Open |

| External-code coverage is uneven | 2026-08-20 | Open — SNOMED CT on 1,732/2,890 nodes (60%) is strong; UMLS (578) and MeSH (232) are sparse; **608 nodes carry no codes at all** |

## Notes

**Structure types.** The node schema is `radlexId`, `description`, `containedById`, `partOfId`, `codes`, `leftId`/`rightId`/`unsidedId`, `synonyms`, `sexSpecific` — no type relation. Specific structures exist and are organised by where they sit, not what they are (`quadriceps tendon ⊂ knee joint`; `inguinal lymph node ⊂ hip`; `adrenal artery ⊂ retroperitoneum`). Roughly 1,110 of 2,890 nodes match one of the five type names above by string. Until the is-a relation lands, scope guidance of the form "applies to tendons" ([01 §2](./01-what-the-vocabulary-must-express.md)) cannot be stated against the data.

**Potential spaces.** Spaces are partially first-class — `peritoneal cavity` (RID397), `retroperitoneum`, and 63 cavity/compartment/fossa terms are present — but the three above are among the most frequently needed locations in radiology reporting and are not. Searched labels and synonyms.
