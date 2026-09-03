#!/usr/bin/env python3
"""Alt 1 ("flow"): typicality as band width, specificity as a glyph at the arrowhead.

Design: causal and manifestation relationships are drawn as bands whose width encodes
typicality (thicker = more expected) and whose arrowhead carries a shape glyph for
specificity (diamond = pathognomonic, triangle = highly suggestive, disc = suggestive,
open circle = none asserted). Every band label sits at the SOURCE end of its band, so
under fan-in the reader never wonders which label belongs to which edge; `expected`
hints ride inside the cause chip itself, maximally attached. Subsumption is never a
band: the taxonomy is a tree descending from the grouping node through the anchor to
its subtypes, drawn as trunk-and-branch connectors. Bindings ride inside the node
cards as green element text; anatomic scope rides as an amber line.

Deterministic layout: fixed columns (causes | anchor + subtype tree | related
findings, resp. diagnosis tree | findings). Rows stack in view-spec order; band slots
on the anchor are assigned in source order, which keeps the fan-in planar. Relations
that cannot be routed in the gutter without crossing chips (a cause targeting the
bottom of the far column) detour through the free channel at the diagram's edge.
All geometry is computed from the view spec only.

Usage: gen_alt1.py pleural-effusion | pyelonephritis > out.svg
"""
import sys, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "docs", "next-gen-schema", "tools"))
from graph import load_graph  # noqa: E402

G = load_graph()
NODES, EDGES = G.nodes, G.edges

# ---- palette (same visual language as the existing renderers) ----
ACCENT = {
    "FindingClass":     ("#2563eb", "#1e3a8a", "#eff6ff"),
    "Diagnosis":        ("#7c3aed", "#4c1d95", "#f5f3ff"),
    "Grouping":         ("#64748b", "#334155", "#f8fafc"),
    "DataElement":      ("#16a34a", "#14532d", "#f0fdf4"),
    "AnatomicLocation": ("#d97706", "#78350f", "#fffbeb"),
}
INK, MUTED, RULE = "#1f2937", "#64748b", "#cbd5e1"
GREEN, GREEN_DARK, GREEN_BG = "#16a34a", "#14532d", "#f0fdf4"
AMBER, AMBER_DARK, AMBER_BG = "#d97706", "#78350f", "#fffbeb"
C_RED, C_MAN, C_PROG, C_OCC, C_SUB = "#dc2626", "#7c3aed", "#0891b2", "#64748b", "#94a3b8"

TYP_W = {"obligate": 13, "very_frequent": 10, "frequent": 7, "occasional": 4.5,
         "very_rare": 3, "excluded": 2}
TYP_TXT = {"very_frequent": "very frequent", "highly_suggestive": "highly suggestive"}


def esc(s):
    return html.escape(str(s), quote=True)


def tw(s, fs):
    return len(str(s)) * fs * 0.56


def txt(x, y, s, fs, fill, anchor="start", weight=None, style=None, spacing=None, rotate=None):
    a = f' x="{x}" y="{y}" font-size="{fs}" fill="{fill}" text-anchor="{anchor}"'
    if weight: a += f' font-weight="{weight}"'
    if style: a += f' font-style="{style}"'
    if spacing: a += f' letter-spacing="{spacing}"'
    if rotate: a += f' transform="rotate({rotate} {x} {y})"'
    return f"<text{a}>{esc(s)}</text>"


def halo_label(x, y, s, fs, color, anchor="start"):
    """Edge label with a white halo, anchored at the SOURCE end of a band."""
    w = tw(s, fs) + 8
    rx = x - 4 if anchor == "start" else x - w + 4
    return (f'<rect x="{rx}" y="{y - fs - 3}" width="{w}" height="{fs + 7}" rx="3" '
            f'fill="#ffffff" fill-opacity="0.92"/>'
            + txt(x, y, s, fs, color, anchor))


