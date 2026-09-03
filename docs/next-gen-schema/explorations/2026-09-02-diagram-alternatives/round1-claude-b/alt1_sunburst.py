"""Alternative 1: radial taxonomy (sunburst) with port-anchored relationship cards.

Layout algorithm (deterministic, described in README.md):
  1. The hub and its SUBTYPE_OF descendants become a sunburst: hub disc, one
     ring per taxonomic depth, each sector centred in its parent's span with
     angular share proportional to leaf count (capped).
  2. The hub's ancestors become concentric halos (rounded rectangles); every
     other class in the view becomes a card at the level of its nearest
     ancestor halo (0 = outside all halos). Cards nest when the parent is a card.
  3. Every typed relationship gets exactly one text row, on the card farthest
     from the hub. The spoke for that relationship leaves/enters the card at
     that row's baseline, so label and edge are one object.
  4. Cards are placed on the side (W/E/S/N) implied by their spokes' angles,
     stacked in columns per halo level, overlap-resolved in one dimension.
  5. Spokes are cubic curves; if the angular gap is too wide they take a
     "ring road" arc around the sunburst instead of crossing it.
"""
from __future__ import annotations

import math
import sys

from common import (EDGE, INK, KIND, MUTED, PAPER, RULE, Graph, ang, edge_lines,
                    edge_path, esc, family_ids, legend_block, markers, polar, text, tw,
                    wrap, wrapdiff)

CW = 220            # card width
PAD = 8
RW, RG = 74, 4      # ring width, ring gap
SPOKE_GAP = 66      # sunburst edge -> first card column
HALO_PAD = 46
COL_GAP = 58        # between halo levels on one side
SECTOR_CAP = 100    # max angular width of one sector, degrees
SIB_GAP = 1.6


class Card:
    def __init__(self, nid):
        self.id = nid
        self.rows = []        # list of dicts: edge, lines, port_dy, other, from_target
        self.nested = []
        self.x = self.y = 0.0
        self.w = CW
        self.h = 0.0
        self.side = "E"
        self.level = 0
        self.theta = 0.0
        self.parent = None
        self.binding_rows = []  # (binding id, label)

    def abs_row_y(self, row):
        return self.y + row["port_dy"]


def measure(g, card, w, hub_scope, extra_title=""):
    """Lay out text inside the card; returns height and sets row port offsets."""
    kind = g.kind(card.id)
    italic = kind == "Diagnosis"
    y = PAD + 12
    inner = w - 2 * PAD - 6
    card.title_lines = wrap(g.name(card.id), 11.5, inner - 4, bold=True, italic=italic, max_lines=3)
    y += 13 * (len(card.title_lines) - 1)
    sub = {"FindingClass": "finding", "Diagnosis": "diagnosis", "AnatomicLocation": "anatomy",
           "Grouping": "grouping"}[kind]
    scope = g.scope(card.id)
    card.badge = g.name(scope) if scope and scope != hub_scope else ""
    card.sub = sub
    y += 13
    card.sub_y = y
    els = g.elements(card.id) if kind != "AnatomicLocation" else []
    card.el_lines = wrap("◦ " + " · ".join(els), 9, inner) if els else []
    for _ in card.el_lines:
        y += 12
    card.el_y = y
    for b in card.binding_rows:
        y += 13
        b["port_dy"] = y - 3
        b["y"] = y
    for r in card.rows:
        y += 5
        l1, l2 = r["lines"]
        y += 12
        r["port_dy"] = y - 3.5
        r["y1"] = y
        r["l1"] = wrap(l1, 9.5, inner - 24, bold=True, max_lines=3)
        y += 11 * (len(r["l1"]) - 1)
        r["l2"] = wrap(l2, 9, inner - 22) if l2 else []
        y += 11 * len(r["l2"])
    for n in card.nested:
        y += 7
        n.w = w - 2 * PAD
        n.h = measure(g, n, n.w, hub_scope)
        n.rel_y = y
        y += n.h
    y += PAD
    card.h = y
    return y


