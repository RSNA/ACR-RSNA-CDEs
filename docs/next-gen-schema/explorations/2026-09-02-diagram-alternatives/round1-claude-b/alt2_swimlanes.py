"""Alternative 2: role swimlanes, nested taxonomy boxes, orthogonal per-edge tracks.

Layout algorithm (deterministic, described in README.md):
  1. Lanes, left to right, emitted only when non-empty: CAUSES (classes whose
     only relationships are outgoing MAY_CAUSE edges into the family), THE
     FAMILY (the hub, its ancestors as nested boxes, its descendants as nested
     stacks), FINDINGS & COMPANIONS (everything else), ANATOMY (bindings).
  2. A Grouping ancestor is not a box but a band spanning the family lane and
     the top of the findings lane; its members in the findings lane are laid
     out first, so the band is a rectangle.
  3. Subtypes are stacked inside their parent's box; siblings joined by
     MAY_PROGRESS_TO are made adjacent and the edge is a short vertical arrow
     in the gap between them.
  4. Every cross-lane edge leaves its source at its own port on the right
     edge, runs horizontally into the channel where its label sits (labels are
     left-aligned in the channel, one per port, never stacked), turns down or
     up on its own vertical track, and enters the target at its own port on
     the left edge. All tracks lie to the right of all labels, so a track can
     cross a wire but never a label.
  5. Tracks are assigned by interval colouring in descending source-y order,
     which makes order-preserving pairs of edges cross-free.
"""
from __future__ import annotations

import sys

from common import (EDGE, INK, KIND, MUTED, PAPER, RULE, Graph, edge_lines, edge_path,
                    esc, family_ids, legend_block, markers, text, tw, wrap)

LANE_W = {"causes": 186, "family": 292, "findings": 228, "anatomy": 176}
INDENT = 12
PAD = 8
GAP = 16            # between stacked cards
PROG_GAP = 34       # between siblings joined by a progression edge
TRACK = 9
LABEL_FONT = 9.5
DETAIL_FONT = 8.5
LABEL_W_MAX = 176


class Box:
    def __init__(self, nid):
        self.id = nid
        self.children = []
        self.parent = None
        self.x = self.y = 0.0
        self.w = self.h = 0.0
        self.header_h = 0.0
        self.out_ports = []   # edges leaving from the right edge
        self.in_ports = []    # edges arriving at the left edge
        self.port_y = {}      # edge id -> absolute y
        self.binding_rows = []
        self.lane = None

    @property
    def right(self):
        return self.x + self.w

    @property
    def bottom(self):
        return self.y + self.h


def ekey(e):
    return e.get("id") or f"{e['edge']}|{e['from']}|{e['to']}"


