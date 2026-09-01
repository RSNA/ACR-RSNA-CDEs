#!/usr/bin/env python3
"""Render a FindingClass as an object dossier: one card, sections tagged by
relationship type, sub-objects as typed reference chips.

Usage: render_neighborhood.py SPEC.json > out.svg

A FindingClass is the collected set of its edges; this view gathers them.
Each section header names the relationship type doing the gathering; each
chip inside is a typed reference to a shared node (color = node type).
See examples/*.neighborhood.json for the spec format.
"""
import json, sys, html, re

ACCENT = {  # node-type accents
    "class":    ("#2563eb", "#1e3a8a"),
    "element":  ("#16a34a", "#14532d"),
    "location": ("#d97706", "#78350f"),
    "concept":  ("#64748b", "#334155"),
}
INK, MUTED, RULE, CARD_BORDER = "#1f2937", "#64748b", "#e2e8f0", "#cbd5e1"

_NUMERIC_ATTR_RE = re.compile(
    r'(?P<prefix>\b(?:font-size|font-weight|height|letter-spacing|rx|stroke-dasharray|'
    r'stroke-width|transform|viewBox|width|x|x1|x2|y|y1|y2)=")'
    r'(?P<value>[^"]*)"'
)
_NUMBER_RE = re.compile(r'-?(?:\d+(?:\.\d*)?|\.\d+)')

def fmt_svg_numbers(svg):
    """Format every numeric SVG attribute value to at most three decimal places."""
    def attr(match):
        def number(token):
            value = f'{float(token.group()):.3f}'.rstrip("0").rstrip(".")
            return "0" if value == "-0" else value
        return match.group("prefix") + _NUMBER_RE.sub(number, match.group("value")) + '"'
    return _NUMERIC_ATTR_RE.sub(attr, svg)

def esc(s): return html.escape(str(s), quote=True)

def wrap(text, max_chars):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: lines.append(cur)
    return lines
def tw(s, fs): return len(s) * fs * 0.62          # rough text width

def chip(x, y, name, sub, kind, w=None):
    """Typed reference chip. Returns (svg, w, h)."""
    a, dark = ACCENT[kind]
    w = w or max(tw(name, 13), tw(sub, 9.5)) + 34
    h = 46
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="#ffffff" stroke="{CARD_BORDER}"/>'
         f'<rect x="{x}" y="{y}" width="4" height="{h}" rx="2" fill="{a}"/>'
         f'<text x="{x+16}" y="{y+20}" font-size="13" font-weight="600" fill="{dark}">{esc(name)}</text>'
         f'<text x="{x+16}" y="{y+36}" font-size="9.5" fill="{MUTED}">{esc(sub)}</text>')
    return s, w, h

def pill(x, y, v):
    w = tw(v, 11) + 20
    return (f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="#f0fdf4" stroke="#86efac"/>'
            f'<text x="{x+w/2}" y="{y+15}" text-anchor="middle" font-size="11" fill="#14532d">{esc(v)}</text>'), w

def sect_header(x, y, w, label):
    lw = tw(label, 10) + len(label) * 1.5 + 24
    return (f'<text x="{x}" y="{y+10}" font-size="10" letter-spacing="1.2" font-weight="600" fill="{MUTED}">{esc(label)}</text>'
            f'<line x1="{x+lw}" y1="{y+6}" x2="{x+w}" y2="{y+6}" stroke="{RULE}" stroke-width="1"/>'), 22

