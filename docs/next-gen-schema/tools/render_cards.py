#!/usr/bin/env python3
"""The mat and the tree, per docs/plans/2026-09-02-mat-and-tree-decisions.md.

  render_cards.py VIEW.json > out.svg        VIEW is {"kind": "mat"|"tree", "hub": "<id>", "title": "..."}
  render_cards.py mat  RDE2_000502 > out.svg
  render_cards.py tree RDE2_000516 > out.svg

The MAT is one context object drawn in full (title, anatomy, text, attribute table, relationship
containers, mappings, stat row). Everything one hop away is a minimal mini-card (name, kind, id)
inside a container labelled with the relationship read from the context object's side. An edge
with typicality or specificity draws as a dotted edge box around the mini-card with those two
values in gray riding the bottom border. No wires.

The TREE is the is-a outline of a family rooted at a grouping node: one mini-card per row,
indented by subsumption, nothing else drawn. Relationships are for the interactive layer.
Rows are the card height (50 px) plus 16 px of clearance so the site layer has room for
relationship labels riding box borders above and below a card.

Hover: every mini-card has a detail card revealed by CSS (`:has()`), so the SVG works alone in a
browser and inline in HTML. Scope and context edges propagate down SUBTYPE_OF when a node has
none of its own; the mat says so in gray. Deterministic output; byte-checked by the bundle checker.
"""
import json, os, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from graph import load_graph  # noqa: E402

ACCENT = {"FindingClass": ("#2563eb", "#1e3a8a", "#eff6ff"), "Diagnosis": ("#7c3aed", "#4c1d95", "#f5f3ff"),
          "Grouping": ("#64748b", "#334155", "#f8fafc"), "DataElement": ("#16a34a", "#14532d", "#f0fdf4"),
          "AnatomicLocation": ("#d97706", "#78350f", "#fffbeb"), "Concept": ("#94a3b8", "#475569", "#f8fafc")}
KIND = {"FindingClass": "FINDING", "Diagnosis": "DIAGNOSIS", "Grouping": "GROUPING", "DataElement": "ELEMENT",
        "AnatomicLocation": "ANATOMY", "Concept": "CONCEPT", "Value": "VALUE", "RelationshipType": "RELATIONSHIP"}
INK, MUTED, RULE, SOFT, GRAY = "#1f2937", "#64748b", "#cbd5e1", "#f8fafc", "#94a3b8"
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, monospace"
W, PAD, GAP = 1100, 14, 8
FS, FS_S, FS_T = 15, 12.5, 24          # body, small, title
FS_XS = 12                             # floor: ids, container labels, edge-box props (>= 11 px rendered on the site)
MINI_H, MINI_COLS = 50, 3
CONTAINERS = [("A KIND OF", "SUBTYPE_OF", "out"), ("KINDS OF", "SUBTYPE_OF", "in"),
              ("MANIFESTS AS", "MAY_MANIFEST_AS", "out"), ("MAY REPRESENT", "MAY_MANIFEST_AS", "in"),
              ("MAY BE CAUSED BY", "MAY_CAUSE", "in"), ("MAY CAUSE", "MAY_CAUSE", "out"),
              ("PROGRESSES TO", "MAY_PROGRESS_TO", "out"), ("PROGRESSES FROM", "MAY_PROGRESS_TO", "in"),
              ("OCCURS WITH", "OCCURS_WITH", "both"), ("ASSESSED BY", "ASSESSED_BY", "out"), ("ASSESSES", "ASSESSED_BY", "in"),
              ("MAY HAVE COMPONENT", "MAY_HAVE_COMPONENT", "out"), ("MAY BE COMPONENT OF", "MAY_HAVE_COMPONENT", "in"),
              ("MAY BE RELATED TO", "MAY_BE_RELATED_TO", "both")]
CONTEXT = [("MODALITY", "SEEN_ON"), ("REGION", "IN_REGION"), ("SUBSPECIALTY", "IN_SUBSPECIALTY"), ("SEX", "SEX"),
           ("AGE", "AGE_APPLICABILITY"), ("COURSE", "TIME_COURSE"), ("ETIOLOGY", "HAS_ETIOLOGY")]
PROP_WORDS = {"very_frequent": "very frequent", "highly_suggestive": "highly suggestive", "very_rare": "very rare"}


