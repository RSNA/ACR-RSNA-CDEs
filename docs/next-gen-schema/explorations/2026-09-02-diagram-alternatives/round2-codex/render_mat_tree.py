#!/usr/bin/env python3
"""Render deterministic MAT and TREE SVG views from the canonical CDE graph.

The only semantic view inputs are an object id and an optional title. Graph data is
always loaded through docs/next-gen-schema/tools/graph.py:load_graph.

Usage:
  python render_mat_tree.py all
  python render_mat_tree.py mat RDE2_000502 --title "Pleural effusion" -o out.svg
  python render_mat_tree.py tree RDE2_000516 --title "Pleural abnormality" -o out.svg
"""

from __future__ import annotations

import argparse
import html
import math
import sys
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[3]
TOOLS = REPO / "docs" / "next-gen-schema" / "tools"
sys.path.insert(0, str(TOOLS))

from graph import load_graph  # noqa: E402  (repository loader is intentionally late-bound)


W = 1280
MAT_H = 1820
PAD = 28

KIND_LABEL = {
    "FindingClass": "FINDING",
    "Diagnosis": "DIAGNOSIS",
    "Grouping": "GROUPING",
    "DataElement": "ELEMENT",
    "AnatomicLocation": "ANATOMY",
    "Concept": "CONCEPT",
    "RelationshipType": "RELATIONSHIP",
    "Value": "VALUE",
}

NODE_STYLE = {
    "FindingClass": ("#eaf3ff", "#5b93d3", "#184b86", 8),
    "Diagnosis": ("#f4efff", "#9c82cf", "#4f3285", 22),
    "Grouping": ("#f4f5f7", "#667085", "#344054", 4),
    "DataElement": ("#fff8e6", "#d4a130", "#72520b", 4),
    "AnatomicLocation": ("#edf8f1", "#70a984", "#265f3a", 22),
    "Concept": ("#f5f6f8", "#98a2b3", "#344054", 8),
}

REL_STYLE = {
    "MAY_CAUSE": ("#b8433d", "#fff0ee", "#e0a29d", ""),
    "MAY_MANIFEST_AS": ("#6949a8", "#f4efff", "#baa9df", ""),
    "MAY_PROGRESS_TO": ("#14786f", "#eaf8f6", "#7abbb5", ""),
    "OCCURS_WITH": ("#44546a", "#f4f6f8", "#aab3bf", "7 4"),
    "ASSESSED_BY": ("#a26012", "#fff7e8", "#d7ad72", "3 3"),
}

CONTEXT_EDGES = {
    "modality": "SEEN_ON",
    "region": "IN_REGION",
    "sex": "SEX",
    "age": "AGE_APPLICABILITY",
    "course": "TIME_COURSE",
    "etiology": "HAS_ETIOLOGY",
}

HIDDEN_CONNECTION_EDGES = {
    "HAS_ELEMENT",
    "SCOPED_TO",
    "exactMatch",
    "closeMatch",
    "member",
    "SEEN_ON",
    "IN_REGION",
    "IN_SUBSPECIALTY",
    "SEX",
    "AGE_APPLICABILITY",
    "TIME_COURSE",
    "HAS_ETIOLOGY",
    "INTERPRETED_FROM",
}


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def wrap(text: str, max_chars: int, max_lines: int | None = None) -> list[str]:
    """Stable whitespace wrapping for SVG text (no renderer-dependent flow text)."""
    words = str(text or "").split()
    if not words:
        return []
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > max_chars:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        lines[-1] = (last[: max(1, max_chars - 1)].rstrip(" ·,;:") + "…")
    return lines


def text_lines(
    x: float,
    y: float,
    lines: Iterable[str],
    *,
    size: float = 11,
    line_height: float = 15,
    fill: str = "#344054",
    weight: int = 400,
    anchor: str = "start",
    css: str = "",
) -> str:
    out = []
    for i, line in enumerate(lines):
        out.append(
            f'<text x="{x}" y="{y + i * line_height}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{css}>{esc(line)}</text>'
        )
    return "".join(out)


def node_kind(node: dict[str, Any]) -> str:
    return KIND_LABEL.get(node.get("node", "Concept"), node.get("node", "OBJECT").upper())