def elem_card(x, y, w, e):
    a, dark = ACCENT["element"]
    rows = []
    names = [v["name"] if isinstance(v, dict) else v for v in e.get("values", [])]
    if names:
        row, rw = [], 0
        for v in names:
            pw = tw(v, 11) + 20
            if row and rw + 8 + pw > w - 30: rows.append(row); row, rw = [], 0
            row.append(v); rw += (8 if row[1:] else 0) + pw
        if row: rows.append(row)
    is_ref = bool(e.get("ref"))
    defn = None if is_ref else e.get("definition")
    dlines = wrap(defn, int((w - 32) / 6.3)) if defn else []
    h = 48 + 16 * len(dlines) + (len(rows) * 30 + 4 if rows else 0)
    if is_ref:
        sub = f'→ existing element {e["ref"]} · shared · {e.get("kind","")}' + (" · multi-select" if e.get("multi_select") else "")
        subcol = "#2563eb"
    else:
        sub = f'defined here as {e.get("id","")} · DataElement · {e.get("kind","")}' + (" · multi-select" if e.get("multi_select") else "")
        subcol = MUTED
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="#ffffff" stroke="{CARD_BORDER}"' + (' stroke-dasharray="4 3"' if is_ref else '') + '/>'
         f'<rect x="{x}" y="{y}" width="4" height="{h}" rx="2" fill="{a}"/>'
         f'<text x="{x+16}" y="{y+21}" font-size="13" font-weight="600" fill="{dark}">{esc(e["name"])}</text>'
         f'<text x="{x+16}" y="{y+37}" font-size="9.5" fill="{subcol}">{esc(sub)}</text>')
    for i, dl in enumerate(dlines):
        s += f'<text x="{x+16}" y="{y+54+16*i}" font-size="10.5" fill="{INK}">{esc(dl)}</text>'
    prop = " · ".join(filter(None, ["required" if e.get("required") else None, e.get("edge_note")]))
    if prop:
        s += f'<text x="{x+w-12}" y="{y+20}" text-anchor="end" font-size="9.5" font-style="italic" fill="{MUTED}">{esc(prop)}</text>'
    py = y + 46 + 16 * len(dlines)
    for row in rows:
        px = x + 16
        for v in row:
            ps, pw = pill(px, py, v); s += ps; px += pw + 8
        py += 30
    return s, h