def render(g, view):
    hub = view["hub"]
    ids = family_ids(g, view["family"])
    rels = g.relations(ids)
    hub_scope = g.scope(hub)
    chain = [a for a in g.ancestors(hub) if a in ids]
    band = chain[-1] if chain and g.kind(chain[-1]) == "Grouping" else None
    box_chain = [a for a in chain if a != band]                # nested boxes, nearest first
    lineage = set([hub] + g.descendants(hub) + box_chain)
    for a in box_chain:
        lineage |= set(g.descendants(a))
    lineage &= set(ids)
    others = [n for n in ids if n not in lineage and n != band]

    def only_causes(n):
        mine = [e for e in rels if n in (e["from"], e["to"])]
        return bool(mine) and all(e["edge"] == "MAY_CAUSE" and e["from"] == n for e in mine)

    causes = [n for n in others if only_causes(n)]
    findings = [n for n in others if n not in causes]
    bindings = {}
    for e in rels:
        if e["edge"] == "INTERPRETED_FROM":
            b = g.binding[e["to"]]
            bindings.setdefault(b["from"], []).append(e["to"])

    boxes = {}

    def mk(n):
        if n not in boxes:
            boxes[n] = Box(n)
        return boxes[n]

    # family tree of boxes
    root_family = box_chain[-1] if box_chain else hub
    def build(n):
        b = mk(n)
        kids = [c for c in g.children.get(n, []) if c in lineage]
        # progression pairs adjacent (source before target), then by out-degree, then name
        def outdeg(c):
            return -sum(1 for e in rels if e["from"] == c and e["edge"] != "MAY_PROGRESS_TO")
        kids.sort(key=lambda c: (outdeg(c), g.name(c)))
        for e in rels:
            if e["edge"] == "MAY_PROGRESS_TO" and e["from"] in kids and e["to"] in kids:
                kids.remove(e["from"])
                kids.insert(kids.index(e["to"]), e["from"])
        for c in kids:
            cb = build(c)
            cb.parent = b
            b.children.append(cb)
        return b
    family_root = build(root_family)

    # findings lane: nested where the parent is also a finding-lane node
    finding_tops = []
    for n in findings:
        b = mk(n)
        b.lane = "findings"
    for n in findings:
        p = g.parent.get(n)
        if p in findings:
            boxes[n].parent = boxes[p]
            boxes[p].children.append(boxes[n])
        else:
            finding_tops.append(boxes[n])
    for n in causes:
        mk(n).lane = "causes"
    for anat, bs in bindings.items():
        b = mk(anat)
        b.lane = "anatomy"
        b.binding_rows = bs
    def mark(b, lane):
        b.lane = lane
        for c in b.children:
            mark(c, lane)
    mark(family_root, "family")

    # ------------------------------------------------ ports
    lane_order = ["causes", "family", "findings", "anatomy"]
    lanes = [l for l in lane_order if any(b.lane == l for b in boxes.values())]
    lane_idx = {l: i for i, l in enumerate(lanes)}

    def lane_of(n):
        if n in g.binding:
            return "anatomy"
        return boxes[n].lane

    cross, same = [], []
    for e in rels:
        src = e["from"]
        tgt = g.binding[e["to"]]["from"] if e["to"] in g.binding else e["to"]
        li, lj = lane_idx[lane_of(src)], lane_idx[lane_of(tgt)]
        if li == lj:
            same.append(e)
        else:
            if li > lj:
                e = dict(e, _rev=True)
            cross.append(e)
            boxes[src if li < lj else tgt].out_ports.append(e)
            boxes[tgt if li < lj else src].in_ports.append(e)

    PRIO = {"MAY_MANIFEST_AS": 0, "OCCURS_WITH": 1, "MAY_CAUSE": 2, "MAY_PROGRESS_TO": 3, "INTERPRETED_FROM": 4}
    for b in boxes.values():
        b.out_ports.sort(key=lambda e: (PRIO[e["edge"]], g.name(e["to"] if e["to"] not in g.binding else g.binding[e["to"]]["from"])))

    # label text per cross edge
    labels = {}
    for e in cross:
        l1, l2 = edge_lines(e)
        l1s = wrap(l1, LABEL_FONT, LABEL_W_MAX, bold=True, max_lines=2)
        l2s = wrap(l2, DETAIL_FONT, LABEL_W_MAX, max_lines=2) if l2 else []
        labels[ekey(e)] = (l1s, l2s)

    def label_h(e):
        l1s, l2s = labels[ekey(e)]
        return 11 * len(l1s) + 10 * len(l2s) + 6

    # ------------------------------------------------ measure boxes
    def measure(b, w):
        kind = g.kind(b.id)
        italic = kind == "Diagnosis"
        inner = w - 2 * PAD - 18
        b.title = wrap(g.name(b.id), 11.5, inner, bold=True, italic=italic, max_lines=3)
        y = PAD + 12 + 13 * (len(b.title) - 1)
        y += 13
        b.sub_y = y
        scope = g.scope(b.id)
        b.badge = g.name(scope) if scope and scope != hub_scope and kind != "AnatomicLocation" else ""
        els = g.elements(b.id) if kind != "AnatomicLocation" else []
        b.el_lines = wrap("◦ " + " · ".join(els), 9, inner) if els else []
        y += 12 * len(b.el_lines)
        b.bind_y = []
        for bid in b.binding_rows:
            y += 13
            b.bind_y.append(y)
        # room for ports: out ports need label height each, in ports 12 each
        need_out = 8 + sum(label_h(e) + 4 for e in b.out_ports) + 8
        need_in = 12 * len(b.in_ports) + 8
        header = max(y + PAD, need_out, need_in)
        b.header_h = header
        y = header
        for c in b.children:
            y += 4 if c is b.children[0] else 0
            cw = w - 2 * INDENT
            measure(c, cw)
            c.rel_y = y
            y += c.h
            nxt = b.children[b.children.index(c) + 1] if c is not b.children[-1] else None
            if nxt is not None:
                prog = any(e["edge"] == "MAY_PROGRESS_TO" and {e["from"], e["to"]} == {c.id, nxt.id} for e in same)
                y += PROG_GAP if prog else 10
        if b.children:
            y += INDENT
        b.w, b.h = w, y

    for b in boxes.values():
        if b.parent is None:
            measure(b, LANE_W[b.lane])

    # ------------------------------------------------ lane x positions
    def channel_w(li):
        es = [e for e in cross if lane_idx[lane_of(e["from"])] == li or lane_idx[lane_of(e["to"] if e["to"] not in g.binding else g.binding[e["to"]]["from"])] == li + 1]
        es = [e for e in cross if min(lane_idx[lane_of(e["from"])], lane_idx[lane_of(g.binding[e["to"]]["from"] if e["to"] in g.binding else e["to"])]) == li]
        lw = max([max([tw(l, LABEL_FONT, bold=True) for l in labels[ekey(e)][0]] +
                      [tw(l, DETAIL_FONT) for l in labels[ekey(e)][1]]) for e in es], default=40)
        lw = lw * 1.08 + 6
        return lw, 12 + lw + 12 + TRACK * (len(es) + 1) + 10

    lane_x, x = {}, 24
    chan = {}
    for i, l in enumerate(lanes):
        lane_x[l] = x
        x += LANE_W[l]
        if i < len(lanes) - 1:
            lw, cw = channel_w(i)
            chan[i] = (x, lw, cw)
            x += cw
    W = x + 24

    # ------------------------------------------------ vertical placement
    TOP = 96
    band_pad = 30
    fy = TOP + (band_pad if band else 0)
    family_root.x, family_root.y = lane_x["family"], fy

    def settle(b):
        for c in b.children:
            c.x = b.x + INDENT
            c.y = b.y + c.rel_y
            settle(c)
    settle(family_root)

    # assign port ys inside headers (out ports on the right, in ports on the left)
    def assign_ports(b):
        y = b.y + 8
        for e in b.out_ports:
            y += label_h(e)
            b.port_y[("out", ekey(e))] = y
            y += 4
        y = b.y + 12
        for e in b.in_ports:
            b.port_y[("in", ekey(e))] = y + 4
            y += 12
        for c in b.children:
            assign_ports(c)

    def all_boxes(b):
        yield b
        for c in b.children:
            yield from all_boxes(c)

    def endpoints(e):
        src = e["from"]
        tgt = g.binding[e["to"]]["from"] if e["to"] in g.binding else e["to"]
        if e.get("_rev"):
            src, tgt = tgt, src
        return boxes[src], boxes[tgt]

    assign_ports(family_root)

    def place_lane(tops, lane, first_group=None):
        """Stack top-level boxes of a lane by barycentre of their placed partners."""
        placed_y = {}
        def bary(b):
            ys = []
            for bb in all_boxes(b):
                for e in bb.out_ports:
                    s, t = endpoints(e)
                    if ("in", ekey(e)) in t.port_y:
                        ys.append(t.port_y[("in", ekey(e))] - (bb.port_y.get(("out", ekey(e)), bb.y + 18) - bb.y))
                for e in bb.in_ports:
                    s, t = endpoints(e)
                    if ("out", ekey(e)) in s.port_y:
                        ys.append(s.port_y[("out", ekey(e))] - (bb.port_y.get(("in", ekey(e)), bb.y + 16) - bb.y))
            return sum(ys) / len(ys) if ys else fy
        groups = [tops] if first_group is None else [[b for b in tops if b.id in first_group], [b for b in tops if b.id not in first_group]]
        y_cursor = fy
        for gi, grp in enumerate(groups):
            grp.sort(key=lambda b: (bary(b), g.name(b.id)))
            for b in grp:
                want = bary(b)
                b.x = lane_x[lane]
                b.y = max(y_cursor, want)
                settle(b)
                assign_ports(b)
                y_cursor = b.bottom + GAP
            if gi == 0 and len(groups) > 1:
                y_cursor = max(y_cursor, family_root.bottom + GAP)
                y_cursor += 24
        return y_cursor

    members = set(g.descendants(band)) if band else set()
    fin_tops = [b for b in boxes.values() if b.lane == "findings" and b.parent is None]
    place_lane(fin_tops, "findings", first_group={b.id for b in fin_tops if b.id in members} if band else None)
    cause_tops = [b for b in boxes.values() if b.lane == "causes"]
    place_lane(cause_tops, "causes")
    anat_tops = [b for b in boxes.values() if b.lane == "anatomy"]
    place_lane(anat_tops, "anatomy")

    # out ports keep their semantic order; in ports follow their sources' y
    for b in boxes.values():
        b.in_ports.sort(key=lambda e: endpoints(e)[0].y)
    for b in boxes.values():
        if b.parent is None:
            assign_ports(b)

    # ------------------------------------------------ band rect
    band_rect = None
    if band:
        mem_boxes = [b for b in fin_tops if b.id in members]
        x0 = lane_x["family"] - 14
        x1 = lane_x["findings"] + LANE_W["findings"] + 14
        y0 = TOP
        y1 = max([family_root.bottom] + [b.bottom for b in mem_boxes]) + 16
        band_rect = (x0, y0, x1, y1)

    # ------------------------------------------------ routes
    out = []
    routes = []
    for ci, (cx, lw, cw) in chan.items():
        es = [e for e in cross if min(lane_idx[endpoints(e)[0].lane], lane_idx[endpoints(e)[1].lane]) == ci]
        track_x0 = cx + 12 + lw + 12
        # interval colouring, descending source y
        es.sort(key=lambda e: -endpoints(e)[0].port_y[("out", ekey(e))])
        tracks = []
        for e in es:
            s, t = endpoints(e)
            ys = s.port_y[("out", ekey(e))]
            yt = t.port_y[("in", ekey(e))]
            lo, hi = min(ys, yt) - 4, max(ys, yt) + 4
            k = 0
            while k < len(tracks) and any(not (hi < a or lo > b) for a, b in tracks[k]):
                k += 1
            if k == len(tracks):
                tracks.append([])
            tracks[k].append((lo, hi))
            tx = track_x0 + TRACK * k
            d = f"M{s.right:.1f},{ys:.1f} L{tx:.1f},{ys:.1f} L{tx:.1f},{yt:.1f} L{t.x:.1f},{yt:.1f}"
            if abs(ys - yt) < 0.5:
                d = f"M{s.right:.1f},{ys:.1f} L{t.x:.1f},{yt:.1f}"
            kind = e["edge"]
            if e.get("_rev"):
                # arrow at the left end: draw reversed
                d = f"M{t.x:.1f},{yt:.1f} L{tx:.1f},{yt:.1f} L{tx:.1f},{ys:.1f} L{s.right:.1f},{ys:.1f}"
            routes.append(edge_path(d, kind))
            # label in the channel on the source-side run
            l1s, l2s = labels[ekey(e)]
            color = EDGE[kind][0]
            ly = ys - 4 - 10 * len(l2s) - 11 * (len(l1s) - 1)
            for l in l1s:
                out.append(text(cx + 12, ly, l, LABEL_FONT, color, bold=True))
                ly += 11
            for l in l2s:
                out.append(text(cx + 12, ly, l, DETAIL_FONT, MUTED, italic=True))
                ly += 10
            # port dots
            out.append(f'<circle cx="{s.right:.1f}" cy="{ys:.1f}" r="2.4" fill="{PAPER}" stroke="{color}" stroke-width="1.3"/>')

    # same-lane progression arrows
    for e in same:
        s, t = boxes[e["from"]], boxes[e["to"]]
        if s.parent is t.parent and s.parent is not None and abs(t.y - s.bottom) < PROG_GAP + 2:
            x = s.x + 26
            d = f"M{x:.1f},{s.bottom:.1f} L{x:.1f},{t.y:.1f}"
            routes.append(edge_path(d, e["edge"], width=2))
            l1, _ = edge_lines(e)
            out.append(text(x + 10, (s.bottom + t.y) / 2 + 3.5, l1, LABEL_FONT, EDGE[e["edge"]][0], bold=True))
        else:
            # fallback: route around the left of the lane
            x = min(s.x, t.x) - 16
            d = f"M{s.x:.1f},{s.y + s.header_h / 2:.1f} L{x:.1f},{s.y + s.header_h / 2:.1f} L{x:.1f},{t.y + t.header_h / 2:.1f} L{t.x:.1f},{t.y + t.header_h / 2:.1f}"
            routes.append(edge_path(d, e["edge"], width=2))
            l1, _ = edge_lines(e)
            out.append(text(x - 4, (s.y + t.y) / 2, l1, LABEL_FONT, EDGE[e["edge"]][0], bold=True, anchor="end"))

    # ------------------------------------------------ draw
    body = []
    if band_rect:
        x0, y0, x1, y1 = band_rect
        a, dark, tint = KIND["Grouping"]
        body.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0:.1f}" rx="14" fill="{tint}" stroke="{a}" stroke-width="1.6" stroke-dasharray="7 5"/>')
        body.append(text(x0 + 14, y0 + 19, g.name(band), 12.5, dark, bold=True))
        body.append(text(x1 - 14, y0 + 19, "grouping · reported only as absent", 9.5, MUTED, anchor="end"))

    # lane headers
    titles = {"causes": "CAUSES (CLINICAL DIAGNOSES)", "family": "THE FAMILY", "findings": "FINDINGS & COMPANIONS", "anatomy": "ANATOMY & BINDINGS"}
    for l in lanes:
        body.append(text(lane_x[l], TOP - 14, titles[l], 9.5, MUTED, bold=True, extra='letter-spacing="1.1"'))
        body.append(f'<line x1="{lane_x[l]}" y1="{TOP - 8}" x2="{lane_x[l] + LANE_W[l]}" y2="{TOP - 8}" stroke="{RULE}"/>')

    def draw(b, depth=0):
        kind = g.kind(b.id)
        a, dark, tint = KIND[kind]
        rx = 10 if kind == "Diagnosis" else 3
        italic = kind == "Diagnosis"
        fill = PAPER if depth == 0 else tint
        body.append(f'<rect x="{b.x:.1f}" y="{b.y:.1f}" width="{b.w:.1f}" height="{b.h:.1f}" rx="{rx}" fill="{fill}" fill-opacity="{1 if depth == 0 else 0.75}" stroke="{a}" stroke-width="1.5"/>')
        body.append(f'<rect x="{b.x:.1f}" y="{b.y:.1f}" width="5" height="{b.h:.1f}" rx="2" fill="{a}"/>')
        tx = b.x + PAD + 10
        y = b.y + PAD + 12
        for l in b.title:
            body.append(text(tx, y, l, 11.5, dark, bold=True, italic=italic))
            y += 13
        sub = {"FindingClass": "finding", "Diagnosis": "diagnosis", "AnatomicLocation": "anatomy", "Grouping": "grouping"}[kind]
        if b.id == hub and hub_scope:
            sub += f" · scoped to {g.name(hub_scope)}"
        body.append(text(tx, b.y + b.sub_y, sub, 9, MUTED))
        if b.badge:
            ba, bd, bt = KIND["AnatomicLocation"]
            bx = tx + tw(sub, 9) + 8
            bw = tw("scope: " + b.badge, 9) + 10
            body.append(f'<rect x="{bx:.1f}" y="{b.y + b.sub_y - 9.5:.1f}" width="{bw:.1f}" height="13" rx="6.5" fill="{bt}" stroke="{ba}" stroke-width="0.8"/>')
            body.append(text(bx + 5, b.y + b.sub_y, "scope: " + b.badge, 9, bd))
        ea, ed, _ = KIND["DataElement"]
        yy = b.y + b.sub_y
        for l in b.el_lines:
            yy += 12
            body.append(text(tx, yy, l, 9, ed))
        for bid, by in zip(b.binding_rows, b.bind_y):
            bnd = g.binding[bid]
            body.append(text(tx, b.y + by, f"◦ {g.name(bnd['to'])} · binding {bid}", 9, ed, bold=True))
        # in-port dots
        for e in b.in_ports:
            color = EDGE[e["edge"]][0]
            body.append(f'<circle cx="{b.x:.1f}" cy="{b.port_y[("in", ekey(e))]:.1f}" r="2.4" fill="{PAPER}" stroke="{color}" stroke-width="1.3"/>')
        for c in b.children:
            draw(c, depth + 1)

    for b in boxes.values():
        if b.parent is None:
            draw(b)

    H_body = max(b.bottom for b in boxes.values()) + 30
    legend_h = 62
    H = H_body + legend_h + 10
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" '
           f'font-family="system-ui, -apple-system, Segoe UI, Helvetica, Arial, sans-serif" role="img" aria-label="{esc(view["aria"])}">',
           f"<defs>{markers()}</defs>", f'<rect width="{W:.0f}" height="{H:.0f}" fill="{PAPER}"/>',
           text(24, 30, view["title"], 16, INK, bold=True), text(24, 48, view["subtitle"], 10.5, MUTED),
           *body, *routes, *out,
           legend_block(24, H_body + 4, W - 48,
                        f"Scope: every class is scoped to {g.name(hub_scope)} unless a card says otherwise.",
                        "Boxes inside boxes are subtypes. Each wire carries its own label at its own port; the label sits where the wire leaves its source."),
           "</svg>"]
    return "\n".join(svg)