def sort_edges(graph: Any, edges: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    def key(edge: dict[str, Any]) -> tuple[str, str, str, str]:
        src = graph.nodes.get(edge["from"], {"name": edge["from"]})["name"]
        dst = graph.nodes.get(edge["to"], {"name": edge["to"]})["name"]
        return (str(src).casefold(), str(dst).casefold(), edge["edge"], edge.get("id", ""))

    return sorted(edges, key=key)


def node_edges(graph: Any, node_id: str, edge_type: str, direction: str) -> list[dict[str, Any]]:
    if direction == "out":
        return sort_edges(graph, (e for e in graph.out_edges(node_id) if e["edge"] == edge_type))
    if direction == "in":
        return sort_edges(graph, (e for e in graph.in_edges(node_id) if e["edge"] == edge_type))
    both = [e for e in graph.out_edges(node_id) if e["edge"] == edge_type]
    both.extend(e for e in graph.in_edges(node_id) if e["edge"] == edge_type and e not in both)
    return sort_edges(graph, both)


def other_end(edge: dict[str, Any], hub_id: str) -> str:
    return edge["to"] if edge["from"] == hub_id else edge["from"]


def preferred_mapping(edge: dict[str, Any]) -> str | None:
    """A mapping is omitted rather than ever showing a bare code."""
    display = edge.get("props", {}).get("display")
    if not display:
        return None
    target = edge["to"]
    if ":" in target:
        system, code = target.split(":", 1)
        target = f"{system} {code}"
    qualifier = " · close" if edge["edge"] == "closeMatch" else ""
    return f'{target} “{display}”{qualifier}'


def mappings_for(graph: Any, node_id: str) -> list[str]:
    result = []
    for edge in sorted(
        (e for e in graph.out_edges(node_id) if e["edge"] in {"exactMatch", "closeMatch"}),
        key=lambda e: (e["edge"], e["to"]),
    ):
        label = preferred_mapping(edge)
        if label:
            result.append(label)
    return result


def stats_for(graph: Any, node_id: str) -> list[tuple[str, str]]:
    result = []
    for label, edge_type in CONTEXT_EDGES.items():
        names = sorted(
            {
                graph.nodes[e["to"]]["name"]
                for e in graph.out_edges(node_id)
                if e["edge"] == edge_type and e["to"] in graph.nodes
            },
            key=str.casefold,
        )
        result.append((label.upper(), " · ".join(names) if names else "—"))
    return result


def format_props(edge: dict[str, Any], *, include_note: bool = True) -> str:
    props = edge.get("props", {})
    bits: list[str] = []
    if props.get("typicality"):
        bits.append(str(props["typicality"]).replace("_", " "))
    if props.get("specificity"):
        bits.append(str(props["specificity"]).replace("_", " "))
    expected = props.get("expected")
    if isinstance(expected, dict):
        exp = "; ".join(f"{k}: {expected[k]}" for k in sorted(expected))
        bits.append(f"expect {exp}")
    if include_note and props.get("note"):
        bits.append(f'note: {props["note"]}')
    return " · ".join(bits) if bits else "—"


def relation_friendly(edge_type: str) -> str:
    return {
        "MAY_CAUSE": "MAY CAUSE",
        "MAY_MANIFEST_AS": "MANIFESTS AS",
        "MAY_PROGRESS_TO": "PROGRESSES TO",
        "OCCURS_WITH": "OCCURS WITH",
        "ASSESSED_BY": "ASSESSED BY",
    }.get(edge_type, edge_type.replace("_", " "))


def mat_container_specs(graph: Any, hub_id: str) -> list[tuple[str, list[dict[str, Any]]]]:
    specs = [
        ("A KIND OF", node_edges(graph, hub_id, "SUBTYPE_OF", "out")),
        ("KINDS OF", node_edges(graph, hub_id, "SUBTYPE_OF", "in")),
        ("MANIFESTS AS", node_edges(graph, hub_id, "MAY_MANIFEST_AS", "out")),
        ("MAY BE CAUSED BY", node_edges(graph, hub_id, "MAY_CAUSE", "in")),
        ("MAY CAUSE", node_edges(graph, hub_id, "MAY_CAUSE", "out")),
        ("PROGRESSES TO", node_edges(graph, hub_id, "MAY_PROGRESS_TO", "out")),
        ("PROGRESSES FROM", node_edges(graph, hub_id, "MAY_PROGRESS_TO", "in")),
        ("OCCURS WITH", node_edges(graph, hub_id, "OCCURS_WITH", "both")),
        ("ASSESSED BY", node_edges(graph, hub_id, "ASSESSED_BY", "out")),
    ]
    return [(label, edges) for label, edges in specs if edges]


def mini_face(graph: Any, node_id: str, x: float, y: float, w: float, h: float = 52) -> str:
    node = graph.nodes[node_id]
    fill, stroke, dark, radius = NODE_STYLE.get(node["node"], NODE_STYLE["Concept"])
    dash = ' stroke-dasharray="5 3"' if node["node"] == "Grouping" else ""
    fs = 11.2 if len(node["name"]) < 28 else 10
    return (
        f'<g class="mini-face" data-node="{esc(node_id)}">'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{min(radius, h/2)}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.2"{dash}/>'
        f'<text x="{x + 12}" y="{y + 21}" font-size="{fs}" font-weight="720" fill="{dark}">{esc(node["name"])}</text>'
        f'<text x="{x + 12}" y="{y + 40}" font-size="9" font-weight="650" letter-spacing=".35" fill="#667085">'
        f'{node_kind(node)} · {esc(node_id)}</text></g>'
    )


def own_connection_lines(graph: Any, node_id: str, context_id: str) -> list[str]:
    lines: list[tuple[str, str, str]] = []
    for edge in graph.out_edges(node_id):
        if edge["edge"] in HIDDEN_CONNECTION_EDGES or edge["to"] not in graph.nodes:
            continue
        if edge["to"] == context_id:
            continue
        label = {
            "SUBTYPE_OF": "A KIND OF",
            "MAY_CAUSE": "MAY CAUSE",
            "MAY_MANIFEST_AS": "MANIFESTS AS",
            "MAY_PROGRESS_TO": "PROGRESSES TO",
            "OCCURS_WITH": "OCCURS WITH",
            "ASSESSED_BY": "ASSESSED BY",
        }.get(edge["edge"], relation_friendly(edge["edge"]))
        target = graph.nodes[edge["to"]]
        lines.append((label, target["name"], target["id"]))
    for edge in graph.in_edges(node_id):
        if edge["edge"] in HIDDEN_CONNECTION_EDGES or edge["from"] not in graph.nodes:
            continue
        if edge["from"] == context_id:
            continue
        label = {
            "SUBTYPE_OF": "KIND OF",
            "MAY_CAUSE": "MAY BE CAUSED BY",
            "MAY_MANIFEST_AS": "MANIFESTATION OF",
            "MAY_PROGRESS_TO": "PROGRESSES FROM",
            "OCCURS_WITH": "OCCURS WITH",
        }.get(edge["edge"], relation_friendly(edge["edge"]))
        source = graph.nodes[edge["from"]]
        lines.append((label, source["name"], source["id"]))
    lines = sorted(set(lines), key=lambda x: (x[0], x[1].casefold(), x[2]))
    shown = [f"{label} · {name} · {nid}" for label, name, nid in lines[:3]]
    if len(lines) > 3:
        shown.append(f"+ {len(lines) - 3} more connections")
    return shown


def hover_detail(graph: Any, node_id: str, context_id: str, hit: tuple[float, float, float, float]) -> str:
    node = graph.nodes[node_id]
    hx, hy, hw, hh = hit
    dw, dh = 470, 286
    dx = min(max(PAD + 4, hx), W - PAD - dw - 4)
    dy = hy + hh + 6
    if dy + dh > MAT_H - 24:
        dy = hy - dh - 6
    fill, stroke, dark, _ = NODE_STYLE.get(node["node"], NODE_STYLE["Concept"])
    definitions = wrap(node.get("definition", "—"), 67, 3)
    maps = mappings_for(graph, node_id)
    own = own_connection_lines(graph, node_id, context_id)
    stats = stats_for(graph, node_id)
    out = [
        '<g class="hover-target" tabindex="0">',
        f'<rect class="hover-hit" x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="8" fill="#fff" fill-opacity=".001"/>',
        '<g class="hover-detail">',
        f'<rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" rx="10" fill="#fff" stroke="{stroke}" stroke-width="1.8" filter="url(#shadow)"/>',
        f'<rect x="{dx}" y="{dy}" width="{dw}" height="44" rx="10" fill="{fill}"/>',
        f'<rect x="{dx}" y="{dy + 34}" width="{dw}" height="10" fill="{fill}"/>',
        f'<text x="{dx + 14}" y="{dy + 27}" font-size="13" font-weight="750" fill="{dark}">{esc(node["name"])}</text>',
        f'<text x="{dx + dw - 14}" y="{dy + 27}" text-anchor="end" font-size="9.5" font-weight="700" fill="{dark}">{node_kind(node)} · {esc(node_id)}</text>',
    ]
    out.append(text_lines(dx + 14, dy + 64, definitions, size=10.5, line_height=14, fill="#344054"))
    map_y = dy + 112
    out.append(f'<text x="{dx + 14}" y="{map_y}" font-size="9" font-weight="760" letter-spacing=".7" fill="#667085">MAPPINGS</text>')
    if maps:
        out.append(text_lines(dx + 14, map_y + 16, maps[:2], size=9.5, line_height=14, fill="#344054"))
    else:
        out.append(f'<text x="{dx + 14}" y="{map_y + 16}" font-size="9.5" fill="#667085">—</text>')
    conn_y = dy + 158
    out.append(f'<text x="{dx + 14}" y="{conn_y}" font-size="9" font-weight="760" letter-spacing=".7" fill="#667085">OWN CONNECTIONS · ONE HOP</text>')
    if own:
        out.append(text_lines(dx + 14, conn_y + 16, own, size=9.2, line_height=13, fill="#344054"))
    else:
        out.append(f'<text x="{dx + 14}" y="{conn_y + 16}" font-size="9.5" fill="#667085">—</text>')
    stat_y = dy + dh - 48
    cell_w = (dw - 28) / 6
    for i, (label, value) in enumerate(stats):
        sx = dx + 14 + i * cell_w
        out.append(f'<rect x="{sx}" y="{stat_y}" width="{cell_w}" height="34" fill="#f8fafc" stroke="#d9dee7"/>')
        out.append(f'<text x="{sx + 5}" y="{stat_y + 12}" font-size="7.4" font-weight="760" fill="#667085">{esc(label)}</text>')
        out.append(f'<text x="{sx + 5}" y="{stat_y + 26}" font-size="8" fill="#344054">{esc(value[:11])}</text>')
    out.extend(["</g>", "</g>"])
    return "".join(out)


def element_summary(graph: Any, element: dict[str, Any]) -> tuple[str, list[str]]:
    kind = element.get("kind", "—")
    modifiers = []
    if element.get("ordered"):
        modifiers.append("ordered")
    if element.get("multi_select"):
        modifiers.append("multi-select")
    kind_label = " · ".join([kind, *modifiers])
    values = [
        graph.nodes[e["to"]]["name"]
        for e in sorted(graph.out_edges(element["id"]), key=lambda e: e["to"])
        if e["edge"] == "member" and e["to"] in graph.nodes
    ]
    if element["id"] == "RDE2_000001":
        return kind_label, ["present · absent · …"]
    if values:
        shown = values if len(values) <= 4 else [*values[:3], "…"]
        return kind_label, [" · ".join(shown)]
    if kind == "quantitative":
        units = ["HU" if u == "[hnsf'U]" else u for u in element.get("units", [])]
        quantity = " · ".join(units) if units else element.get("quantity_type", "quantity")
        if element.get("min") is not None or element.get("max") is not None:
            quantity += f' · {element.get("min", "…")}–{element.get("max", "…")}'
        method = element.get("method")
        lines = [quantity]
        if method:
            lines.extend(wrap(method, 70, 2))
        return kind_label, lines[:3]
    return kind_label, ["—"]


def render_attribute_zone(graph: Any, hub_id: str, x: float, y: float, w: float, h: float) -> str:
    edges = sorted(
        (e for e in graph.out_edges(hub_id) if e["edge"] == "HAS_ELEMENT" and e["to"] in graph.nodes),
        key=lambda e: e["to"],
    )
    # The HAS_ELEMENT.required property is intentionally never read or rendered.
    cols = [x, x + 290, x + 470, x + 680, x + w]
    header_y = y + 38
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#cbd5e1"/>',
        f'<text x="{x + 16}" y="{y + 24}" class="zone-label">ATTRIBUTES</text>',
        f'<rect x="{x + 12}" y="{header_y}" width="{w - 24}" height="26" fill="#f6f8fb" stroke="#d9dee7"/>',
    ]
    headers = ["ELEMENT", "ID", "KIND", "VALUES / QUANTITY / METHOD"]
    for i, label in enumerate(headers):
        out.append(f'<text x="{cols[i] + 12}" y="{header_y + 18}" font-size="9.5" font-weight="760" letter-spacing=".55" fill="#667085">{label}</text>')
    row_y = header_y + 26
    row_h = 50
    max_rows = 5
    for r in range(max_rows):
        fill = "#fff" if r % 2 == 0 else "#fafbfc"
        out.append(f'<rect x="{x + 12}" y="{row_y + r * row_h}" width="{w - 24}" height="{row_h}" fill="{fill}" stroke="#e3e7ed"/>')
        for cx in cols[1:-1]:
            out.append(f'<line x1="{cx}" y1="{row_y + r * row_h}" x2="{cx}" y2="{row_y + (r + 1) * row_h}" stroke="#e3e7ed"/>')
        if r >= len(edges):
            continue
        edge = edges[r]
        element = graph.nodes[edge["to"]]
        kind, summary = element_summary(graph, element)
        name = element["name"]
        note = edge.get("props", {}).get("note")
        if note:
            name += f" ({note})"
        out.append(f'<text x="{cols[0] + 12}" y="{row_y + r * row_h + 30}" font-size="11.5" font-weight="680" fill="#344054">{esc(name)}</text>')
        out.append(f'<text x="{cols[1] + 12}" y="{row_y + r * row_h + 30}" font-size="10.5" fill="#344054">{esc(element["id"])}</text>')
        out.append(f'<text x="{cols[2] + 12}" y="{row_y + r * row_h + 30}" font-size="10.5" fill="#344054">{esc(kind)}</text>')
        sy = row_y + r * row_h + (20 if len(summary) > 1 else 30)
        out.append(text_lines(cols[3] + 12, sy, summary, size=9.5, line_height=13, fill="#344054"))
    return "".join(out)


