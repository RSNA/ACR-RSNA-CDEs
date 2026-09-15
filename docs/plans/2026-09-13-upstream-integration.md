# Park, Understand, and Integrate the reviewer's Upstream Work

Status: superseded by the owner's 14 September direction; retained as an initial inventory

The owner has selected **the reviewer's implementation approach as the foundation going forward**. The selected-porting strategy and authority question below are superseded by [the structural-analysis plan](2026-09-14-alpha-structural-analysis.md). Initial focus is in-depth structural comparison; presentation and clinical-content work are separate.

Correction to the initial Git interpretation: the reviewer's four commits only add `alpha/`. A normal three-way merge would retain the local no-inheritance correction; the absence of that correction in the reviewer's branch does not mean a merge would undo it. The differing semantics inside `alpha/` require review independently of Git merge mechanics.

## Goal

Preserve the reviewer's upstream contribution exactly, understand both its implementation and domain model, and produce a reviewable integration path that does not disturb the current working tree or silently override existing schema decisions.

## Context

the reviewer has reportedly pushed substantial work to the upstream repository, probably on the current branch. This checkout already contains unrelated uncommitted work, so discovery and comparison must remain isolated. The immediate audience is the project owner and collaborators deciding what should be adopted, adapted, discussed, or retained as an alternative.

## Process Overview

1. Record local repository state, fetch upstream refs without merging, and identify the new commits and exact source ref.
2. Park the fetched commit under a durable local name and inspect it in an isolated Worktrunk worktree.
3. Inventory the contribution by files, runtime/tooling, data model, UI behavior, documentation, and tests.
4. Compare its vocabulary and assumptions against the current graph, decision record, worked examples, and no-inheritance rule.
5. Classify each meaningful difference as compatible, additive, conflicting, superseding, or unclear, with evidence from both sides.
6. Propose integration slices with explicit ownership, dependencies, verification, and rollback boundaries; implement nothing until the owner approves a slice.
7. Update this plan and relevant documentation/logs to reflect the final reviewed outcome.

## Detailed Steps

### Step 1: Locate the upstream contribution

**What happens:** Inspect local status and configured remotes, fetch without merging, and compare local HEAD with the likely upstream branch.
**Input:** Current checkout and configured Git remotes.
**Output:** Exact remote ref, commit range, commit hashes, and changed-file summary.
**Decisions:** If more than one candidate branch exists, identify candidates and ask the owner which is the reviewer's.
**Owner:** Codex performs read-only discovery; the project owner resolves ambiguous authorship.
**Notes:** Do not stash, reset, merge, rebase, or overwrite the dirty working tree.

### Step 2: Park and isolate it

**What happens:** Create a durable local branch at the fetched commit and a separate Worktrunk-managed worktree for inspection.
**Input:** Confirmed upstream commit.
**Output:** Named local parking branch and isolated worktree path.
**Decisions:** Recommended naming is `the review branch of 13 September`; adjust only if repository conventions require another namespace.
**Owner:** Codex after the source commit is unambiguous.
**Notes:** Parking preserves the contribution exactly; no integration commit is created here.

### Step 3: Build an evidence-backed inventory

**What happens:** Read the contribution's own documentation and entry points, identify generated versus authored files, run its documented checks where safe, and summarize architecture and user-visible behavior.
**Input:** Isolated upstream worktree.
**Output:** Inventory of files, components, commands, tests, generated assets, and operational dependencies.
**Decisions:** None; uncertain behavior is recorded rather than inferred.
**Owner:** Codex.
**Notes:** Avoid importing dependencies or starting services until their effects and required credentials are understood.

### Step 4: Compare domain models

**What happens:** Map the reviewer's terms, node and edge types, identity rules, cardinalities, provenance, and rendering behavior to the current schema vocabulary and recorded decisions.
**Input:** Upstream inventory plus `00`, `03`, `07`, `08`, `09`, `10`, and canonical graph files.
**Output:** A comparison matrix with concrete examples and source locations.
**Decisions:** Classify differences as compatible, additive, conflicting, superseding, or unclear.
**Owner:** Codex proposes classifications; the project owner decides genuine semantic conflicts.
**Notes:** `IS_A`/`SUBTYPE_OF` must not be treated as OOP-style propagation of outgoing edges.

