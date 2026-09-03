#!/usr/bin/env python3
"""The mat and the tree, per docs/plans/2026-09-02-mat-and-tree-decisions.md.

The MAT: one context object drawn in full (the mat), its one-hop neighbours as
minimal mini-cards inside dotted containers labelled with the relationship to the
context object. No wires. Fixed card zones: title / anatomy / text / attributes /
connections / mappings / stat row. Mini-cards show name, kind, id only; in an inline
HTML context, hovering a mini-card reveals a detail card via CSS inside the SVG.

The TREE: the is-a hierarchy of a family, rooted at a grouping node — boxes with
orthogonal elbow connectors, top-down. Relationship edges are drawn and labelled with
the label on the horizontal run at the source end of its own edge, so fan-in never
leaves a label ambiguous. Arrowheads use markerUnits="userSpaceOnUse" with
orient="auto" on straight final segments, so every head is aligned with its line.

Usage:
  render_mat_tree.py mat  RDE2_000502 "Pleural effusion"        > mat.svg
  render_mat_tree.py tree RDE2_000516 "Pleural abnormality"     > tree.svg

The view is exactly a hub id and a title; everything else comes from the graph.
The `required` property of HAS_ELEMENT is ignored entirely (per the decisions doc).
"""
import sys, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "docs", "next-gen-schema", "tools"))
from graph import load_graph  # noqa: E402

G = load_graph()
NODES, EDGES = G.nodes, G.edges

# ------------------------------------------------------------------
# palette and text helpers
# ------------------------------------------------------------------
ACCENT = {
    "FindingClass":     ("#2563eb", "#1e3a8a", "#eff6ff"),
    "Diagnosis":        ("#7c3aed", "#4c1d95", "#f5f3ff"),
    "Grouping":         ("#64748b", "#334155", "#f8fafc"),
    "DataElement":      ("#16a34a", "#14532d", "#f0fdf4"),
    "AnatomicLocation": ("#d97706", "#78350f", "#fffbeb"),
}
INK, MUTED, RULE, HAIR = "#1f2937", "#64748b", "#cbd5e1", "#e2e8f0"
GREEN_DARK, AMBER_DARK = "#14532d", "#78350f"
EDGE_COLOR = {"MAY_MANIFEST_AS": "#7c3aed", "MAY_CAUSE": "#dc2626",
              "MAY_PROGRESS_TO": "#0891b2", "OCCURS_WITH": "#64748b"}
KIND_LABEL = {"FindingClass": "FINDING", "Diagnosis": "DIAGNOSIS", "Grouping": "GROUPING",
              "DataElement": "ELEMENT", "AnatomicLocation": "ANATOMY", "Concept": "CONCEPT"}
TYP = {"very_frequent": "very frequent", "highly_suggestive": "highly suggestive"}
SPEC = {"pathognomonic": "pathognomonic", "highly_suggestive": "highly suggestive",
        "suggestive": "suggestive"}


def esc(s):
    return html.escape(str(s), quote=True)


def tw(s, fs, bold=False):
    return len(str(s)) * fs * (0.60 if bold else 0.55)


def txt(x, y, s, fs, fill, anchor="start", weight=None, style=None, spacing=None, mono=None):
    a = f' x="{x}" y="{y}" font-size="{fs}" fill="{fill}" text-anchor="{anchor}"'
    if weight: a += f' font-weight="{weight}"'
    if style: a += f' font-style="{style}"'
    if spacing: a += f' letter-spacing="{spacing}"'
    if mono: a += ' font-family="ui-monospace, monospace"'
    return f"<text{a}>{esc(s)}</text>"


def wrap(s, fs, max_w):
    """Greedy word wrap to pixel width; returns list of lines."""
    words, lines, cur = str(s).split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and tw(trial, fs) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def name_of(nid):
    return NODES.get(nid, {"name": nid})["name"]


def kind_of(nid):
    n = NODES.get(nid, {"node": "Concept"})
    return KIND_LABEL.get(n["node"], n["node"].upper())


def node_edges(nid, etype, direction="both"):
    out = []
    for e in EDGES:
        if e["edge"] != etype:
            continue
        if direction in ("out", "both") and e["from"] == nid:
            out.append(e)
        elif direction in ("in", "both") and e["to"] == nid:
            out.append(e)
    return out


