# Structural meeting agenda: preparation and publication

Status: complete — owner-requested document corrections integrated and the single agenda page republished and verified on 15 September 2026.

## 15 September revision plan

1. Record this revision scope before editing the discussion documents.
2. Record the owner's tissue-type and structure-type scope families, with hierarchy connections still unresolved. Keep the assistant's alternative connection models exploratory.
3. Correct the agenda and comparison: Measurement nodes, sided Observation locations, and presence=absent are existing working-model answers, not fresh structural questions. Move OWL mapping, export metadata, and verification into later implementation work; retain genuinely unresolved anatomy connections and explicit proposals.
4. Update the glossary, anatomy notes/gap log, decision record, handoff, relevant metadata/index descriptions, and bundle log. Record ordinary-chat questions as the communication preference; do not create queued question widgets.
5. Preserve the published HTML's layout and diagrams, update its content and revision date, check the bundle/denylist/anchors and responsive rendering, and compare the existing remote page with the original published hash before replacing it.
6. Upload only the revised agenda to its existing exact key, verify anonymous retrieval and matching hashes, and mark this revision complete here. Preserve the original publication record below as history. No commits, demo changes, schema implementation, or review of the held branch.

## Authorized scope

The owner requests a discussion agenda, in this order: anatomy axis; apparent active conflicts; improvement proposals; remaining open questions. The owner explicitly requests publication in `oidm-public/cde-next-gen` and a nice HTML format with possible diagram changes. This authorizes one new, sanitized agenda page, not a deployment of the working tree or changes to either demo. The earlier committed-site-only publication brief governs those demo deployments, not this explicitly requested new document. No commit is authorized.

## Plan

1. Record scope and this plan before creating the agenda.
2. Synthesize existing anatomy summaries, the comparison, and current owner positions. Label snapshot evidence, proposals, and open questions distinctly; do not inspect the held implementation anew.
3. Create one self-contained, responsive, printable HTML agenda with inline explanatory diagrams. No external assets, application code, private correspondence, personal names, or local-only links in the published page. Existing diagrams remain unchanged.
4. Check content, denylist, links, and desktop/mobile rendering. Update this plan with the final artifact and checks.
5. Upload only `docs/plans/2026-09-14-structural-meeting-agenda.html` to `t3://oidm-public/cde-next-gen/2026-09-14-structural-meeting-agenda.html`. Verify anonymous retrieval and exact content; record the resulting URL and outcome here. Do not change bucket permissions, overwrite demos, or upload this plan.

## Document design

Read-mode meeting handout: restrained editorial typography, numbered sections in the requested order, short discussion prompts, explicit intended outcomes, and print styling. Diagrams illustrate the anatomy substrate, the difference between taxonomy and bindings, and proposed component-of scope. They are discussion sketches, not approved schema changes.

## Sources

- `docs/next-gen-schema/11-anatomy-axis.md`
- `docs/next-gen-schema/04-anatomy-gaps.md`
- `docs/next-gen-schema/12-alpha-structural-comparison.md`
- `docs/next-gen-schema/10-decision-record-2026-09-02.md`, especially S37–S49
- `docs/plans/2026-09-14-structural-decision-agenda.md`

No changes to the domain model or public schema release are part of this task; no schema changelog entry is needed. This plan records the document's final publication state.

## Original publication, 14 September

The record below describes the original artifact; the 15 September revision result at the end is the current publication state.

- Source: `docs/plans/2026-09-14-structural-meeting-agenda.html`, explicitly authorized new discussion content, not a committed-site build. Repository HEAD during preparation: `fa2fb7e032f0d5e4715c29833cb559e5f7d45ae1`; the agenda is uncommitted.
- Published file count: **1**, 25,200 bytes; three inline diagrams, no scripts or external assets. Existing demo files and diagrams are unchanged.
- Public URL: https://oidm-public.t3.storage.dev/cde-next-gen/2026-09-14-structural-meeting-agenda.html
- Denylist: zero matches; no email addresses, private/local paths, or personal names in the artifact.
- Browser checks: desktop 1440px and mobile 390px; no document overflow, all internal anchors resolve, all four sections appear in the requested order. Wide diagrams have keyboard-accessible horizontal scrolling on mobile. Print styling hides navigation; a seven-page PDF was generated locally, but pagination was not independently visually reviewed. No PDF or screenshots were uploaded.
- Independent final review: **ship**, no material issue requiring revision. The design detector's two warnings were reviewed: compact heading/connector leading does not govern body text, and “next-generation” is the project terminology.
- Bundle check: 48 documents, 11 diagrams, zero errors or warnings. Whitespace check passes. Documentation reviewed; only this plan records publication, with no schema changelog change warranted.
- Upload used the exact command below. The target was absent before upload; bucket settings and other objects were not changed.

```sh
tigris cp docs/plans/2026-09-14-structural-meeting-agenda.html t3://oidm-public/cde-next-gen/2026-09-14-structural-meeting-agenda.html --cache-control 'public, max-age=300'
```

Anonymous retrieval returned HTTP 200 and `Content-Type: text/html`. Downloaded content exactly matches the source SHA-256: `6378b83af52d0e63a25db3ad2877746758db4646426ef5431fcaaca200415c84`. The public page was also opened in a fresh browser context and its title, four section headings, and three diagrams confirmed. No commit was made.

## Revision completed, 15 September

- Integrated scope families and corrected question status as S50–S51 in the decision record, glossary, anatomy summary/gap log, requirements, draft structures, structural comparison, and working agenda. Connection models remain exploratory; newly named tissue candidates are not asserted to be missing from the source data.
- Recorded ordinary-chat questions in the handoff and working agenda only. This workflow guidance was not added to the public handout or domain glossary.
- Updated dated source metadata, index descriptions, and bundle log. No schema artifacts or existing demo files changed; no commit was made.
- Preserved the page's CSS and both SVG diagrams byte-for-byte. Updated the anatomy dependency sketch's text to include tissue scope. Three inline diagrams remain, with no scripts or external assets.
- Checks: 48 bundle documents and 11 diagrams, zero errors/warnings; clean whitespace; zero denylist matches or private references. Browser DOM checks at 1440px and 390px confirm no document-wide overflow, working anchors, correct section order, the new families, and withdrawal of the original seven questions. Print styling hides navigation. This content-only revision did not include a new screenshot or PDF-pagination review.
- Existing public content was downloaded before replacement and matched the original hash above. The recovery copy is `/tmp/cde-agenda-update-xdP8ST/previous-public-agenda.html`; it was not uploaded.
- Republished **one file, 26,142 bytes**, at the same URL: https://oidm-public.t3.storage.dev/cde-next-gen/2026-09-14-structural-meeting-agenda.html

```sh
tigris cp docs/plans/2026-09-14-structural-meeting-agenda.html t3://oidm-public/cde-next-gen/2026-09-14-structural-meeting-agenda.html --cache-control 'public, max-age=300' --yes
```

Anonymous retrieval returned HTTP 200 and `Content-Type: text/html`; the downloaded and source SHA-256 values both equal `cc5601b60070567e9efe66cec2dd7469392f401b142baeb618e16ab952914bad`. The public page was opened in an unauthenticated browser and its 15 September revision marker, scope families, corrected question section, and four section headings confirmed. Only this exact agenda object was replaced; bucket settings and other objects were unchanged.