VIEWS = {
    "pleural-effusion": {
        "hub": "RDE2_000502", "family": "pleural-effusion.jsonl",
        "title": "Pleural effusion: causes on the left, the family in the middle, what it brings on the right",
        "subtitle": "Nested boxes are subtypes. The dashed band is the grouping node. Each wire has its own port and its own label; labels never stack.",
        "aria": "Swimlane diagram: cause diagnoses on the left wired to pleural effusion and its subtypes in the family lane; the family lane wired to pleural thickening, atelectasis, mediastinal shift, and split pleura sign on the right.",
    },
    "pyelonephritis": {
        "hub": "RDE2_000801", "family": "pyelonephritis.jsonl",
        "title": "Acute pyelonephritis: the diagnosis tree on the left, what it looks like on the right",
        "subtitle": "Nested boxes are subtypes. The dashed band is the renal abnormality grouping. Each wire has its own port and its own label.",
        "aria": "Swimlane diagram: the pyelonephritis diagnosis tree in the family lane wired to seven kidney findings in the findings lane, and renal enlargement wired to the kidney length binding in the anatomy lane.",
    },
}

if __name__ == "__main__":
    for key in sys.argv[1:] or VIEWS:
        v = VIEWS[key]
        g = Graph(["core.jsonl", v["family"]])
        open(f"alt2-{key}.svg", "w").write(render(g, v))
        print("wrote", f"alt2-{key}.svg")