def render(spec):
    W, PAD, GUT = 1000, 28, 28
    IW = W - 2*PAD                       # inner width
    HALF = (IW - GUT) / 2
    c = spec["center"]
    body = []                            # (svg, height) fragments stacked with gaps
    y = 0                                # body-local y; offset later

    def half_sections(pairs):
        """pairs: list of (label, items:[(name, sub, kind, note)])"""
        nonlocal y
        frags, maxh = [], 0
        for col, (label, items) in enumerate(pairs):
            x0 = PAD + col * (HALF + GUT)
            hs, hh = sect_header(x0, y, HALF, label)
            frags.append(hs)
            cy = y + hh
            cx = x0
            rowh = 0
            for name, sub, kind, note in items:
                s, w, h = chip(cx, cy, name, sub, kind)
                if cx + w > x0 + HALF and cx > x0:
                    cy += h + 10; cx = x0
                    s, w, h = chip(cx, cy, name, sub, kind)
                frags.append(s)
                if note:
                    frags.append(f'<text x="{cx+w+10}" y="{cy+28}" font-size="10" fill="{MUTED}">{esc(note)}</text>')
                cx += w + 12; rowh = h
            maxh = max(maxh, cy + rowh - y)
        body.append(("".join(frags), maxh))
        y += maxh + 24

    def full_section(label, render_content):
        nonlocal y
        hs, hh = sect_header(PAD, y, IW, label)
        content, ch = render_content(y + hh)
        body.append((hs + content, hh + ch))
        y += hh + ch + 24

    # --- taxonomy + scope, side by side
    supers = [r for r in spec.get("related", []) if r["edge"] == "SUBTYPE_OF"]
    pairs = []
    if supers:
        pairs.append(("SUBTYPE_OF — is a",
                      [(r["name"], "FindingClass" + (f' · {r["note"]}' if r.get("note") else ""), "class", None) for r in supers]))
    if spec.get("scope"):
        pairs.append(("SCOPED_TO — anatomic scope",
                      [(s["name"], f'AnatomicLocation · {s.get("ref","")}', "location",
                        f'{s.get("kind","structure")} · {s.get("strength","expected")}') for s in spec["scope"]]))
    if pairs: half_sections(pairs)

    # --- elements, two-column grid
    elements = spec.get("elements", [])
    if elements:
        def content(cy0):
            colw = HALF
            xs = [PAD, PAD + HALF + GUT]
            ys = [cy0, cy0]
            frags = []
            for e in elements:
                ci = 0 if ys[0] <= ys[1] else 1
                s, h = elem_card(xs[ci], ys[ci], colw, e)
                frags.append(s); ys[ci] += h + 12
            return "".join(frags), max(ys) - cy0 - 12
        full_section(f'HAS_ELEMENT — characterized by · ×{len(elements)}', content)

    # --- other class relations, grouped by edge type, side by side
    below = [r for r in spec.get("related", []) if r["edge"] != "SUBTYPE_OF"]
    if below:
        groups = {}
        for r in below: groups.setdefault(r["edge"], []).append(r)
        titles = {"MAY_REPRESENT": "may represent", "ASSESSED_BY": "assessed by", "MAY_HAVE_COMPONENT": "may have component", "MAY_CAUSE": "may cause", "OCCURS_WITH": "occurs with"}
        pairs = [(f'{e} — {titles.get(e, e.lower().replace("_"," "))}',
                  [(r["name"], "FindingClass" + (f' · {r["note"]}' if r.get("note") else ""), "class", None) for r in rs])
                 for e, rs in groups.items()]
        for i in range(0, len(pairs), 2):
            half_sections(pairs[i:i+2])

    # --- context
    ctx = spec.get("metadata", [])
    if ctx:
        def content(cy0):
            frags, cx, cy = [], PAD, cy0
            for m in ctx:
                sub = f'{m["edge"]} · {m["type"]}' + (f' · {m["note"]}' if m.get("note") else "")
                s, w, h = chip(cx, cy, m["name"], sub, "concept")
                if cx + w > PAD + IW:
                    cy += h + 10; cx = PAD
                    s, w, h = chip(cx, cy, m["name"], sub, "concept")
                frags.append(s); cx += w + 12
            return "".join(frags), cy + 46 - cy0
        full_section("CONTEXT — discoverability edges", content)

    # --- mappings (skos:exactMatch / closeMatch)
    maps = spec.get("mappings", [])
    if maps:
        def content(cy0):
            frags, cx = [], PAD
            for m in maps:
                s, w, h = chip(cx, cy0, m.get("display", m["code"]), f'{m["system"]} {m["code"]} · skos:{m.get("match","exactMatch")}', "concept")
                frags.append(s); cx += w + 12
            return "".join(frags), 46
        full_section("MAPPINGS — skos:exactMatch / closeMatch", content)

    # --- header
    defn = spec.get("definition", "")
    syn = spec.get("synonyms", [])
    syn_txt = " · ".join(s["term"] + (f' ({s["type"]})' if isinstance(s, dict) and s.get("type") not in (None, "synonym") else "") if isinstance(s, dict) else s for s in syn)
    meta_line = " · ".join(filter(None, [spec.get("id"), f'v{spec["version"]}' if spec.get("version") else None, spec.get("status"), spec.get("status_date")]))
    head_h = 96 + (18 if syn else 0) + (16 if meta_line else 0)
    body_off = head_h + 20
    H = int(body_off + y + PAD - 8)

    a, dark = ACCENT["class"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="system-ui, sans-serif" role="img" aria-label="{esc(spec.get("aria","FindingClass"))}">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           # object frame
           f'<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="14" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>',
           f'<rect x="1.5" y="1.5" width="{W-3}" height="{head_h}" rx="14" fill="#eff6ff"/>',
           f'<rect x="1.5" y="{head_h-12}" width="{W-3}" height="14" fill="#eff6ff"/>',
           f'<line x1="1.5" y1="{head_h+2}" x2="{W-1.5}" y2="{head_h+2}" stroke="{RULE}"/>',
           f'<text x="{PAD}" y="30" font-size="10" letter-spacing="1.6" font-weight="700" fill="{a}">FINDING CLASS</text>',
           f'<text x="{PAD}" y="58" font-size="21" font-weight="700" fill="{dark}">{esc(c["name"])}</text>',
           f'<text x="{PAD}" y="80" font-size="11" fill="{INK}">{esc(defn)}</text>']
    yy = 98
    if syn:
        out.append(f'<text x="{PAD}" y="{yy}" font-size="10" fill="{MUTED}">synonyms: {esc(syn_txt)}</text>'); yy += 16
    if meta_line:
        out.append(f'<text x="{PAD}" y="{yy}" font-size="10" fill="{MUTED}">{esc(meta_line)}</text>')
    et = f'entity_type: {c["entity_type"]}'
    etw = tw(et, 11) + 24
    out.append(f'<rect x="{W-PAD-etw}" y="22" width="{etw}" height="24" rx="12" fill="#dbeafe" stroke="#93c5fd"/>'
               f'<text x="{W-PAD-etw/2}" y="38" text-anchor="middle" font-size="11" fill="{dark}">{esc(et)}</text>')
    for frag, h in body:
        out.append(f'<g transform="translate(0,{body_off})">{frag}</g>')
    out.append("</svg>")
    return fmt_svg_numbers("".join(out))

