#!/usr/bin/env python3
"""Validate and render a text-anchored report as observation and definition planes."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from graph import load_graph  # noqa: E402
from render_cards import (  # noqa: E402
    ACCENT, FONT, FS, FS_S, FS_XS, GRAY, INK, KIND, MINI_H, MONO, MUTED,
    RULE, Cards, esc, tw, txt, wrap,
)

W, LEFT, RIGHT = 1100, 32, 1068
OBS_COLORS = ["#2563eb", "#0891b2", "#d97706", "#7c3aed", "#dc2626", "#64748b"]


def fail(message):
    raise SystemExit(f"report validation failed: {message}")


def read_report(path):
    rows = []
    with open(path, encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                fail(f"{path}:{line_no}: bad JSON: {exc}")
    reports = [row for row in rows if "report" in row]
    if len(reports) != 1:
        fail(f"expected exactly one report line, found {len(reports)}")
    return reports[0], [r for r in rows if "observation" in r], [r for r in rows if "relation" in r]


def ancestors(graph, node_id):
    seen, queue = set(), [node_id]
    while queue:
        current = queue.pop(0)
        if current in seen:
            continue
        seen.add(current)
        queue.extend(e["to"] for e in graph.out_edges(current) if e["edge"] == "SUBTYPE_OF")
    return seen


def validate(report, observations, relations, graph, cards):
    text_value = report.get("text")
    if not isinstance(text_value, str):
        fail("report text must be a string")
    obs_ids = set()
    for obs in observations:
        oid = obs.get("observation", "<missing>")
        if oid in obs_ids:
            fail(f"duplicate observation {oid}")
        obs_ids.add(oid)
        subject = graph.nodes.get(obs.get("subject"))
        if not subject or subject.get("node") not in {"FindingClass", "Diagnosis", "Grouping"}:
            fail(f"{oid}: subject {obs.get('subject')!r} is not a FindingClass, Diagnosis, or Grouping")
        location = graph.nodes.get(obs.get("location"))
        if not location or location.get("node") != "AnatomicLocation":
            fail(f"{oid}: location {obs.get('location')!r} is not an AnatomicLocation")
        own_elements = {e["to"] for e in graph.out_edges(subject["id"]) if e["edge"] == "HAS_ELEMENT"}
        for element_id, value in obs.get("values", {}).items():
            if element_id not in own_elements:
                fail(f"{oid}: element {element_id} is not bound directly to {subject['id']} by HAS_ELEMENT")
            element = graph.nodes.get(element_id)
            if not element or element.get("node") != "DataElement":
                fail(f"{oid}: value key {element_id} is not a DataElement")
            if str(element.get("kind", "")).startswith("categorical"):
                allowed = {v.get("value") for v in cards.values(element_id)}
                if value not in allowed:
                    fail(f"{oid}: {value!r} is not in {element_id}'s value set")
        scopes, _ = cards.scope(subject["id"])
        if not {scope for scope, _ in scopes}.intersection(ancestors(graph, location["id"])):
            fail(f"{oid}: location {location['id']} does not satisfy the scope of {subject['id']}")
        span = obs.get("span")
        if not (isinstance(span, list) and len(span) == 2 and all(isinstance(v, int) for v in span)):
            fail(f"{oid}: span must be [start, end)")
        start, end = span
        if start < 0 or end < start or end > len(text_value) or text_value[start:end] != obs.get("quote"):
            fail(f"{oid}: quote does not equal report text at span [{start}, {end})")
    for rel in relations:
        if rel.get("from") not in obs_ids or rel.get("to") not in obs_ids:
            fail(f"relation {rel.get('relation')} has an endpoint that is not an observation in the file")


def line_layout(text_value, max_chars):
    lines, start = [], 0
    while start < len(text_value):
        limit = min(len(text_value), start + max_chars)
        end = limit if limit == len(text_value) else text_value.rfind(" ", start, limit + 1)
        if end <= start:
            end = limit
        lines.append((start, end, text_value[start:end]))
        start = end + (1 if end < len(text_value) and text_value[end] == " " else 0)
    return lines


def route(points, color, opacity=.28, width=1.4, dash=None):
    attrs = f'fill="none" stroke="{color}" stroke-width="{width}" opacity="{opacity}"'
    if dash:
        attrs += f' stroke-dasharray="{dash}"'
    return f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}" {attrs}/>'


def pack_rows(items, top, max_per_row, gap=16, row_gap=28):
    """Pack measured dicts and assign x/y/row without ever reducing their widths."""
    rows, row = [], []
    for item in items:
        trial = sum(i["w"] for i in row) + item["w"] + gap * len(row)
        if row and (len(row) >= max_per_row or trial > RIGHT - LEFT):
            rows.append(row); row = []
        if item["w"] > RIGHT - LEFT:
            raise ValueError(f'measured card wider than canvas: {item.get("id", "card")}')
        row.append(item)
    if row:
        rows.append(row)
    y = top
    for row_no, packed in enumerate(rows):
        row_w = sum(i["w"] for i in packed) + gap * (len(packed) - 1)
        row_h = max(i["h"] for i in packed)
        x = (W - row_w) / 2
        for item in packed:
            item.update(x=x, y=y, row=row_no)
            x += item["w"] + gap
        y += row_h + row_gap
    return rows, y - row_gap


def measured_mini(cards, node_id, max_content=132):
    node = cards.n[node_id]
    name_lines = wrap(node["name"], FS, max_content, 3)
    kind_line, id_line = cards.kind(node_id), node_id
    content_w = max([tw(line, FS, True) for line in name_lines] + [tw(kind_line, FS_XS, True), tw(id_line, FS_XS)])
    width = max(140, content_w + 24)
    name_lh, meta_lh = FS + 3, FS_XS + 2
    height = max(MINI_H, 10 + len(name_lines) * name_lh + 2 * meta_lh + 9)
    return {"id": node_id, "w": width, "h": height, "name_lines": name_lines,
            "kind_line": kind_line, "id_line": id_line}


def draw_mini(cards, box):
    node = cards.n[box["id"]]
    accent, dark, bg = ACCENT.get(node["node"], ACCENT["Concept"])
    x, y, w, h = box["x"], box["y"], box["w"], box["h"]
    out = [f'<g class="mini" id="m-{esc(box["id"])}" data-node="{esc(box["id"])}">',
           f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" fill="{bg}" stroke="{RULE}"/>',
           f'<rect x="{x:.1f}" y="{y:.1f}" width="4" height="{h:.1f}" rx="2" fill="{accent}"/>']
    yy = y + FS + 7
    for line in box["name_lines"]:
        out.append(txt(x + 12, yy, line, FS, dark, weight="600")); yy += FS + 3
    out.append(txt(x + 12, yy + 2, box["kind_line"], FS_XS, MUTED, weight="600"))
    out.append(txt(x + 12, yy + FS_XS + 5, box["id_line"], FS_XS, MUTED, mono=True))
    out.append("</g>")
    return "".join(out)


def observation_measure(obs, graph):
    node, loc = graph.nodes[obs["subject"]], graph.nodes[obs["location"]]
    cap = 270
    subject_lines = wrap(node["name"], FS, cap, 3)
    quote_lines = wrap(f'“{obs["quote"]}”', FS_S, cap, 3)
    fixed = [tw(obs["observation"], FS_XS, True) + tw(node["node"].upper(), FS_XS) + 42,
             tw(node["id"], FS_XS), tw(f'⌂ {loc["name"]}', FS_S, True), tw(loc["id"], FS_XS)]
    for eid, value in obs["values"].items():
        fixed.append(tw(graph.nodes[eid]["name"], FS_S, True) + tw(value, FS_S, True) + 40)
        fixed.append(tw(eid, FS_XS))
    if obs.get("confidence"):
        fixed.append(tw(f'confidence: {obs["confidence"]}', FS_S, True))
    content_w = max(fixed + [tw(line, FS, True) for line in subject_lines] + [tw(line, FS_S) for line in quote_lines])
    width = max(230, content_w + 24)
    subject_lh, small_lh = FS + 3, FS_S + 3
    header_h = FS_XS + 20
    height = (header_h + 10 + len(subject_lines) * subject_lh + FS_XS + 9 +
              FS_S + FS_XS + 14 + len(obs["values"]) * (FS_S + FS_XS + 15) +
              8 + len(quote_lines) * small_lh + (small_lh if obs.get("confidence") else 0) + 12)
    return {"id": obs["observation"], "obs": obs, "w": width, "h": height,
            "subject_lines": subject_lines, "quote_lines": quote_lines, "header_h": header_h}


def draw_observation(box, index, graph):
    obs, x, y, w, h = box["obs"], box["x"], box["y"], box["w"], box["h"]
    node, loc, color = graph.nodes[obs["subject"]], graph.nodes[obs["location"]], OBS_COLORS[index]
    accent = ACCENT[node["node"]][1]
    out = [f'<g id="{esc(obs["observation"])}">',
           f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="9" fill="#ffffff" stroke="{color}" stroke-width="1.5"/>',
           f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{box["header_h"]:.1f}" rx="9" fill="{color}" opacity=".09"/>']
    out.append(txt(x + 12, y + FS_XS + 8, obs["observation"], FS_XS, color, weight="700", mono=True))
    out.append(txt(x + w - 12, y + FS_XS + 8, node["node"].upper(), FS_XS, MUTED, anchor="end"))
    yy = y + box["header_h"] + FS + 8
    for line in box["subject_lines"]:
        out.append(txt(x + 12, yy, line, FS, accent, weight="700")); yy += FS + 3
    out.append(txt(x + 12, yy + 1, node["id"], FS_XS, MUTED, mono=True)); yy += FS_XS + 10
    out.append(txt(x + 12, yy, f'⌂ {loc["name"]}', FS_S, ACCENT["AnatomicLocation"][1], weight="600")); yy += FS_S + 3
    out.append(txt(x + 12, yy, loc["id"], FS_XS, MUTED, mono=True)); yy += FS_XS + 11
    box["location_anchor"] = (x + 18, yy - FS_XS - 4)
    box["element_anchors"] = {}
    for eid, value in obs["values"].items():
        row_h = FS_S + FS_XS + 15
        out.append(f'<rect x="{x + 8:.1f}" y="{yy - FS_S:.1f}" width="{w - 16:.1f}" height="{row_h:.1f}" rx="4" fill="{ACCENT["DataElement"][2]}"/>')
        out.append(txt(x + 14, yy, graph.nodes[eid]["name"], FS_S, ACCENT["DataElement"][1], weight="600"))
        out.append(txt(x + w - 14, yy, value, FS_S, ACCENT["DataElement"][1], anchor="end", weight="700"))
        out.append(txt(x + 14, yy + FS_XS + 3, eid, FS_XS, MUTED, mono=True))
        box["element_anchors"][eid] = (x + w - 20, yy)
        yy += row_h
    yy += 8
    for line in box["quote_lines"]:
        out.append(txt(x + 12, yy, line, FS_S, MUTED, italic=True)); yy += FS_S + 3
    if obs.get("confidence"):
        out.append(txt(x + 12, yy, f'confidence: {obs["confidence"]}', FS_S, color, weight="600"))
    out.append("</g>")
    return "".join(out)


def labelled_arc(x1, y1, x2, y2, apex, label, color, marker, meta="", control_x=None):
    control_x = (x1 + x2) / 2 if control_x is None else control_x
    control_y = 2 * apex - (y1 + y2) / 2
    label_x = (x1 + 2 * control_x + x2) / 4
    label_y = apex + 3
    path = f'M {x1:.1f} {y1:.1f} Q {control_x:.1f} {control_y:.1f} {x2:.1f} {y2:.1f}'
    label_w = tw(label, FS_XS, True) + 12
    out = [f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="3" fill="{color}"/>',
           f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.5" opacity=".86" marker-end="url(#{marker})"/>',
           f'<rect x="{label_x - label_w / 2:.1f}" y="{label_y - FS_XS:.1f}" width="{label_w:.1f}" height="{FS_XS + 5:.1f}" rx="3" fill="#ffffff"/>',
           txt(label_x, label_y, label, FS_XS, color, anchor="middle", weight="700")]
    if meta:
        meta_w = tw(meta, FS_XS) + 10
        out.extend([f'<rect x="{label_x - meta_w / 2:.1f}" y="{label_y + 4:.1f}" width="{meta_w:.1f}" height="{FS_XS + 4:.1f}" rx="3" fill="#ffffff"/>',
                    txt(label_x, label_y + FS_XS + 3, meta, FS_XS, MUTED, anchor="middle")])
    return "".join(out)


def value_lines(values, max_width):
    text = " · ".join(str(v.get("value")) for v in values)
    return wrap(text, FS_XS, max_width, None)


def render(report, observations, relations, graph, cards):
    body = []
    report_fs = FS
    char_w = report_fs * .61
    max_chars = max(30, int((W - 2 * 72) / char_w))
    report_lines = line_layout(report["text"], max_chars)
    text_x, text_y = 72, FS_XS + 40
    line_h = report_fs + FS_XS + 13
    body.append(txt(48, FS_XS + 12, "REPORT TEXT", FS_XS, MUTED, weight="700"))
    for line_no, (start, end, line) in enumerate(report_lines):
        y = text_y + line_no * line_h
        body.append(f'<text x="{text_x}" y="{y}" font-size="{report_fs}" fill="{INK}" font-family="{MONO}">{esc(line)}</text>')
        for obs_index, obs in enumerate(observations):
            left, right = max(obs["span"][0], start), min(obs["span"][1], end)
            if left < right:
                ux1, ux2 = text_x + (left - start) * char_w, text_x + (right - start) * char_w
                color = OBS_COLORS[obs_index]
                body.append(f'<line x1="{ux1:.1f}" y1="{y + 5:.1f}" x2="{ux2:.1f}" y2="{y + 5:.1f}" stroke="{color}" stroke-width="3"/>')
                body.append(txt((ux1 + ux2) / 2, y + FS_XS + 7, obs["observation"], FS_XS, color, anchor="middle", weight="700"))

    report_bottom = text_y + (len(report_lines) - 1) * line_h + FS_XS + 12
    obs_items = [observation_measure(obs, graph) for obs in observations]
    obs_top = report_bottom + 70
    obs_rows, obs_bottom = pack_rows(obs_items, obs_top, 3, gap=24, row_gap=130)
    obs_boxes = {item["id"]: item for item in obs_items}
    for index, box in enumerate(obs_items):
        body.append(draw_observation(box, index, graph))
    body.append(txt(48, obs_top - 22, "OBSERVATIONS", FS_XS, MUTED, weight="700"))

    # Report-span pointers follow the measured observation geometry; second-row cards use the outer gutter.
    for obs_index, obs in enumerate(observations):
        box = obs_boxes[obs["observation"]]
        span_mid = sum(obs["span"]) / 2
        line_no = next(i for i, (a, b, _) in enumerate(report_lines) if a <= span_mid <= b)
        sx = text_x + (span_mid - report_lines[line_no][0]) * char_w
        sy = text_y + line_no * line_h + FS_XS + 10
        cx = box["x"] + box["w"] / 2
        if box["row"] == 0:
            points = [(sx, sy), (sx, box["y"] - 14), (cx, box["y"])]
        else:
            gutter = RIGHT - obs_index * 5
            points = [(sx, sy), (sx, obs_top - 12), (gutter, obs_top - 12), (gutter, box["y"] - 12), (cx, box["y"])]
        body.append(route(points, GRAY, .22, 1.0))

    # Observation-space relations use final card borders.
    upper_row_bottom = max(box["y"] + box["h"] for box in obs_items if box["row"] == 0)
    lower_row_top = min((box["y"] for box in obs_items if box["row"] > 0), default=upper_row_bottom + 100)
    lane_low, lane_high = upper_row_bottom + 18, lower_row_top - 34
    lane_step = (lane_high - lane_low) / max(1, len(relations) - 1)
    for index, rel in enumerate(relations):
        source, target = obs_boxes[rel["from"]], obs_boxes[rel["to"]]
        color = "#7c3aed" if rel["relation"] == "SUPPORTS" else "#dc2626"
        marker = "arrow-purple" if rel["relation"] == "SUPPORTS" else "arrow-red"
        if source["row"] != target["row"]:
            x1, y1 = source["x"] + source["w"] / 2, source["y"] + source["h"]
            x2, y2 = target["x"] + target["w"] / 2, target["y"]
            apex = lane_low + index * lane_step
            control_x = (x1 + x2) / 2 + (index - 1) * 24
        else:
            x1, y1 = source["x"] + source["w"] / 2, source["y"]
            x2, y2 = target["x"] + target["w"] / 2, target["y"]
            apex = lane_low + index * lane_step
            control_x = None
        body.append(labelled_arc(x1, y1, x2, y2, apex, rel["relation"], color, marker, control_x=control_x))

    def_rule_y = obs_bottom + 58
    body.append(f'<line x1="48" y1="{def_rule_y:.1f}" x2="1052" y2="{def_rule_y:.1f}" stroke="{RULE}" stroke-width="1.5"/>')
    body.append(txt(48, def_rule_y + FS_XS + 12, "DEFINITIONS", FS_XS, MUTED, weight="700"))
    class_items = [measured_mini(cards, obs["subject"]) for obs in observations]
    class_top = def_rule_y + FS_XS + 28
    class_rows, class_bottom = pack_rows(class_items, class_top, 6, gap=14, row_gap=24)
    class_boxes = {item["id"]: item for item in class_items}
    for box in class_items:
        body.append(draw_mini(cards, box))

    # Subject pointers route from measured Observation cards to measured definition cards.
    for index, obs in enumerate(observations):
        source, target = obs_boxes[obs["observation"]], class_boxes[obs["subject"]]
        sx, tx = source["x"] + source["w"] / 2, target["x"] + target["w"] / 2
        if source["row"] == len(obs_rows) - 1:
            points = [(sx, source["y"] + source["h"]), (sx, target["y"])]
        else:
            gutter = LEFT - 8 + index * 4
            points = [(sx, source["y"] + source["h"]), (gutter, source["y"] + source["h"] + 10), (gutter, target["y"] - 10), (tx, target["y"])]
        body.append(route(points, ACCENT[graph.nodes[obs["subject"]]["node"]][0], .28, 1.2))

    acute = measured_mini(cards, "RDE2_000801", max_content=180)
    pyelo = class_boxes["RDE2_000800"]
    acute.update(x=max(LEFT, min(RIGHT - acute["w"], pyelo["x"] + pyelo["w"] / 2 - acute["w"] / 2)),
                 y=class_bottom + 165)
    body.append(draw_mini(cards, acute))
    pyelo_cx, acute_cx = pyelo["x"] + pyelo["w"] / 2, acute["x"] + acute["w"] / 2
    body.append(route([(pyelo_cx, pyelo["y"] + pyelo["h"]), (pyelo_cx, acute["y"] - 12), (acute_cx, acute["y"])], ACCENT["Diagnosis"][0], .55, 2.0))
    body.append(txt(acute_cx + 6, acute["y"] - 7, "SUBTYPE_OF", FS_XS, MUTED))

    subjects = set(class_boxes)
    def_edges = [e for e in graph.out_edges("RDE2_000801") if e["edge"] in {"MAY_MANIFEST_AS", "OCCURS_WITH", "MAY_CAUSE"} and e["to"] in subjects]
    for index, edge in enumerate(def_edges):
        target = class_boxes[edge["to"]]
        props = edge.get("props", {})
        meta = " · ".join(str(props[k]).replace("_", " ") for k in ("typicality", "specificity") if props.get(k))
        apex = class_bottom + 30 + index * (FS_XS * 2 + 12)
        body.append(labelled_arc(acute_cx, acute["y"], target["x"] + target["w"] / 2,
                                 target["y"] + target["h"], apex, edge["edge"],
                                 ACCENT["Diagnosis"][0], "arrow-purple", meta))

    lower_top = acute["y"] + acute["h"] + 105
    observed_locations = {obs["location"] for obs in observations}
    scope_targets = {scope for obs in observations for scope, _ in cards.scope(obs["subject"])[0]}
    anatomy_ids, anatomy_edges = observed_locations | scope_targets, []
    for location in sorted(observed_locations):
        seen, queue = set(), [location]
        while queue:
            current = queue.pop(0)
            if current in seen or current in scope_targets:
                continue
            seen.add(current)
            for edge in graph.out_edges(current):
                if edge["edge"] == "SUBTYPE_OF" and edge["to"] in graph.nodes:
                    anatomy_ids.add(edge["to"]); anatomy_edges.append((current, edge["to"])); queue.append(edge["to"])
    anatomy_edges = sorted(set(anatomy_edges))
    roots = sorted(scope_targets, key=lambda nid: cards.name(nid).lower())
    tree_specs, anatomy_width, anatomy_height = [], 0, 0
    for root in roots:
        root_box = measured_mini(cards, root)
        child_boxes = [measured_mini(cards, child) for child, parent in anatomy_edges if parent == root]
        children_w = sum(c["w"] for c in child_boxes) + max(0, len(child_boxes) - 1) * 18
        tree_w = max(root_box["w"], children_w)
        tree_h = root_box["h"] + 34 + (max((c["h"] for c in child_boxes), default=0))
        tree_specs.append((root_box, child_boxes, tree_w, tree_h))
        anatomy_width += tree_w
        anatomy_height = max(anatomy_height, tree_h)
    anatomy_width += max(0, len(tree_specs) - 1) * 28

    element_ids = [eid for eid in ("RDE2_000001", "RDE2_000077") if any(eid in obs["values"] for obs in observations)]
    element_boxes = []
    for eid in element_ids:
        node, values = graph.nodes[eid], cards.values(eid)
        width = max(285, tw(node["name"], FS, True) + 28, tw(f'ELEMENT · {eid}', FS_XS) + 28)
        lines = value_lines(values, width - 28)
        height = 14 + FS + 5 + FS_XS + 10 + len(lines) * (FS_XS + 3) + 12
        element_boxes.append({"id": eid, "w": width, "h": height, "lines": lines})
    element_width = max(e["w"] for e in element_boxes)
    element_height = sum(e["h"] for e in element_boxes) + max(0, len(element_boxes) - 1) * 18

    side_by_side = anatomy_width + 36 + element_width <= RIGHT - LEFT
    anatomy_x, anatomy_y = LEFT, lower_top
    elements_x = LEFT + anatomy_width + 36 if side_by_side else LEFT
    elements_y = lower_top if side_by_side else lower_top + anatomy_height + 60
    body.append(txt(anatomy_x, anatomy_y - 18, "ANATOMY", FS_XS, MUTED, weight="700"))
    anatomy_pos, cursor_x = {}, anatomy_x
    for root_box, child_boxes, tree_w, tree_h in tree_specs:
        root_box.update(x=cursor_x + (tree_w - root_box["w"]) / 2, y=anatomy_y)
        anatomy_pos[root_box["id"]] = root_box
        body.append(draw_mini(cards, root_box))
        child_y = anatomy_y + root_box["h"] + 34
        child_x = cursor_x + (tree_w - (sum(c["w"] for c in child_boxes) + max(0, len(child_boxes) - 1) * 18)) / 2
        for child in child_boxes:
            child.update(x=child_x, y=child_y); anatomy_pos[child["id"]] = child
            body.append(draw_mini(cards, child)); child_x += child["w"] + 18
        cursor_x += tree_w + 28
    for child, parent in anatomy_edges:
        cb, pb = anatomy_pos[child], anatomy_pos[parent]
        cx, px = cb["x"] + cb["w"] / 2, pb["x"] + pb["w"] / 2
        heavier = child == "RID29663"
        body.append(route([(cx, cb["y"]), (cx, cb["y"] - 18), (px, cb["y"] - 18), (px, pb["y"] + pb["h"])],
                          ACCENT["AnatomicLocation"][0], .65 if heavier else .42, 2.5 if heavier else 1.4))

    body.append(txt(elements_x, elements_y - 18, "ELEMENTS", FS_XS, MUTED, weight="700"))
    element_pos, ey = {}, elements_y
    for box in element_boxes:
        box.update(x=elements_x, y=ey); element_pos[box["id"]] = box
        accent, dark, bg = ACCENT["DataElement"]
        body.extend([f'<rect x="{box["x"]:.1f}" y="{ey:.1f}" width="{box["w"]:.1f}" height="{box["h"]:.1f}" rx="7" fill="{bg}" stroke="{RULE}"/>',
                     f'<rect x="{box["x"]:.1f}" y="{ey:.1f}" width="4" height="{box["h"]:.1f}" rx="2" fill="{accent}"/>',
                     txt(box["x"] + 14, ey + FS + 8, graph.nodes[box["id"]]["name"], FS, dark, weight="700"),
                     txt(box["x"] + 14, ey + FS + FS_XS + 13, f'ELEMENT · {box["id"]}', FS_XS, MUTED, mono=True)])
        vy = ey + FS + FS_XS * 2 + 19
        for line in box["lines"]:
            body.append(txt(box["x"] + 14, vy, line, FS_XS, dark)); vy += FS_XS + 3
        ey += box["h"] + 18

    # Measured pointer trunks and target drops.
    location_trunk_y, element_trunk_y = obs_bottom + 14, obs_bottom + 28
    loc_sources, elem_sources = [], {eid: [] for eid in element_ids}
    for box in obs_items:
        lx, ly = box["location_anchor"]; loc_sources.append(lx)
        body.append(route([(lx, ly), (lx, location_trunk_y)], ACCENT["AnatomicLocation"][0], .14, 1.0))
        for eid, (ex, ey0) in box["element_anchors"].items():
            elem_sources[eid].append(ex)
            body.append(route([(ex, ey0), (ex, element_trunk_y)], ACCENT["DataElement"][0], .12, 1.0))
    body.append(route([(LEFT - 10, location_trunk_y), (max(loc_sources), location_trunk_y)], ACCENT["AnatomicLocation"][0], .16, 1.2))
    for i, target in enumerate(sorted(observed_locations, key=lambda nid: cards.name(nid).lower())):
        box = anatomy_pos[target]; drop_x = LEFT - 10 + i * 8
        body.append(route([(drop_x, location_trunk_y), (drop_x, box["y"] + box["h"] / 2), (box["x"], box["y"] + box["h"] / 2)], ACCENT["AnatomicLocation"][0], .14, 1.0))
    all_elem_sources = [x for values in elem_sources.values() for x in values]
    right_gutter = RIGHT + 10
    body.append(route([(min(all_elem_sources), element_trunk_y), (right_gutter, element_trunk_y)], ACCENT["DataElement"][0], .14, 1.2))
    for i, eid in enumerate(element_ids):
        box = element_pos[eid]; gx = right_gutter - i * 8
        body.append(route([(gx, element_trunk_y), (gx, box["y"] + 24), (box["x"] + box["w"], box["y"] + 24)], ACCENT["DataElement"][0], .14, 1.0))

    # Vocabulary scope and binding guides derive from final definition/lower geometry.
    guide_y1, guide_y2 = lower_top - 44, lower_top - 28
    for nid, source in class_boxes.items():
        sx = source["x"] + source["w"] / 2
        for scope, _ in cards.scope(nid)[0]:
            if scope in anatomy_pos:
                target = anatomy_pos[scope]; tx = target["x"] + target["w"] / 2
                body.append(route([(sx, source["y"] + source["h"]), (sx, guide_y1), (tx, guide_y1), (tx, target["y"])], ACCENT["AnatomicLocation"][0], .14, 1.0, "4 3"))
        for edge in graph.out_edges(nid):
            if edge["edge"] == "HAS_ELEMENT" and edge["to"] in element_pos:
                target = element_pos[edge["to"]]
                body.append(route([(sx, source["y"] + source["h"]), (sx, guide_y2), (target["x"], guide_y2), (target["x"], target["y"] + 18)], ACCENT["DataElement"][0], .12, 1.0, "4 3"))

    lower_bottom = max(anatomy_y + anatomy_height, elements_y + element_height)
    foot_y, height = lower_bottom + 48, lower_bottom + 82
    body.append(txt(48, foot_y, "Solid pointers: report observations → definitions. Dashed guides: vocabulary scope and element bindings.", FS_XS, MUTED))
    body.append(txt(48, foot_y + FS_XS + 7, "The sided location satisfies the unsided scope by SUBTYPE_OF; observation relationships do not point to definition relationships.", FS_XS, MUTED))
    defs = ('<defs><marker id="arrow-purple" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L8,4 L0,8 Z" fill="#7c3aed"/></marker>'
            '<marker id="arrow-red" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L8,4 L0,8 Z" fill="#dc2626"/></marker></defs>')
    aria = "A radiology report shown as observations pointing into vocabulary definitions"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height:.0f}" font-family="{FONT}" role="img" aria-label="{esc(aria)}">'
            f'<rect width="{W}" height="{height:.0f}" fill="#ffffff"/>' + defs + "".join(body) + "</svg>\n")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: render_report.py REPORT.jsonl")
    graph = load_graph(); cards = Cards(graph)
    report, observations, relations = read_report(sys.argv[1])
    validate(report, observations, relations, graph, cards)
    sys.stdout.write(render(report, observations, relations, graph, cards))


if __name__ == "__main__":
    main()