def stat_values(nid):
    """The six stat-row cells: modality, region, sex, age, course, etiology."""
    def names(etype):
        return [name_of(e["to"]) for e in node_edges(nid, etype, "out")]
    return {
        "MODALITY": " ".join(names("SEEN_ON")),
        "REGION": " ".join(names("IN_REGION")),
        "SEX": " ".join(names("SEX")),
        "AGE": " ".join(names("AGE_APPLICABILITY")),
        "COURSE": " ".join(names("TIME_COURSE")),
        "ETIOLOGY": " ".join(names("HAS_ETIOLOGY")),
    }


def mappings(nid):
    """External codes with their preferred terms; close matches marked."""
    out = []
    for e in EDGES:
        if e["from"] != nid or e["edge"] not in ("exactMatch", "closeMatch"):
            continue
        system, _, code = e["to"].partition(":")
        label = {"RADLEX": "RADLEX", "SNOMEDCT": "SNOMED CT", "LOINC": "LOINC"}.get(system, system)
        term = e.get("props", {}).get("display", "")
        mark = "" if e["edge"] == "exactMatch" else "close: "
        out.append(f'{mark}{label} {code} \u201c{term}\u201d')
    return out


def props_text(e):
    """Edge properties for beside the mini-card; edge ids are never shown."""
    p = e.get("props", {})
    bits = []
    if p.get("typicality"):
        bits.append(TYP.get(p["typicality"], p["typicality"]))
    if p.get("specificity"):
        bits.append(SPEC.get(p["specificity"], p["specificity"]))
    elif e["edge"] == "MAY_MANIFEST_AS":
        bits.append("no specificity asserted")
    exp = p.get("expected")
    if exp:
        bits.append("expect: " + " · ".join(f"{k}: {v}" for k, v in exp.items()))
    if p.get("note"):
        bits.append(p["note"])
    return " · ".join(bits)


# ==================================================================
# THE MAT
# ==================================================================
MAT_W = 1180
MINI_W, MINI_H = 310, 40
DETAIL_W = 400

CONTAINERS = [  # (label, edge, direction from the context object's side)
    ("A KIND OF", "SUBTYPE_OF", "out"),
    ("KINDS OF", "SUBTYPE_OF", "in"),
    ("MANIFESTS AS", "MAY_MANIFEST_AS", "out"),
    ("MAY BE CAUSED BY", "MAY_CAUSE", "in"),
    ("MAY CAUSE", "MAY_CAUSE", "out"),
    ("PROGRESSES TO", "MAY_PROGRESS_TO", "out"),
    ("PROGRESSES FROM", "MAY_PROGRESS_TO", "in"),
    ("OCCURS WITH", "OCCURS_WITH", "both"),
    ("ASSESSED BY", "ASSESSED_BY", "out"),
]
INV = {"SUBTYPE_OF": "has kind", "MAY_MANIFEST_AS": "manifested by",
       "MAY_CAUSE": "may be caused by", "MAY_PROGRESS_TO": "progresses from",
       "OCCURS_WITH": "occurs with", "ASSESSED_BY": "assessed by"}
FWD = {"SUBTYPE_OF": "a kind of", "MAY_MANIFEST_AS": "manifests as",
       "MAY_CAUSE": "may cause", "MAY_PROGRESS_TO": "progresses to",
       "OCCURS_WITH": "occurs with", "ASSESSED_BY": "assessed by"}


def mini_connections(nid, hub):
    """Lines on the hover detail: this node's own edges to third parties, one hop."""
    lines = []
    for e in EDGES:
        if e["edge"] not in FWD:
            continue
        if e["from"] == nid and e["to"] != hub and e["to"] in NODES:
            lines.append(f'{FWD[e["edge"]]} \u2192 {name_of(e["to"])}')
        elif e["to"] == nid and e["from"] != hub and e["from"] in NODES:
            lines.append(f'\u2190 {INV[e["edge"]]} {name_of(e["from"])}')
    lines.sort()
    return lines[:4] + ([f"+ {len(lines) - 4} more"] if len(lines) > 4 else [])


