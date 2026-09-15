# Path: commit this week's work and merge with the reviewer's branch

**Written:** 2026-09-15 by Claude. **Status:** proposed. **Owner approves each commit and each push; nothing below is done until then.**

## Where things stand

- Local `next-gen-2026` is at fa2fb7e (the inheritance correction, 9 September) plus a large uncommitted set: the viewer review, two email extracts, the anatomy summary (11), the structural comparison (12), the rewritten gap log, decisions S30 to S51, the root glossary `CONTEXT.md`, and nine plan files.
- `origin/next-gen-2026` has the reviewer's six commits ("next-gen alpha first pass" I to VI, 10 to 14 September), every one of them under `docs/next-gen-schema/alpha/` (95 files). It does not have fa2fb7e. First pass VI (14 September) is expected to carry her anatomy refactor announced on 13 September.
- **No file is touched on both sides.** A test merge (`git merge-tree`) of her branch into ours produced no conflicts.
- **The only breakage after merging is ours:** the bundle checker requires OKF frontmatter on every Markdown file under `docs/next-gen-schema/`, and her eleven Markdown files (README, SHAPE, MECHANISMS, evaluation notes, example docs) have none. Her tree contains no denylisted names.
- The review worktree of 13 September is stale; her later commits are on origin.

## Part 1: physical (git)

1. **Leak fixes, done in this pass.** The plan file that carried the reviewer's name in its filename and body is renamed and sanitized, as is the second plan file; the checker's denylist sweep now also covers `docs/plans/` and `CONTEXT.md`. Run `python3 docs/check_bundle.py` and a denylist grep over the whole tree before every commit.
2. **Commit locally, in three commits, each checker-clean:**
   - (a) *Decisions and notes of the week:* the viewer review, the 8 and 13 September extracts, 11, the rewritten 04, S30 to S37, pointer edits, and the plans for the nodule, the to-do, the libraries, and the punch list.
   - (b) *The structural comparison and agenda* (Codex's, approved by the owner in its tab): 12, the two agenda plans and the published agenda page, `CONTEXT.md`, S38 to S51, and the corrections to 00, 01, 03, 06, 11, 04.
   - (c) *Housekeeping:* the checker sweep extension, the publishing section in the tools playbook, `.gitignore`.
   If the owner prefers one commit, fold (a) to (c) together; the split only keeps provenance legible.
3. **Merge origin.** `git merge origin/next-gen-2026` (no conflicts expected). In the same merge commit, make the checker treat `docs/next-gen-schema/alpha/` as an external subtree: skip the frontmatter, index-coverage, and diagram rules there, keep the denylist and link checks. That is a Claude default to record in 10 before applying; the alternative is asking the reviewer to add frontmatter, which imposes our conventions on her directory.
4. **Verify and push.** Checker clean on the merged tree; `git push origin next-gen-2026`.
5. **Publish** the site from the merged commit by the documented process, after deciding whether her `alpha/` Markdown appears in the site (the site builder renders every Markdown file under the bundle; recommend excluding `alpha/` until the conceptual merge, and linking her generated documentation instead).
6. **Remove the stale worktree** with Worktrunk (`wt`), when the owner says so; do not delete the branch.

## Part 2: conceptual (getting on the same page)

The owner has already ruled that the reviewer's implementation approach is the foundation (S38) and that nothing in the comparison is settled by our own discussion alone (S49). So the conceptual merge is a sequence of joint decisions, not a rewrite of either side.

1. **The working session.** Use the published agenda (anatomy axis first; apparent active conflicts; improvement proposals; remaining open questions) and the sixteen structural dossiers in 12, in the order 12 §7 recommends. Each dossier ends with a question; each answer becomes a decision-record row.
2. **A provenance mark for joint decisions.** Add **AGREED WITH REVIEWER** (date, source) to the marks in 10, so that rows settled in the session are distinguishable from the owner's unilateral rulings and from Claude's defaults.
3. **Anatomy first.** Confirm with her the overlay ruling (S37), hand over the derived structure-type layer (to-do 11) and the node request list (04), and agree the edge names for is-a and part-of (to-do 5).
4. **One canonical form.** Her Python specification generates JSON and OWL; our canonical JSON Lines graph generates the mats, trees, and report pictures. Decide which is the source and which is derived, then convert the other: our two worked families and three report examples expressed in her specification, or her specification emitting our JSON Lines. The libraries plan waits on this.
5. **Reconcile the decision record with her SHAPE and MECHANISMS documents** row by row: where they agree, cite both; where they differ, the dossier question applies; where she has something we lack (her probes, her authoring lint), adopt it.
6. **Build the punch-list examples in the agreed form**, starting with the four nodule classes and the part-solid component, each one a test of the merged model and an entry in the book of report patterns.
7. **One public face.** Decide what the published site shows once both sides are merged: our documents and pictures, her generated documentation, or both under one index.

## Done means

Local and origin `next-gen-2026` identical, checker clean, no denylisted term anywhere in the tree, the site republished from the merged commit, the stale worktree gone, and the first joint decisions recorded in 10 with the new mark.
