#!/usr/bin/env python3
"""Alt 2 ("annotated outline"): the taxonomy as an indented document, the typed
relationships as numbered margin notes.

Design: the diagram reads like a page from a structured textbook. The left two-thirds
are an outline of the subtype tree — one row per class, indentation for subsumption,
tree guides, kind pills (FINDING / DIAGNOSIS / GROUPING) and inline green element tags
and amber scope tags. Rows are numbered in the gutter like a document. The right margin
holds one numbered note per typed relationship (MAY_CAUSE, MAY_MANIFEST_AS,
MAY_PROGRESS_TO, OCCURS_WITH), vertically aligned with its source row and connected by
a short leader. Each note carries the edge type as a colored chip, the target name, a
bar meter for typicality, a shape glyph for specificity, and the `expected` hint as an
italic line. Target rows carry a back-reference pill ("◂ n3"), so a reader can trace an
edge in either direction without any line ever crossing the outline. SUBTYPE_OF never
produces a note — it is the indentation.

Deterministic layout: DFS preorder over the subtype forest (children sorted by id)
assigns rows; nodes with no subtype edge into the tree fall into a second section,
causes (MAY_CAUSE sources outside the tree) into a third. Notes are numbered in
(source-row, edge type, target-row) order and placed at their source row, pushed down
on collision. All geometry derives from row count and note count.

Usage: gen_alt2.py pleural-effusion | pyelonephritis > out.svg
"""
import sys, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "docs", "next-gen-schema", "tools"))
from graph import load_graph  # noqa: E402

G = load_graph()
NODES, EDGES = G.nodes, G.edges

INK, MUTED, RULE, HAIR = "#1f2937", "#64748b", "#cbd5e1", "#eef2f7"
GREEN, GREEN_DARK, GREEN_BG = "#16a34a", "#14532d", "#f0fdf4"
AMBER, AMBER_DARK, AMBER_BG = "#d97706", "#78350f", "#fffbeb"
KIND_COLOR = {"FindingClass": "#2563eb", "Diagnosis": "#7c3aed", "Grouping": "#64748b"}
KIND_LABEL = {"FindingClass": "FINDING", "Diagnosis": "DIAGNOSIS", "Grouping": "GROUPING"}
EDGE_STYLE = {"MAY_CAUSE": ("#dc2626", "CAUSES", "\u2192"),
              "MAY_MANIFEST_AS": ("#7c3aed", "MANIFESTS AS", "\u2192"),
              "MAY_PROGRESS_TO": ("#0891b2", "PROGRESSES TO", "\u2192"),
              "OCCURS_WITH": ("#64748b", "OCCURS WITH", "\u2194")}
TYP_RANK = {"obligate": 5, "very_frequent": 4, "frequent": 3, "occasional": 2,
            "very_rare": 1, "excluded": 0}
TXT = {"very_frequent": "very frequent", "highly_suggestive": "highly suggestive"}
SPEC_LABEL = {"pathognomonic": "pathognomonic", "highly_suggestive": "highly suggestive",
              "suggestive": "suggestive"}

ROW_H, SUB_H, SEC_H = 34, 20, 30
GUT_X, TREE_X, INDENT = 24, 60, 26
OUT_R = 852                    # outline right edge
NOTE_X, NOTE_W = 876, 340      # margin notes


def esc(s):
    return html.escape(str(s), quote=True)


def tw(s, fs, bold=False):
    return len(str(s)) * fs * (0.60 if bold else 0.56)


def txt(x, y, s, fs, fill, anchor="start", weight=None, style=None, spacing=None):
    a = f' x="{x}" y="{y}" font-size="{fs}" fill="{fill}" text-anchor="{anchor}"'
    if weight: a += f' font-weight="{weight}"'
    if style: a += f' font-style="{style}"'
    if spacing: a += f' letter-spacing="{spacing}"'
    return f"<text{a}>{esc(s)}</text>"


def name_of(nid):
    return NODES.get(nid, {"name": nid})["name"]


def elements_of(nid):
    out = []
    for e in EDGES:
        if e["edge"] == "HAS_ELEMENT" and e["from"] == nid:
            p = e.get("props", {})
            s = name_of(e["to"])
            if p.get("note"):
                s += f": {p['note']}"
            if p.get("required"):
                s += " (required)"
            out.append(s)
    return out


def scope_of(nid):
    for e in EDGES:
        if e["edge"] == "SCOPED_TO" and e["from"] == nid:
            return name_of(e["to"])
    return None


def interp_from(nid):
    for e in EDGES:
        if e["edge"] == "INTERPRETED_FROM" and e["from"] == nid:
            return e["to"]
    return None