def mini_detail(nid, hub, dx, dy):
    """The hover-revealed detail card: definition, mappings, stat row, connections."""
    n = NODES.get(nid, {"node": "Concept", "name": nid})
    lines = []
    defn = wrap(n.get("definition", ""), 8.5, DETAIL_W - 24)
    if len(defn) > 4:
        defn = defn[:4]
        defn[-1] += " \u2026"
    maps = mappings(nid)
    stats = stat_values(nid)
    stat_line = " · ".join(v or "\u2014" for v in stats.values())
    conn = mini_connections(nid, hub)
    h = 30 + 13 * (len(defn) + len(maps) + 1 + len(conn)) + 8
    out = [f'<g class="mdetail" transform="translate({dx},{dy})">',
           f'<rect x="0" y="0" width="{DETAIL_W}" height="{h}" rx="8" fill="#ffffff" '
           f'stroke="{MUTED}" stroke-width="1" filter="drop-shadow(0 2px 3px rgba(0,0,0,0.25))"/>']
    y = 16
    out.append(txt(10, y, f'{n["name"]}  ·  {kind_of(nid)} · {nid}', 9, INK, weight="700"))
    y += 6
    for ln in defn:
        y += 12
        out.append(txt(10, y, ln, 8.5, INK))
    for ln in maps:
        y += 12
        out.append(txt(10, y, ln, 8, MUTED))
    y += 12
    out.append(txt(10, y, "stats: " + stat_line, 8, MUTED))
    for ln in conn:
        y += 12
        out.append(txt(10, y, ln, 8, GREEN_DARK))
    out.append("</g>")
    return "".join(out)


def mini_card(nid, hub, x, y):
    """Minimal face: name, kind, id. The hover detail is a sibling <g>."""
    n = NODES.get(nid, {"node": "Concept", "name": nid})
    a, dark, bg = ACCENT.get(n["node"], (MUTED, INK, "#f8fafc"))
    face = (f'<rect x="{x}" y="{y}" width="{MINI_W}" height="{MINI_H}" rx="7" fill="{bg}" stroke="{RULE}"/>'
            f'<rect x="{x}" y="{y}" width="4" height="{MINI_H}" rx="2" fill="{a}"/>'
            + txt(x + 12, y + 17, n["name"], 10.5, dark, weight="600")
            + txt(x + 12, y + 31, f'{kind_of(nid)} · {nid}', 7.5, MUTED))
    detail = mini_detail(nid, hub, min(x, MAT_W - DETAIL_W - 30), y + MINI_H + 4)
    return f'<g class="mini">{face}{detail}</g>'


