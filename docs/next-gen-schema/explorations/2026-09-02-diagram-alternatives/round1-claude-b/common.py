"""Shared graph loading, text metrics, and SVG helpers for the claude-b mockups.

Reads the canonical JSON Lines graph files. Nothing here is specific to a
layout; both alternatives import from it.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GRAPH = ROOT / "docs" / "next-gen-schema" / "graph"

PRESENCE = "RDE2_000001"  # bound by every class; suppressed in element lists

# ---------------------------------------------------------------- palette
INK, MUTED, RULE, PAPER = "#1f2937", "#6b7280", "#cbd5e1", "#ffffff"
KIND = {  # accent, dark text, tint
    "FindingClass": ("#2563eb", "#1e3a8a", "#eaf1fe"),
    "Diagnosis": ("#7c3aed", "#4c1d95", "#f1ecfe"),
    "Grouping": ("#64748b", "#334155", "#f3f5f8"),
    "DataElement": ("#15803d", "#14532d", "#effaf1"),
    "AnatomicLocation": ("#d97706", "#78350f", "#fff7e6"),
}
EDGE = {  # color, dash, marker kind, verb (forward), verb (from target's view)
    "MAY_CAUSE": ("#dc2626", "", "solid", "may cause", "caused by"),
    "MAY_MANIFEST_AS": ("#7c3aed", "", "open", "manifests as", "manifestation of"),
    "MAY_PROGRESS_TO": ("#0e7490", "7 4", "solid", "may progress to", "progresses from"),
    "OCCURS_WITH": ("#64748b", "2 4", "none", "occurs with", "occurs with"),
    "INTERPRETED_FROM": ("#15803d", "5 3 1 3", "open", "interpreted from", "interpreted by"),
}
TYP = {"obligate": "obligate", "very_frequent": "very frequent", "frequent": "frequent",
       "occasional": "occasional", "very_rare": "very rare", "excluded": "excluded"}
SPEC = {"pathognomonic": "pathognomonic", "highly_suggestive": "highly suggestive",
        "suggestive": "suggestive"}
RELATION_KINDS = set(EDGE)


# ---------------------------------------------------------------- graph
class Graph:
    def __init__(self, files):
        self.nodes, self.edges = {}, []
        for f in files:
            for line in (GRAPH / f).read_text().splitlines():
                if not line.strip():
                    continue
                o = json.loads(line)
                if "node" in o:
                    self.nodes[o["id"]] = o
                else:
                    self.edges.append(o)
        # names for shared nodes that only the converted specs define (severity, size)
        try:
            dump = subprocess.run([sys.executable, str(ROOT / "docs/next-gen-schema/tools/graph.py"), "dump"],
                                  capture_output=True, text=True, check=True).stdout
            for line in dump.splitlines():
                if line.strip():
                    o = json.loads(line)
                    if "node" in o and o["id"] not in self.nodes:
                        self.nodes[o["id"]] = o
        except (subprocess.CalledProcessError, OSError):
            pass
        self.parent = {}      # SUBTYPE_OF child -> parent
        self.children = {}
        for e in self.edges:
            if e["edge"] == "SUBTYPE_OF":
                self.parent[e["from"]] = e["to"]
                self.children.setdefault(e["to"], []).append(e["from"])
        self.binding = {e["id"]: e for e in self.edges if e["edge"] == "HAS_ELEMENT" and "id" in e}

    def name(self, nid):
        n = self.nodes.get(nid)
        return n["name"] if n else nid

    def kind(self, nid):
        n = self.nodes.get(nid)
        return n["node"] if n else "?"

    def ancestors(self, nid):
        out = []
        while nid in self.parent:
            nid = self.parent[nid]
            out.append(nid)
        return out  # nearest first

    def descendants(self, nid):
        out = []
        for c in self.children.get(nid, []):
            out.append(c)
            out.extend(self.descendants(c))
        return out

    def elements(self, nid):
        """Element names bound by nid, presence suppressed, in file order."""
        out = []
        for e in self.edges:
            if e["edge"] == "HAS_ELEMENT" and e["from"] == nid and e["to"] != PRESENCE:
                label = self.name(e["to"])
                note = (e.get("props") or {}).get("note")
                if note:
                    label = f"{note}: {label}" if note != label else label
                if (e.get("props") or {}).get("required"):
                    label += "*"
                out.append(label)
        return out

    def own_scope(self, nid):
        for e in self.edges:
            if e["edge"] == "SCOPED_TO" and e["from"] == nid:
                return e["to"]
        return None

    def scope(self, nid):
        """Anatomic scope, inherited from the nearest scoped ancestor when unset."""
        for n in [nid] + self.ancestors(nid):
            s = self.own_scope(n)
            if s:
                return s
        return None

    def relations(self, ids):
        """Typed relationship edges with both ends in ids (or a binding end)."""
        ids = set(ids)
        out = []
        for e in self.edges:
            if e["edge"] not in RELATION_KINDS:
                continue
            if e["from"] in ids and (e["to"] in ids or e["to"] in self.binding):
                out.append(e)
        return out


def family_ids(g, family_file):
    """Owned class nodes (finding, diagnosis, grouping) declared in one family file."""
    ids = []
    for line in (GRAPH / family_file).read_text().splitlines():
        if line.strip():
            o = json.loads(line)
            if "node" in o and o["node"] in ("FindingClass", "Diagnosis", "Grouping"):
                ids.append(o["id"])
    return ids


def edge_lines(e, from_target=False):
    """(verb line, detail line) for a typed edge. Detail may be ''."""
    color, dash, marker, verb, verb_rev = EDGE[e["edge"]]
    p = e.get("props") or {}
    bits = []
    if p.get("typicality"):
        bits.append(TYP.get(p["typicality"], p["typicality"]))
    if p.get("specificity"):
        bits.append(SPEC.get(p["specificity"], p["specificity"]))
    line1 = (verb_rev if from_target else verb)
    if bits:
        line1 += " · " + " · ".join(bits)
    detail = []
    if p.get("expected"):
        ex = p["expected"]
        detail = ([ex["location"]] if "location" in ex else []) + \
                 [f"{k}: {v}" for k, v in ex.items() if k != "location"]
    elif p.get("note") and not p["note"].startswith(("assumes", "the parapneumonic", "obstruction")):
        detail = [p["note"]]
    return line1, "; ".join(detail)


# ---------------------------------------------------------------- text metrics
_NARROW = set("iljtfr.,;:'!|I ()[]")
_WIDE = set("mwMW@")


def tw(text, size, bold=False, italic=False):
    w = 0.0
    for ch in text:
        if ch in _NARROW:
            w += 0.30
        elif ch in _WIDE:
            w += 0.84
        elif ch.isupper():
            w += 0.70
        elif ch.isdigit():
            w += 0.58
        else:
            w += 0.57
    return w * size * (1.16 if bold else 1.0) * (1.02 if italic else 1.0)


def wrap(text, size, width, bold=False, italic=False, max_lines=4):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and tw(trial, size, bold, italic) > width:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines[:max_lines]


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


# ---------------------------------------------------------------- svg bits
def text(x, y, s, size=10, fill=INK, bold=False, italic=False, anchor="start", extra=""):
    attrs = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'font-size="{size}"', f'fill="{fill}"']
    if bold:
        attrs.append('font-weight="600"')
    if italic:
        attrs.append('font-style="italic"')
    if anchor != "start":
        attrs.append(f'text-anchor="{anchor}"')
    if extra:
        attrs.append(extra)
    return f"<text {' '.join(attrs)}>{esc(s)}</text>"


def markers():
    out = []
    for kind, (color, dash, marker, _, _) in EDGE.items():
        if marker == "solid":
            out.append(f'<marker id="m-{kind}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
                       f'orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="{color}"/></marker>')
        elif marker == "open":
            out.append(f'<marker id="m-{kind}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" '
                       f'orient="auto-start-reverse"><path d="M0.5,1 L9,5 L0.5,9 z" fill="{PAPER}" stroke="{color}" stroke-width="1.3"/></marker>')
    return "".join(out)


def edge_path(d, kind, width=1.6):
    color, dash, marker, _, _ = EDGE[kind]
    a = f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"'
    if dash:
        a += f' stroke-dasharray="{dash}"'
    if marker != "none":
        a += f' marker-end="url(#m-{kind})"'
    return a + "/>"


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def ang(cx, cy, x, y):
    return math.degrees(math.atan2(y - cy, x - cx)) % 360


def wrapdiff(a, b):
    """Signed smallest difference b - a in degrees, in (-180, 180]."""
    d = (b - a + 180) % 360 - 180
    return d if d != -180 else 180


def legend_block(x, y, w, scope_note, extra_note=""):
    """A three-row legend: node kinds, edge kinds, notes."""
    out = [f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" stroke="{RULE}"/>']
    yy = y + 18
    cx = x
    for label, kind, italic, dashed in (("finding", "FindingClass", False, False),
                                        ("diagnosis", "Diagnosis", True, False),
                                        ("grouping (negative-only)", "Grouping", False, True),
                                        ("anatomy", "AnatomicLocation", False, False)):
        a, dark, tint = KIND[kind]
        dash = ' stroke-dasharray="4 3"' if dashed else ""
        rx = 5 if kind == "Diagnosis" else 2
        out.append(f'<rect x="{cx}" y="{yy - 10}" width="14" height="12" rx="{rx}" fill="{tint}" stroke="{a}"{dash}/>')
        out.append(text(cx + 19, yy, label, 9.5, dark, italic=italic))
        cx += 19 + tw(label, 9.5) + 16
    a, dark, tint = KIND["DataElement"]
    out.append(text(cx, yy, "◦ element (every class also binds presence; * = required)", 9.5, dark))
    yy += 17
    cx = x
    for kind, label in (("MAY_CAUSE", "may cause"), ("MAY_MANIFEST_AS", "manifests as"),
                        ("MAY_PROGRESS_TO", "progresses to"), ("OCCURS_WITH", "occurs with"),
                        ("INTERPRETED_FROM", "interpreted from")):
        color = EDGE[kind][0]
        out.append(edge_path(f"M{cx},{yy - 4} L{cx + 26},{yy - 4}", kind))
        out.append(text(cx + 32, yy, label, 9.5, color))
        cx += 32 + tw(label, 9.5) + 16
    out.append(text(cx + 6, yy, scope_note, 9.5, MUTED))
    if extra_note:
        out.append(text(x, yy + 15, extra_note, 9.5, MUTED))
    return "\n".join(out)
