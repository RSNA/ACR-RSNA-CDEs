# Structural analysis of the alpha implementation

Status: analysis delivery complete — structural decisions remain open for discussion; no implementation changes

## Direction and scope

The owner's 14 September instruction supersedes the integration strategy proposed on 13 September: **the reviewer's implementation approach is the foundation going forward.** Compare its structural semantics carefully against the discussions and identify decisions to agree on. The existing prototype is evidence, not the implementation to preserve by default.

Keep three workstreams separate:

- **Structure, now:** definition identity, node and relationship semantics, anatomy integration, elements/measurements/values, definition versus observation, governance, and consistency across authored sources, graph, OWL, and JSON consumers.
- **Presentation, later:** adapt the reviewer's presentation layers toward the owner's preferred mat-based definition view. Record data-contract implications now; do not redesign or implement views.
- **Clinical content, separate thread:** individual definitions, codes, values, and disease-family modeling. Examples may demonstrate a structural distinction but are not changed or adjudicated here.

Anatomic Locations is a priority structural area. Incorporate the 13 September definition-library discussion and S31–S37, especially the existing Anatomic Locations substrate and its missing taxonomy/structure-type layer. Identify the decisions and evidence needed for the later detailed anatomy discussion without inventing a replacement substrate.

## Plan

1. Write this plan and correct the superseded 13 September framing.
2. Freeze evidence at the reviewer's parked commit `ae08188534fd59f1f38ed49e327355782c14bd9b`; record the current discussion files and their uncommitted status.
3. Delegate independent reviews: Sol for anatomy and Sol for formal semantics; Luna for identifier/governance/export contracts. The primary agent reviews decision provenance, definition/observation boundaries, elements and measurements, and reconciles all findings.
4. Verify substantial claims against code and generated artifacts; distinguish actual behavioral differences, explicit owner decisions, provisional proposals, omissions, and disagreements among the reviewer's own artifacts. Use primary standards for formal semantic claims.
5. Write a substantive analysis under `docs/next-gen-schema/`, with a structural comparison matrix, detailed decision dossiers, concrete acceptance probes, anatomy agenda, and separately parked presentation/content backlogs.
6. Have a reviewer challenge the synthesis for overstatements, missing structure, and accidental conflation of clinical or presentation choices.
7. Update relevant OKF metadata, index, handoff, and log; run the documentation checks and review final changes. Mark analysis delivery complete while retaining open model decisions for discussion.

## Deliverables and completion criteria

- An evidence-backed report treating the reviewer's architecture as the implementation foundation.
- Each major difference includes the prior discussion's authority, what source/code/artifacts actually do, downstream consequences, and a precise decision to discuss.
- Anatomy includes identity/source ownership, taxonomy versus partonomy/containment, sidedness, scope/applicability, normal-anatomy attributes, and library composition.
- No content corrections, presentation implementation, merge, deployment, or commit in this analysis task.

## Progress

- Plan written before analysis work; supersession of the prior strategy recorded.
- Two Sol reviewers examined formal semantics and anatomy; Luna inventoried public contracts and challenged the synthesis. Their substantive findings were reconciled against the source and artifacts.
- Delivered discussion draft: `docs/next-gen-schema/12-alpha-structural-comparison.md`, with 16 structural dossiers, implementation evidence, proposed acceptance probes, and separately parked content/presentation tracks. Draft status denotes unapproved model decisions, not an unfinished analysis pass.
- Concurrent anatomy documentation was read and incorporated: `11-anatomy-axis.md`, the revised gap log, and the 13 September exchange. The announced anatomy refactor is not yet on `origin/next-gen-2026` after a fresh 14 September fetch; old anatomy implementation findings are explicitly provisional against the future refactor.
- Corrected the previous assessment's Git-merge, existential-requiredness, and verification-overreach claims.
- Incorporated review corrections on containment encoding, scheme scope versus applicability, exact anchor verdicts, numeric contracts, dormant observation typing, and reasoning-test coverage. Class-defining conditions are discussed separately from clinical content and reportable attributes.
- Updated S38, relevant OKF metadata, the bundle index, next-steps handoff, and the concise bundle log. Preserved concurrent anatomy documentation and unrelated staged/unstaged changes.
- Final documentation review: `python3 -B docs/check_bundle.py` reports 48 documents, 11 diagrams, zero errors and zero warnings; `git diff --check` passes. No complete alpha rebuild or new reasoner run is claimed.
- No application changes, clinical-content edits, presentation implementation, merge, commit, or deployment. Follow-on work is agreement on the structural contracts and rechecking anatomy against the announced upstream refactor.
