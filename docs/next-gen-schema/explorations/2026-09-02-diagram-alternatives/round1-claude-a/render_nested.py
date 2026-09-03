#!/usr/bin/env python3
"""Alternative 1: nested containment.

Subsumption is drawn as containment: a subtype sits inside its parent's box, so the taxonomy
(finding, diagnosis, grouping alike) is read without a single arrow. Typed relationships are
drawn as edges between boxes, but their properties are NOT written on the edge: each edge's
properties are written as a line inside the chip of its lower-degree endpoint, naming the
other endpoint. Under fan-in, that means every cause carries its own typicality and
`expected` hint on its own card. See README.md for the algorithm.

Usage: render_nested.py VIEW.json > out.svg
View: {"title", "aria", "nodes": [ids in the order they should appear]}
"""
import json, sys, os, html, re

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, "..", "..", "..", "docs", "next-gen-schema", "tools")
sys.path.insert(0, os.path.abspath(TOOLS))
from graph import load_graph  # noqa: E402

# ---- visual language (kept from render_constellation.py)
ACCENT = {
    "FindingClass":     ("#2563eb", "#1e3a8a", "#eff6ff"),
    "Diagnosis":        ("#7c3aed", "#4c1d95", "#f5f3ff"),
    "Grouping":         ("#64748b", "#334155", "#f8fafc"),
}
ELEM = ("#16a34a", "#14532d", "#f0fdf4")
ANAT = ("#d97706", "#78350f", "#fffbeb")
INK, MUTED, RULE = "#1f2937", "#64748b", "#cbd5e1"
EDGE = {  # color, dash, head style
    "MAY_CAUSE":       ("#dc2626", "", "filled"),
    "MAY_MANIFEST_AS": ("#7c3aed", "", "open"),
    "MAY_PROGRESS_TO": ("#0891b2", "9 4", "filled"),
    "OCCURS_WITH":     ("#64748b", "2 3", "none"),
}
FLOW = ("MAY_CAUSE", "MAY_MANIFEST_AS", "OCCURS_WITH")   # edges that separate senders from receivers
TYPED = tuple(EDGE)
GLYPH_OUT = {"MAY_CAUSE": "→", "MAY_MANIFEST_AS": "→", "MAY_PROGRESS_TO": "⇢", "OCCURS_WITH": "↔"}
GLYPH_IN = {"MAY_CAUSE": "←", "MAY_MANIFEST_AS": "←", "MAY_PROGRESS_TO": "⇠", "OCCURS_WITH": "↔"}
IMPLICIT_ELEMENTS = {"RDE2_000001"}     # every class binds presence; not repeated on every chip

BASE_W, PAD, CARD_W, COL_GAP, LANE_GAP, MARGIN = 300, 12, 250, 74, 74, 24
STACK_GAP, VGAP_EDGE, CHAN_STEP = 10, 28, 9
FS_TITLE, FS_SUB, FS_ELEM, FS_ANN = 12.5, 9, 9, 9.5
_NUM = re.compile(r'-?\d+\.\d+')


def esc(s): return html.escape(str(s), quote=True)
def tw(s, fs, bold=False): return len(s) * fs * (0.62 if bold else 0.55)
def fmt(svg): return _NUM.sub(lambda m: f'{float(m.group()):.1f}'.rstrip("0").rstrip("."), svg)