def esc(s): return html.escape(str(s), quote=True)
def tw(s, fs, bold=False): return len(str(s)) * fs * (0.58 if bold else 0.53)


def txt(x, y, s, fs: float = FS, fill=INK, anchor="start", weight=None, mono=False, italic=False):
    a = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'font-size="{fs}"', f'fill="{fill}"']
    if anchor != "start": a.append(f'text-anchor="{anchor}"')
    if weight: a.append(f'font-weight="{weight}"')
    if mono: a.append(f'font-family="{MONO}"')
    if italic: a.append('font-style="italic"')
    return f'<text {" ".join(a)}>{esc(s)}</text>'


def wrap(s, fs, max_w, max_lines=None, bold=False):
    words, lines, cur = str(s).split(), [], ""
    for w in words:
        if cur and tw(cur + " " + w, fs, bold) > max_w:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]; lines[-1] = lines[-1].rstrip(" .,;") + " …"
    return lines


class Cards:
    def __init__(self, graph):
        self.g = graph
        self.n = graph.nodes

    # ---- graph queries -----------------------------------------------------------
    def name(self, nid): return self.n.get(nid, {}).get("name", nid)
    def kind(self, nid): return KIND.get(self.n.get(nid, {}).get("node", ""), "NODE")

    def parents(self, nid):
        return [e["to"] for e in self.g.out_edges(nid) if e["edge"] == "SUBTYPE_OF" and e["to"] in self.n]

    def children(self, nid):
        return sorted((e["from"] for e in self.g.in_edges(nid) if e["edge"] == "SUBTYPE_OF" and e["from"] in self.n),
                      key=lambda c: self.name(c).lower())

    def own_or_inherited(self, nid, edge):
        """Edges of a type on the node, or on the nearest ancestor that has any. Returns (edges, source_id)."""
        seen, queue = set(), [nid]
        while queue:
            cur = queue.pop(0)
            if cur in seen: continue
            seen.add(cur)
            es = [e for e in self.g.out_edges(cur) if e["edge"] == edge]
            if es: return es, cur
            queue.extend(self.parents(cur))
        return [], None

    def scope(self, nid):
        es, src = self.own_or_inherited(nid, "SCOPED_TO")
        return [(e["to"], e.get("props", {})) for e in es], src

    def context(self, nid):
        out = {}
        for label, edge in CONTEXT:
            es, src = self.own_or_inherited(nid, edge)
            out[label] = ([e["to"] for e in es], src)
        return out

    def mappings(self, nid):
        return [(e["to"].split(":", 1)[0], e["to"].split(":", 1)[1], e.get("props", {}).get("display", ""), e["edge"])
                for e in self.g.out_edges(nid) if e["edge"] in ("exactMatch", "closeMatch")]

    def elements(self, nid):
        return [(e["to"], e.get("props", {})) for e in self.g.out_edges(nid) if e["edge"] == "HAS_ELEMENT" and e["to"] in self.n]

    def values(self, eid):
        vals = [(e.get("props", {}).get("rank", 0), self.n[e["to"]]) for e in self.g.out_edges(eid) if e["edge"] == "member" and e["to"] in self.n]
        return [v for _, v in sorted(vals, key=lambda t: (t[0], t[1]["id"]))]

    def code_str(self, system, code, display, match="exactMatch"):
        s = f'{code} “{display}”' if display else code
        if system == "RADLEX": s = f'RadLex {s}'
        elif system == "SNOMEDCT": s = f'SNOMED CT {s}'
        elif system == "LOINC": s = f'LOINC {s}'
        else: s = f'{system} {s}'
        return s + (" (close)" if match == "closeMatch" else "")

    def concept_str(self, cid):
        c = self.n.get(cid)
        if not c: return cid
        if cid.startswith("RID"): return f'{c["name"]} {cid}'
        if cid.startswith("RDE2_"): return f'{c["name"]} {cid}'
        return c["name"]

    def anatomy_str(self, nid):
        sc, src = self.scope(nid)
        if not sc: return "⌂ —", None
        parts = []
        for loc, p in sc:
            parts.append(f'{loc} “{self.name(loc)}”' + (f' · {p["kind"]}' if p.get("kind") else ""))
        s = "⌂ " + " · ".join(parts)
        return s, (src if src != nid else None)

    def container_rows(self, hub):
        """[(label, [(other_id, edge)])] in fixed order, empty ones dropped."""
        rows = []
        for label, etype, direction in CONTAINERS:
            items = []
            for e in self.g.edges:
                if e["edge"] != etype: continue
                if direction in ("out", "both") and e["from"] == hub and e["to"] in self.n:
                    items.append((e["to"], e))
                elif direction in ("in", "both") and e["to"] == hub and e["from"] in self.n:
                    items.append((e["from"], e))
            items = sorted({o: e for o, e in items}.items(), key=lambda t: self.name(t[0]).lower())
            if items: rows.append((label, items))
        return rows

    # ---- drawing primitives -------------------------------------------------------
    def mini(self, nid, x, y, w, h=MINI_H):
        node = self.n.get(nid, {"node": "Concept"})
        a, dark, bg = ACCENT.get(node["node"], ACCENT["Concept"])
        name = self.name(nid)
        fs = min(15, (w - 24) / (len(name) * 0.58)) if name else 15
        return (f'<g class="mini" id="m-{esc(nid)}" data-node="{esc(nid)}">'
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="6" fill="{bg}" stroke="{RULE}"/>'
                f'<rect x="{x:.1f}" y="{y:.1f}" width="4" height="{h}" rx="2" fill="{a}"/>'
                + txt(x + 12, y + 22, name, fs, dark, weight="600")
                + txt(x + 12, y + 40, f'{self.kind(nid)} · {nid}', FS_XS, MUTED, mono=True) + "</g>")

    def detail(self, nid, x, y, w=480, hub=None):
        """The hover card: a fuller mini-card, not the whole mat."""
        node = self.n.get(nid, {"node": "Concept", "name": nid})
        a, dark, bg = ACCENT.get(node["node"], ACCENT["Concept"])
        lines = []   # (text, fs, fill, weight, mono)
        d = wrap(node.get("definition", ""), FS_S, w - 24, 4)
        for ln in d: lines.append((ln, FS_S, INK, None, False))
        anat, inh = self.anatomy_str(nid)
        if anat != "⌂ —": lines.append((anat + (f'  (inherited from {self.name(inh)})' if inh else ""), FS_S, "#78350f", None, False))
        syn = node.get("synonyms") or []
        if syn: lines.append(("synonyms: " + " · ".join(s["term"] for s in syn), FS_XS, MUTED, None, False))
        els = self.elements(nid)
        if els: lines.append(("attributes: " + " · ".join(self.name(e) for e, _ in els), FS_XS, "#14532d", None, False))
        conns = []
        for label, etype, direction in CONTAINERS:
            for e in self.g.edges:
                if e["edge"] != etype: continue
                other = None
                if direction in ("out", "both") and e["from"] == nid and e["to"] in self.n and e["to"] != hub: other = e["to"]
                elif direction in ("in", "both") and e["to"] == nid and e["from"] in self.n and e["from"] != hub: other = e["from"]
                if other: conns.append(f'{label.lower()}  {self.name(other)}' + self.props_suffix(e))
        for c in conns[:6]: lines.append((c, FS_XS, "#4c1d95", None, False))
        if len(conns) > 6: lines.append((f'… {len(conns) - 6} more', FS_XS, MUTED, None, False))
        for sysm, code, disp, match in self.mappings(nid): lines.append((self.code_str(sysm, code, disp, match), FS_XS, MUTED, None, False))
        ctx = self.context(nid)
        stats = " · ".join(f'{label.lower()} {", ".join(self.name(c) for c in cs)}' for label, (cs, _) in ctx.items() if cs)
        if stats: lines.extend((ln, FS_XS, MUTED, None, False) for ln in wrap(stats, FS_XS, w - 24, 2))
        h = 48 + sum(16 if fs >= FS_S else 15 for _, fs, *_ in lines) + 6
        idstr = f'{self.kind(nid)} · {nid}'
        nm = node.get("name", nid)
        namefs = min(15, (w - 40 - len(idstr) * 7.2) / (len(nm) * 0.58)) if nm else 15
        out = [f'<g class="detail" id="d-{esc(nid)}" transform="translate({x:.1f},{y:.1f})">',
               f'<rect x="0" y="0" width="{w}" height="{h}" rx="8" fill="#ffffff" stroke="{a}" stroke-width="1.2"/>',
               f'<rect x="0" y="0" width="{w}" height="36" rx="8" fill="{bg}"/><rect x="0" y="26" width="{w}" height="10" fill="{bg}"/>',
               txt(12, 24, nm, namefs, dark, weight="700"), txt(w - 12, 24, idstr, FS_XS, MUTED, anchor="end", mono=True)]
        yy = 52
        for s, fs, fill, weight, mono in lines:
            out.append(txt(12, yy, s, fs, fill, weight=weight, mono=mono)); yy += 16 if fs >= FS_S else 15
        out.append("</g>")
        return "".join(out)

    def props_suffix(self, e):
        p = e.get("props", {})
        bits = [PROP_WORDS.get(p[k], str(p[k]).replace("_", " ")) for k in ("typicality", "specificity") if k in p]
        return ("  · " + " · ".join(bits)) if bits else ""

    def edge_line(self, e):
        p = e.get("props", {})
        bits = [PROP_WORDS.get(p[k], str(p[k]).replace("_", " ")) for k in ("typicality", "specificity") if k in p]
        return " · ".join(bits)

    # ---- the mat --------------------------------------------------------------------
    def mat(self, hub, title=None):
        node = self.n[hub]
        a, dark, bg = ACCENT.get(node["node"], ACCENT["Concept"])
        body, details = [], []
        iw = W - 2 * PAD
        y = 0
        # 1 title band
        body.append(f'<rect x="0" y="0" width="{W}" height="56" fill="{bg}"/>'
                    f'<rect x="0" y="0" width="6" height="56" fill="{a}"/>'
                    + txt(PAD + 4, 37, node["name"], FS_T, dark, weight="700")
                    + txt(W - PAD, 36, f'{self.kind(hub)} · {hub}', FS_S, MUTED, anchor="end", mono=True))
        y = 56
        # 2 anatomy line
        anat, inh = self.anatomy_str(hub)
        body.append(f'<rect x="0" y="{y}" width="{W}" height="28" fill="#fffbeb"/>'
                    + txt(PAD + 4, y + 19, anat, FS_S, "#78350f")
                    + (txt(W - PAD, y + 19, f'inherited from {self.name(inh)}', FS_XS, MUTED, anchor="end", italic=True) if inh else ""))
        y += 28
        body.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{RULE}"/>')
        # 3 text
        y += 10
        for ln in wrap(node.get("definition", ""), FS, iw - 8):
            y += 19; body.append(txt(PAD + 4, y, ln, FS, INK))
        syn = node.get("synonyms") or []
        if syn:
            y += 17; body.append(txt(PAD + 4, y, "synonyms: " + " · ".join(s["term"] + (f' ({s["type"]})' if s.get("type") not in (None, "synonym") else "") for s in syn), FS_S, MUTED))
        if node.get("note"):
            for ln in wrap("note: " + node["note"], FS_S, iw - 8, 2):
                y += 16; body.append(txt(PAD + 4, y, ln, FS_S, MUTED, italic=True))
        y += 12
        # 4 attributes
        els = self.elements(hub)
        if els:
            body.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{RULE}"/>')
            y += 21; body.append(txt(PAD + 4, y, "ATTRIBUTES", FS_XS, MUTED, weight="700"))
            cols = [PAD + 4, PAD + 276, PAD + 390, PAD + 610]
            y += 18
            for h_, cx in zip(("element", "id", "kind", "values / quantity"), cols): body.append(txt(cx, y, h_, FS_XS, GRAY, weight="600"))
            y += 4
            for eid, p in els:
                el = self.n[eid]
                namelines = wrap(el["name"] + (f'  ({p["note"]})' if p.get("note") else ""), 14, cols[1] - cols[0] - 14, 2, bold=True)
                y += 22
                body.append(f'<line x1="{PAD}" y1="{y - 15}" x2="{W - PAD}" y2="{y - 15}" stroke="{SOFT}"/>')
                for j, nl in enumerate(namelines): body.append(txt(cols[0], y + 16 * j, nl, 14, INK, weight="600"))
                body.append(txt(cols[1], y, eid, FS_XS, MUTED, mono=True))
                kindtxt = el.get("kind", "") + (" · ordered" if el.get("ordered") else "") + (" · multi-select" if el.get("multi_select") else "")
                body.append(txt(cols[2], y, kindtxt, 14, MUTED))
                if el.get("kind") == "quantitative":
                    q = " · ".join(filter(None, [", ".join(el.get("units", [])), f'{el["min"]} to {el["max"]}' if el.get("min") is not None else None, el.get("method")]))
                    v = wrap(q, 14, W - PAD - cols[3], 1)[0] if q else ""
                else:
                    names = [v["name"] for v in self.values(eid)]
                    v = " · ".join(names[:4]) + (" · …" if len(names) > 4 else "")
                body.append(txt(cols[3], y, v, 14, INK))
                y += 16 * (len(namelines) - 1)
                maps = self.mappings(eid)
                if maps:
                    y += 16; body.append(txt(cols[3], y, " · ".join(self.code_str(*m) for m in maps), FS_XS, GRAY))
            y += 14
        # 5 containers
        rows = self.container_rows(hub)
        if rows:
            body.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{RULE}"/>')
            y += 6
        colw = (iw - 2 * GAP) / MINI_COLS
        for label, items in rows:
            has_props = any(self.edge_line(e) for _, e in items)
            tile_h = MINI_H + (24 if has_props else 0)
            nrows = (len(items) + MINI_COLS - 1) // MINI_COLS
            ch = 26 + nrows * (tile_h + GAP) + 4
            y += 6
            body.append(f'<rect x="{PAD}" y="{y}" width="{iw}" height="{ch}" rx="8" fill="{SOFT}" stroke="{RULE}" stroke-dasharray="3 3"/>'
                        + txt(PAD + 10, y + 18, label, FS_XS, MUTED, weight="700"))
            for i, (other, e) in enumerate(items):
                cx = PAD + 8 + (i % MINI_COLS) * (colw + GAP) - 8 * (i % MINI_COLS) / MINI_COLS
                cy = y + 26 + (i // MINI_COLS) * (tile_h + GAP)
                tw_ = colw - 8
                line = self.edge_line(e)
                if has_props:
                    body.append(f'<rect x="{cx:.1f}" y="{cy}" width="{tw_:.1f}" height="{tile_h}" rx="7" fill="none" stroke="{GRAY}" stroke-dasharray="2 3"/>')
                    if line:
                        lw = tw(line, FS_XS) + 10
                        body.append(f'<rect x="{cx + 12:.1f}" y="{cy + tile_h - 9}" width="{lw:.1f}" height="16" fill="#ffffff"/>'
                                    + txt(cx + 17, cy + tile_h + 4, line, FS_XS, MUTED))
                    body.append(self.mini(other, cx + 5, cy + 4, tw_ - 10, MINI_H - 4))
                    details.append(self.detail(other, min(cx, W - 480 - PAD), cy + tile_h + 2, hub=hub))
                else:
                    body.append(self.mini(other, cx, cy, tw_))
                    details.append(self.detail(other, min(cx, W - 480 - PAD), cy + MINI_H + 2, hub=hub))
            y += ch
        y += 10
        # 6 mappings
        body.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{RULE}"/>')
        maps = self.mappings(hub)
        y += 19
        body.append(txt(PAD + 4, y, " · ".join(self.code_str(*m) for m in maps) if maps else "no external mappings", FS_S, MUTED if maps else GRAY))
        y += 12
        # 7 stat row
        ctx = self.context(hub)
        cellw = iw / len(CONTEXT)
        cells = []
        maxl = 1
        for i, (label, edge) in enumerate(CONTEXT):
            cs, src = ctx[label]
            lines = [self.concept_str(c) for c in cs] or ["—"]
            wrapped = []
            for ln in lines: wrapped.extend(wrap(ln, FS_S, cellw - 12, 2))
            if src and src != hub: wrapped.append(f'(inherited from {self.name(src)})')
            cells.append((label, wrapped, bool(src and src != hub)))
            maxl = max(maxl, len(wrapped))
        rh = 26 + 16 * maxl
        body.append(f'<rect x="0" y="{y}" width="{W}" height="{rh}" fill="{SOFT}"/><line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{a}" stroke-width="1.5"/>')
        for i, (label, wrapped, inh_) in enumerate(cells):
            cx = PAD + i * cellw
            if i: body.append(f'<line x1="{cx - 6:.1f}" y1="{y + 4}" x2="{cx - 6:.1f}" y2="{y + rh - 4}" stroke="{RULE}"/>')
            body.append(txt(cx, y + 17, label, FS_XS, MUTED, weight="700"))
            for j, ln in enumerate(wrapped):
                body.append(txt(cx, y + 35 + 16 * j, ln, FS_S, GRAY if (ln == "—" or inh_) else INK, italic=ln.startswith("(inherited")))
        y += rh
        H = y + 2
        return self.svg(W, H, body, details, f'The {self.kind(hub).lower()} {node["name"]} as a mat: its attributes, and everything one relationship away as cards in labelled containers.', title)

    # ---- the tree -------------------------------------------------------------------
    def tree(self, root, title=None):
        rows, seen = [], set()
        def walk(nid, depth):
            if nid in seen: return
            seen.add(nid); rows.append((nid, depth))
            for c in self.children(nid): walk(c, depth + 1)
        walk(root, 0)
        body, details = [], []
        RH, IND = MINI_H + 16, 22        # row height = card + 16 px of clearance for the site layer's relationship labels
        y = 8
        body.append(txt(PAD, y + 14, f'{self.name(root)} · is-a outline · {len(rows)} nodes', FS_S, MUTED, weight="700"))
        y += 26
        tops = {}
        for nid, depth in rows:
            x = PAD + depth * IND
            w = W - PAD - x
            cy = y + (RH - MINI_H) / 2
            body.append(self.mini(nid, x, cy, w, MINI_H))
            tops[nid] = (x, cy)
            details.append(self.detail(nid, min(x, W - 480 - PAD), cy + MINI_H + 2))
            y += RH
        # guide lines: from each parent's left edge down to its last child
        for nid, depth in rows:
            kids = [c for c in self.children(nid) if c in tops]
            if not kids: continue
            px, py = tops[nid]
            lx = px + 8
            last = tops[kids[-1]]
            body.append(f'<path d="M{lx},{py + MINI_H} L{lx},{last[1] + MINI_H / 2}" fill="none" stroke="{RULE}" stroke-width="1"/>')
            for c in kids:
                cx, cy = tops[c]
                body.append(f'<path d="M{lx},{cy + MINI_H / 2} L{cx},{cy + MINI_H / 2}" fill="none" stroke="{RULE}" stroke-width="1"/>')
        # draw cards after guides so cards sit on top: re-emit by moving guide lines first
        guides = [b for b in body if b.startswith("<path")]
        cards = [b for b in body if not b.startswith("<path")]
        H = y + 8
        return self.svg(W, H, guides + cards, details, f'The is-a outline of {self.name(root)}: one mini-card per row, indented by subsumption.', title)

    def svg(self, w, h, body, details, aria, title=None):
        css = (".detail{display:none;pointer-events:none}.mini{cursor:default}"
               + "".join(f'svg:has(#m-{esc(d.split("id=\"d-",1)[1].split("\"",1)[0])}:hover) #d-{esc(d.split("id=\"d-",1)[1].split("\"",1)[0])}{{display:inline}}' for d in details))
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h:.0f}" font-family="{FONT}" role="img" aria-label="{esc(aria)}">',
               f'<style>{css}</style>', f'<rect width="{w}" height="{h:.0f}" fill="#ffffff"/>',
               f'<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5:.0f}" rx="10" fill="none" stroke="{RULE}" stroke-width="1.5"/>']
        out.extend(body)
        out.append('<g class="details">' + "".join(details) + "</g>")
        out.append("</svg>")
        return "".join(out) + "\n"


def render_view(graph, view):
    c = Cards(graph)
    return c.mat(view["hub"], view.get("title")) if view.get("kind", "mat") == "mat" else c.tree(view["hub"], view.get("title"))


if __name__ == "__main__":
    g = load_graph()
    if sys.argv[1] in ("mat", "tree"):
        view = {"kind": sys.argv[1], "hub": sys.argv[2]}
    else:
        view = json.load(open(sys.argv[1], encoding="utf-8"))
    sys.stdout.write(render_view(g, view))