def render_element(spec):
    """DataElement dossier: value set (or quantity), binders with per-binding overrides, mappings."""
    W, PAD, GUT = 1000, 28, 28
    IW = W - 2*PAD
    a, dark = ACCENT["element"]
    body = []; y = 0

    def full_section(label, render_content):
        nonlocal y
        hs, hh = sect_header(PAD, y, IW, label)
        content, ch = render_content(y + hh)
        body.append(hs + content); y += hh + ch + 24

    vs = spec.get("value_set")
    if vs:
        def content(cy0):
            frags = []
            sub = "value domain of this element · " + ("ordered" if vs.get("ordered") else "unordered")
            s, w, h = chip(PAD, cy0, vs["name"], sub, "element")
            frags.append(s)
            frags.append(f'<text x="{PAD+w+12}" y="{cy0+28}" font-size="10" fill="{MUTED}">value ids derive from the element: {esc(vs.get("id",""))}.0, .1, …</text>')
            vy = cy0 + h + 12
            for v in vs["values"]:
                rh = 40
                frags.append(f'<rect x="{PAD+24}" y="{vy}" width="{IW-24}" height="{rh}" rx="6" fill="#f8fafc" stroke="{RULE}"/>'
                             f'<rect x="{PAD+24}" y="{vy}" width="3" height="{rh}" rx="1.5" fill="#86efac"/>')
                nm = v["name"] + (f'  ·  rank {v["rank"]}' if v.get("rank") is not None else "")
                frags.append(f'<text x="{PAD+40}" y="{vy+17}" font-size="12.5" font-weight="600" fill="#14532d">{esc(nm)}</text>')
                cs = [f'{c["system"]} {c["code"]} “{c["display"]}”' if isinstance(c, dict) else c for c in v.get("codes", [])]
                meta = " · ".join(filter(None, [v.get("id"), f'value: {v["value"]}' if v.get("value") is not None else None] + cs))
                frags.append(f'<text x="{PAD+40}" y="{vy+32}" font-size="9.5" fill="{MUTED}">{esc(meta)}</text>')
                if v.get("definition"):
                    frags.append(f'<text x="{W-PAD-12}" y="{vy+25}" text-anchor="end" font-size="10.5" fill="{INK}">{esc(v["definition"])}</text>')
                vy += rh + 8
            return "".join(frags), vy - cy0 - 8
        full_section(f'rdfs:range — value set · skos:member ×{len(vs["values"])}', content)

    qn = spec.get("quantity")
    if qn:
        def content(cy0):
            frags, cx = [], PAD
            s, w, h = chip(cx, cy0, qn["type"], "QuantityType · rdfs:range", "element"); frags.append(s); cx += w + 16
            for u in qn.get("units", []):
                ps, pw = pill(cx, cy0 + 11, u); frags.append(ps); cx += pw + 8
            frags.append(f'<text x="{cx+8}" y="{cy0+27}" font-size="10" fill="{MUTED}">permitted units (UCUM)</text>')
            yy = cy0 + h + 14
            rng = " · ".join(f'{k} {qn[k]}' for k in ("min","max","step") if k in qn)
            if rng:
                frags.append(f'<text x="{PAD}" y="{yy}" font-size="11" fill="{INK}"><tspan fill="{MUTED}">range</tspan>  {esc(rng)}</text>'); yy += 18
            if qn.get("method"):
                frags.append(f'<text x="{PAD}" y="{yy}" font-size="11" fill="{INK}"><tspan fill="{MUTED}">method</tspan>  {esc(qn["method"])}</text>'); yy += 18
            return "".join(frags), yy - cy0 - 6
        full_section("QUANTITY — type, units, range, method", content)

    bb = spec.get("bound_by", [])
    if bb:
        def binder(x, y, b):
            a2, dark2 = ACCENT["class"]
            sub = " · ".join(filter(None, [b.get("id"), "required" if b.get("required") else None]))
            w = max(tw(b["name"], 13), tw(sub, 9.5)) + 34
            h = 46
            s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="#ffffff" stroke="{CARD_BORDER}"/>'
                 f'<rect x="{x}" y="{y}" width="4" height="{h}" rx="2" fill="{a2}"/>'
                 f'<text x="{x+16}" y="{y+20}" font-size="13" font-weight="600" fill="{dark2}">{esc(b["name"])}</text>'
                 f'<text x="{x+16}" y="{y+36}" font-size="9.5" fill="{MUTED}">{esc(sub)}</text>')
            return s, w, h
        def content(cy0):
            frags, cx, cy, rowh = [], PAD, cy0, 0
            for b in bb:
                s, w, h = binder(cx, cy, b)
                if cx + w > PAD + IW and cx > PAD:
                    cy += rowh + 12; cx = PAD; rowh = 0
                    s, w, h = binder(cx, cy, b)
                frags.append(s); cx += w + 12; rowh = max(rowh, h)
            return "".join(frags), cy + rowh - cy0
        full_section(f'BOUND BY — HAS_ELEMENT in-degree ×{len(bb)} · per-binding required', content)

    maps = spec.get("mappings", [])
    if maps:
        def content(cy0):
            frags, cx = [], PAD
            for m in maps:
                s, w, h = chip(cx, cy0, m.get("display", m["code"]), f'{m["system"]} {m["code"]} · skos:{m.get("match","exactMatch")}', "concept")
                frags.append(s); cx += w + 12
            return "".join(frags), 46
        full_section("MAPPINGS — skos:exactMatch / closeMatch", content)

    # header
    syn = spec.get("synonyms", [])
    syn_txt = " · ".join(s["term"] + (f' ({s["type"]})' if s.get("type") not in (None, "synonym") else "") for s in syn)
    meta_line = " · ".join(filter(None, [spec.get("id"), f'v{spec["version"]}' if spec.get("version") else None, spec.get("status"), spec.get("status_date")]))
    head_h = 96 + (16 if syn else 0) + (16 if meta_line else 0)
    body_off = head_h + 20
    H = int(body_off + y + PAD - 8)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="system-ui, sans-serif" role="img" aria-label="{esc(spec.get("aria","DataElement " + spec["name"]))}">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           f'<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="14" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>',
           f'<rect x="1.5" y="1.5" width="{W-3}" height="{head_h}" rx="14" fill="#f0fdf4"/>',
           f'<rect x="1.5" y="{head_h-12}" width="{W-3}" height="14" fill="#f0fdf4"/>',
           f'<line x1="1.5" y1="{head_h+2}" x2="{W-1.5}" y2="{head_h+2}" stroke="{RULE}"/>',
           f'<text x="{PAD}" y="30" font-size="10" letter-spacing="1.6" font-weight="700" fill="{a}">DATA ELEMENT</text>',
           f'<text x="{PAD}" y="58" font-size="21" font-weight="700" fill="{dark}">{esc(spec["name"])}</text>',
           f'<text x="{PAD}" y="80" font-size="11" fill="{INK}">{esc(spec.get("definition",""))}</text>']
    yy = 98
    if syn:
        out.append(f'<text x="{PAD}" y="{yy}" font-size="10" fill="{MUTED}">synonyms: {esc(syn_txt)}</text>'); yy += 16
    if meta_line:
        out.append(f'<text x="{PAD}" y="{yy}" font-size="10" fill="{MUTED}">{esc(meta_line)}</text>')
    kd = f'kind: {spec.get("kind","")}'; kw = tw(kd, 11) + 24
    out.append(f'<rect x="{W-PAD-kw}" y="22" width="{kw}" height="24" rx="12" fill="#dcfce7" stroke="#86efac"/>'
               f'<text x="{W-PAD-kw/2}" y="38" text-anchor="middle" font-size="11" fill="{dark}">{esc(kd)}</text>')
    for frag in body:
        out.append(f'<g transform="translate(0,{body_off})">{frag}</g>')
    out.append("</svg>")
    return fmt_svg_numbers("".join(out))