def wrap(text, fs, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(t, fs) <= width or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def kind_of(n):
    t = n["node"]
    return {"FindingClass": "finding", "Diagnosis": "diagnosis", "Grouping": "grouping · negative-only"}.get(t, t.lower())


# ---------------------------------------------------------------------------------------------
class Layout:
    def __init__(self, g, view):
        self.g, self.view = g, view
        self.ids = list(view["nodes"])
        self.inview = set(self.ids)
        self.rel = {n["id"]: n for n in g.nodes.values() if n["node"] == "RelationshipType"}
        self.parent, self.children = {}, {i: [] for i in self.ids}
        for e in g.edges:
            if e["edge"] == "SUBTYPE_OF" and e["from"] in self.inview and e["to"] in self.inview and e["from"] not in self.parent:
                self.parent[e["from"]] = e["to"]
        for c, p in self.parent.items():
            self.children[p].append(c)
        for p in self.children:
            self.children[p].sort(key=self.ids.index)
        self.edges = sorted((e for e in g.edges if e["edge"] in TYPED and e["from"] in self.inview and e["to"] in self.inview),
                            key=lambda e: (e["edge"], e["from"], e["to"]))
        self.degree = {i: 0 for i in self.ids}
        for e in self.edges:
            self.degree[e["from"]] += 1; self.degree[e["to"]] += 1
        # annotations: each edge is written into its lower-degree endpoint (tie: the source)
        self.ann = {i: [] for i in self.ids}
        for e in self.edges:
            at = e["to"] if self.degree[e["to"]] < self.degree[e["from"]] else e["from"]
            self.ann[at].append((e, at == e["from"]))
        # roots and their region
        self.roots = [i for i in self.ids if i not in self.parent]
        self.center, self.left, self.right = [], [], []
        for r in self.roots:
            n = g.nodes[r]
            es = [e for e in self.edges if r in (e["from"], e["to"])]
            if n["node"] == "Grouping" or self.children[r]:
                self.center.append(r)
            elif es and all(e["edge"] == "MAY_CAUSE" and e["from"] == r for e in es):
                self.left.append(r)
            else:
                self.right.append(r)
        self.subtree_cache = {}
        self.mode, self.lanes, self.order = {}, {}, {}
        for r in self.center:
            self.plan(r)
        self.box = {}            # id -> dict(x, y, w, h, head)
        self.channel = {}        # container id -> list of edge keys routed through its right padding

    # ---- structure
    def subtree(self, i):
        if i not in self.subtree_cache:
            s = {i}
            for c in self.children[i]: s |= self.subtree(c)
            self.subtree_cache[i] = s
        return self.subtree_cache[i]

    def child_holding(self, container, node):
        for c in self.children[container]:
            if node in self.subtree(c): return c
        return None

    def plan(self, c):
        """Decide stack vs lanes for container c, and the order of its children."""
        kids = self.children[c]
        if not kids: return
        receivers, senders = set(), set()
        for e in self.edges:
            if e["edge"] not in FLOW: continue
            a, b = self.child_holding(c, e["from"]), self.child_holding(c, e["to"])
            if a and b and a != b:
                receivers.add(b); senders.add(a)
        if len(receivers) >= 2:
            self.mode[c] = "lanes"
            self.lanes[c] = ([k for k in kids if k not in receivers], [k for k in kids if k in receivers])
        else:
            self.mode[c] = "stack"
        # order: view order, but a MAY_PROGRESS_TO target follows its source directly
        order = list(kids)
        for e in self.edges:
            if e["edge"] == "MAY_PROGRESS_TO" and e["from"] in kids and e["to"] in kids:
                order.remove(e["to"]); order.insert(order.index(e["from"]) + 1, e["to"])
        self.order[c] = order
        for k in kids: self.plan(k)

    def lca(self, a, b):
        anc = []
        x = a
        while x is not None:
            anc.append(x); x = self.parent.get(x)
        y = b
        while y is not None:
            if y in anc: return y
            y = self.parent.get(y)
        return None

    def route_kind(self, e):
        """'lane' (horizontal curve), 'vertical' (adjacent in a stack), 'channel', or 'outer' (left/right card)."""
        s, t = e["from"], e["to"]
        if s in self.left or t in self.left or s in self.right or t in self.right:
            return "outer"
        C = self.lca(s, t)
        if C is None or C in (s, t): return "outer"
        a, b = self.child_holding(C, s), self.child_holding(C, t)
        if self.mode[C] == "lanes":
            return "lane"
        o = self.order[C]
        if a == s and b == t and abs(o.index(a) - o.index(b)) == 1:
            return "vertical"
        return "channel"

    # ---- content lines of a chip or box header
    def elements(self, i):
        shown_above = set()
        p = self.parent.get(i)
        while p:
            shown_above |= {e["to"] for e in self.g.out_edges(p) if e["edge"] == "HAS_ELEMENT"}
            p = self.parent.get(p)
        out = []
        for e in self.g.out_edges(i):
            if e["edge"] != "HAS_ELEMENT" or e["to"] in IMPLICIT_ELEMENTS or e["to"] in shown_above: continue
            el = self.g.nodes.get(e["to"], {"name": e["to"]})
            label = el["name"]
            note = e.get("props", {}).get("note")
            if note: label += f" · {note}"
            if el.get("units"): label += " (HU)" if el["units"][0] == "[hnsf'U]" else f" ({el['units'][0]})"
            if el.get("multi_select"): label += " (multi)"
            out.append(label)
        for e in self.g.out_edges(i):
            if e["edge"] == "INTERPRETED_FROM":
                b = self.g.edge_by_id(e["to"])
                if b:
                    out.append(f"≈ interpreted from {self.g.nodes[b['to']]['name']} bound to {self.g.nodes[b['from']]['name']}")
        return out

    def scope(self, i):
        mine = [e["to"] for e in self.g.out_edges(i) if e["edge"] == "SCOPED_TO"]
        if not mine: return None
        p = self.parent.get(i)
        if p:
            theirs = [e["to"] for e in self.g.out_edges(p) if e["edge"] == "SCOPED_TO"]
            if theirs == mine: return None      # inherited from the enclosing box
        return self.g.nodes.get(mine[0], {"name": mine[0]})["name"]

    def ann_lines(self, i, width):
        lines = []
        for e, outgoing in self.ann[i]:
            r = self.rel[e["edge"]]
            verb = r["name"] if outgoing or r.get("symmetric") else r.get("inverse", e["edge"]).lower().replace("_", " ")
            other = self.g.nodes[e["to"] if outgoing else e["from"]]["name"]
            glyph = (GLYPH_OUT if outgoing else GLYPH_IN)[e["edge"]]
            p = e.get("props", {})
            bits = [f"{glyph} {verb} {other}"]
            for k in ("typicality", "specificity"):
                if k in p: bits.append(p[k].replace("_", " "))
            text = " · ".join(bits)
            color = EDGE[e["edge"]][0]
            for k, ln in enumerate(wrap(text, FS_ANN, width)): lines.append((ln, color, k > 0))
            if "expected" in p:
                exp = "expect " + "; ".join(f"{k} {v}" for k, v in sorted(p["expected"].items(), key=lambda kv: kv[0] != "location"))
                for ln in wrap(exp, FS_ANN, width - 14): lines.append((ln, color, True))
            if p.get("note") and "expected" not in p and e["edge"] != "MAY_CAUSE" or (p.get("note") and e["edge"] == "MAY_CAUSE" and "expected" not in p):
                for ln in wrap(f"note: {p['note']}", FS_ANN, width - 14): lines.append((ln, MUTED, True))
        return lines

    def content(self, i, w):
        """Header content of node i at width w: returns (height, element rows, annotation lines)."""
        inner = w - 2 * 10
        rows, cur, curw = [], [], 0
        for label in self.elements(i):
            cw = tw(label, FS_ELEM) + 12
            if cur and curw + cw + 5 > inner:
                rows.append(cur); cur, curw = [], 0
            cur.append((label, cw)); curw += cw + 5
        if cur: rows.append(cur)
        ann = self.ann_lines(i, inner)
        h = 8 + 15 + 12 + len(rows) * 18 + (4 if ann and rows else 0) + len(ann) * 13 + 8
        return h, rows, ann

    # ---- measure and place
    def natural_w(self, i):
        kids = self.children[i]
        if not kids: return BASE_W
        chan = CHAN_STEP * self.channel_count(i) + (6 if self.channel_count(i) else 0)
        if self.mode[i] == "lanes":
            l0, l1 = self.lanes[i]
            return max(map(self.natural_w, l0)) + LANE_GAP + max(map(self.natural_w, l1)) + 2 * PAD + chan
        return max(map(self.natural_w, kids)) + 2 * PAD + chan

    def channel_count(self, c):
        return sum(1 for e in self.edges if self.route_kind(e) == "channel" and self.lca(e["from"], e["to"]) == c)

    def measure(self, i, w):
        head, rows, ann = self.content(i, w)
        self.box[i] = {"w": w, "head": head, "rows": rows, "ann": ann}
        kids = self.children[i]
        if not kids:
            self.box[i]["h"] = head; return head
        chan = CHAN_STEP * self.channel_count(i) + (6 if self.channel_count(i) else 0)
        inner = w - 2 * PAD - chan
        if self.mode[i] == "lanes":
            l0, l1 = self.lanes[i]
            w0 = max(map(self.natural_w, l0)); w1 = inner - LANE_GAP - w0
            h0 = self.stack_h(l0, w0); h1 = self.stack_h(l1, w1)
            h = head + max(h0, h1) + PAD
        else:
            h = head + self.stack_h(self.order[i], inner) + PAD
        self.box[i]["h"] = h
        return h

    def stack_gap(self, a, b):
        for e in self.edges:
            if {e["from"], e["to"]} == {a, b} and self.route_kind(e) == "vertical": return VGAP_EDGE
        return STACK_GAP

    def stack_h(self, kids, w):
        h = 0
        for k, kid in enumerate(kids):
            if k: h += self.stack_gap(kids[k - 1], kid)
            h += self.measure(kid, w)
        return h

    def place(self, i, x, y):
        b = self.box[i]; b["x"], b["y"] = x, y
        kids = self.children[i]
        if not kids: return
        chan = CHAN_STEP * self.channel_count(i) + (6 if self.channel_count(i) else 0)
        inner = b["w"] - 2 * PAD - chan
        b["chan_x"] = x + b["w"] - PAD - chan + 6
        if self.mode[i] == "lanes":
            l0, l1 = self.lanes[i]
            w0 = max(map(self.natural_w, l0))
            self.place_stack(l0, x + PAD, y + b["head"])
            self.place_stack(l1, x + PAD + w0 + LANE_GAP, y + b["head"])
        else:
            self.place_stack(self.order[i], x + PAD, y + b["head"])

    def place_stack(self, kids, x, y):
        for k, kid in enumerate(kids):
            if k: y += self.stack_gap(kids[k - 1], kid)
            self.place(kid, x, y); y += self.box[kid]["h"]


# ---------------------------------------------------------------------------------------------
def render(g, view):
    L = Layout(g, view)
    # center region
    cx = MARGIN + (CARD_W + COL_GAP if L.left else 0)
    y = 56
    for r in L.center:
        w = L.natural_w(r)
        L.measure(r, w); L.place(r, cx, y); y += L.box[r]["h"] + 30
    center_w = max(L.box[r]["w"] for r in L.center)
    center_bottom = y - 30
    # side cards: measure, then align to the y of what they connect to
    def side_cards(ids, x, want_y):
        for i in ids:
            L.measure(i, CARD_W)
        want = sorted(ids, key=lambda i: (want_y(i), ids.index(i)))
        yy = 56
        for i in want:
            yy = max(yy, want_y(i) - L.box[i]["h"] / 2)
            L.place(i, x, yy); yy += L.box[i]["h"] + 12
    def mid_y(i):
        b = L.box[i]; return b["y"] + (b["head"] / 2 if L.children[i] else b["h"] / 2)
    def partner_y(i):
        ys = [mid_y(e["to"] if e["from"] == i else e["from"]) for e in L.edges if i in (e["from"], e["to"])]
        return sum(ys) / len(ys) if ys else 56
    side_cards(L.left, MARGIN, partner_y)
    side_cards(L.right, cx + center_w + COL_GAP, partner_y)
    W = cx + center_w + (COL_GAP + CARD_W if L.right else 0) + MARGIN
    H = max([center_bottom] + [L.box[i]["y"] + L.box[i]["h"] for i in L.left + L.right]) + MARGIN + 30

    # ---- anchor slots: spread edges that share a side of a node
    slots = {}
    for e in L.edges:
        k = L.route_kind(e)
        s, t = e["from"], e["to"]
        if k == "vertical": continue
        if k == "channel":
            slots.setdefault((s, "R"), []).append(e); slots.setdefault((t, "R"), []).append(e)
        else:
            left_first = L.box[s]["x"] <= L.box[t]["x"]
            slots.setdefault((s, "R" if left_first else "L"), []).append(e)
            slots.setdefault((t, "L" if left_first else "R"), []).append(e)
    def anchor(i, side, e):
        b = L.box[i]
        band = (b["y"] + 10, b["y"] + b["head"] - 10) if L.children[i] else (b["y"] + 12, b["y"] + b["h"] - 12)
        es = slots[(i, side)]
        other = lambda ee: mid_y(ee["to"] if ee["from"] == i else ee["from"])
        es = sorted(es, key=lambda ee: (other(ee), ee["edge"], ee["from"], ee["to"]))
        n = len(es); k = es.index(e)
        yy = band[0] + (band[1] - band[0]) * (k + 1) / (n + 1)
        return (b["x"] if side == "L" else b["x"] + b["w"], yy)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="system-ui, sans-serif" role="img" aria-label="{esc(view.get("aria", view.get("title", "")))}">']
    heads = []
    for name, (color, dash, head) in EDGE.items():
        if head == "filled":
            heads.append(f'<marker id="h-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>')
        elif head == "open":
            heads.append(f'<marker id="h-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto"><path d="M1,1 L9,5 L1,9 z" fill="#ffffff" stroke="{color}" stroke-width="1.3"/></marker>')
    out.append(f'<defs>{"".join(heads)}</defs><rect width="{W}" height="{H}" fill="#ffffff"/>')
    if view.get("title"):
        out.append(f'<text x="{MARGIN}" y="28" font-size="15" font-weight="700" fill="{INK}">{esc(view["title"])}</text>')
    if L.left: out.append(f'<text x="{MARGIN}" y="48" font-size="10" letter-spacing="1.2" font-weight="600" fill="{MUTED}">CAUSES</text>')
    out.append(f'<text x="{cx}" y="48" font-size="10" letter-spacing="1.2" font-weight="600" fill="{MUTED}">THE FAMILY · A BOX INSIDE A BOX IS A SUBTYPE</text>')
    if L.right: out.append(f'<text x="{cx + center_w + COL_GAP}" y="48" font-size="10" letter-spacing="1.2" font-weight="600" fill="{MUTED}">COMPANIONS</text>')

    # ---- nodes (containers first, so children paint over them)
    def draw_node(i):
        n = g.nodes[i]; b = L.box[i]
        a, dark, bg = ACCENT.get(n["node"], ACCENT["Grouping"])
        x, y, w, h = b["x"], b["y"], b["w"], b["h"]
        is_box = bool(L.children[i])
        rx = 10 if n["node"] == "Diagnosis" else 3
        dash = ' stroke-dasharray="6 4"' if n["node"] == "Grouping" else ''
        sw = 1.6 if is_box else 1
        fill = bg if not is_box else bg
        out.append(f'<g data-node="{esc(i)}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{a}" stroke-width="{sw}"{dash} fill-opacity="{0.55 if is_box else 1}"/>')
        if not is_box:
            out.append(f'<rect x="{x}" y="{y + 6}" width="4" height="{h - 12}" rx="2" fill="{a}"/>')
        ty = y + 8 + 13
        out.append(f'<text x="{x + 12}" y="{ty}" font-size="{FS_TITLE}" font-weight="700" fill="{dark}">{esc(n["name"])}</text>')
        sub = f'{kind_of(n)} · {i}'
        out.append(f'<text x="{x + 12}" y="{ty + 13}" font-size="{FS_SUB}" fill="{MUTED}">{esc(sub)}</text>')
        sc = L.scope(i)
        if sc:
            label = f"in {sc}"; lw = tw(label, FS_SUB) + 12
            out.append(f'<rect x="{x + w - 10 - lw}" y="{y + 8}" width="{lw}" height="16" rx="8" fill="{ANAT[2]}" stroke="{ANAT[0]}"/>'
                       f'<text x="{x + w - 10 - lw / 2}" y="{y + 19.5}" text-anchor="middle" font-size="{FS_SUB}" fill="{ANAT[1]}">{esc(label)}</text>')
        yy = ty + 13 + 8
        for row in b["rows"]:
            xx = x + 10
            for label, cw in row:
                out.append(f'<rect x="{xx}" y="{yy}" width="{cw}" height="15" rx="4" fill="{ELEM[2]}" stroke="{ELEM[0]}" stroke-width="0.8"/>'
                           f'<text x="{xx + 6}" y="{yy + 11}" font-size="{FS_ELEM}" fill="{ELEM[1]}">{esc(label)}</text>')
                xx += cw + 5
            yy += 18
        if b["ann"] and b["rows"]: yy += 4
        for ln, color, indent in b["ann"]:
            italic = indent and (ln.startswith("expect ") or ln.startswith("note: ") or color == MUTED)
            out.append(f'<text x="{x + 10 + (14 if indent else 0)}" y="{yy + 10}" font-size="{FS_ANN}" fill="{color}"{" font-style=\"italic\"" if italic else ""}>{esc(ln)}</text>')
            yy += 13
        out.append('</g>')
        for c in (L.order.get(i) or []):
            draw_node(c)
    for r in L.center + L.left + L.right:
        draw_node(r)

    # ---- edges
    for e in L.edges:
        color, dash, head = EDGE[e["edge"]]
        s, t = e["from"], e["to"]
        k = L.route_kind(e)
        attrs = f'fill="none" stroke="{color}" stroke-width="1.5"' + (f' stroke-dasharray="{dash}"' if dash else '') + (f' marker-end="url(#h-{e["edge"]})"' if head != "none" else '')
        if k == "vertical":
            bs, bt = L.box[s], L.box[t]
            x1, x2 = bs["x"] + min(bs["w"], bt["w"]) / 2, bt["x"] + min(bs["w"], bt["w"]) / 2
            if bs["y"] < bt["y"]:
                d = f'M{x1},{bs["y"] + bs["h"]} L{x2},{bt["y"]}'
            else:
                d = f'M{x1},{bs["y"]} L{x2},{bt["y"] + bt["h"]}'
        elif k == "channel":
            C = L.lca(s, t)
            chan = [ee for ee in L.edges if L.route_kind(ee) == "channel" and L.lca(ee["from"], ee["to"]) == C]
            cxk = L.box[C]["chan_x"] + CHAN_STEP * chan.index(e)
            (sx, sy), (tx, ty) = anchor(s, "R", e), anchor(t, "R", e)
            d = f'M{sx},{sy} L{cxk},{sy} L{cxk},{ty} L{tx},{ty}'
        else:
            left_first = L.box[s]["x"] <= L.box[t]["x"]
            (sx, sy) = anchor(s, "R" if left_first else "L", e)
            (tx, ty) = anchor(t, "L" if left_first else "R", e)
            dx = (tx - sx) / 2
            d = f'M{sx},{sy} C{sx + dx},{sy} {tx - dx},{ty} {tx},{ty}'
        out.append(f'<path d="{d}" {attrs}><title>{esc(s)} {e["edge"]} {esc(t)}</title></path>')

    # ---- key
    ky = H - 30
    kx = MARGIN
    for name, (color, dash, head) in EDGE.items():
        out.append(f'<path d="M{kx},{ky} L{kx + 26},{ky}" fill="none" stroke="{color}" stroke-width="1.5"{f" stroke-dasharray={chr(34)}{dash}{chr(34)}" if dash else ""}{f" marker-end={chr(34)}url(#h-{name}){chr(34)}" if head != "none" else ""}/>')
        label = L.rel[name]["name"]
        out.append(f'<text x="{kx + 32}" y="{ky + 3.5}" font-size="9.5" fill="{MUTED}">{esc(label)}</text>')
        kx += 32 + tw(label, 9.5) + 22
    out.append(f'<text x="{MARGIN}" y="{ky + 18}" font-size="9.5" fill="{MUTED}">Every class also binds presence. An amber tag is the anatomic scope; everything inside a box inherits it unless its own tag says otherwise.</text>')
    out.append("</svg>")
    return fmt("".join(out)) + "\n"


if __name__ == "__main__":
    g = load_graph()
    view = json.load(open(sys.argv[1], encoding="utf-8"))
    sys.stdout.write(render(g, view))