def render_mat(hub, title):
    n = NODES[hub]
    a, dark, bg = ACCENT.get(n["node"], ACCENT["FindingClass"])
    MX, MW = 16, MAT_W - 32     # mat frame x, width
    IX = MX + 16                # inner content x
    IW = MW - 32                # inner content width

    bg_chunks, minis = [], []   # minis paint last (bottom-up) so hover details overlay

    # ---- zone 1: title line ----
    y = 40
    bg_chunks.append(txt(MX, 26, title, 13, INK, weight="700"))
    bg_chunks.append(f'<rect x="{MX}" y="{y}" width="{MW}" height="46" rx="10" fill="{bg}" stroke="{a}" stroke-width="1.5"/>')
    bg_chunks.append(txt(IX, y + 29, n["name"], 17, dark, weight="700"))
    bg_chunks.append(txt(MX + MW - 16, y + 29, f'{kind_of(hub)} · {hub}', 10, MUTED, anchor="end", mono=True))
    y += 46

    # ---- zone 2: anatomy line (always drawn) ----
    scope = node_edges(hub, "SCOPED_TO", "out")
    bg_chunks.append(f'<rect x="{MX}" y="{y}" width="{MW}" height="24" fill="#ffffff" stroke="{RULE}" stroke-width="0.6"/>')
    if scope:
        p = scope[0].get("props", {})
        bg_chunks.append(txt(IX, y + 16, f'\u2302 {scope[0]["to"]} \u201c{name_of(scope[0]["to"])}\u201d', 9.5, AMBER_DARK))
        bg_chunks.append(txt(MX + MW - 16, y + 16, f'{p.get("kind", "")} · {p.get("strength", "")}', 8.5, MUTED, anchor="end"))
    else:
        bg_chunks.append(txt(IX, y + 16, "\u2302 \u2014 (no anatomic scope)", 9.5, MUTED))
    y += 24

    # ---- zone 3: text ----
    lines = wrap(n.get("definition", ""), 9.5, IW)
    syns = [s["term"] for s in n.get("synonyms", [])]
    h3 = 10 + 13 * len(lines) + (14 if True else 0)
    bg_chunks.append(f'<rect x="{MX}" y="{y}" width="{MW}" height="{h3}" fill="#ffffff" stroke="{RULE}" stroke-width="0.6"/>')
    yy = y + 16
    for ln in lines:
        bg_chunks.append(txt(IX, yy, ln, 9.5, INK))
        yy += 13
    bg_chunks.append(txt(IX, yy + 1, "synonyms: " + (" · ".join(syns) if syns else "\u2014"), 8.5, MUTED))
    y += h3

    # ---- zone 4: attributes table (context object only) ----
    elems = node_edges(hub, "HAS_ELEMENT", "out")
    col = [IX, IX + 230, IX + 360, IX + 480]
    row_h = 19
    h4 = 26 + row_h * (len(elems) + 1) + 8
    bg_chunks.append(f'<rect x="{MX}" y="{y}" width="{MW}" height="{h4}" fill="#ffffff" stroke="{RULE}" stroke-width="0.6"/>')
    bg_chunks.append(txt(IX, y + 16, "ATTRIBUTES", 8.5, MUTED, weight="700", spacing="1.2"))
    ty = y + 26
    heads = ["element", "id", "kind", "values / quantity"]
    for ci, htxt in enumerate(heads):
        bg_chunks.append(txt(col[ci], ty + 13, htxt, 8, MUTED, style="italic"))
    bg_chunks.append(f'<line x1="{IX}" y1="{ty + row_h}" x2="{IX + IW}" y2="{ty + row_h}" stroke="{HAIR}"/>')
    ty += row_h
    for e in elems:
        el = NODES.get(e["to"], {})
        vals = [name_of(x["to"]) for x in node_edges(e["to"], "member", "out")]
        if el.get("kind") == "quantitative":
            units = " ".join(el.get("units", []))
            rng = f'{el.get("min", "")}\u2009\u2013\u2009{el.get("max", "")}' if "min" in el else ""
            method = el.get("method", "")
            if tw(method, 8) > 560:
                method = " ".join(method.split()[:10]) + " \u2026"
            vtext = " · ".join(b for b in (rng, units, method) if b)
        else:
            show = vals[:3] + (["\u2026"] if len(vals) > 3 else [])
            vtext = " · ".join(show)
            note = e.get("props", {}).get("note")
            if note:
                vtext += f"   ({note})"
        kind = "multi-select" if el.get("multi_select") else ("ordered" if el.get("ordered") else el.get("kind", ""))
        for ci, (v, fs_, c_) in enumerate(((el.get("name", e["to"]), 9, INK),
                                           (e["to"], 8, MUTED),
                                           (kind, 8.5, MUTED),
                                           (vtext, 8.5, INK))):
            bg_chunks.append(txt(col[ci], ty + 13, v, fs_, c_, mono=(ci == 1)))
        ty += row_h
        bg_chunks.append(f'<line x1="{IX}" y1="{ty}" x2="{IX + IW}" y2="{ty}" stroke="{HAIR}" stroke-width="0.6"/>')
    y += h4

    # ---- zone 5: connections = containers ----
    cont_chunks = []
    cy = y
    for label, etype, direction in CONTAINERS:
        if direction == "both":
            edges = node_edges(hub, etype, "out") + node_edges(hub, etype, "in")
        else:
            edges = node_edges(hub, etype, direction)
        edges = [e for e in edges if (e["to"] if e["from"] == hub else e["from"]) in NODES]
        if not edges:
            continue
        edges.sort(key=lambda e: (e["to"] if e["from"] == hub else e["from"]))
        rows = []
        for e in edges:
            other = e["to"] if e["from"] == hub else e["from"]
            rows.append((other, props_text(e)))
        # single-column rows when any row carries properties, else a 3-wide grid
        any_props = any(p for _, p in rows)
        row_hs = [MINI_H + 8] * len(rows)
        inner_x, inner_w = IX + 10, IW - 20
        if any_props:
            row_hs = []
            for _, p in rows:
                pl = wrap(p, 8.5, inner_w - MINI_W - 30) if p else []
                row_hs.append(max(MINI_H + 8, 14 + 12 * len(pl)))
            ch = 24 + sum(row_hs) + 10
        else:
            per_row = 3
            nrow = (len(rows) + per_row - 1) // per_row
            ch = 24 + nrow * (MINI_H + 8) + 6
        cont_chunks.append((cy, f'<rect x="{IX - 4}" y="{cy}" width="{IW + 8}" height="{ch}" rx="8" '
                                f'fill="{bg}40" stroke="{a}" stroke-width="0.9" stroke-dasharray="4 3"/>'
                                + txt(IX + 4, cy + 16, label, 8.5, dark, weight="700", spacing="1.2")))
        ry = cy + 24
        for i, (other, p) in enumerate(rows):
            if any_props:
                minis.append((ry, mini_card(other, hub, inner_x, ry)))
                if p:
                    plines = wrap(p, 8.5, inner_w - MINI_W - 30)
                    for j, pl_ in enumerate(plines):
                        cont_chunks.append((ry, txt(inner_x + MINI_W + 18, ry + 15 + 12 * j, pl_, 8.5, INK)))
                ry += row_hs[i]
            else:
                gx = inner_x + (i % 3) * (MINI_W + 14)
                gy = ry + (i // 3) * (MINI_H + 8)
                minis.append((gy, mini_card(other, hub, gx, gy)))
        cy += ch + 10
    y = cy

    # ---- zone 6: mappings ----
    maps = mappings(hub)
    h6 = 22 + 14 * max(1, len(maps)) + 6
    bg_chunks.append(f'<rect x="{MX}" y="{y}" width="{MW}" height="{h6}" fill="#ffffff" stroke="{RULE}" stroke-width="0.6"/>')
    bg_chunks.append(txt(IX, y + 15, "MAPPINGS", 8.5, MUTED, weight="700", spacing="1.2"))
    yy = y + 29
    if not maps:
        bg_chunks.append(txt(IX, yy, "\u2014", 9, MUTED))
    for m in maps:
        bg_chunks.append(txt(IX, yy, m, 9, INK, mono=True))
        yy += 14
    y += h6

    # ---- zone 7: stat row ----
    stats = stat_values(hub)
    cw = MW / 6
    bg_chunks.append(f'<rect x="{MX}" y="{y}" width="{MW}" height="42" fill="{bg}"/>')
    for ci, (k, v) in enumerate(stats.items()):
        x0 = MX + ci * cw
        bg_chunks.append(f'<line x1="{x0}" y1="{y}" x2="{x0}" y2="{y + 42}" stroke="{RULE}" stroke-width="0.8"/>')
        bg_chunks.append(txt(x0 + 8, y + 13, k, 7.5, MUTED, weight="700", spacing="0.8"))
        bg_chunks.append(txt(x0 + 8, y + 31, v if v else "\u2014", 9.5, INK))
    bg_chunks.append(f'<rect x="{MX}" y="{y}" width="{MW}" height="42" fill="none" stroke="{RULE}" stroke-width="0.8"/>')
    y += 42

    # mat frame around everything
    H = y + 16
    frame = (f'<rect x="{MX}" y="40" width="{MW}" height="{H - 56}" rx="10" fill="none" '
             f'stroke="{a}" stroke-width="1.8"/>')
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MAT_W} {H}" font-family="system-ui, sans-serif" '
           f'role="img" aria-label="{esc(title)} — mat view of {esc(n["name"])}">',
           '<style>.mdetail{display:none} .mini:hover .mdetail{display:inline}</style>',
           f'<rect width="{MAT_W}" height="{H}" fill="#f1f5f9"/>']
    out.append(frame)
    out.extend(bg_chunks)
    out.extend(c for _, c in sorted(cont_chunks, key=lambda t: t[0]))
    # mini-cards paint bottom-up so a hover detail covers everything below it
    for _, c in sorted(minis, key=lambda t: -t[0]):
        out.append(c)
    out.append(frame)  # frame strokes over container edges
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ==================================================================
# THE TREE
# ==================================================================
TREE_BW, TREE_BH, TREE_GX, TREE_GY = 152, 48, 16, 70
REL_TYPES = ("MAY_MANIFEST_AS", "MAY_CAUSE", "MAY_PROGRESS_TO", "OCCURS_WITH")
REL_LABEL = {"MAY_MANIFEST_AS": "manifests as", "MAY_CAUSE": "may cause",
             "MAY_PROGRESS_TO": "progresses to", "OCCURS_WITH": "occurs with"}