def spec_glyph(x, y, specificity, color):
    k = {"pathognomonic": "diamond", "highly_suggestive": "triangle", "suggestive": "disc"}.get(specificity)
    if k == "diamond":
        return f'<path d="M{x},{y-5} L{x+5},{y} L{x},{y+5} L{x-5},{y} Z" fill="{color}"/>'
    if k == "triangle":
        return f'<path d="M{x},{y-5} L{x+4.5},{y+4} L{x-4.5},{y+4} Z" fill="{color}"/>'
    if k == "disc":
        return f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>'
    return f'<circle cx="{x}" cy="{y}" r="4" fill="#fff" stroke="{color}" stroke-width="1.4"/>'


def meter(x, y, rank, color):
    out = []
    for i in range(5):
        filled = i < rank
        out.append(f'<rect x="{x + i * 7}" y="{y}" width="5" height="9" rx="1" '
                   f'fill="{color if filled else "#e2e8f0"}"/>')
    return "".join(out)


# -----------------------------------------------------------------
# View construction: pure function of the graph.
# -----------------------------------------------------------------
def build_view(grouping_id, include):
    include = set(include)
    children = {}
    for e in EDGES:
        if e["edge"] == "SUBTYPE_OF" and e["from"] in include and e["to"] in include:
            children.setdefault(e["to"], []).append(e["from"])
    for c in children.values():
        c.sort()                       # by id: canonical order
    rows = []                          # (nid, depth)
    def dfs(nid, d):
        rows.append((nid, d))
        for c in children.get(nid, []):
            dfs(c, d + 1)
    dfs(grouping_id, 0)
    in_tree = {n for n, _ in rows}
    cause_srcs = sorted({e["from"] for e in EDGES if e["edge"] == "MAY_CAUSE"
                         and e["to"] in include and e["from"] not in in_tree},
                        key=name_of)
    rest = sorted(include - in_tree - set(cause_srcs), key=name_of)
    return rows, rest, cause_srcs


def notes_for(include):
    include = set(include)
    out = []
    for e in EDGES:
        if e["edge"] in EDGE_STYLE and e["from"] in include and e["to"] in include:
            out.append(e)
    return out


