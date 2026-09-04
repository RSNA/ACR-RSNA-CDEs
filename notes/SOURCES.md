---
type: Reference
title: Notes — Provenance
description: Provenance for the notes directory — upstream URLs for the fetched OIFM copies and extraction records for the sanitized committee and working-group material.
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

## Test material

| File | Source | What it is |
|---|---|---|
| `hood-taxonomies-profile-2026-09-01.md` | https://github.com/openimagingdata/findingmodels/tree/main/lists, exported 2026-08-15, local checkout at `../findingmodels/lists` | A measured profile of Michael Hood's six per-modality finding taxonomies, used as test material for the vocabulary; the lists themselves are not copied here |

## Sanitized extracts of committee material

The raw committee material — a slide deck, meeting minutes, meeting notes, and an initial written proposal — was not written for publication and is kept out of the repository (in the gitignored `raw_sources/` directory). What is committed instead are extracts preserving the substantive technical content with participants' identifying details removed.

| File | Extracted from | What it is |
|---|---|---|
| `proposed-schema-changes-deck-extract.md` | `RSNA-ACR_CDE_Committee_schema_changes_proposed_2026-06-12.pdf` | Slide deck presented at the SIIM committee meeting, 12 June 2026 |
| `siim-meeting-extract.md` | `siim_meeting_minutes.txt` | Minutes of that meeting, with action items |
| `committee-notes-extract.md` | `committee_meeting_notes.txt` | Later committee notes; source of the Finding Class / Data Element / Value terminology and the draft reusable-element list |
| `schema-recommendations-part2.md` | `first_ideas.txt` | "CDE schema recommendations — Part II"; the initial written proposal |

## Working-group material, August 2026

Working sessions that followed the analysis bundle being pushed to `next-gen-2026` on 21 August 2026. The call summary and the email thread carry contact details, affiliations, and scheduling and were not written for publication, so they are kept in `raw_sources/` and committed only as extracts. The memo attached to the thread needed no sanitization and is reproduced verbatim.

| File | Extracted from | What it is |
|---|---|---|
| `working-group-call-2026-08-20-extract.md` | `working_group_call_2026-08-20.txt` | Automatically generated summary of the 20 August 2026 call recording. Not reviewed minutes; treat the wording as approximate |
| `review-exchange-2026-08-25-extract.md` | `schema_exchange_2026-08-25.txt` | Email thread, 21 to 26 August 2026. Five structural questions on the bundle, with the answers given |
| `conditional-relationships-memo.md` | `conditional_relationships_memo.md` | Verbatim copy of the memo attached to the closing message of that thread, arguing for a condition on the edge over subtype classes |

The appendix to the exchange extract records a verification of the two candidate Sets it names (RDES332, RDES329) against the live RadElement API on 31 August 2026, including an identifier correction to the memo.

## Standards extracts

| File | Upstream |
|---|---|
| `source-review-2026-08-20.md` | Radiopaedia, Radiology Assistant, and Wikipedia articles on pulmonary and thyroid nodules, Lung-RADS, Fleischner, and ACR TI-RADS; URLs in the file's frontmatter |
| `ihe-idr-extract.md` | IHE RAD IDR Phase II, Rev. 1.2 public-comment draft (2026-03-04): https://www.ihe.net/uploadedFiles/Documents/Radiology/IHE_RAD_Suppl_IDR_PhII_Rev1-2_PC_2026-03-04.pdf — read directly, 2026-08-21 |

## Ontology background research, September 2026

[`ontology-background-research-2026-09-04.md`](ontology-background-research-2026-09-04.md) synthesizes a requested GPT-5.6 Sol web survey and independent review of the branch. Primary sources and proposed follow-ups are cited in the note; it records research and recommendations, not approved vocabulary changes.

## Not retained

A private email thread reviewing the OIFM material was distilled into [`docs/next-gen-schema/02-review-questions.md`](../docs/next-gen-schema/02-review-questions.md) and not committed, as it contained personal contact details and was not written for publication. The August 2026 thread is handled the same way, distilled into [`review-exchange-2026-08-25-extract.md`](review-exchange-2026-08-25-extract.md).

`raw_sources/denylist.txt` holds the participant names the leak sweep in [`docs/check_bundle.py`](../docs/check_bundle.py) checks the committed documents against. It is gitignored along with the rest of `raw_sources/`, so a fresh clone will report the name sweep as skipped until it is recreated.