def tree_members(root):
    kids = {}
    for e in EDGES:
        if e["edge"] == "SUBTYPE_OF" and e["from"] in NODES and e["to"] in NODES:
            kids.setdefault(e["to"], []).append(e["from"])
    for v in kids.values():
        v.sort()
    members, order = [], []

    def dfs(nid, depth):
        members.append(nid)
        order.append((nid, depth))
        for c in kids.get(nid, []):
            dfs(c, depth + 1)
    dfs(root, 0)
    return members, order, kids


def render_tree(root, title):
    members, order, kids = tree_members(root)
    mset = set(members)
    parent = {c: p for p, cs in kids.items() for c in cs if c in mset}
    depth = dict(order)

    # ---- tidy layout: leaves get sequential slots, parents centre over children
    x, next_leaf = {}, [0]
    def place(nid):
        cs = [c for c in kids.get(nid, []) if c in mset]
        if not cs:
            x[nid] = next_leaf[0]
            next_leaf[0] += 1
        else:
            for c in cs:
                place(c)
            x[nid] = (x[cs[0]] + x[cs[-1]]) / 2
    place(root)
    nleaves = next_leaf[0]
    X0, Y0 = 40, 84
    px = {nid: X0 + xi * (TREE_BW + TREE_GX) for nid, xi in x.items()}
    py = {nid: Y0 + depth[nid] * (TREE_BH + TREE_GY) for nid in members}
    W = int(X0 + (nleaves - 1) * (TREE_BW + TREE_GX) + TREE_BW + 40)
    maxdepth = max(depth.values())

    out_edges = []
    for e in EDGES:
        if e["edge"] in REL_TYPES and e["from"] in mset and e["to"] in mset:
            out_edges.append(e)
    out_edges.sort(key=lambda e: (e["edge"], e["from"], e["to"]))

    markers = {}
    defs = []
    for i, (t, c) in enumerate(sorted(EDGE_COLOR.items())):
        if t == "OCCURS_WITH":
            continue
        markers[t] = f"arr{i}"
        defs.append(f'<marker id="arr{i}" viewBox="0 0 12 10" refX="11" refY="5" markerWidth="13" '
                    f'markerHeight="11" markerUnits="userSpaceOnUse" orient="auto">'
                    f'<path d="M0,0 L12,5 L0,10 z" fill="{c}"/></marker>')

    # ---- gap channels: every relationship edge has one horizontal run in a
    # gap channel of its own, so a label on the run can never be ambiguous.
    # The tree's elbow bus rides at the bottom of each gap, below the channels.
    gap_k = {}
    def channel(gap):
        k = gap_k.get(gap, 0)
        gap_k[gap] = k + 1
        return Y0 + gap * (TREE_BH + TREE_GY) + TREE_BH + 7 + 9 * k
    side_exit, bot_exit, top_entry, bot_entry, riser_cnt = {}, {}, {}, {}, {}
    def side_y(nid, side):
        key = (nid, side)
        i = side_exit.get(key, 0)
        side_exit[key] = i + 1
        return py[nid] + 12 + 7 * i
    def riser_x(nid, side):
        # risers are shared per gutter across rows: boxes stacked in the same slot
        # share px, so keying by (px, side) keeps every riser at its own x
        key = (round(px[nid]), side)
        i = riser_cnt.get(key, 0)
        riser_cnt[key] = i + 1
        return px[nid] + TREE_BW + 4 + 5 * i if side == "r" else px[nid] - 4 - 5 * i
    def riser_ok(nid, side):
        return riser_cnt.get((round(px[nid]), side), 0) < 3
    def bot_x(nid):
        i = bot_exit.get(nid, 0)
        bot_exit[nid] = i + 1
        return px[nid] + 16 + 12 * i
    def top_in(nid):
        i = top_entry.get(nid, 0)
        top_entry[nid] = i + 1
        return px[nid] + 16 + 12 * i
    def bot_in(nid):
        i = bot_entry.get(nid, 0)
        bot_entry[nid] = i + 1
        return px[nid] + 16 + 12 * i

    edges_svg, rel_labels, labels_out = [], [], []

    # ---- tree connectors: parent bottom -> bus near child row -> child top
    for nid in members:
        if nid == root:
            continue
        p = parent[nid]
        x1, y1 = px[p] + TREE_BW / 2, py[p] + TREE_BH
        x2, y2 = px[nid] + TREE_BW / 2, py[nid]
        bus = y1 + TREE_GY - 14
        edges_svg.append(f'<path d="M{x1},{y1} V{bus} H{x2} V{y2}" fill="none" stroke="{RULE}" stroke-width="1.4"/>')

    # ---- relationship edges
    for e in out_edges:
        t = e["edge"]
        color = EDGE_COLOR[t]
        sf, st = e["from"], e["to"]
        ds, dt = depth[sf], depth[st]
        dash = ' stroke-dasharray="5 4"' if t == "OCCURS_WITH" else ""
        arrow = f' marker-end="url(#{markers[t]})"' if t in markers else ""
        if t == "OCCURS_WITH":
            # symmetric: exit the source's side, rise to the gap above the target,
            # enter the target's top edge
            side = "r" if (px[st] >= px[sf] and riser_ok(sf, "r")) else "l"
            if not riser_ok(sf, side):
                side = "r" if side == "l" else "l"
            ex = px[sf] + (TREE_BW if side == "r" else 0)
            ey = side_y(sf, side)
            rx = riser_x(sf, side)
            gap = max(dt - 1, 0)
            cy = channel(gap)
            tin = top_in(st)
            start_x = rx
            d = f'M{ex},{ey} H{rx} V{cy} H{tin} V{py[st]}'
        elif dt > ds:
            # down the tree: bottom exit, channel in the gap below, into the top edge
            bx = bot_x(sf)
            gap = ds
            cy = channel(gap)
            tin = top_in(st)
            start_x = bx
            d = f'M{bx},{py[sf] + TREE_BH} V{cy} H{tin} V{py[st]}'
        elif dt == ds:
            # same row: bottom exit, channel in the gap below, up into the bottom edge
            bx = bot_x(sf)
            gap = ds
            cy = channel(gap)
            tin = bot_in(st)
            start_x = bx
            d = f'M{bx},{py[sf] + TREE_BH} V{cy} H{tin} V{py[st] + TREE_BH}'
        else:
            # up the tree: exit the side facing the target, riser in the gutter,
            # channel in the gap below the target's row, up into the bottom edge
            want = "r" if px[st] >= px[sf] else "l"
            side = want if riser_ok(sf, want) else ("r" if want == "l" else "l")
            ex = px[sf] + (TREE_BW if side == "r" else 0)
            ey = side_y(sf, side)
            rx = riser_x(sf, side)
            gap = dt
            cy = channel(gap)
            tin = bot_in(st)
            start_x = rx
            d = f'M{ex},{ey} H{rx} V{cy} H{tin} V{py[st] + TREE_BH}'
        edges_svg.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.6"{dash}{arrow}/>')
        p = e.get("props", {})
        bits = []
        if p.get("typicality"):
            bits.append(TYP.get(p["typicality"], p["typicality"]))
        if p.get("specificity"):
            bits.append(SPEC.get(p["specificity"], p["specificity"]))
        rel_labels.append({"gap": gap, "type": t, "bits": bits, "color": color,
                           "cy": cy, "start_x": start_x, "entry_x": tin,
                           "below": dt >= ds and t != "OCCURS_WITH"})

    # ---- labels: on the channel run at the TARGET end, so runs that share a gap
    # carry their labels at different x. The edge-type word is included only when
    # the gap mixes types (or the edge has no properties to show). Labels sit above
    # their line, or below it when the channel runs beneath a row of boxes.
    gap_types = {}
    for rl in rel_labels:
        gap_types.setdefault(rl["gap"], set()).add(rl["type"])
    for rl in rel_labels:
        bits = list(rl["bits"])
        if len(gap_types[rl["gap"]]) > 1 or not bits:
            bits.insert(0, REL_LABEL[rl["type"]])
        label = " · ".join(bits)
        rightward = rl["entry_x"] >= rl["start_x"]
        if rightward:
            lx, anchor = rl["entry_x"] - 6, "end"
        else:
            lx, anchor = rl["entry_x"] + 6, "start"
        w = tw(label, 8.5) + 8
        rx0 = lx - 4 if anchor == "start" else lx - w + 4
        ry0 = rl["cy"] + 3 if rl["below"] else rl["cy"] - 16
        rel_labels_svg = (f'<rect x="{rx0}" y="{ry0}" width="{w}" height="14" rx="3" '
                          f'fill="#ffffff" fill-opacity="0.93"/>'
                          + txt(lx, ry0 + 11, label, 8.5, rl["color"], anchor=anchor, weight="600"))
        labels_out.append(rel_labels_svg)

    # ---- boxes: findings rounded, diagnoses chamfered, grouping dashed
    boxes = []
    for nid in members:
        n = NODES[nid]
        a, dark, bgc = ACCENT.get(n["node"], (MUTED, INK, "#f8fafc"))
        bx, by = px[nid], py[nid]
        if n["node"] == "Diagnosis":
            c = 9
            path = (f'M{bx + c},{by} H{bx + TREE_BW - c} L{bx + TREE_BW},{by + c} V{by + TREE_BH - c} '
                    f'L{bx + TREE_BW - c},{by + TREE_BH} H{bx + c} L{bx},{by + TREE_BH - c} V{by + c} Z')
            shape = f'<path d="{path}" fill="{bgc}" stroke="{a}" stroke-width="1.4"/>'
        else:
            dash = ' stroke-dasharray="5 3"' if n["node"] == "Grouping" else ""
            shape = f'<rect x="{bx}" y="{by}" width="{TREE_BW}" height="{TREE_BH}" rx="8" fill="{bgc}" stroke="{a}" stroke-width="1.4"{dash}/>'
        nm = wrap(n["name"], 10, TREE_BW - 14)
        if len(nm) > 2:
            nm = nm[:2]
            nm[-1] += " \u2026"
        lines = "".join(txt(bx + TREE_BW / 2, by + 16 + 11 * i, ln, 9.5, dark, anchor="middle", weight="600")
                        for i, ln in enumerate(nm))
        kid = txt(bx + TREE_BW / 2, by + TREE_BH - 6, f'{kind_of(nid)} · {nid}', 6.8, MUTED, anchor="middle")
        boxes.append(f'<g data-node="{esc(nid)}">{shape}{lines}{kid}</g>')

    # legend
    ly = Y0 - 34
    leg = [txt(X0, ly, title, 15, INK, weight="700")]
    lx = X0
    ly2 = Y0 - 12
    for t in REL_TYPES:
        c = EDGE_COLOR[t]
        dash = ' stroke-dasharray="4 3"' if t == "OCCURS_WITH" else ""
        arrow = f' marker-end="url(#{markers[t]})"' if t in markers else ""
        leg.append(f'<path d="M{lx},{ly2} h26" stroke="{c}" stroke-width="1.6"{dash}{arrow}/>')
        leg.append(txt(lx + 32, ly2 + 3, REL_LABEL[t], 8.5, INK))
        lx += 32 + tw(REL_LABEL[t], 8.5) + 18
    leg.append(f'<path d="M{lx},{ly2} h26" stroke="{RULE}" stroke-width="1.4"/>')
    leg.append(txt(lx + 32, ly2 + 3, "is a (subtype of)", 8.5, INK))

    H = Y0 + maxdepth * (TREE_BH + TREE_GY) + TREE_BH + TREE_GY
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="system-ui, sans-serif" '
           f'role="img" aria-label="{esc(title)} — is-a family tree">',
           f'<defs>{"".join(defs)}</defs>',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
    out.extend(edges_svg)
    out.extend(boxes)
    # labels paint last: each sits on its edge's own channel run, halo over any crossing
    out.extend(labels_out)
    out.extend(leg)
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ==================================================================
if __name__ == "__main__":
    mode, hub, title = sys.argv[1], sys.argv[2], sys.argv[3]
    if mode == "mat":
        sys.stdout.write(render_mat(hub, title))
    else:
        sys.stdout.write(render_tree(hub, title))