### Step 5: Design integration slices

**What happens:** Break adoption into independently reviewable slices such as static viewer hosting, data adapters, graph additions, UI components, tests, and documentation.
**Input:** Comparison matrix and owner decisions.
**Output:** Ordered integration backlog with acceptance checks and rollback boundaries.
**Decisions:** Which source is authoritative for each slice; whether incompatible ideas remain as experiments or are rejected.
**Owner:** Project owner approves; Codex can then implement approved slices.
**Notes:** Do not combine semantic decisions, generated assets, deployment tooling, and unrelated documentation in one commit.

### Step 6: Execute approved slices

**What happens:** Implement one approved slice at a time in an isolated worktree, validate it, update OKF metadata and relevant documentation, then request explicit permission for each commit.
**Input:** Approved slice.
**Output:** Small, reviewable change with tests and documentation.
**Decisions:** Any newly discovered semantic choice returns to Step 4 rather than being silently assumed.
**Owner:** Codex and collaborators as assigned.
**Notes:** Deployment remains a separate, commit-based, denylist-checked operation.

### Step 7: Close the review

**What happens:** Reconcile the plan, current-state documents, decision record, and user-facing log with what was actually accepted.
**Input:** Completed or rejected slices.
**Output:** Completed plan, accurate documentation, and a clear record of unresolved items.
**Decisions:** Whether to retain or remove the parking worktree and branch; branch deletion requires explicit owner approval.
**Owner:** Codex prepares; project owner approves destructive cleanup and commits.
**Notes:** Historical alternatives should remain clearly marked rather than presented as current behavior.

## Edge Cases and Failure Modes

- The work is on a different branch or fork: enumerate candidate refs and compare authorship before parking anything.
- The upstream branch was force-pushed: preserve the fetched commit under the parking branch before any further fetch changes the remote-tracking ref.
- Generated files dominate the diff: identify their source and compare authored inputs separately from generated output.
- The contribution assumes inheritance or another rejected semantic rule: demonstrate the conflict with one concrete graph/rendering example and ask for an explicit decision.
- Dependencies require credentials or modify external systems: stop at static inspection until separately authorized.
- Local and upstream edits overlap: use an isolated worktree and patch-level integration; do not merge into the dirty checkout.

## Dependencies and Requirements

- Network access to the configured upstream Git remote.
- Worktrunk (`wt`) for isolated Git worktree lifecycle.
- Existing current-state and decision documents as the semantic baseline.
- Explicit owner approval before integration commits, deployments, or branch deletion.

## Open Questions

- Should the reviewer's alpha remain a parallel candidate from which we adopt selected mechanisms, or should it replace the current model as the semantic baseline? The recommendation from this assessment is the former.
- Once authority is settled, which low-conflict slice should be first: reproducible build/test plumbing, terminology anchoring and verification, or edge identity/version metadata?

## Success Criteria

- the reviewer's exact source commit is durably named and inspectable without modifying the current worktree.
- The contribution can be built or otherwise examined using documented, reproducible commands.
- Every material model difference is tied to evidence in both implementations and to the applicable recorded decision.
- The owner receives a prioritized set of integration slices and encounters no unannounced semantic or publication changes.

## Discovery Record

### Source and parking location

- Fetched ref: `origin/next-gen-2026`
- Merge base with the local branch: `7b68a49b980572d2fb64f27e8cab14a072bbf72b`
- the reviewer's four commits: `06948d6`, `73f8e93`, `16e8d51`, and `ae08188`
- Exact parked tip: `ae08188534fd59f1f38ed49e327355782c14bd9b`
- Local parking branch: `the review branch of 13 September`
- Isolated Worktrunk worktree: `/home/talkasab/the sibling review worktree`
- Local branch tip remains `fa2fb7e032f0d5e4715c29833cb559e5f7d45ae1`; no merge, rebase, stash, upload, or deployment was performed.