def render_location(spec):
    """AnatomicLocation dossier: descriptor elements bound to the structure, inherited bindings,
    FindingClasses scoped here, mappings. The node is upstream (RadLex); the bindings are ours."""
    W, PAD, GUT = 1000, 28, 28
    IW = W - 2*PAD; HALF = (IW - GUT) / 2
    a, dark = ACCENT["location"]
    body = []; y = 0
    def full_section(label, render_content):
        nonlocal y
        hs, hh = sect_header(PAD, y, IW, label)
        content, ch = render_content(y + hh)
        body.append(hs + content); y += hh + ch + 24

    els = spec.get("elements", [])
    if els:
        def content(cy0):
            xs = [PAD, PAD + HALF + GUT]; ys = [cy0, cy0]; frags = []
            for e in els:
                ci = 0 if ys[0] <= ys[1] else 1
                s, h = elem_card(xs[ci], ys[ci], HALF, e); frags.append(s); ys[ci] += h + 12
            return "".join(frags), max(ys) - cy0 - 12
        full_section(f'HAS_ELEMENT — descriptors of this structure · ×{len(els)} · an Observation whose subject is this location uses these', content)

    inh = spec.get("inherits_from", [])
    if inh:
        def content(cy0):
            frags, cx = [], PAD
            for i in inh:
                s, w, h = chip(cx, cy0, i["name"], f'{i["edge"]} · bindings inherited', "location"); frags.append(s)
                frags.append(f'<text x="{cx+w+12}" y="{cy0+28}" font-size="10" fill="{MUTED}">{esc(i.get("note",""))}</text>')
                cx += w + 12
            return "".join(frags), 46
        full_section("INHERITED BINDINGS — via partOf / is-a / laterality triad", content)

    sc = spec.get("scoped_classes", [])
    if sc:
        def content(cy0):
            frags, cx, cy = [], PAD, cy0
            for c in sc:
                s, w, h = chip(cx, cy, c["name"], f'FindingClass · {c.get("entity_type","")} · {c.get("id","")}', "class")
                if cx + w > PAD + IW and cx > PAD:
                    cy += 60; cx = PAD; s, w, h = chip(cx, cy, c["name"], f'FindingClass · {c.get("entity_type","")} · {c.get("id","")}', "class")
                frags.append(s)
                if c.get("note"):
                    frags.append(f'<text x="{cx+w+10}" y="{cy+28}" font-size="10" fill="{MUTED}">{esc(c["note"])}</text>')
                    cx += tw(c["note"], 10) + 10
                cx += w + 12
            return "".join(frags), cy + 46 - cy0
        full_section(f'SCOPED_TO in-degree — FindingClasses scoped to this structure · ×{len(sc)}', content)

    maps = spec.get("mappings", [])
    if maps:
        def content(cy0):
            frags, cx = [], PAD
            for m in maps:
                s, w, h = chip(cx, cy0, m.get("display", m["code"]), f'{m["system"]} {m["code"]} · skos:{m.get("match","exactMatch")}', "concept")
                frags.append(s); cx += w + 12
            return "".join(frags), 46
        full_section("MAPPINGS — carried by AnatomicLocations.org", content)

    head_h = 112; body_off = head_h + 20; H = int(body_off + y + PAD - 8)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="system-ui, sans-serif" role="img" aria-label="{esc("AnatomicLocation " + spec["name"])}">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           f'<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="14" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>',
           f'<rect x="1.5" y="1.5" width="{W-3}" height="{head_h}" rx="14" fill="#fffbeb"/>',
           f'<rect x="1.5" y="{head_h-12}" width="{W-3}" height="14" fill="#fffbeb"/>',
           f'<line x1="1.5" y1="{head_h+2}" x2="{W-1.5}" y2="{head_h+2}" stroke="{RULE}"/>',
           f'<text x="{PAD}" y="30" font-size="10" letter-spacing="1.6" font-weight="700" fill="{a}">ANATOMIC LOCATION</text>',
           f'<text x="{PAD}" y="58" font-size="21" font-weight="700" fill="{dark}">{esc(spec["name"])}</text>',
           f'<text x="{PAD}" y="80" font-size="11" fill="{INK}">{esc(spec.get("id",""))} · contained by {esc(spec.get("contained_by",""))} · part of {esc(spec.get("part_of",""))}</text>',
           f'<text x="{PAD}" y="98" font-size="10" fill="{MUTED}">{esc(spec.get("owner",""))}</text>']
    for frag in body:
        out.append(f'<g transform="translate(0,{body_off})">{frag}</g>')
    out.append("</svg>")
    return fmt_svg_numbers("".join(out))

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    kind = spec.get("node")
    rendered = render_element(spec) if kind == "DataElement" else render_location(spec) if kind == "AnatomicLocation" else render(spec)
    sys.stdout.buffer.write((rendered.rstrip("\r\n") + "\n").encode("utf-8"))