def render(g, view):
    hub = view["hub"]
    ids = family_ids(g, view["family"])
    chain = [a for a in g.ancestors(hub) if a in ids]           # nearest first
    K = len(chain)
    halo_level = {a: K - i for i, a in enumerate(chain)}         # nearest -> K, outermost -> 1
    sun_ids = [hub] + [d for d in g.descendants(hub) if d in ids]
    card_ids = [n for n in ids if n not in sun_ids and n not in chain]
    rels = g.relations(ids)
    hub_scope = g.scope(hub)

    # binding targets (INTERPRETED_FROM) add an anatomy card
    cards = {}
    for n in card_ids:
        cards[n] = Card(n)
    for e in rels:
        if e["edge"] == "INTERPRETED_FROM":
            b = g.binding[e["to"]]
            anat = b["from"]
            if anat not in cards:
                cards[anat] = Card(anat)
            c = cards[anat]
            if not any(r["id"] == e["to"] for r in c.binding_rows):
                c.binding_rows.append({"id": e["to"], "label": f"◦ {g.name(b['to'])}  · binding {e['to']}"})
    for n, c in cards.items():
        p = g.parent.get(n)
        if p in cards:
            c.parent = cards[p]
            cards[p].nested.append(c)
        anc = [a for a in g.ancestors(n) if a in halo_level]
        c.level = max((halo_level[a] for a in anc), default=0)
    top_cards = [c for c in cards.values() if c.parent is None]

    # ------------------------------------------------ rows: one per relation, on the outer end
    def is_card(n):
        return n in cards

    def outer_end(e):
        s, t = e["from"], e["to"]
        if t in g.binding:
            t = g.binding[t]["from"]
        sc, tc = is_card(s), is_card(t)
        if e["edge"] == "INTERPRETED_FROM" and sc:
            return s, False
        if sc and not tc:
            return s, False
        if tc and not sc:
            return t, True
        if sc and tc:
            ls, lt = cards[s].level, cards[t].level
            if ls != lt:
                return (s, False) if ls < lt else (t, True)
            return t, True
        return None, None

    spokes = []   # dict(edge, origin=(kind,id), card, row) or sector-sector
    for e in rels:
        owner, from_target = outer_end(e)
        t_node = g.binding[e["to"]]["from"] if e["to"] in g.binding else e["to"]
        if owner is None:
            spokes.append({"edge": e, "kind": "sun-sun"})
            continue
        far = e["to"] if not from_target else e["from"]
        far_name = g.name(far) if far not in g.binding else g.name(g.binding[far]["to"])
        if e["edge"] == "INTERPRETED_FROM":
            far_name = f"{g.name(g.binding[e['to']]['from'])} {g.name(g.binding[e['to']]['to'])}"
        l1, l2 = edge_lines(e, from_target)
        verb_part, _, props = l1.partition(" · ")
        line1 = f"{verb_part} {far_name}" + (f" · {props}" if props else "")
        row = {"edge": e, "lines": (line1, l2), "from_target": from_target}
        cards[owner].rows.append(row)
        far_end = far if far in g.binding else far
        spokes.append({"edge": e, "kind": "card", "card": cards[owner], "row": row,
                       "far": far_end, "from_target": from_target})

    # ------------------------------------------------ sunburst angles
    def leaves(n):
        ch = [c for c in g.children.get(n, []) if c in sun_ids]
        return 1 if not ch else sum(leaves(c) for c in ch)

    # hub openings from hub-level spokes
    hub_in = [s for s in spokes if s["kind"] == "card" and s["edge"]["to"] == hub]
    hub_out = [s for s in spokes if s["kind"] == "card" and s["edge"]["from"] == hub
               and s["edge"]["edge"] != "MAY_PROGRESS_TO"]
    hub_prog = [s for s in spokes if s["kind"] == "card" and s["edge"]["from"] == hub
                and s["edge"]["edge"] == "MAY_PROGRESS_TO"]
    open_w = max(26, 10 * len(hub_in) + 10) if hub_in else 0
    open_e = max(26, 10 * len(hub_out) + 10) if hub_out else 0
    open_s = max(26, 12 * len(hub_prog) + 10) if hub_prog else 0
    openings = {"W": (180, open_w), "E": (0, open_e), "S": (90, open_s)}

    sector = {}   # nid -> (a0, a1, ring)

    def pull(n):
        p = 0
        for s in spokes:
            if s["kind"] != "card":
                continue
            e = s["edge"]
            if e["to"] == n:
                p -= 1
            if e["from"] == n:
                p += 1
        for c in g.children.get(n, []):
            if c in sun_ids:
                p += pull(c)
        return p

    def biased_mid(cur, share, width, p, east_is_high):
        """Centre of a capped arc inside its share, pushed toward the side it pulls to."""
        slack = (share - width) / 2
        if p == 0 or slack <= 0:
            return cur + share / 2
        toward_high = (p > 0) == east_is_high
        return cur + share / 2 + (slack if toward_high else -slack)

    def place_children(parent, a0, a1, ring, east_is_high=True):
        ch = [c for c in g.children.get(parent, []) if c in sun_ids]
        if not ch:
            return
        ch.sort(key=lambda c: (pull(c), g.name(c)))
        # keep progression pairs adjacent (source immediately before target)
        for e in rels:
            if e["edge"] == "MAY_PROGRESS_TO" and e["from"] in ch and e["to"] in ch:
                ch.remove(e["from"])
                ch.insert(ch.index(e["to"]), e["from"])
        total = sum(leaves(c) for c in ch)
        span = a1 - a0
        cur = a0
        for c in ch:
            share = span * leaves(c) / total
            width = min(share - SIB_GAP, SECTOR_CAP)
            mid = biased_mid(cur, share, width, pull(c), east_is_high)
            sector[c] = (mid - width / 2, mid + width / 2, ring)
            place_children(c, mid - width / 2, mid + width / 2, ring + 1, east_is_high)
            cur += share

    ch1 = [c for c in g.children.get(hub, []) if c in sun_ids]
    if ch1:
        ch1.sort(key=lambda c: (pull(c), g.name(c)))
        for e in rels:
            if e["edge"] == "MAY_PROGRESS_TO" and e["from"] in ch1 and e["to"] in ch1:
                ch1.remove(e["from"])
                ch1.insert(ch1.index(e["to"]), e["from"])
        # north arc: W opening -> E opening clockwise via 270; south arc: via 90
        n_north = math.ceil(len(ch1) / 2) if not hub_prog else len(ch1)
        north, south = ch1[:n_north], ch1[n_north:]
        arcs = []
        # north arc runs from 180+open_w/2 up to 360-open_e/2 (increasing angle)
        arcs.append((north, 180 + open_w / 2, 360 - open_e / 2, True))
        if south:
            # south arc: from E opening (open_e/2) increasing to W opening (180-open_w/2);
            # order west-first means reverse
            arcs.append((list(reversed(south)), open_e / 2, 180 - open_w / 2, False))
        for group, a0, a1, east_is_high in arcs:
            if not group:
                continue
            total = sum(leaves(c) for c in group)
            span = a1 - a0
            cur = a0
            for c in group:
                share = span * leaves(c) / total
                width = min(share - SIB_GAP, SECTOR_CAP)
                mid = biased_mid(cur, share, width, pull(c), east_is_high)
                sector[c] = (mid - width / 2, mid + width / 2, 1)
                place_children(c, mid - width / 2, mid + width / 2, 2, east_is_high)
                cur += share
    depth = max([s[2] for s in sector.values()], default=0)

    # hub disc content
    hub_els = g.elements(hub)
    R0 = 98 if hub_els else 70
    hub_name_lines = wrap(g.name(hub), 14, 1.5 * R0, bold=True, italic=g.kind(hub) == "Diagnosis", max_lines=2)
    hub_el_lines = wrap("◦ " + " · ".join(hub_els), 9, 1.4 * R0) if hub_els else []

    def ring_r(ring):
        r_in = R0 + RG + (ring - 1) * (RW + RG)
        return r_in, r_in + RW

    R_out = ring_r(depth)[1] if depth else R0

    # ------------------------------------------------ measure cards
    for c in top_cards:
        measure(g, c, CW, hub_scope)

    # ------------------------------------------------ origin angle per spoke -> card theta
    def spoke_origin_angle(s):
        far = s["far"]
        if far in sector:
            a0, a1, _ = sector[far]
            return (a0 + a1) / 2
        if far == hub:
            e = s["edge"]
            if e["to"] == hub:
                return 180
            if e["edge"] == "MAY_PROGRESS_TO":
                return 90
            return 0
        return None   # card-to-card; resolved after the far card is placed

    for c in cards.values():
        c.theta = None

    def all_rows(c):
        for r in c.rows:
            yield c, r
        for n in c.nested:
            yield from all_rows(n)

    def top(c):
        while c.parent:
            c = c.parent
        return c

    # first pass: cards whose spokes reach the sunburst
    pending = list(top_cards)
    for _ in range(4):
        for c in list(pending):
            angs = []
            for cc, r in all_rows(c):
                s = next(sp for sp in spokes if sp["kind"] == "card" and sp["row"] is r)
                a = spoke_origin_angle(s)
                if a is None:
                    fc = cards.get(s["far"] if s["far"] not in g.binding else g.binding[s["far"]]["from"])
                    if fc is not None and top(fc).theta is not None:
                        a = top(fc).theta
                if a is not None:
                    angs.append(a)
            if angs:
                x = sum(math.cos(math.radians(a)) for a in angs)
                y = sum(math.sin(math.radians(a)) for a in angs)
                c.theta = ang(0, 0, x, y)
                pending.remove(c)
    for c in pending:
        c.theta = 0.0

    def side_of(t):
        if 135 <= t < 225:
            return "W"
        if t < 45 or t >= 315:
            return "E"
        if 225 <= t < 315:
            return "N"
        return "S"

    def semantic_side(c):
        votes = {"W": 0, "E": 0, "S": 0, "N": 0}
        for cc, r in all_rows(c):
            e = r["edge"]
            far = e["to"] if not r["from_target"] else e["from"]
            in_sun = far == hub or far in sector
            if in_sun:
                if e["to"] == far and e["edge"] == "MAY_CAUSE":
                    votes["W"] += 1
                elif e["from"] == far and e["edge"] == "MAY_PROGRESS_TO":
                    votes["S"] += 1
                else:
                    votes["E"] += 1
            else:
                fc = cards.get(far if far not in g.binding else g.binding[far]["from"])
                if fc is not None and getattr(top(fc), "side_done", False):
                    votes[top(fc).side] += 1
        best = max(votes.values())
        if best == 0:
            return side_of(c.theta)
        for k in ("W", "E", "S", "N"):
            if votes[k] == best:
                return k

    for c in top_cards:
        c.side_done = False
    for _ in range(3):
        for c in top_cards:
            c.side = semantic_side(c)
            c.side_done = True

    # ------------------------------------------------ placement, innermost level outward
    def pack(cs, key_order, size, gap=16):
        """Stack in key order with uniform gaps, centred on the hub axis."""
        cs = sorted(cs, key=key_order)
        total = sum(size(c) for c in cs) + gap * (len(cs) - 1)
        pos, cur = {}, -total / 2
        for c in cs:
            pos[c.id] = cur + size(c) / 2
            cur += size(c) + gap
        return pos

    ext = {"W": -R_out, "E": R_out, "N": -R_out, "S": R_out}   # occupied extent per side
    halos = []  # (level, x0,y0,x1,y1, nid)
    levels_present = sorted({c.level for c in top_cards}, reverse=True)
    all_levels = sorted(set(levels_present) | set(range(0, K + 1)), reverse=True)
    first = True
    for lv in all_levels:
        gap = SPOKE_GAP if first else COL_GAP
        for side in ("W", "E"):
            cs = [c for c in top_cards if c.side == side and c.level == lv]
            if not cs:
                continue
            X = ext[side] + (gap if side == "E" else -gap)          # inner edge of the column
            xc = X + (CW / 2 if side == "E" else -CW / 2)

            def pref(c, side=side):
                return wrapdiff(0 if side == "E" else 180, c.theta) * (1 if side == "E" else -1)
            ys = pack(cs, pref, lambda c: c.h)
            for c in cs:
                c.x = X if side == "E" else X - CW
                c.y = ys[c.id] - c.h / 2
            # an inner column must leave the hub's opening clear when hub spokes
            # continue past it to an outer level on the same side
            hub_spokes = [sp for sp in spokes if sp["kind"] == "card" and sp["far"] == hub]
            if any(top(sp["card"]).side == side and top(sp["card"]).level < lv for sp in hub_spokes):
                lift = (R0 + 14) - min(c.y for c in cs)
                if lift > 0:
                    for c in cs:
                        c.y += lift
            # cards connected to the sunburst must not sit behind an inner column on this side
            inner = [c2 for c2 in top_cards if c2.side == side and c2.level > lv and c2.h]
            sun_linked = {top(sp["card"]).id for sp in spokes if sp["kind"] == "card"
                          and (sp["far"] == hub or sp["far"] in sector)}
            cs = [c for c in cs if c.id in sun_linked]
            if inner and cs:
                band = (min(c2.y for c2 in inner) - 14, max(c2.y + c2.h for c2 in inner) + 14)
                above = [c for c in cs if c.y + c.h / 2 < (band[0] + band[1]) / 2]
                below = [c for c in cs if c not in above]
                bottom = band[0]
                for c in reversed(sorted(above, key=lambda c: c.y)):
                    if c.y + c.h > bottom:
                        c.y = bottom - c.h
                    bottom = c.y - 16
                topy = band[1]
                for c in sorted(below, key=lambda c: c.y):
                    if c.y < topy:
                        c.y = topy
                    topy = c.y + c.h + 16
            first = False
        for side in ("N", "S"):
            cs = [c for c in top_cards if c.side == side and c.level == lv]
            if not cs:
                continue
            Y = ext[side] + (gap if side == "S" else -gap)
            hmax = max(c.h for c in cs)
            yc = Y + (hmax / 2 if side == "S" else -hmax / 2)

            def pref(c, side=side):
                return wrapdiff(90 if side == "S" else 270, c.theta) * (-1 if side == "S" else 1)
            xs = pack(cs, pref, lambda c: c.w, gap=20)
            for c in cs:
                c.x = xs[c.id] - c.w / 2
                c.y = Y if side == "S" else Y - c.h
            first = False
        # update extents from everything placed at this level or inside
        for c in top_cards:
            if c.level >= lv and c.h:
                ext["W"] = min(ext["W"], c.x)
                ext["E"] = max(ext["E"], c.x + c.w)
                ext["N"] = min(ext["N"], c.y)
                ext["S"] = max(ext["S"], c.y + c.h)
        if lv >= 1:
            pad = HALO_PAD
            rect = [ext["W"] - pad, ext["N"] - pad - 8, ext["E"] + pad, ext["S"] + pad]
            halos.append((lv, *rect, chain[K - lv]))
            ext = {"W": rect[0], "E": rect[2], "N": rect[1], "S": rect[3]}
            first = False

    # absolute positions of nested cards
    def settle(c):
        for n in c.nested:
            n.x = c.x + PAD
            n.y = c.y + n.rel_y
            settle(n)
    for c in top_cards:
        settle(c)

    # ------------------------------------------------ spokes geometry
    def port(card, row, origin_xy):
        """Port point and travel direction (unit) for a spoke arriving at card row.

        Side entry lands exactly on the row. Top/bottom entry (used when the origin
        is above/below a card and within its x-span) lands on the edge and a short
        leader inside the card continues down/up to the row."""
        y = card.abs_row_y(row) if row is not None else card.y + card.h / 2
        tc = top(card)
        ox, oy = origin_xy
        within = card.x + 10 <= ox <= card.x + card.w - 10
        if within and (oy < card.y or oy > card.y + card.h):
            idx = card.rows.index(row) if row in card.rows else 0
            x = card.x + 11 + 7 * idx
            if oy < card.y:
                row["leader"] = (x, tc.y if card is tc else card.y, y)
                return (x, tc.y if card is tc else card.y), (0, 1)
            row["leader"] = (x, card.y + card.h, y)
            return (x, card.y + card.h), (0, -1)
        if ox < card.x - 4:
            left = True
        elif ox > card.x + card.w + 4:
            left = False
        elif tc.side in ("N", "S"):
            left = ox <= card.x + card.w / 2
        else:
            left = tc.side == "E"
        if left:
            return (card.x, y), (1, 0)
        return (card.x + card.w, y), (-1, 0)

    def sector_origins():
        """Assign each sector-based spoke an origin angle spread over its sector."""
        by = {}
        for s in spokes:
            if s["kind"] == "card" and s["far"] in sector:
                by.setdefault(s["far"], []).append(s)
        for nid, ss in by.items():
            a0, a1, ring = sector[nid]
            r_out = ring_r(ring)[1]
            # order by target card angle
            ss.sort(key=lambda s: wrapdiff((a0 + a1) / 2, ang(0, 0, s["card"].x + s["card"].w / 2, s["card"].abs_row_y(s["row"]))))
            m = len(ss)
            for j, s in enumerate(ss):
                a = a0 + (a1 - a0) * (j + 1) / (m + 1)
                s["origin"] = polar(0, 0, r_out, a)
                s["oangle"] = a
        by = {}
        for s in spokes:
            if s["kind"] == "card" and s["far"] == hub:
                e = s["edge"]
                key = "W" if e["to"] == hub else ("S" if e["edge"] == "MAY_PROGRESS_TO" else "E")
                by.setdefault(key, []).append(s)
        for key, ss in by.items():
            centre, width = openings[key]
            ss.sort(key=lambda s: wrapdiff(centre, ang(0, 0, s["card"].x + s["card"].w / 2, s["card"].abs_row_y(s["row"]))))
            m = len(ss)
            for j, s in enumerate(ss):
                a = centre - width / 2 + width * (j + 1) / (m + 1)
                s["origin"] = polar(0, 0, R0, a)
                s["oangle"] = a
        for s in spokes:
            if s["kind"] == "card" and "origin" not in s:
                fc = cards[s["far"] if s["far"] not in g.binding else g.binding[s["far"]]["from"]]
                # card-to-card: origin on the far card's outward side, at a free slot
                oc = s["card"]
                if oc.x < fc.x + fc.w and oc.x + oc.w > fc.x:      # stacked
                    if oc.y > fc.y:
                        s["origin"] = (fc.x + fc.w / 2, fc.y + fc.h)
                    else:
                        s["origin"] = (fc.x + fc.w / 2, fc.y)
                    s["oangle"] = "v"
                else:
                    ox = fc.x + fc.w if oc.x > fc.x else fc.x
                    oy = fc.y + fc.h / 2
                    for b in fc.binding_rows:
                        if b["id"] == s["edge"]["to"]:
                            oy = fc.y + b["port_dy"]
                    s["origin"] = (ox, oy)
                    s["oangle"] = None
    sector_origins()

    def spoke_path(s, road_index):
        ox, oy = s["origin"]
        (px, py), (dx, dy) = port(s["card"], s["row"], (ox, oy))
        s["row"]["port_xy"] = (px, py)
        e = s["edge"]
        # direction: arrow at the card if the card is the target, else at the origin
        arrow_at_card = s["from_target"]
        a_o = s["oangle"]
        if a_o == "v":
            d = max(24, abs(py - oy) * 0.5)
            sgn = 1 if py > oy else -1
            pts = (ox, oy, ox, oy + sgn * d, px - dx * d, py - dy * d, px, py)
        elif a_o is None:
            # card to card: simple S-curve
            d = max(30, abs(px - ox) * 0.45)
            sgn = 1 if px > ox else -1
            pts = (ox, oy, ox + sgn * d, oy, px - dx * d, py - dy * d, px, py)
        else:
            a_p = ang(0, 0, px, py)
            if s["far"] == hub:
                e2 = s["edge"]
                key = "W" if e2["to"] == hub else ("S" if e2["edge"] == "MAY_PROGRESS_TO" else "E")
                tol = openings[key][1] / 2 + 12
            else:
                tol = 62
            if abs(wrapdiff(a_o, a_p)) <= tol:
                d = max(40, math.hypot(px - ox, py - oy) * 0.42)
                c1 = polar(ox, oy, d, a_o)
                c2 = (px - dx * d, py - dy * d)
                pts = (ox, oy, *c1, *c2, px, py)
            else:
                r_road = R_out + 44 + 8 * road_index
                sweep = 1 if wrapdiff(a_o, a_p) > 0 else 0
                rx, ry = polar(0, 0, r_road, a_o)
                # leave the road at the angle where the port lies, then curve in
                a_leave = a_p + (-12 if sweep else 12) * (1 if abs(px) < abs(py) else 0.3)
                lx, ly = polar(0, 0, r_road, a_leave)
                d = max(30, math.hypot(px - lx, py - ly) * 0.4)
                t = polar(0, 0, 1, a_leave + (90 if sweep else -90))
                c1 = (lx + t[0] * d, ly + t[1] * d)
                c2 = (px - dx * d, py - dy * d)
                path = (f"M{ox:.1f},{oy:.1f} L{rx:.1f},{ry:.1f} "
                        f"A{r_road:.1f},{r_road:.1f} 0 0 {sweep} {lx:.1f},{ly:.1f} "
                        f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {px:.1f},{py:.1f}")
                return path, arrow_at_card
        x0, y0, x1, y1, x2, y2, x3, y3 = pts
        if arrow_at_card:
            return f"M{x0:.1f},{y0:.1f} C{x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f} {x3:.1f},{y3:.1f}", True
        return f"M{x3:.1f},{y3:.1f} C{x2:.1f},{y2:.1f} {x1:.1f},{y1:.1f} {x0:.1f},{y0:.1f}", False

    # ------------------------------------------------ emit
    out = []
    # halos, outermost first
    for lv, x0, y0, x1, y1, nid in sorted(halos):
        a, dark, tint = KIND[g.kind(nid)]
        dash = ' stroke-dasharray="7 5"' if g.kind(nid) == "Grouping" else ""
        out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="22" '
                   f'fill="{tint}" fill-opacity="0.55" stroke="{a}" stroke-width="1.6"{dash}/>')
        label = g.name(nid)
        sub = {"Grouping": "grouping · reported only as absent", "Diagnosis": "diagnosis", "FindingClass": "finding"}[g.kind(nid)]
        out.append(text(x0 + 16, y0 + 20, label, 12.5, dark, bold=True, italic=g.kind(nid) == "Diagnosis"))
        out.append(text(x1 - 16, y0 + 20, sub, 9.5, MUTED, anchor="end"))

    # sunburst sectors
    for nid, (a0, a1, ring) in sector.items():
        r_in, r_out = ring_r(ring)
        p0 = polar(0, 0, r_in, a0)
        p1 = polar(0, 0, r_out, a0)
        p2 = polar(0, 0, r_out, a1)
        p3 = polar(0, 0, r_in, a1)
        large = 1 if a1 - a0 > 180 else 0
        d = (f"M{p0[0]:.1f},{p0[1]:.1f} L{p1[0]:.1f},{p1[1]:.1f} "
             f"A{r_out},{r_out} 0 {large} 1 {p2[0]:.1f},{p2[1]:.1f} "
             f"L{p3[0]:.1f},{p3[1]:.1f} A{r_in},{r_in} 0 {large} 0 {p0[0]:.1f},{p0[1]:.1f} Z")
        a, dark, tint = KIND[g.kind(nid)]
        out.append(f'<path d="{d}" fill="{tint}" stroke="{a}" stroke-width="1.4"/>')
        mid = (a0 + a1) / 2
        r_mid = (r_in + r_out) / 2
        cx, cy = polar(0, 0, r_mid, mid)
        chord = 2 * ((r_in + r_out) / 2 - 14) * math.sin(math.radians((a1 - a0) / 2)) - 6
        chord = min(chord, RW * 1.9)
        italic = g.kind(nid) == "Diagnosis"
        size = 10
        lines = wrap(g.name(nid), size, chord, bold=True, italic=italic, max_lines=3)
        if any(tw(l, size, True, italic) > chord for l in lines) or len(lines) > 3:
            size = 9.5
            lines = wrap(g.name(nid), size, chord, bold=True, italic=italic, max_lines=4)
        els = g.elements(nid)
        n_lines = len(lines) + (1 if els else 0)
        y0 = cy - (n_lines - 1) * 6 + 4
        for i, l in enumerate(lines):
            out.append(text(cx, y0 + i * 12, l, size, dark, bold=True, italic=italic, anchor="middle"))
        if els:
            ea, ed, _ = KIND["DataElement"]
            out.append(text(cx, y0 + len(lines) * 12, "◦ " + " · ".join(els), 8.5, ed, anchor="middle"))

    # progression arcs between sectors
    chip_later = []
    for s in spokes:
        if s["kind"] != "sun-sun":
            continue
        e = s["edge"]
        if e["from"] in sector and e["to"] in sector:
            a_s = sum(sector[e["from"]][:2]) / 2
            a_t = sum(sector[e["to"]][:2]) / 2
            r = max(ring_r(sector[e["from"]][2])[1], ring_r(sector[e["to"]][2])[1]) + 9
            sweep = 1 if wrapdiff(a_s, a_t) > 0 else 0
            # shorten toward the target sector's edge so the arrow sits in the gap
            shrink = 6
            a_s2 = a_s + (shrink if sweep else -shrink)
            a_t2 = a_t - (shrink if sweep else -shrink)
            p0, p1 = polar(0, 0, r, a_s2), polar(0, 0, r, a_t2)
            out.append(edge_path(f"M{p0[0]:.1f},{p0[1]:.1f} A{r},{r} 0 0 {sweep} {p1[0]:.1f},{p1[1]:.1f}", e["edge"]))
            mid = (a_s2 + a_t2) / 2
            lx, ly = polar(0, 0, r + 12, mid)
            l1, _ = edge_lines(e)
            chip_later.append((lx, ly, l1, EDGE[e["edge"]][0]))

    # spokes
    road = 0
    for s in spokes:
        if s["kind"] != "card":
            continue
        path, _ = spoke_path(s, road)
        if "A" in path.split("C")[0]:
            road += 1
        out.append(edge_path(path, s["edge"]["edge"]))

    # hub disc
    a, dark, tint = KIND[g.kind(hub)]
    out.append(f'<circle cx="0" cy="0" r="{R0}" fill="{tint}" stroke="{a}" stroke-width="2"/>')
    n_lines = len(hub_name_lines) + 1 + len(hub_el_lines)
    y = -(n_lines * 12) / 2 + 8
    for l in hub_name_lines:
        out.append(text(0, y, l, 14, dark, bold=True, italic=g.kind(hub) == "Diagnosis", anchor="middle"))
        y += 15
    sub = {"FindingClass": "finding", "Diagnosis": "diagnosis"}[g.kind(hub)]
    if hub_scope:
        sub += f" · scoped to {g.name(hub_scope)}"
    out.append(text(0, y, sub, 9, MUTED, anchor="middle"))
    y += 13
    ea, ed, _ = KIND["DataElement"]
    for l in hub_el_lines:
        out.append(text(0, y, l, 9, ed, anchor="middle"))
        y += 11

    # cards
    def draw_card(c, nested=False):
        kind = g.kind(c.id)
        a, dark, tint = KIND[kind]
        rx = 10 if kind == "Diagnosis" else 3
        italic = kind == "Diagnosis"
        out.append(f'<rect x="{c.x:.1f}" y="{c.y:.1f}" width="{c.w}" height="{c.h:.1f}" rx="{rx}" '
                   f'fill="{PAPER if not nested else tint}" stroke="{a}" stroke-width="{1.2 if nested else 1.5}"/>')
        out.append(f'<rect x="{c.x:.1f}" y="{c.y:.1f}" width="5" height="{c.h:.1f}" rx="2" fill="{a}"/>')
        tx = c.x + PAD + 10
        y = c.y + PAD + 12
        for l in c.title_lines:
            out.append(text(tx, y, l, 11.5, dark, bold=True, italic=italic))
            y += 13
        subline = c.sub
        out.append(text(tx, c.y + c.sub_y, subline, 9, MUTED))
        if c.badge:
            ba, bd, bt = KIND["AnatomicLocation"]
            bx = tx + tw(subline, 9) + 8
            bw = tw("scope: " + c.badge, 9) + 10
            out.append(f'<rect x="{bx:.1f}" y="{c.y + c.sub_y - 9.5:.1f}" width="{bw:.1f}" height="13" rx="6.5" fill="{bt}" stroke="{ba}" stroke-width="0.8"/>')
            out.append(text(bx + 5, c.y + c.sub_y, "scope: " + c.badge, 9, bd))
        ea, ed, _ = KIND["DataElement"]
        yy = c.y + c.sub_y
        for l in c.el_lines:
            yy += 12
            out.append(text(tx, yy, l, 9, ed))
        for b in c.binding_rows:
            out.append(text(tx, c.y + b["y"], b["label"], 9, ed, bold=True))
            bx = c.x if top(c).side == "E" else c.x + c.w
            out.append(f'<circle cx="{bx:.1f}" cy="{c.y + b["port_dy"]:.1f}" r="2.6" fill="{PAPER}" stroke="{ed}" stroke-width="1.4"/>')
        for r in c.rows:
            color = EDGE[r["edge"]["edge"]][0]
            for i, l in enumerate(r["l1"]):
                out.append(text(tx + 8, c.y + r["y1"] + 11 * i, l, 9.5, color, bold=True))
            px, py = r.get("port_xy", (c.x, c.abs_row_y(r)))
            if "leader" in r:
                lx, ly0, ly1 = r["leader"]
                out.append(f'<path d="M{lx:.1f},{ly0:.1f} L{lx:.1f},{ly1 - 3:.1f}" fill="none" stroke="{color}" stroke-width="1.4"/>')
                px, py = lx, ly1
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.6" fill="{PAPER}" stroke="{color}" stroke-width="1.4"/>')
            base = c.y + r["y1"] + 11 * (len(r["l1"]) - 1)
            for i, l in enumerate(r["l2"]):
                out.append(text(tx + 8, base + 11 * (i + 1), l, 9, MUTED, italic=True))
        for n in c.nested:
            draw_card(n, nested=True)

    for c in top_cards:
        draw_card(c)

    # chips for sector-to-sector arcs
    for lx, ly, s, color in chip_later:
        w = tw(s, 9) + 10
        out.append(f'<rect x="{lx - w / 2:.1f}" y="{ly - 10:.1f}" width="{w:.1f}" height="14" rx="4" fill="{PAPER}" fill-opacity="0.95" stroke="{color}" stroke-width="0.8"/>')
        out.append(text(lx, ly, s, 9, color, anchor="middle"))

    # bbox
    xs, ys = [-R_out], [-R_out]
    xs2, ys2 = [R_out], [R_out]
    for lv, x0, y0, x1, y1, nid in halos:
        xs.append(x0); ys.append(y0); xs2.append(x1); ys2.append(y1)
    for c in top_cards:
        xs.append(c.x); ys.append(c.y); xs2.append(c.x + c.w); ys2.append(c.y + c.h)
    minx, miny, maxx, maxy = min(xs) - 24, min(ys) - 24, max(xs2) + 24, max(ys2) + 24
    W = maxx - minx
    title_h = 58
    legend_h = 62
    H = maxy - miny + title_h + legend_h
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" '
           f'font-family="system-ui, -apple-system, Segoe UI, Helvetica, Arial, sans-serif" role="img" aria-label="{esc(view["aria"])}">',
           f"<defs>{markers()}</defs>", f'<rect width="{W:.0f}" height="{H:.0f}" fill="{PAPER}"/>',
           text(24, 28, view["title"], 16, INK, bold=True), text(24, 46, view["subtitle"], 10.5, MUTED),
           f'<g transform="translate({-minx:.1f},{-miny + title_h:.1f})">', *out, "</g>",
           legend_block(24, H - legend_h + 4, W - 48,
                        f"Scope: every class is scoped to {g.name(hub_scope)} unless a card says otherwise.",
                        "Diagnoses are italic with rounded corners; findings upright with square corners. "
                        "Each relationship's properties sit on the row where its line meets the card."),
           "</svg>"]
    return "\n".join(svg)