The branches diverge one local commit against four upstream commits. the reviewer's commits only add `alpha/`; a normal three-way merge would retain the no-inheritance correction at `fa2fb7e`. The separate alpha's semantics still differ and require review.

### Inventory

the reviewer added one parallel implementation under `docs/next-gen-schema/alpha/`: 96 files and about 98 MiB on disk. The first commit contains the entire semantic model; the next three commits refine generated documentation and visualization code.

The authored center is `alpha/scripts/spec.py` (2,318 lines). It generates:

- a definition graph with 553 nodes and 1,126 edges;
- 45 FindingClasses, 25 Diagnoses, 37 DataElements, 16 Measurements, and 226 imported anatomy nodes;
- 45 flat per-finding JSON shapes plus aggregate files;
- Turtle, RDF/XML, standalone OWL, and reasoner probes;
- narrative mechanism, shape, evaluation, and visualization documents;
- two interactive HTML visualizations and two conceptual PNGs.

Two vendored RadLex source files account for about 80 MiB of the 98 MiB directory. `RadLex.owl` alone is about 62 MiB, above GitHub's 50 MiB warning threshold. Before any integration, confirm source/license provenance and decide whether these are reproducible external inputs, release artifacts, object-storage assets, or Git LFS objects rather than ordinary Git content.

### Reproducibility and validation findings

- `spec.lint()` reports zero findings, but its anatomy-scope check is skipped because the generated `scripts/anatomy.json` is absent. Zero findings is not complete scope validation.
- The committed definition graph passes the structural invariants that can be run read-only: referential integrity, acyclic taxonomy and partonomy, anatomic reachability, value ownership, same-type `OCCURS_WITH`, diagnosis-to-finding routes, anchor verdicts, and edge identity.
- The RadLex verifier parses 45,987 English labels and checks 344 distinct codes across 425 references. Every code resolves under that check; 27 label differences pass a substring/stem heuristic and 18 mappings deliberately bypass strict label agreement. This is not proof of clinical correctness or semantic equivalence.
- The alpha has no dependency manifest or single repository-relative build command. The README names `rdflib` and `owlready2`; evaluation also imports `networkx`.
- Most builders and tests hard-code `/mnt/user-data/outputs/radcde-alpha`; the RadLex verifier also defaults to `/home/claude/work/...`. They cannot yet reproduce the committed artifacts directly from an arbitrary checkout.
- Authored and generated files are mixed in the same committed subtree, with duplicate serializations. Integration should first establish one source of truth, repository-relative output paths, pinned dependencies, and a clean/regenerate/diff check.

### Semantic comparison