def container_geometry(graph: Any, edges: list[dict[str, Any]], hub_id: str, w: float, wide: bool) -> tuple[float, list[tuple[dict[str, Any], float, float, float, list[str]]]]:
    """Return deterministic height and row geometry relative to container origin."""
    rows = []
    if wide and len(edges) > 2 and all(format_props(e) == "—" for e in edges):
        card_w = (w - 42) / 2
        for idx, edge in enumerate(edges):
            col, row = idx % 2, idx // 2
            rows.append((edge, 14 + col * (card_w + 14), 36 + row * 62, card_w, []))
        return 44 + math.ceil(len(edges) / 2) * 62, rows
    card_w = 270 if wide else 238
    prop_chars = 120 if wide else 46
    cy = 36
    for edge in edges:
        props = format_props(edge)
        lines = [] if props == "—" else wrap(props, prop_chars, 4)
        row_h = max(58, 20 + len(lines) * 14)
        rows.append((edge, 14, cy, card_w, lines))
        cy += row_h + 6
    return cy + 4, rows


def render_container(
    graph: Any,
    hub_id: str,
    label: str,
    edges: list[dict[str, Any]],
    x: float,
    y: float,
    w: float,
    wide: bool,
) -> tuple[str, float, list[tuple[str, tuple[float, float, float, float]]]]:
    h, rows = container_geometry(graph, edges, hub_id, w, wide)
    out = [
        f'<g class="relationship-container" data-container="{esc(label)}">',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#f7f8fa" stroke="#98a2b3" stroke-dasharray="5 4"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="30" rx="10" fill="#eef1f5"/>',
        f'<rect x="{x}" y="{y + 21}" width="{w}" height="9" fill="#eef1f5"/>',
        f'<text x="{x + 14}" y="{y + 20}" font-size="10" font-weight="780" letter-spacing="1.05" fill="#475467">{esc(label)}</text>',
        f'<text x="{x + w - 14}" y="{y + 20}" text-anchor="end" font-size="9.5" fill="#667085">{len(edges)}</text>',
    ]
    hover_hits = []
    for edge, rx, ry, card_w, prop_lines in rows:
        node_id = other_end(edge, hub_id)
        ax, ay = x + rx, y + ry
        out.append(mini_face(graph, node_id, ax, ay, card_w))
        hover_hits.append((node_id, (ax, ay, card_w, 52)))
        if prop_lines:
            px = ax + card_w + 14
            py = ay + 18
            out.append(text_lines(px, py, prop_lines, size=9.5, line_height=14, fill="#475467"))
    out.append("</g>")
    return "".join(out), h, hover_hits