# -----------------------------------------------------------------
def render(title, aria, grouping_id, include, sec2_label, sec3_label, sublines):
    rows, rest, cause_srcs = build_view(grouping_id, include)
    row_no, row_y = {}, {}
    outline = []
    y = 78

    def sec(label):
        nonlocal y
        outline.append(txt(GUT_X, y + 10, label, 9, MUTED, weight="700", spacing="1.2"))
        outline.append(f'<line x1="{GUT_X}" y1="{y + 16}" x2="{OUT_R}" y2="{y + 16}" stroke="{RULE}"/>')
        y += SEC_H

    def class_row(nid, depth):
        nonlocal y
        no = len(row_no) + 1
        row_no[nid] = no
        row_y[nid] = y
        mid = y + ROW_H / 2
        n = NODES[nid]
        color = KIND_COLOR[n["node"]]
        outline.append(f'<line x1="{GUT_X}" y1="{y + ROW_H}" x2="{OUT_R}" y2="{y + ROW_H}" stroke="{HAIR}"/>')
        outline.append(txt(GUT_X, mid + 3, str(no), 8.5, MUTED))
        x = TREE_X + depth * INDENT
        if depth:  # tree elbow: vertical from the parent's row middle to this row
            xv = TREE_X + (depth - 1) * INDENT + 4
            p_mid = row_y[rows_parent[nid]] + ROW_H / 2
            outline.append(f'<path d="M{xv},{p_mid} V{mid} H{x}" fill="none" stroke="{RULE}" stroke-width="1.2"/>')
        # kind pill
        kl = KIND_LABEL[n["node"]]
        kw = tw(kl, 7.5, bold=True) + 14
        outline.append(f'<rect x="{x}" y="{mid - 8}" width="{kw}" height="15" rx="7.5" fill="{color}"/>'
                       + txt(x + kw / 2, mid + 3, kl, 7.5, "#ffffff", anchor="middle", weight="700"))
        x += kw + 8
        outline.append(txt(x, mid + 4, n["name"], 12, INK, weight="600"))
        x += tw(n["name"], 12, bold=True) + 14
        # inline tags: scope (amber), negative-only (gray), elements (green, if they fit)
        elems = elements_of(nid)
        sc = scope_of(nid)
        gscope = scope_of(grouping_id)
        differs = bool(sc and gscope and sc != gscope)
        if n["node"] == "Grouping":
            ng = "negative-only"
            ngw = tw(ng, 8) + 14
            outline.append(f'<rect x="{x}" y="{mid - 8}" width="{ngw}" height="15" rx="7.5" fill="#f1f5f9" stroke="{RULE}"/>'
                           + txt(x + ngw / 2, mid + 2.5, ng, 8, "#334155", anchor="middle", style="italic"))
            x += ngw + 8
        if sc:
            sw = tw("scope: " + sc, 8, bold=differs) + 14
            outline.append(f'<rect x="{x}" y="{mid - 8}" width="{sw}" height="15" rx="7.5" fill="{AMBER_BG}" stroke="{AMBER}"/>'
                           + txt(x + sw / 2, mid + 2.5, "scope: " + sc, 8, AMBER_DARK, anchor="middle",
                                 weight="700" if differs else None))
            x += sw + 8
        etext = "binds: " + " · ".join(elems) if elems else ""
        if nid not in sublines:    # caller-supplied sub-lines replace the auto element line
            if etext and x + tw(etext, 8.5) < OUT_R - 90:
                outline.append(txt(x, mid + 3, etext, 8.5, GREEN_DARK))
            elif etext:
                sublines.setdefault(nid, []).append((etext, GREEN_DARK))
        b = interp_from(nid)
        if b:
            sublines.setdefault(nid, []).append(
                (f"interpreted from binding {b} (kidney HAS_ELEMENT length)", GREEN_DARK))
        y += ROW_H
        for line, color_ in sublines.get(nid, []):
            outline.append(txt(TREE_X + depth * INDENT + 4, y + 12, line, 8.5, color_))
            y += SUB_H

    # parent map for tree elbows
    rows_parent = {}
    stack = []
    for nid, d in rows:
        while stack and stack[-1][1] >= d:
            stack.pop()
        if stack:
            rows_parent[nid] = stack[-1][0]
        stack.append((nid, d))

    sec("THE TAXONOMY — ONE SUBTYPE TREE OVER FINDINGS, DIAGNOSES, AND THE GROUPING NODE")
    for nid, d in rows:
        class_row(nid, d)
    if rest:
        sec(sec2_label)
        for nid in rest:
            class_row(nid, 0)
    if cause_srcs:
        sec(sec3_label)
        for nid in cause_srcs:
            class_row(nid, 0)

    out_h = y + 20

    # ---- margin notes ----
    notes = notes_for(include)
    notes.sort(key=lambda e: (row_no.get(e["from"], 999), e["edge"], row_no.get(e["to"], 999)))
    note_no = {id(e): i + 1 for i, e in enumerate(notes)}
    targets = {}
    for e in notes:
        targets.setdefault(e["to"], []).append(note_no[id(e)])

    # back-reference pills on target rows
    back = []
    for nid, nos in targets.items():
        compact = " ".join(f"n{n}" for n in sorted(nos))
        back.append(txt(OUT_R - 6, row_y[nid] + ROW_H / 2 + 3, "\u25c2 " + compact, 8, MUTED, anchor="end"))

    # note placement: prefer source row center, push down on collision
    placed = []
    notes_svg, leaders = [], []
    prev_bottom = 76
    for e in notes:
        i = note_no[id(e)]
        color, verb, arrow = EDGE_STYLE[e["edge"]]
        p = e.get("props", {})
        lines2 = []
        extra = []
        if p.get("expected"):
            extra.append("expect: " + " · ".join(p["expected"].values()))
        if p.get("note"):
            extra.extend(p["note"].split("; "))
        nh = 54 + 13 * len(extra)
        src_mid = row_y[e["from"]] + ROW_H / 2
        ny = max(src_mid - 17, prev_bottom + 8)
        prev_bottom = ny + nh
        cy = ny + 16
        # leader from source row right edge to the note
        if abs(cy - src_mid) <= 4:
            leaders.append(f'<path d="M{OUT_R},{src_mid} H{NOTE_X - 8}" stroke="{color}" stroke-width="1" opacity="0.55"/>')
        else:
            leaders.append(f'<path d="M{OUT_R},{src_mid} H{NOTE_X - 16} V{cy} H{NOTE_X - 8}" fill="none" '
                           f'stroke="{color}" stroke-width="1" opacity="0.55"/>')
        # note card
        notes_svg.append(f'<rect x="{NOTE_X - 8}" y="{ny}" width="{NOTE_W}" height="{nh}" rx="6" '
                         f'fill="#ffffff" stroke="{color}" stroke-width="1"/>')
        notes_svg.append(f'<circle cx="{NOTE_X + 4}" cy="{cy}" r="9" fill="{color}"/>'
                         + txt(NOTE_X + 4, cy + 3, f"n{i}", 8, "#fff", anchor="middle", weight="700"))
        vw = tw(verb, 7.5, bold=True) + 14
        notes_svg.append(f'<rect x="{NOTE_X + 18}" y="{cy - 7}" width="{vw}" height="14" rx="7" fill="{color}"/>'
                         + txt(NOTE_X + 18 + vw / 2, cy + 3, verb, 7.5, "#fff", anchor="middle", weight="700"))
        notes_svg.append(txt(NOTE_X + 18 + vw + 8, cy + 3, f"{arrow} {name_of(e['to'])}", 10.5, INK, weight="600"))
        # meter + typicality + specificity on the second line, extras below
        my = ny + 34
        typ = p.get("typicality")
        mx = NOTE_X + 18
        if typ:
            notes_svg.append(meter(mx, my, TYP_RANK.get(typ, 0), color))
            notes_svg.append(txt(mx + 42, my + 8, TXT.get(typ, typ), 8.5, INK))
            mx += 42 + tw(TXT.get(typ, typ), 8.5) + 12
        if e["edge"] == "MAY_MANIFEST_AS":
            spec = p.get("specificity")
            notes_svg.append(spec_glyph(mx + 4, my + 4.5, spec, "#7c3aed"))
            notes_svg.append(txt(mx + 12, my + 8, SPEC_LABEL.get(spec, "no specificity asserted"), 8.5, INK))
        for j, xl in enumerate(extra):
            notes_svg.append(txt(NOTE_X + 18, ny + 54 + 13 * j, xl, 8, MUTED, style="italic"))
        placed.append((ny, nh))

    H = max(out_h, prev_bottom) + 64
    W = 1240
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="system-ui, sans-serif" '
           f'role="img" aria-label="{esc(aria)}">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           txt(GUT_X, 32, title, 16, INK, weight="700"),
           txt(GUT_X, 52, "Indentation is subsumption; numbered margin notes are the typed relationships. "
                          "\u25c2 n markers on a row are the relationships that point at it.", 9, MUTED),
           txt(NOTE_X - 8, 66, "RELATIONSHIP NOTES", 9, MUTED, weight="700", spacing="1.2")]
    out += leaders          # leaders under the outline rows
    out += outline
    out += back
    out += notes_svg
    # legend strip
    ly = H - 30
    out.append(f'<rect x="{GUT_X}" y="{ly - 14}" width="{W - 48}" height="30" rx="8" fill="#f8fafc" stroke="{RULE}" stroke-width="0.8"/>')
    lx = GUT_X + 12
    for typ, rank in (("obligate", 5), ("very frequent", 4), ("frequent", 3), ("occasional", 2)):
        out.append(meter(lx, ly - 2, rank, "#475569"))
        out.append(txt(lx + 40, ly + 6, typ, 8.5, INK))
        lx += 40 + tw(typ, 8.5) + 18
    lx += 10
    for spec, label in (("pathognomonic", "pathognomonic"), ("highly_suggestive", "highly suggestive"),
                        ("suggestive", "suggestive"), (None, "none asserted")):
        out.append(spec_glyph(lx + 4, ly + 2, spec, "#7c3aed"))
        out.append(txt(lx + 12, ly + 6, label, 8.5, INK))
        lx += 12 + tw(label, 8.5) + 18
    out.append("</svg>")
    return "\n".join(out) + "\n"