| Area | the reviewer's alpha | Current recorded position | Classification |
|---|---|---|---|
| Subtype behavior | `SUBTYPE_OF` has `inheritance: strict`; compiled shapes walk ancestors and label inherited elements, measurements, scopes, modalities, and other relationships. OWL emits `rdfs:subClassOf`, so parent restrictions apply to subclass instances. | S3 and rejected S13: `SUBTYPE_OF` propagates no outgoing edge; shared facts are asserted directly. | **Direct conflict** |
| Element applicability | OWL emits existential restrictions for applied elements and measurements. These entail a filler but do not require its explicit serialization in a report. | S9: no required element. The meaning of catalog applicability versus logical existence still needs a precise mapping. | **Structural clarification needed; earlier direct-conflict claim was too broad** |
| Finding/diagnosis taxonomy | Only FindingClass-to-FindingClass subtyping; diagnosis and finding are separate layers. Empyema is a Diagnosis that obligatorily `MAY_MANIFEST_AS` pleural effusion, explicitly not its subtype. | S1: one taxonomy may cross FindingClass, Diagnosis, and Grouping; owner explicitly identifies empyema as a subtype of pleural effusion. | **Direct conflict** |
| Pulmonary nodule composition | Solid, part-solid, and non-solid are reasoner-defined subclasses of pulmonary nodule through fixed `attenuation` values; definitions rely on inheritance. | S30: four explicit FindingClasses; composition is identity, not an element; none binds a composition element; part-solid has a component. | **Direct conflict, with one compatible component idea** |
| Identifiers | Type-prefixed `FC-`, `DX-`, `DE-`, `V-`, and other spaces. | One owned `RDE2_` lineage space; type is graph data. | **Direct conflict** |
| Anatomy and region | Three scope kinds; body region derived by walking containment; `IN_REGION` rejected as redundant. | Explicit context nodes and `IN_REGION`; anatomy subtype may satisfy applicability without copying edges. | **Mixed: scope-kind machinery is additive; region policy conflicts** |
| Measurements | Measurement is a distinct node whose method is its identity; categorical elements remain DataElements. | Measurement, method, and interpretation are separate, but quantitative values currently remain a DataElement kind and use `INTERPRETED_FROM`. | **Promising but requires mapping** |
| Authoring patterns | Topic-only checklists; never nodes, never element bundles, never automatic reuse. | Current work also resists implicit element propagation and forced bundles. | **Compatible** |
| Terminology anchoring | Multiple bindings, one primary; match strength, source label/version, synonyms, anchor verdicts, post-coordination, and automated RadLex code/label checks. | Current graph has exact/close mappings and a code-lookup policy, but less machinery. | **Strong additive candidate** |
| Edge identity and governance | 791 authored edges carry IDs and version blocks; imported anatomy edges regenerate. | Important relationships and citable bindings have IDs; lifecycle/event model remains open. | **Strong additive candidate, schema mapping required** |
| Consumer artifacts | Compiles a definition graph into flat, reference-resolved finding shapes. | JSON is intended as a consumer export rather than the canonical model. | **Compatible architecture** |
| Coverage gaps | Explicitly records plurality, category/remainder negation, certainty, procedures, prior-study identity, and multi-finding diagnostic conjunctions as gaps. | Several are already open in the current documents and report-plane work. | **Useful shared backlog** |

### Recommended integration strategy

Treat the reviewer's work as a **parallel candidate implementation and evidence source**, not as a branch to merge wholesale. Keep the parking branch immutable. If reproduction work is approved, create a separate Worktrunk branch from `ae08188` for mechanical build fixes only. Actual integration should start from the current local line after it has a clean committed base, then import deliberately selected files or concepts. Do not merge `origin/next-gen-2026` into the dirty checkout: that would combine the entire 98 MiB artifact set with known semantic reversals and obscure which decisions were accepted.

Proposed slices, each separately reviewed and committed only with explicit permission:

1. **Make the alpha reproducible in isolation on a derivative review branch.** Add a dependency manifest and repository-relative CLI/task entry points; separate authored inputs from generated outputs; run lint, graph invariants, code verification, artifact-diff checks, and the reasoner probes. Preserve semantics unchanged in this slice and keep the exact parking branch untouched.
2. **Write a decision crosswalk.** Convert the comparison above into explicit proposals keyed to S1, S3, S9, S30, identifiers, region derivation, measurements, and OWL export semantics. No graph changes until the owner decides each conflict.
3. **Adopt low-conflict mechanisms.** Port terminology binding/anchor metadata and RadLex verification, edge identity/version ideas, topic-only authoring patterns, and useful invariants into the current canonical model and toolchain.
4. **Rework OWL as a projection of our semantics.** Retain OWL for exchange/checking where it is faithful, but do not encode `HAS_ELEMENT` applicability as existential requiredness or encode our non-propagating taxonomy as ordinary OWL subclass restrictions without an explicit alternative design.
5. **Port clinical content in small families.** Start with one shared family (pyelonephritis or pleural effusion), map IDs and relationships to current decisions, regenerate the existing pages, and review the semantic diff before taking another family.
6. **Rationalize artifacts and publishing.** Decide which large sources and generated serializations belong in Git, Git LFS, releases, or object storage; then publish only an approved build through the existing commit-based deployment process.

### Decision gate

No semantic content, generated page, deployment, or upstream history has been integrated. The next step requires the owner's answer on model authority: selected adoption into the current model (recommended), or replacement of the current model by the reviewer's alpha.
