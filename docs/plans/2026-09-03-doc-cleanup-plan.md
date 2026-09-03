# Plan: documentation cleanup, incidental issues

**Written:** 2026-09-03. **Status:** proposed. This collects issues noticed while restructuring the bundle for the mat-and-tree work that are *not* part of that work. Nothing here has been done. Each item is small; do them in a batch when convenient, running `python3 docs/check_bundle.py` after each.

## Bundle documents

- [ ] **01 §5 table.** The diagnosis row now carries a strike-through note in the cell. Rewrite the table cleanly for the two-node-type world (Diagnosis is a node type, not an `entity_type` value) and move the history to 10 or the archive.
- [ ] **03 §1 and §2** carry dated "since 2026-09-02" notes inline. Fold them into the tables and move the history to the log.
- [ ] **03 §9** still shows the `RID199/HAS_ELEMENT/RDE2_000090` path form for a binding target; bindings now carry ids (`RDE2_000831` for the bile duct caliber). Update the sample.
- [ ] **03 §6.2** canonical-form sample still uses `FC-`/`DE-` placeholder ids and shows a `required` property. Regenerate the sample from `graph.py dump`.
- [ ] **03 §3** describes the dossier renderer as the standard neighborhood view; since 09 the mat is. Reword to present the dossier as the element and location view and point at 09 for classes.
- [ ] **06** has grown a "§0 update" block on top of the 2026-08-21 handoff. Rewrite 06 as a current handoff and move the dated narrative into `log.md`.
- [ ] **07 §7 and the closing "consequential edits owed"** list is partly done (the domain column, the subsumption test) and partly not (00 §2.4 and §5.1 corrections, the ten-exemplar-sets request). Tick or move.
- [ ] **00 §8 issues list** does not know about the Grouping node type, the unrestricted taxonomy, or the removal of `required`. Add pointers to 10.
- [ ] **02 Q5** says a grouping is "not an entity_type at all"; it is now a node type (S8). Add a pointer.
- [ ] **Em-dash pass** (06 §2 of the handoff): still owed across the eight prose documents, now ten.
- [ ] **08** keeps a paragraph explaining that its pictures were replaced. Once 09 has settled, drop it.
- [ ] **index.md descriptions** should match each document's frontmatter description; the checker warns, it does not fail. Re-sync after this batch.

## Checker and tooling

- [ ] `check_bundle.py` validates `docs/plans/` for nothing; plans are working artifacts by decision, but a link check from bundle documents *into* plans would catch renames.
- [ ] `check_bundle.py` renders every committed diagram on every run; fine at ten, slow at fifty. Cache by spec mtime.
- [ ] `spec_to_graph.py` is a bridge; the six interim specs should migrate into `graph/` and `render_neighborhood.py` should read the graph (06 §0).
- [ ] `build_site.py` link sweep reports the site's links into `astro-docs/`, `build_schemas.py`, and `raw_sources/` as broken because those are outside the bundle. Either copy the two public targets or mark the links as external.
- [ ] Pyright reports `float` passed for `int` font sizes in `render_cards.py`; harmless, tidy the annotations.

## Notes directory

- [ ] `notes/index.md` headings use em-dashes in titles copied from frontmatter; part of the em-dash pass.
- [ ] `notes/SOURCES.md` should record the Hood taxonomy lists (`../findingmodels/lists`, exported 2026-08-15) as a source, since 08 and 10 cite them.

## Site and astro-docs

- [ ] `astro-docs/` is untouched, deploys from the `styleguide` branch, and documents the old set/element vocabulary. Decide whether it is retired or becomes the published home of `site/`.
- [ ] `.github/workflows/jekyll-gh-pages.yml` and `astro-deploy.yml` both exist; one is dead.