# =================================================================
if __name__ == "__main__":
    which = sys.argv[1]
    if which == "pleural-effusion":
        include = ["RDE2_000516", "RDE2_000502", "RDE2_000510", "RDE2_000511", "RDE2_000512",
                   "RDE2_000513", "RDE2_000514", "RDE2_000515", "RDE2_000520", "RDE2_000521",
                   "RDE2_000522", "RDE2_000523", "RDE2_000524", "RDE2_000525", "RDE2_000526",
                   "RDE2_000530", "RDE2_000531", "RDE2_000532", "RDE2_000533", "RDE2_000534"]
        sublines = {"RDE2_000502": [
            ("binds: presence (required) · change from prior · size (qualitative): amount · "
             "fluid attenuation · internal complexity (multi-select)", GREEN_DARK),
            ("internal complexity values: septations · loculation · gas · dependent debris · fluid-fluid level", MUTED)]}
        print(render("Pleural effusion — annotated outline: taxonomy as a document, relationships as margin notes",
                     "Pleural effusion as an indented outline with numbered margin notes for the typed relationships",
                     "RDE2_000516", include,
                     "ATTACHED BY RELATIONSHIP ONLY — NO SUBSUMPTION EDGE",
                     "CLINICAL CAUSES — DIAGNOSIS NODES WITH NO IMAGING ELEMENTS",
                     sublines))
    else:
        include = ["RDE2_000814", "RDE2_000800", "RDE2_000801", "RDE2_000802", "RDE2_000803",
                   "RDE2_000804", "RDE2_000805", "RDE2_000806", "RDE2_000807", "RDE2_000808",
                   "RDE2_000809", "RDE2_000811", "RDE2_000812", "RDE2_000813"]
        print(render("Acute pyelonephritis — annotated outline: taxonomy as a document, relationships as margin notes",
                     "Acute pyelonephritis as an indented outline with numbered margin notes for the typed relationships",
                     "RDE2_000814", include, "", "", {}))