def render_mat(graph: Any, hub_id: str, title: str | None = None) -> str:
    if hub_id not in graph.nodes:
        raise SystemExit(f"unknown graph node: {hub_id}")
    hub = graph.nodes[hub_id]
    title = title or hub["name"]
    fill, stroke, dark, _ = NODE_STYLE.get(hub["node"], NODE_STYLE["Concept"])
    outer_x, outer_y, outer_w, outer_h = 20, 20, W - 40, MAT_H - 40
    y_title, h_title = 20, 64
    y_anat, h_anat = 84, 50
    y_text, h_text = 134, 100
    y_attr, h_attr = 234, 330
    y_conn, h_conn = 564, 998
    y_map, h_map = 1562, 92
    y_stats, h_stats = 1654, 146
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {MAT_H}" width="{W}" height="{MAT_H}" role="img" aria-labelledby="mat-title mat-desc">',
        f'<title id="mat-title">{esc(title)} MAT</title>',
        f'<desc id="mat-desc">One-hop context-object mat for {esc(hub["name"])} with fixed card zones and wire-free relationship containers.</desc>',
        """<defs>
          <filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#101828" flood-opacity=".2"/></filter>
          <style>
            text { font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
            .zone-label { font-size:10px; font-weight:780; letter-spacing:1.25px; fill:#526071; }
            .hover-detail { opacity:0; visibility:hidden; pointer-events:none; transition:opacity .12s ease; }
            .hover-hit { pointer-events:all; cursor:help; }
            @media (hover:hover) {
              .hover-target:hover .hover-detail, .hover-target:focus .hover-detail { opacity:1; visibility:visible; }
            }
          </style>
        </defs>""",
        f'<rect width="{W}" height="{MAT_H}" fill="#f5f7fa"/>',
        f'<rect x="{outer_x}" y="{outer_y}" width="{outer_w}" height="{outer_h}" rx="14" fill="#fff" stroke="#7f8da3" stroke-width="1.5"/>',
        f'<rect x="{outer_x}" y="{y_title}" width="{outer_w}" height="{h_title}" rx="14" fill="{fill}"/>',
        f'<rect x="{outer_x}" y="{y_title + h_title - 12}" width="{outer_w}" height="12" fill="{fill}"/>',
        f'<text x="{outer_x + 20}" y="{y_title + 39}" font-size="22" font-weight="780" fill="{dark}">{esc(title)}</text>',
        f'<text x="{outer_x + outer_w - 20}" y="{y_title + 37}" text-anchor="end" font-size="10.5" font-weight="760" letter-spacing=".55" fill="{dark}">{node_kind(hub)} · {esc(hub_id)}</text>',
    ]

    # Anatomy zone: direct scope only; scope strength remains visible.
    scopes = [e for e in graph.out_edges(hub_id) if e["edge"] == "SCOPED_TO" and e["to"] in graph.nodes]
    out.extend(
        [
            f'<rect x="{outer_x}" y="{y_anat}" width="{outer_w}" height="{h_anat}" fill="#fbfcfd" stroke="#d9dee7"/>',
            f'<text x="{outer_x + 20}" y="{y_anat + 20}" class="zone-label">ANATOMY</text>',
        ]
    )
    if scopes:
        pieces = []
        for edge in sorted(scopes, key=lambda e: e["to"]):
            location = graph.nodes[edge["to"]]
            props = edge.get("props", {})
            pieces.append(f'{location["id"]} “{location["name"]}” · {props.get("kind", "—")} · {props.get("strength", "—")}')
        anatomy_text = "  |  ".join(pieces)
    else:
        anatomy_text = "—"
    out.append(f'<text x="{outer_x + 126}" y="{y_anat + 31}" font-size="11.5" fill="#344054">{esc(anatomy_text)}</text>')

    # Text zone.
    out.append(f'<rect x="{outer_x}" y="{y_text}" width="{outer_w}" height="{h_text}" fill="#fff" stroke="#d9dee7"/>')
    out.append(f'<text x="{outer_x + 20}" y="{y_text + 23}" class="zone-label">TEXT</text>')
    definition = wrap(hub.get("definition", "—"), 158, 3)
    out.append(text_lines(outer_x + 92, y_text + 23, definition, size=10.8, line_height=15, fill="#344054"))
    synonyms = [s["term"] if isinstance(s, dict) else str(s) for s in hub.get("synonyms", [])]
    syn_text = " · ".join(synonyms) if synonyms else "—"
    out.append(f'<text x="{outer_x + 92}" y="{y_text + 82}" font-size="9.8" fill="#667085"><tspan font-weight="700">synonyms</tspan> · {esc(syn_text)}</text>')

    out.append(render_attribute_zone(graph, hub_id, outer_x, y_attr, outer_w, h_attr))

    # Connections zone and containers.
    out.append(f'<rect x="{outer_x}" y="{y_conn}" width="{outer_w}" height="{h_conn}" fill="#fff" stroke="#cbd5e1"/>')
    out.append(f'<text x="{outer_x + 16}" y="{y_conn + 25}" class="zone-label">CONNECTIONS · ONE HOP · NO WIRES</text>')
    container_specs = mat_container_specs(graph, hub_id)
    col_gap = 16
    inner_x = outer_x + 16
    inner_w = outer_w - 32
    col_w = (inner_w - col_gap) / 2
    y_cols = [y_conn + 42, y_conn + 42]
    hover_hits: list[tuple[str, tuple[float, float, float, float]]] = []
    for label, edges in container_specs:
        wide = len(edges) >= 3 or any(format_props(e) != "—" and len(format_props(e)) > 58 for e in edges)
        if wide:
            cy = max(y_cols)
            fragment, ch, hits = render_container(graph, hub_id, label, edges, inner_x, cy, inner_w, True)
            out.append(fragment)
            y_cols = [cy + ch + 12, cy + ch + 12]
        else:
            ci = 0 if y_cols[0] <= y_cols[1] else 1
            cx = inner_x + ci * (col_w + col_gap)
            fragment, ch, hits = render_container(graph, hub_id, label, edges, cx, y_cols[ci], col_w, False)
            out.append(fragment)
            y_cols[ci] += ch + 12
        hover_hits.extend(hits)
    if max(y_cols) > y_conn + h_conn - 8:
        raise SystemExit(f"MAT connections overflow for {hub_id}: {max(y_cols):.1f} > {y_conn + h_conn - 8}")

    # Mappings zone. Preferred display terms are mandatory.
    out.append(f'<rect x="{outer_x}" y="{y_map}" width="{outer_w}" height="{h_map}" fill="#fff" stroke="#cbd5e1"/>')
    out.append(f'<text x="{outer_x + 16}" y="{y_map + 24}" class="zone-label">MAPPINGS</text>')
    maps = mappings_for(graph, hub_id)
    map_text = "   ·   ".join(maps) if maps else "—"
    out.append(text_lines(outer_x + 16, y_map + 51, wrap(map_text, 170, 2), size=10.5, line_height=16, fill="#344054"))

    # Fixed six-cell stat row, always last.
    out.append(f'<rect x="{outer_x}" y="{y_stats}" width="{outer_w}" height="{h_stats}" rx="0" fill="#f8fafc" stroke="#7f8da3" stroke-width="1.2"/>')
    stats = stats_for(graph, hub_id)
    stat_w = outer_w / 6
    for i, (label, value) in enumerate(stats):
        sx = outer_x + i * stat_w
        if i:
            out.append(f'<line x1="{sx}" y1="{y_stats}" x2="{sx}" y2="{y_stats + h_stats}" stroke="#cbd5e1"/>')
        out.append(f'<text x="{sx + 13}" y="{y_stats + 30}" font-size="9.5" font-weight="780" letter-spacing=".75" fill="#667085">{esc(label)}</text>')
        out.append(text_lines(sx + 13, y_stats + 60, wrap(value, 22, 3), size=11, line_height=15, fill="#344054", weight=650))

    # Hover targets/details are last so their revealed faces paint above every container.
    for node_id, hit in hover_hits:
        out.append(hover_detail(graph, node_id, hub_id, hit))
    out.append("</svg>")
    return "".join(out) + "\n"


