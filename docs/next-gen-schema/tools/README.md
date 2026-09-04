---
type: Playbook
title: Tools, and How to Look at the Pictures
description: Process and tooling only - what each script under tools/ does, the commands that regenerate and check the bundle, how to look up external codes for a new node, and how to rasterize or screenshot the pictures and verify hover on this machine.
tags: [next-gen-schema, tooling, process, renderer, site, checker]
status: draft
generated: { by: "claude-code/claude-fable-5.1", at: 2026-09-04 }
sources:
  - id: graph-readme
    resource: /docs/next-gen-schema/graph/README.md
    title: The graph format the tools read
  - id: spec
    resource: /docs/next-gen-schema/09-mat-and-tree.md
    title: The display specification the renderers implement
---

# Tools, and How to Look at the Pictures

Process and tooling. Nothing here is a decision about the vocabulary or the pictures; those are in [09](../09-mat-and-tree.md) and [10](../10-decision-record-2026-09-02.md).

## The scripts

| Script | Reads | Writes | Run |
|---|---|---|---|
| `graph.py` | `graph/*.jsonl` and, through `spec_to_graph.py`, the interim specs in `examples/` | nothing (`check`), or the graph files in canonical order (`normalize`) | `python3 docs/next-gen-schema/tools/graph.py check` |
| `spec_to_graph.py` | `examples/*.{neighborhood,element,location}.json` | graph lines, used in memory by the loader | not run directly |
| `render_cards.py` | the merged graph, a `*.mat.json` or `*.tree.json` view | one SVG | `python3 tools/render_cards.py examples/pleural-effusion.mat.json > diagrams/mat-pleural-effusion.svg` |
| `render_report.py` | a `*.report.jsonl` file | one SVG | `python3 tools/render_report.py examples/pyelonephritis.report.jsonl > diagrams/report-pyelonephritis.svg` |
| `render_neighborhood.py` | one interim spec | one SVG, the older object dossiers | `python3 tools/render_neighborhood.py examples/presence.element.json > diagrams/de-presence.svg` |
| `build_site.py` | everything above plus every Markdown document in the bundle and `notes/` | `site/` (gitignored) | `uv run docs/next-gen-schema/tools/build_site.py` |
| `../check_bundle.py` (one level up) | the whole bundle | a report; non-zero on error | `python3 docs/check_bundle.py` |

Regenerate a committed diagram whenever a graph file or a view changes; the checker compares every committed SVG byte for byte with a fresh render and fails on drift. Run the checker before every commit.

## Adding a node: looking up codes

The policy is in [03 §2.1](../03-draft-structures.md): every external code is written with the term as that ontology states it, codes are never invented, near matches are marked close, and an anatomic location's only id is its RID. The mechanics:

1. Search with the `molu` tool in the sibling repository, which queries BioPortal and UMLS. It does not read its own `.env`, so run it from that directory with the file injected:

   ```
   cd ../med-ontology-lookup && uv run --env-file=.env molu search "pleural effusion" -o RADLEX,SNOMEDCT -n 6 -f json
   ```

   `molu lookup <term or code>` auto-detects a term, a RID, a SNOMED code, or a CUI; `molu crosswalk <CUI>` walks a UMLS concept to other vocabularies; `molu children <code> -o SNOMEDCT` lists a hierarchy level.
2. Take an `exact_match` hit as `exactMatch`. Take a broader or narrower concept as `closeMatch` only when the graph needs the mapping now; otherwise leave the node unmapped and say so in its `note`. Malignant pleural effusion is unmapped for that reason.
3. When RadLex has no concept for a finding radiologists use (striated nephrogram, perinephric fat stranding, chylothorax so far), record it in the node's `note` as a candidate for upstream proposal; [04](../04-anatomy-gaps.md) carries the anatomy gaps, and the same treatment applies to RadLex's finding branch.
4. Context concepts (modality, region, subspecialty) come from `graph/concepts.jsonl`; add a RadLex concept there with its aliases before pointing an edge at it. Etiology, sex, age, and time course have provisional `RDE2_` codes in the same file.

## Looking at the pictures

**Rasterize an SVG** for a quick look without a browser:

```
uv run --with cairosvg python -c "import cairosvg; cairosvg.svg2png(url='diagrams/mat-pleural-effusion.svg', write_to='/tmp/x.png', output_width=1600)"
```

cairosvg renders the static face only; hover detail and the site's click layer do not exist in a PNG.

**Screenshot a site page, and verify hover, in a real browser.** On this machine `playwright-cli` cannot launch Chromium (the kernel forbids its sandbox) and refuses `file://` URLs, so drive Playwright directly from Node with the sandbox off. The package is the one bundled with the CLI:

```js
const { chromium } = require('/home/linuxbrew/.linuxbrew/lib/node_modules/@playwright/cli/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ chromiumSandbox: false, args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
  await p.goto('file://' + process.cwd() + '/site/nodes/RDE2_000502.html');
  await p.locator('#m-RDE2_000510').hover();
  console.log(await p.evaluate(() => getComputedStyle(document.querySelector('#d-RDE2_000510')).display)); // "inline" means the hover detail is showing
  await p.screenshot({ path: '/tmp/mat.png', fullPage: true });
  await b.close();
})();
```

Save it as a `.cjs` file and run it with `node`. The hover reveal is CSS `:has()` inside the SVG, so it also works when the SVG is opened alone in a browser; it does not work when the SVG is placed as an image.

**Serve the site to another device** with a plain file server bound to one interface, never the repository root (the gitignored raw sources live there):

```
python3 -m http.server 8765 --bind <tailnet-ip> --directory site
```

## Dispatching a picture task to another agent

What the two rounds of 2 September 2026 taught, recorded in full in [the exploration review](../explorations/2026-09-02-diagram-alternatives/review.md): give the agent the decision record and the specification, not a prose brief; state density rules in numbers, because "no overlaps" as the success criterion produces inflated frames and shrunken type; require both examples from one design; require the agent to rasterize and look at its own output; and have it write only into its own directory under the gitignored `.preview/`, never into `docs/`.