VIEWS = {
    "pleural-effusion": {
        "hub": "RDE2_000502", "family": "pleural-effusion.jsonl",
        "title": "Pleural effusion: the finding, its kinds, what causes it, and what it brings",
        "subtitle": "Rings are subtypes (a kind of the thing inside them). The dashed frame is the grouping node. Each line ends on the row that describes it.",
        "aria": "Sunburst of pleural effusion and its six diagnosis subtypes inside the pleural abnormality grouping frame, with cause cards on the left and manifestation and complication cards on the right.",
    },
    "pyelonephritis": {
        "hub": "RDE2_000801", "family": "pyelonephritis.jsonl",
        "title": "Acute pyelonephritis: the diagnosis, its manifestations, and its neighbours in the kidney",
        "subtitle": "Rings are subtypes. Nested frames are the ancestors: pyelonephritis, then the renal abnormality grouping. Each line ends on the row that describes it.",
        "aria": "Sunburst of acute pyelonephritis with emphysematous pyelonephritis as its subtype, inside the pyelonephritis and renal abnormality frames, with finding cards around it and the kidney binding outside.",
    },
}

if __name__ == "__main__":
    for key in sys.argv[1:] or VIEWS:
        v = VIEWS[key]
        g = Graph(["core.jsonl", v["family"]])
        svg = render(g, v)
        outp = f"alt1-{key}.svg"
        open(outp, "w").write(svg)
        print("wrote", outp)