def descendants_and_tree(graph: Any, root_id: str) -> tuple[set[str], dict[str, str], dict[str, list[str]], dict[str, list[str]]]:
    subtype_edges = [e for e in graph.edges if e["edge"] == "SUBTYPE_OF"]
    descendants = {root_id}
    depth = {root_id: 0}
    changed = True
    while changed:
        changed = False
        for edge in subtype_edges:
            if edge["to"] in descendants and edge["from"] not in descendants:
                descendants.add(edge["from"])
                depth[edge["from"]] = depth[edge["to"]] + 1
                changed = True
            elif edge["to"] in depth and edge["from"] in descendants:
                depth[edge["from"]] = min(depth.get(edge["from"], 10**6), depth[edge["to"]] + 1)
    parents: dict[str, list[str]] = {}
    for edge in subtype_edges:
        if edge["from"] in descendants and edge["to"] in descendants:
            parents.setdefault(edge["from"], []).append(edge["to"])
    primary: dict[str, str] = {}
    extra: dict[str, list[str]] = {}
    for child in sorted(descendants):
        if child == root_id:
            continue
        candidates = sorted(set(parents.get(child, [])), key=lambda p: (depth.get(p, 10**6), p))
        if not candidates:
            continue
        primary[child] = candidates[0]
        if len(candidates) > 1:
            extra[child] = candidates[1:]
    children: dict[str, list[str]] = {nid: [] for nid in descendants}
    for child, parent in primary.items():
        children[parent].append(child)
    for parent in children:
        children[parent].sort()
    return descendants, primary, children, extra