def bez(sx, sy, tx, ty):
    dx = (tx - sx) / 2
    return f"M{sx},{sy} C{sx + dx},{sy} {tx - dx},{ty} {tx},{ty}"


def bez_pt(sx, sy, tx, ty, t):
    dx = (tx - sx) / 2
    cx1, cy1, cx2, cy2 = sx + dx, sy, tx - dx, ty
    mt = 1 - t
    x = mt**3 * sx + 3 * mt * mt * t * cx1 + 3 * mt * t * t * cx2 + t**3 * tx
    y = mt**3 * sy + 3 * mt * mt * t * cy1 + 3 * mt * t * t * cy2 + t**3 * ty
    return x, y


MARKERS = {}
def marker_defs(colors):
    """Fixed-size arrowheads (userSpaceOnUse) so marker size never scales with band width."""
    out = []
    for i, c in enumerate(sorted(set(colors))):
        MARKERS[c] = f"arr{i}"
        out.append(f'<marker id="arr{i}" viewBox="0 0 12 10" refX="11" refY="5" '
                   f'markerWidth="15" markerHeight="13" markerUnits="userSpaceOnUse" '
                   f'orient="auto"><path d="M0,0 L12,5 L0,10 z" fill="{c}"/></marker>')
    return "".join(out)


GLYPHS = {"pathognomonic": "diamond", "highly_suggestive": "triangle", "suggestive": "disc"}


def spec_glyph(x, y, specificity, color):
    """Specificity as a shape just behind the arrowhead."""
    k = GLYPHS.get(specificity)
    if k == "diamond":
        return f'<path d="M{x},{y-6} L{x+6},{y} L{x},{y+6} L{x-6},{y} Z" fill="{color}" stroke="#fff" stroke-width="1"/>'
    if k == "triangle":
        return f'<path d="M{x},{y-6} L{x+5.5},{y+4.5} L{x-5.5},{y+4.5} Z" fill="{color}" stroke="#fff" stroke-width="1"/>'
    if k == "disc":
        return f'<circle cx="{x}" cy="{y}" r="4.5" fill="{color}" stroke="#fff" stroke-width="1"/>'
    return f'<circle cx="{x}" cy="{y}" r="4.5" fill="#fff" stroke="{color}" stroke-width="1.6"/>'  # none asserted


def band(sx, sy, tx, ty, color, width, dash=None, arrow=True, glyph_spec=None):
    a = (f'<path d="{bez(sx, sy, tx, ty)}" fill="none" stroke="{color}" stroke-width="{width}"'
         f' stroke-linecap="round"')
    if dash: a += ' stroke-dasharray="5 4"'
    if arrow: a += f' marker-end="url(#{MARKERS[color]})"'
    a += "/>"
    if glyph_spec is not None:
        gx, gy = bez_pt(sx, sy, tx, ty, 0.84)
        a += spec_glyph(round(gx, 1), round(gy, 1), glyph_spec if glyph_spec != "__none__" else None, color)
    return a


def name_of(nid):
    return NODES.get(nid, {"name": nid})["name"]


def elem_name(nid):
    n = NODES.get(nid)
    return n["name"] if n else nid


def elements_of(nid):
    out = []
    for e in EDGES:
        if e["edge"] == "HAS_ELEMENT" and e["from"] == nid:
            p = e.get("props", {})
            out.append((elem_name(e["to"]), bool(p.get("required")), p.get("note")))
    return out


def scope_of(nid):
    for e in EDGES:
        if e["edge"] == "SCOPED_TO" and e["from"] == nid:
            return name_of(e["to"]), e["to"]
    return None


def pills(x, y, items, kind="green", fs=9):
    fg, bg, brd = ((GREEN_DARK, GREEN_BG, GREEN) if kind == "green"
                   else (AMBER_DARK, AMBER_BG, AMBER) if kind == "amber"
                   else (MUTED, "#f8fafc", RULE))
    out, cx = [], x
    for s in items:
        w = tw(s, fs) + 14
        out.append(f'<rect x="{cx}" y="{y}" width="{w}" height="17" rx="8.5" fill="{bg}" stroke="{brd}" stroke-width="0.8"/>'
                   + txt(cx + 7, y + 12, s, fs, fg))
        cx += w + 6
    return "".join(out)


