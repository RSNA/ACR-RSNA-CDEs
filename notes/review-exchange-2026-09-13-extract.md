---
type: Review Record
title: Anatomy Exchange, 13 September 2026 — Extract
description: Sanitized extract of the 13 September 2026 email exchange on the anatomy axis, in which the reviewer announced a refactor pointing her anatomy at RadLex directly and the owner asked that the anatomic locations file be treated as an overlay on RadLex and the basis of the RadLex anatomy axis going forward, with a running list of specific node requests.
tags: [committee, review, next-gen-schema, anatomy, radlex, anatomic-locations]
status: stable
generated: { by: "claude-code/claude-fable-5.1", at: 2026-09-14 }
sources:
  - id: thread
    resource: raw_sources/ (email thread of 13 September 2026; internal, pasted by the owner into the working session)
    title: Email thread of 13 September 2026, five messages
  - id: prior
    resource: /notes/review-exchange-2026-09-08-extract.md
    title: The 8 September exchange this one continues (its §4 raised the RadLex anatomy question)
  - id: axis
    resource: /docs/next-gen-schema/11-anatomy-axis.md
    title: The current-state summary of the anatomy axis this exchange feeds
sanitization: Participants other than the repo owner (Tarik Alkasab) are referred to by role. Greetings and sign-offs removed. Direct quotations are verbatim.
---

# Anatomy Exchange, 13 September 2026

**Status:** Record of an exchange. One topic; agreement reached; a working session owed.
**Participants:** Tarik Alkasab and the external reviewer drafting the model.

## 1. The reviewer's refactor

The reviewer reported a major refactor of her anatomy implementation. She had, by mistake, been working from a RadLex CSV import that flattened relationships while believing she was working from the OWL file, and the errors compounded. Her anatomy now "is pointing directly at Radlex and using its predicates correctly with no ontology reproduction". She planned further tests and safeguards and a merge the following day, and warned that the refactor would make much of her then-current code moot, so that no one should invest time reviewing it.

**Bearing.** The branch checked out for review on 13 September (to-do item 10) is the pre-refactor state; wait for the merge before reviewing.

## 2. The owner's request: the anatomic locations file

The owner asked her to "keep within/use that JSON file of anatomy nodes I referred you to", the anatomic locations data behind the published `anatomic-locations` package (decision record S37).

The reviewer asked for precision: did he mean treating the file as the sole source of truth, referencing only its ids, connector types, and composite id formats "without pulling or decomposing anything from Radlex"?

**Answered.** Not sole. Verbatim:

> "Not 'only'--consider it an overlay on existing RadLex. Obviously, it's not complete, and we should discuss in detail the things that we're already planning and the directions we need it to evolve to support the CDE work. But the key thing is that this is going to be the basis for the RadLex anatomy axis going forward. Since it's so important that the anatomy portion of Radlex change WITH our work, we need to try to work with the closest we can to current-ish state. If you aim at the currently published RadLex, it's like you're editing a three-year old version of a document that others have been editing."

And, confirming her reading of the mechanics: "…but yes, your idea is right."

Two further points from the owner:

- A working session is needed on the currently planned changes to RadLex anatomic locations, to identify the new needs the CDE work is surfacing and make sure they are incorporated. If disagreement remained, "we need to connect to get on the same page ASAP, because this is really fundamental to our modeling."
- "let's FOR SURE keep a list of the SPECIFIC 'we need this node' changes we see as we go, and those can be brought in regardless."

## 3. What this settles

- The anatomic locations file is an overlay on RadLex, not a replacement and not the only source: RadLex concepts and predicates underneath, the file's ids (including its compound sided ids), containment, part-of, and laterality on top.
- That file, not the published RadLex release, is the working state of the RadLex anatomy axis for this project, because it is what the RadLex anatomy track is editing.
- A running list of specific node requests is kept and fed upstream regardless of the larger discussion. The anatomy gap log carries it.

## 4. Left open

- The working session on planned changes to RadLex anatomic locations.
- The reviewer's merged refactor, to be reviewed when it lands.