def tree_positions(root_id: str, children: dict[str, list[str]], width: int = W) -> tuple[dict[str, tuple[float, int]], int]:
    leaves: list[str] = []

    def collect(node_id: str, depth: int) -> None:
        kids = children.get(node_id, [])
        if not kids:
            leaves.append(node_id)
            return
        for child in kids:
            collect(child, depth + 1)

    collect(root_id, 0)
    leaf_count = max(1, len(leaves))
    left, right = 42, width - 42
    slot = (right - left) / leaf_count
    leaf_x = {nid: left + slot * (i + 0.5) for i, nid in enumerate(leaves)}
    pos: dict[str, tuple[float, int]] = {}
    max_depth = 0

    def assign(node_id: str, depth: int) -> float:
        nonlocal max_depth
        max_depth = max(max_depth, depth)
        kids = children.get(node_id, [])
        if not kids:
            x = leaf_x[node_id]
        else:
            child_x = [assign(child, depth + 1) for child in kids]
            x = (child_x[0] + child_x[-1]) / 2
        pos[node_id] = (x, depth)
        return x

    assign(root_id, 0)
    return pos, max_depth


def tree_node_box(graph: Any, node_id: str, cx: float, y: float, w: float, h: float = 76, ghost: bool = False) -> str:
    node = graph.nodes[node_id]
    fill, stroke, dark, radius = NODE_STYLE.get(node["node"], NODE_STYLE["Concept"])
    x = cx - w / 2
    dash = ' stroke-dasharray="6 4"' if node["node"] == "Grouping" or ghost else ""
    opacity = ' opacity=".62"' if ghost else ""
    name_lines = wrap(node["name"], max(14, int((w - 18) / 6.2)), 2)
    fs = 10.6 if len(node["name"]) <= 30 else 8.1
    name_y = y + 24 if len(name_lines) == 1 else y + 18
    out = [
        f'<g data-node="{esc(node_id)}"{opacity}>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{min(radius, h/2)}" fill="{fill}" stroke="{stroke}" stroke-width="1.3"{dash}/>',
        text_lines(cx, name_y, name_lines, size=fs, line_height=13, fill=dark, weight=730, anchor="middle"),
        f'<text x="{cx}" y="{y + h - 24}" text-anchor="middle" font-size="7.6" font-weight="720" letter-spacing=".45" fill="#667085">{node_kind(node)}</text>',
        f'<text x="{cx}" y="{y + h - 10}" text-anchor="middle" font-size="8" font-weight="650" fill="#667085">{esc(node_id)}</text>',
        "</g>",
    ]
    return "".join(out)