def chip(x, y, w, h, nid, sub=None, sub2=None, sub2_color=None):
    n = NODES[nid]
    a, dark, bg = ACCENT.get(n["node"], ACCENT["Grouping"])
    fs = min(12.5, (w - 26) / max(1, len(n["name"]) * 0.6))
    out = [f'<g data-node="{esc(nid)}">',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{bg}" stroke="{RULE}"/>',
           f'<rect x="{x}" y="{y}" width="4" height="{h}" rx="2" fill="{a}"/>',
           txt(x + 14, y + 18, n["name"], round(fs, 1), dark, weight="600")]
    if sub:
        out.append(txt(x + 14, y + 32, sub, 8.5, MUTED))
    if sub2:
        out.append(txt(x + 14, y + 46, sub2, 8, sub2_color or MUTED, style="italic"))
    out.append("</g>")
    return "".join(out)


def kind_sub(nid, extra=None):
    n = NODES[nid]
    base = {"FindingClass": "finding", "Diagnosis": "diagnosis", "Grouping": "grouping"}[n["node"]]
    bits = [base]
    if extra:
        bits.append(extra)
    return " · ".join(bits)


def grouping_band(x, w, y, node_id, negated_example):
    """The grouping node as a loud dashed band, not a quiet chip."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="36" rx="6" fill="#f8fafc" '
            f'stroke="{C_SUB}" stroke-width="1.4" stroke-dasharray="6 3"/>'
            + txt(x + 12, y + 14, "GROUPING · NEGATIVE-ONLY", 8.5, MUTED, weight="700", spacing="0.8")
            + txt(x + 12, y + 29, name_of(node_id), 11.5, "#334155", weight="700")
            + txt(x + w + 10, y + 22, f'asserted only as \u201c{negated_example}\u201d', 8.5, MUTED, style="italic"))


def legend(W, H):
    ly = H - 46
    out = [f'<rect x="24" y="{ly - 16}" width="{W - 48}" height="40" rx="8" fill="#f8fafc" stroke="{RULE}" stroke-width="0.8"/>',
           band(40, ly + 4, 118, ly + 4, C_MAN, TYP_W["frequent"], glyph_spec="highly_suggestive"),
           txt(128, ly + 8, "band width = typicality (thicker = more expected)", 9.5, INK)]
    gx = 446
    for spec, label in (("pathognomonic", "pathognomonic"), ("highly_suggestive", "highly suggestive"),
                        ("suggestive", "suggestive"), (None, "none asserted")):
        out.append(spec_glyph(gx, ly + 4, spec, C_MAN))
        out.append(txt(gx + 10, ly + 8, label, 9.5, INK))
        gx += 30 + tw(label, 9.5)
    out.append(f'<path d="M{gx + 6},{ly + 4} h40" stroke="{C_OCC}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    out.append(txt(gx + 54, ly + 8, "co-occurrence (symmetric)", 9.5, INK))
    gx += 54 + tw("co-occurrence (symmetric)", 9.5) + 16
    out.append(f'<path d="M{gx},{ly + 4} h34" stroke="{C_PROG}" stroke-width="2.4" marker-end="url(#{MARKERS[C_PROG]})"/>')
    out.append(txt(gx + 42, ly + 8, "progression", 9.5, INK))
    out.append(txt(24, H - 6, "* = required element · causal bands carry no specificity glyph by design (an effusion points nowhere in particular)",
                   8.5, MUTED))
    return "".join(out)


def svg_open(W, H, aria):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'font-family="system-ui, sans-serif" role="img" aria-label="{esc(aria)}">'
            f'<rect width="{W}" height="{H}" fill="#ffffff"/>')


# =================================================================
# Pleural effusion: causes fan in from the left, subtype tree descends
# from the anchor, manifestations flow out to the right.
# =================================================================
def render_pleural():
    W = 1214
    LX, LW = 24, 280            # causes column (ends 304)
    CX, CW = 430, 320           # anchor column (430..750)
    TX = CX + 36                # subtype tree indent
    RX, RW = 856, 334           # related findings column
    ANCHOR = "RDE2_000502"

    causes = [  # view order: typicality rank desc, then name
        "RDE2_000520",  # heart failure      frequent
        "RDE2_000526",  # nephrotic syndrome frequent
        "RDE2_000523",  # pancreatitis       occasional
        "RDE2_000522",  # pneumonia          frequent
        "RDE2_000525",  # pulmonary embolism frequent
        "RDE2_000521",  # cirrhosis          occasional -> hepatic hydrothorax
        "RDE2_000524",  # malignant neoplasm occasional -> malignant pleural effusion
    ]
    subtypes = ["RDE2_000515", "RDE2_000510", "RDE2_000511",
                "RDE2_000512", "RDE2_000514", "RDE2_000513"]
    right = ["RDE2_000530", "RDE2_000531", "RDE2_000532", "RDE2_000533", "RDE2_000534"]

    cause_edges = {e["from"]: e for e in EDGES if e["edge"] == "MAY_CAUSE" and e["from"] in causes}
    anchor_in = [c for c in causes if cause_edges[c]["to"] == ANCHOR]

    CAUSE_Y0, CAUSE_PITCH, CAUSE_H = 92, 68, 56
    cause_y = {c: CAUSE_Y0 + i * CAUSE_PITCH for i, c in enumerate(causes)}
    CARD_Y, CARD_H = 130, 112
    slots = {c: CARD_Y + 18 + 18 * i for i, c in enumerate(anchor_in)}
    TREE_Y0, TREE_PITCH, TREE_H = 266, 54, 40
    tree_y = {s: TREE_Y0 + i * TREE_PITCH for i, s in enumerate(subtypes)}
    RIGHT_Y0, RIGHT_PITCH, RIGHT_H = 150, 82, 64
    right_y = {r: RIGHT_Y0 + i * RIGHT_PITCH for i, r in enumerate(right)}

    H = max(tree_y[subtypes[-1]] + TREE_H, cause_y[causes[-1]] + CAUSE_H,
            right_y[right[-1]] + RIGHT_H + 14) + 96

    out = [svg_open(W, H, "Pleural effusion: causes flow in from the left as bands whose width encodes typicality, with expected hints inside each cause chip; diagnosis subtypes descend as a tree; manifestations flow out right with specificity glyphs at the arrowheads.")]
    out.append(txt(24, 34, "Pleural effusion — flow layout: band width = typicality, arrowhead glyph = specificity",
                   16, INK, weight="700"))
    for x, label in ((LX, "CLINICAL CAUSES"), (CX, "THE FINDING AND ITS DIAGNOSIS SUBTYPES"),
                     (RX, "RELATED FINDINGS")):
        out.append(txt(x, 66, label, 10, MUTED, weight="600", spacing="1.2"))

    # ---- taxonomy: grouping band, trunk, anchor card, subtype tree ----
    out.append(grouping_band(CX - 20, CW + 40, 78, "RDE2_000516", "no pleural abnormality"))
    out.append(f'<path d="M{CX + 40},114 V{CARD_Y}" stroke="{C_SUB}" stroke-width="3"/>')

    n = NODES[ANCHOR]
    out.append(f'<g data-node="{ANCHOR}">'
               f'<rect x="{CX}" y="{CARD_Y}" width="{CW}" height="{CARD_H}" rx="9" '
               f'fill="{ACCENT["FindingClass"][2]}" stroke="{ACCENT["FindingClass"][0]}" stroke-width="1.6"/>'
               + txt(CX + 14, CARD_Y + 22, n["name"], 15, ACCENT["FindingClass"][1], weight="700")
               + txt(CX + 14, CARD_Y + 37, "finding · RADLEX RID34539 · SNOMEDCT 60046008", 8.5, MUTED)
               + txt(CX + 14, CARD_Y + 54, "elements: presence * · change from prior · size: amount", 9.5, GREEN_DARK)
               + txt(CX + 14, CARD_Y + 69, "fluid attenuation (HU) · internal complexity (multi):", 9.5, GREEN_DARK)
               + txt(CX + 14, CARD_Y + 83, "septations · loculation · gas · dependent debris · fluid-fluid level", 7.5, MUTED)
               + txt(CX + 14, CARD_Y + 100, "scoped to pleural space (RID1363)", 9.5, AMBER_DARK, weight="600")
               + "</g>")

    # subtype tree (subsumption as descent)
    guide_x = TX - 18
    out.append(f'<path d="M{CX + 40},{CARD_Y + CARD_H} V{TREE_Y0 - 12} H{guide_x} '
               f'V{tree_y[subtypes[-1]] + TREE_H / 2}" fill="none" stroke="{C_SUB}" stroke-width="1.6"/>')
    for s in subtypes:
        my = tree_y[s] + TREE_H / 2
        out.append(f'<path d="M{guide_x},{my} H{TX}" stroke="{C_SUB}" stroke-width="1.6"/>')
        out.append(chip(TX, tree_y[s], CW - 36, TREE_H, s, kind_sub(s, "binds presence *")))

    # progression parapneumonic -> empyema (teal), routed left of the tree guide
    py0 = tree_y["RDE2_000515"] + TREE_H / 2
    py1 = tree_y["RDE2_000510"] + TREE_H / 2
    px = guide_x - 10
    out.append(f'<path d="M{TX},{py0} H{px} V{py1} H{TX}" fill="none" stroke="{C_PROG}" stroke-width="2.4" '
               f'marker-end="url(#{MARKERS[C_PROG]})"/>')
    out.append(halo_label(px - 6, (py0 + py1) / 2 + 3, "progresses to", 8.5, C_PROG, anchor="end"))

    # ---- causal bands: width = typicality, word label at source end, expected inside chip ----
    for c in causes:
        e = cause_edges[c]
        typ = e["props"]["typicality"]
        sx, sy = LX + LW, cause_y[c] + CAUSE_H / 2
        tgt = e["to"]
        if tgt == ANCHOR:
            tx, ty = CX, slots[c]
        else:
            tx, ty = TX, tree_y[tgt] + TREE_H / 2
        out.append(band(sx, sy, tx, ty, C_RED, TYP_W[typ]))
        out.append(halo_label(sx + 8, sy - TYP_W[typ] / 2 - 4, TYP_TXT.get(typ, typ), 9.5, C_RED))

    for c in causes:
        e = cause_edges[c]
        exp = e["props"].get("expected", {})
        sub2 = "expect: " + " · ".join(exp.values()) if exp else None
        out.append(chip(LX, cause_y[c], LW, CAUSE_H, c, "diagnosis · clinical cause", sub2, C_RED))

    # ---- effusion's own consequences + co-occurrence (right gutter) ----
    mid_r = CARD_Y + CARD_H / 2
    out.append(band(CX + CW, mid_r - 28, RX, right_y["RDE2_000530"] + 28, C_RED, TYP_W["frequent"]))
    out.append(halo_label(CX + CW + 8, mid_r - 36, "causes · frequent", 9.5, C_RED))
    out.append(band(CX + CW, mid_r - 8, RX, right_y["RDE2_000531"] + 28, C_RED, TYP_W["occasional"]))
    out.append(halo_label(CX + CW + 8, mid_r - 16, "causes · occasional · large effusions", 9.5, C_RED))
    out.append(band(CX + CW, mid_r + 12, RX, right_y["RDE2_000532"] + RIGHT_H - 8, C_OCC, 1.6,
                    dash=True, arrow=False))
    out.append(halo_label(CX + CW + 8, mid_r + 30, "occurs with", 9.5, C_OCC))

    # ---- manifestation bands from subtypes (glyph at arrowhead) ----
    def manifest(frm, tgt, exit_dy, slot_dy, label_dy):
        e = next(e for e in EDGES if e["edge"] == "MAY_MANIFEST_AS"
                 and e["from"] == frm and e["to"] == tgt)
        p = e["props"]
        typ, spec = p["typicality"], p.get("specificity")
        sy = tree_y[frm] + TREE_H / 2 + exit_dy
        indent = 20 if tgt == "RDE2_000534" else 0
        ty = right_y[tgt] + RIGHT_H / 2 + slot_dy
        out.append(band(TX + CW - 36, sy, RX + indent, ty, C_MAN, TYP_W[typ],
                        glyph_spec=spec or "__none__"))
        out.append(halo_label(TX + CW - 36 + 8, sy + label_dy, TYP_TXT.get(typ, typ), 9.5, C_MAN))

    manifest("RDE2_000510", "RDE2_000532", -8, -8, -16)  # empyema -> pleural thickening
    manifest("RDE2_000510", "RDE2_000533", 8, 0, 14)     # empyema -> split pleura sign
    manifest("RDE2_000513", "RDE2_000534", 0, 0, -10)    # malignant -> nodular pleural thickening

    # ---- right column chips ----
    rtags = {
        "RDE2_000530": ["presence *", "size (qualitative)"],
        "RDE2_000531": ["presence *"],
        "RDE2_000532": ["presence *", "distribution"],
        "RDE2_000533": ["presence *"],
        "RDE2_000534": ["presence *"],
    }
    for r in right:
        indent = 20 if r == "RDE2_000534" else 0
        y = right_y[r]
        out.append(chip(RX + indent, y, RW - indent, RIGHT_H, r,
                        kind_sub(r, "subtype of pleural thickening" if indent else None)))
        out.append(pills(RX + indent + 14, y + 38, rtags[r]))
        sc = scope_of(r)
        if sc:
            out.append(txt(RX + indent + 14, y + RIGHT_H + 11, f"scoped to {sc[0]}", 8.5, AMBER_DARK))
    # thickening -> nodular is subsumption: tree elbow, not a band
    out.append(f'<path d="M{RX + 10},{right_y["RDE2_000532"] + RIGHT_H} V{right_y["RDE2_000534"] + RIGHT_H / 2} '
               f'H{RX + 20}" fill="none" stroke="{C_SUB}" stroke-width="1.6"/>')

    out.append(legend(W, H))
    out.append("</svg>")
    return "\n".join(out) + "\n"


# =================================================================
# Pyelonephritis: diagnosis family tree on the left, findings under
# their grouping node on the right, manifestation bands across.
# =================================================================
def render_pyelo():
    W = 1214
    LX, LW = 24, 330            # diagnosis tree (right edges all at 354)
    RX, RW = 560, 420           # findings column (560..980)
    abscess = "RDE2_000809"

    tree = [  # view order: the family tree
        ("RDE2_000800", 0), ("RDE2_000801", 1), ("RDE2_000812", 2),
        ("RDE2_000811", 1), ("RDE2_000813", 2),
    ]
    findings = ["RDE2_000802", "RDE2_000803", "RDE2_000804", "RDE2_000805",
                "RDE2_000806", "RDE2_000808", "RDE2_000807", abscess]

    TY0, TP, TH = 104, 64, 52
    tree_y = {n: TY0 + i * TP for i, (n, _) in enumerate(tree)}
    FY0, FP, FH = 140, 78, 56
    fy, y = {}, FY0
    for f in findings:  # renal enlargement carries an extra INTERPRETED_FROM line
        fy[f] = y
        y += FP + (18 if f == "RDE2_000804" else 0)

    CHAN_Y = y + 26   # bottom channel for the cause band to renal abscess
    H = CHAN_Y + 90

    out = [svg_open(W, H, "Acute pyelonephritis: diagnosis family tree left, findings under the renal abnormality grouping right; manifestation band width encodes typicality and arrowhead glyphs encode specificity.")]
    out.append(txt(24, 34, "Acute pyelonephritis — flow layout: band width = typicality, arrowhead glyph = specificity",
                   16, INK, weight="700"))
    out.append(txt(LX, 66, "THE DIAGNOSIS FAMILY", 10, MUTED, weight="600", spacing="1.2"))
    out.append(txt(RX, 66, "FINDINGS — ALL UNDER THE GROUPING NODE", 10, MUTED, weight="600", spacing="1.2"))

    # grouping band over findings column + thin trunks to each finding
    out.append(grouping_band(RX - 16, RW + 40, 78, "RDE2_000814", "no renal abnormality"))
    for f in findings[:7]:
        out.append(f'<path d="M{RX + 16},114 V{fy[f]}" stroke="{C_SUB}" stroke-width="1.1" opacity="0.45"/>')

    # diagnosis tree
    def tx_(depth):
        return LX + depth * 30
    guide = LX + 12
    parent = {"RDE2_000801": "RDE2_000800", "RDE2_000812": "RDE2_000801",
              "RDE2_000811": "RDE2_000800", "RDE2_000813": "RDE2_000811"}
    for n, d in tree:
        if d == 0:
            continue
        xv = guide + (d - 1) * 30
        pmid = tree_y[parent[n]] + TH / 2
        cmid = tree_y[n] + TH / 2
        out.append(f'<path d="M{xv},{pmid} V{cmid} H{tx_(d)}" fill="none" stroke="{C_SUB}" stroke-width="1.6"/>')
    for n, d in tree:
        out.append(chip(tx_(d), tree_y[n], LW - d * 30, TH, n, kind_sub(n, "binds presence *")))

    # progression acute -> chronic (teal), routed down the left margin of the subtree
    ay = tree_y["RDE2_000801"] + TH
    cy = tree_y["RDE2_000811"] + TH / 2
    out.append(f'<path d="M60,{ay} V{cy} H{tx_(1)}" fill="none" stroke="{C_PROG}" stroke-width="2.4" '
               f'marker-end="url(#{MARKERS[C_PROG]})"/>')
    out.append(txt(52, (ay + cy) / 2, "progresses to", 8.5, C_PROG, anchor="middle", rotate=-90))

    # manifestation bands
    def manifest(frm, tgt, exit_dy=0):
        e = next(e for e in EDGES if e["edge"] == "MAY_MANIFEST_AS"
                 and e["from"] == frm and e["to"] == tgt)
        p = e["props"]
        typ, spec = p["typicality"], p.get("specificity")
        d = dict(tree)[frm]
        sx = tx_(d) + LW - d * 30
        sy = tree_y[frm] + TH / 2 + exit_dy
        tx, ty = RX, fy[tgt] + FH / 2
        out.append(band(sx, sy, tx, ty, C_MAN, TYP_W[typ], glyph_spec=spec or "__none__"))
        out.append(halo_label(sx + 8, sy - TYP_W[typ] / 2 - 4, TYP_TXT.get(typ, typ), 9.5, C_MAN))

    manifest("RDE2_000801", "RDE2_000802", -14)  # acute -> striated nephrogram
    manifest("RDE2_000801", "RDE2_000803", -4)   # acute -> perinephric fat stranding
    manifest("RDE2_000801", "RDE2_000804", 6)    # acute -> renal enlargement
    manifest("RDE2_000812", "RDE2_000805")       # emphysematous -> renal parenchymal gas
    manifest("RDE2_000811", "RDE2_000806")       # chronic -> renal cortical scarring

    # co-occurrence acute -- hydronephrosis (dashed, symmetric): bottom exit slot
    sx_acute = tx_(1) + LW - 30
    out.append(band(sx_acute, tree_y["RDE2_000801"] + TH / 2 + 16, RX, fy["RDE2_000808"] + FH / 2,
                    C_OCC, 1.6, dash=True, arrow=False))
    out.append(halo_label(sx_acute + 8, tree_y["RDE2_000801"] + TH / 2 + 28,
                          "occurs with (obstruction predisposes)", 9.5, C_OCC))

    # causal band acute -> renal abscess: cannot cross the findings column, so it
    # detours through the left margin and the free channel below the diagram.
    ax, ay2 = tx_(1), tree_y["RDE2_000801"] + TH / 2 - 12
    out.append(f'<path d="M{ax},{ay2} H10 V{CHAN_Y} H{RX + 200} V{fy[abscess] + FH}" fill="none" '
               f'stroke="{C_RED}" stroke-width="{TYP_W["occasional"]}" stroke-linecap="round" '
               f'marker-end="url(#{MARKERS[C_RED]})"/>')
    out.append(halo_label(375, CHAN_Y - 8, "may cause · occasional  (acute pyelonephritis \u2192 renal abscess)", 9.5, C_RED))

    # finding chips with element pills and scope lines
    etags = {
        "RDE2_000802": (["presence *", "distribution"], "kidney"),
        "RDE2_000803": (["presence *", "severity"], "perirenal space"),
        "RDE2_000804": (["presence *"], "kidney"),
        "RDE2_000805": (["presence *"], "kidney"),
        "RDE2_000806": (["presence *", "distribution"], "kidney"),
        "RDE2_000808": (["presence *", "severity"], "kidney"),
        "RDE2_000807": (["presence *", "size (mean diameter)"], "kidney"),
        abscess:       (["presence *", "size (mean diameter)"], "kidney"),
    }
    for f in findings:
        indent = 24 if f == abscess else 0
        yy = fy[f]
        out.append(chip(RX + indent, yy, RW - indent, FH, f,
                        kind_sub(f, "subtype of renal lesion" if indent else None)))
        out.append(pills(RX + indent + 14, yy + 36, etags[f][0]))
        scope = etags[f][1]
        differs = scope == "perirenal space"
        out.append(txt(RX + indent + 14, yy + FH + 11,
                       f"scoped to {scope}" + ("  \u2190 differs from the family" if differs else ""),
                       8.5, AMBER_DARK, weight="700" if differs else None))
    # renal lesion -> renal abscess: tree elbow (subsumption crossing finding/diagnosis)
    out.append(f'<path d="M{RX + 10},{fy["RDE2_000807"] + FH} V{fy[abscess] + FH / 2} H{RX + 24}" '
               f'fill="none" stroke="{C_SUB}" stroke-width="1.6"/>')

    # INTERPRETED_FROM under renal enlargement
    iy = fy["RDE2_000804"] + FH + 24
    out.append(f'<rect x="{RX + 14}" y="{iy - 12}" width="360" height="19" rx="9.5" fill="{GREEN_BG}" stroke="{GREEN}" stroke-width="0.8"/>')
    out.append(txt(RX + 24, iy + 1, "interpreted from binding RDE2_000830 · kidney HAS_ELEMENT length",
                   8.5, GREEN_DARK, weight="600"))

    out.append(legend(W, H))
    out.append("</svg>")
    return "\n".join(out) + "\n"


# =================================================================
if __name__ == "__main__":
    which = sys.argv[1]
    defs = marker_defs([C_RED, C_MAN, C_PROG, C_OCC])
    body = render_pleural() if which == "pleural-effusion" else render_pyelo()
    close = body.index(">") + 1
    sys.stdout.write(body[:close] + f"<defs>{defs}</defs>" + body[close:])
