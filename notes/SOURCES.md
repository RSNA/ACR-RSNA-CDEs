---
type: Reference
title: Notes — Provenance
description: Provenance for the notes directory — upstream URLs for the fetched OIFM copies and extraction records for the sanitized committee material.
tags: [provenance]
status: stable
---

# Notes — provenance

Working reference material for the next-generation schema effort. Analysis lives in [`docs/next-gen-schema/`](../docs/next-gen-schema/); this directory holds the public reference material it draws on.

## Fetched copies of external documents

Retrieved 2026-07-29. These are verbatim copies apart from a locally prepended OKF frontmatter block — edit the upstream source, not these.

| File | Upstream |
|---|---|
| `oifm-overview.md` | https://github.com/openimagingdata/findingmodels/blob/main/prompts/overview.md |
| `oifm-schema-v2-draft.md` | https://gist.github.com/talkasab/8648a8887e4ee6ce381375485bc280c7 |
| `oifm-metadata-fields.md` | https://gist.github.com/talkasab/2d366555a8c371d8f2e2316f9d39d0e0 |

All three were circulated together as the starting material for the schema review (see [`docs/next-gen-schema/02-review-questions.md`](../docs/next-gen-schema/02-review-questions.md)), with the caveat from their author that they are "AI-organized distilled notes from hours of detailed interactions," intended to be further distilled into prompts rather than read as specifications.

## Sanitized extracts of committee material

The raw committee material — a slide deck, meeting minutes, meeting notes, and an initial written proposal — was not written for publication and is kept out of the repository (in the gitignored `raw_sources/` directory). What is committed instead are extracts preserving the substantive technical content with participants' identifying details removed.

| File | Extracted from | What it is |
|---|---|---|
| `proposed-schema-changes-deck-extract.md` | `RSNA-ACR_CDE_Committee_schema_changes_proposed_2026-06-12.pdf` | Slide deck presented at the SIIM committee meeting, 12 June 2026 |
| `siim-meeting-extract.md` | `siim_meeting_minutes.txt` | Minutes of that meeting, with action items |
| `committee-notes-extract.md` | `committee_meeting_notes.txt` | Later committee notes; source of the Finding Class / Data Element / Value terminology and the draft reusable-element list |
| `schema-recommendations-part2.md` | `first_ideas.txt` | "CDE schema recommendations — Part II"; the initial written proposal |

## Standards extracts

| File | Upstream |
|---|---|
| `source-review-2026-08-20.md` | Radiopaedia, Radiology Assistant, and Wikipedia articles on pulmonary and thyroid nodules, Lung-RADS, Fleischner, and ACR TI-RADS; URLs in the file's frontmatter |
| `ihe-idr-extract.md` | IHE RAD IDR Phase II, Rev. 1.2 public-comment draft (2026-03-04): https://www.ihe.net/uploadedFiles/Documents/Radiology/IHE_RAD_Suppl_IDR_PhII_Rev1-2_PC_2026-03-04.pdf — read directly, 2026-08-21 |

## Not retained

A private email thread reviewing the OIFM material was distilled into [`docs/next-gen-schema/02-review-questions.md`](../docs/next-gen-schema/02-review-questions.md) and not committed, as it contained personal contact details and was not written for publication.