def tree_relationships(graph: Any, descendants: set[str]) -> list[dict[str, Any]]:
    allowed = set(REL_STYLE)
    edges = [
        edge
        for edge in graph.edges
        if edge["edge"] in allowed and edge["from"] in descendants and edge["to"] in descendants
    ]
    order = {"MAY_MANIFEST_AS": 0, "MAY_CAUSE": 1, "MAY_PROGRESS_TO": 2, "OCCURS_WITH": 3, "ASSESSED_BY": 4}
    return sorted(
        edges,
        key=lambda e: (
            order.get(e["edge"], 99),
            graph.nodes[e["from"]]["name"].casefold(),
            graph.nodes[e["to"]]["name"].casefold(),
            e.get("id", ""),
        ),
    )


def render_tree(graph: Any, root_id: str, title: str | None = None) -> str:
    if root_id not in graph.nodes:
        raise SystemExit(f"unknown graph node: {root_id}")
    root = graph.nodes[root_id]
    title = title or root["name"]
    descendants, primary, children, extra = descendants_and_tree(graph, root_id)
    pos, max_depth = tree_positions(root_id, children)
    rels = tree_relationships(graph, descendants)
    node_h = 76
    top_y = 132
    level_gap = 128
    tree_bottom = top_y + max_depth * level_gap + node_h
    rel_y = tree_bottom + 68
    row_h = 62
    tree_h = int(rel_y + 48 + len(rels) * row_h + 34)
    slot = (W - 84) / max(1, len([n for n in descendants if not children.get(n)]))
    node_w = max(112, min(158, slot - 10))

    markers = []
    for edge_type, (color, _, _, _) in REL_STYLE.items():
        marker_id = edge_type.lower().replace("_", "-")
        markers.append(
            f'<marker id="arr-{marker_id}" markerUnits="userSpaceOnUse" viewBox="0 0 9 9" refX="8" refY="4.5" markerWidth="9" markerHeight="9" orient="auto">'
            f'<path d="M0 0L9 4.5L0 9Z" fill="{color}"/></marker>'
        )

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {tree_h}" width="{W}" height="{tree_h}" role="img" aria-labelledby="tree-title tree-desc">',
        f'<title id="tree-title">{esc(title)} TREE</title>',
        f'<desc id="tree-desc">Is-a hierarchy rooted at {esc(root["name"])} with orthogonal connectors and unambiguous relationship tracks.</desc>',
        f'<defs>{"".join(markers)}<style>text {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }}</style></defs>',
        f'<rect width="{W}" height="{tree_h}" fill="#fbfcfe"/>',
        '<rect x="0" y="0" width="1280" height="8" fill="#31486d"/>',
        f'<text x="32" y="43" font-size="10.5" font-weight="780" letter-spacing="1.45" fill="#526071">TREE · IS-A FAMILY</text>',
        f'<text x="32" y="76" font-size="26" font-weight="780" fill="#172033">{esc(title)}</text>',
        f'<text x="32" y="99" font-size="11.5" fill="#667085">More specific downward · boxes retain node kind · relationship tracks repeat endpoint references so every label owns one edge.</text>',
    ]

    # Orthogonal taxonomy connectors are drawn first, then boxes paint above them.
    for parent in sorted(children):
        kids = children[parent]
        if not kids:
            continue
        px, pd = pos[parent]
        py = top_y + pd * level_gap
        child_points = [(pos[child][0], top_y + pos[child][1] * level_gap) for child in kids]
        bus_y = py + node_h + (level_gap - node_h) / 2
        if len(kids) == 1:
            cx, cy = child_points[0]
            out.append(f'<path d="M{px} {py + node_h}V{cy}" fill="none" stroke="#465568" stroke-width="2"/>')
        else:
            out.append(f'<path d="M{px} {py + node_h}V{bus_y}H{child_points[-1][0]}M{child_points[0][0]} {bus_y}H{px}" fill="none" stroke="#465568" stroke-width="2"/>')
            for cx, cy in child_points:
                out.append(f'<path d="M{cx} {bus_y}V{cy}" fill="none" stroke="#465568" stroke-width="2"/>')

    for node_id, (cx, depth) in sorted(pos.items(), key=lambda item: (item[1][1], item[1][0], item[0])):
        y = top_y + depth * level_gap
        w = 220 if node_id == root_id else node_w
        out.append(tree_node_box(graph, node_id, cx, y, w, node_h))

    # Second taxonomy parents are repeated as ghost boxes beside the affected child.
    for child, parents in sorted(extra.items()):
        child_x, child_depth = pos[child]
        child_y = top_y + child_depth * level_gap
        for idx, parent in enumerate(parents):
            gx = min(W - 88, child_x + node_w / 2 + 82 + idx * 140)
            gy = child_y - 2
            out.append(tree_node_box(graph, parent, gx, gy, 126, node_h, ghost=True))
            out.append(f'<path d="M{gx - 63} {gy + node_h/2}H{child_x + node_w/2}" fill="none" stroke="#98a2b3" stroke-width="1.4" stroke-dasharray="5 4"/>')

    # Relationship edges: dedicated horizontal tracks make fan-in labels unambiguous.
    rel_box_y = rel_y - 30
    rel_box_h = 38 + len(rels) * row_h
    out.append(f'<rect x="24" y="{rel_box_y}" width="1232" height="{rel_box_h}" rx="12" fill="#fff" stroke="#cbd5e1"/>')
    out.append(f'<text x="42" y="{rel_y - 7}" font-size="10" font-weight="780" letter-spacing="1.25" fill="#526071">RELATIONSHIPS WITHIN THIS FAMILY</text>')
    if not rels:
        out.append(f'<text x="42" y="{rel_y + 24}" font-size="11" fill="#667085">—</text>')
    source_x, source_w = 42, 244
    target_x, target_w = 994, 244
    line_x1, line_x2 = source_x + source_w + 12, target_x - 12
    for idx, edge in enumerate(rels):
        y = rel_y + 12 + idx * row_h
        mid = y + 26
        out.append(mini_face(graph, edge["from"], source_x, y, source_w, 52))
        out.append(mini_face(graph, edge["to"], target_x, y, target_w, 52))
        color, label_fill, label_stroke, dash = REL_STYLE[edge["edge"]]
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        marker = ""
        if edge["edge"] != "OCCURS_WITH":
            marker_id = edge["edge"].lower().replace("_", "-")
            marker = f' marker-end="url(#arr-{marker_id})"'
        edge_data = f' data-edge="{esc(edge.get("id", edge["edge"]))}"'
        out.append(f'<path{edge_data} d="M{line_x1} {mid}H{line_x2}" fill="none" stroke="{color}" stroke-width="2"{dash_attr}{marker}/>' )
        if edge["edge"] == "OCCURS_WITH":
            out.append(f'<circle cx="{line_x1}" cy="{mid}" r="3" fill="#fff" stroke="{color}" stroke-width="1.5"/><circle cx="{line_x2}" cy="{mid}" r="3" fill="#fff" stroke="{color}" stroke-width="1.5"/>')
        props = format_props(edge)
        label = relation_friendly(edge["edge"]) + (f" · {props}" if props != "—" else "")
        label_lines = wrap(label, 82, 2)
        label_w = min(650, max(260, max(len(line) for line in label_lines) * 5.9 + 24))
        label_h = 22 if len(label_lines) == 1 else 36
        lx = (line_x1 + line_x2) / 2 - label_w / 2
        ly = mid - label_h / 2
        out.append(f'<rect x="{lx}" y="{ly}" width="{label_w}" height="{label_h}" rx="6" fill="{label_fill}" stroke="{label_stroke}"/>')
        out.append(text_lines((line_x1 + line_x2) / 2, ly + (15 if len(label_lines) == 1 else 13), label_lines, size=9.5, line_height=13, fill=color, weight=750, anchor="middle"))
    out.append("</svg>")
    return "".join(out) + "\n"


DEFAULT_OUTPUTS = [
    ("mat", "RDE2_000502", "Pleural effusion", "mat-pleural-effusion.svg"),
    ("mat", "RDE2_000801", "Acute pyelonephritis", "mat-acute-pyelonephritis.svg"),
    ("tree", "RDE2_000516", "Pleural abnormality", "tree-pleural-abnormality.svg"),
    ("tree", "RDE2_000814", "Renal abnormality", "tree-renal-abnormality.svg"),
]


def write_svg(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("all", help="generate the four decision-set pictures beside this script")
    for mode in ("mat", "tree"):
        command = sub.add_parser(mode)
        command.add_argument("node_id")
        command.add_argument("--title")
        command.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    graph = load_graph()
    if args.mode == "all":
        output_dir = Path(__file__).resolve().parent
        for mode, node_id, title, filename in DEFAULT_OUTPUTS:
            content = render_mat(graph, node_id, title) if mode == "mat" else render_tree(graph, node_id, title)
            write_svg(output_dir / filename, content)
        return
    content = render_mat(graph, args.node_id, args.title) if args.mode == "mat" else render_tree(graph, args.node_id, args.title)
    write_svg(args.output, content)


if __name__ == "__main__":
    main()
