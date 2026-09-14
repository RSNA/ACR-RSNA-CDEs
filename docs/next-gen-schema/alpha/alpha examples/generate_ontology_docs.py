#!/usr/bin/env python3
"""Generate the human-readable alpha example documentation from definition-graph.json.

Outputs:
  - findingclass_relationships_scope_and_diagnosis.md
  - diagnosis_relationships_and_scope.md
  - dataelement_concepts.md

The Markdown presentation intentionally mirrors the original alpha examples while
using the canonical definition graph as the source of truth.
"""
from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
GRAPH = ROOT / "graph" / "definition-graph.json"
ANATOMY = ROOT / "scripts" / "anatomy.json"

SCOPE_HEADINGS = {
    "region": "SCOPED_TO_REGION",
    "specific": "SCOPED_TO_SPECIFIC",
    "class": "SCOPED_TO_CLASS",
}

DIAGNOSIS_RELATIONS = {
    "MAY_MANIFEST_AS": "mayManifestAs",
    "MAY_CAUSE": "mayCause",
    "MAY_PROGRESS_TO": "mayProgressTo",
}

REFINEMENT_HEADING = "AVAILABLE_LOCATION_REFINEMENTS (example of the mechanism, not a comprehensive or confirmed set)"


def load():
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    anatomy = json.loads(ANATOMY.read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in graph["nodes"]}
    outgoing = defaultdict(list)
    incoming = defaultdict(list)
    for edge in graph["edges"]:
        outgoing[edge["from"]].append(edge)
        incoming[edge["to"]].append(edge)
    return graph, anatomy, nodes, outgoing, incoming


def name(nodes, node_id):
    return nodes.get(node_id, {}).get("name") or node_id


def anatomy_name(anatomy, nodes, node_id):
    """Resolve an anatomy concept without materializing native RadLex into the CDE graph."""
    canonical_name = nodes.get(node_id, {}).get("name")
    if canonical_name:
        return canonical_name
    return anatomy.get("classes", {}).get(node_id, {}).get("label") or node_id


def display_name(nodes, node_id):
    node = nodes.get(node_id, {})
    if node.get("node") in {"Modality", "Subspecialty"} and node.get("definition"):
        return node["definition"]
    return node.get("name") or node_id


def edge_targets(outgoing, node_id, edge_name):
    return [e["to"] for e in outgoing.get(node_id, []) if e["edge"] == edge_name]


def direct_scope_edges(outgoing, node_id):
    return [e for e in outgoing.get(node_id, []) if e["edge"] == "SCOPED_TO"]


def scope_heading(edge):
    return SCOPE_HEADINGS.get(edge.get("props", {}).get("kind"), "SCOPED_TO")


def parent_ids(outgoing, node_id):
    return edge_targets(outgoing, node_id, "SUBTYPE_OF")


def resolved_scopes(nodes, outgoing, node_id):
    direct = direct_scope_edges(outgoing, node_id)
    if direct:
        return [(scope_heading(e), e["to"], None) for e in direct]

    visited = {node_id}
    q = deque((parent, 1) for parent in parent_ids(outgoing, node_id))
    nearest = None
    found = []
    while q:
        ancestor, depth = q.popleft()
        if ancestor in visited:
            continue
        visited.add(ancestor)
        if nearest is not None and depth > nearest:
            break
        scopes = direct_scope_edges(outgoing, ancestor)
        if scopes:
            nearest = depth
            found.extend((scope_heading(e), e["to"], ancestor) for e in scopes)
            continue
        for parent in parent_ids(outgoing, ancestor):
            q.append((parent, depth + 1))

    result = []
    seen = set()
    for item in found:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def descendants(anatomy, root, include_root=False):
    children = defaultdict(list)
    for edge in anatomy.get("taxonomy", []):
        children[edge["to"]].append(edge["from"])
    found = {root} if include_root else set()
    q = deque(children.get(root, []))
    seen = {root}
    while q:
        current = q.popleft()
        if current in seen:
            continue
        seen.add(current)
        found.add(current)
        q.extend(children.get(current, []))
    return found


def direct_refinement_rule_ids(outgoing, finding_id):
    return edge_targets(outgoing, finding_id, "HAS_ANATOMIC_REFINEMENT_RULE")


def inherited_refinement_rule(nodes, outgoing, finding_id):
    direct = direct_refinement_rule_ids(outgoing, finding_id)
    if direct:
        return direct, None
    visited = {finding_id}
    q = deque(parent_ids(outgoing, finding_id))
    while q:
        ancestor = q.popleft()
        if ancestor in visited:
            continue
        visited.add(ancestor)
        rules = direct_refinement_rule_ids(outgoing, ancestor)
        if rules:
            return rules, ancestor
        q.extend(parent_ids(outgoing, ancestor))
    return [], None


def refinement_targets(anatomy, nodes, outgoing, finding_id):
    rule_ids, inherited_from = inherited_refinement_rule(nodes, outgoing, finding_id)
    targets = set()
    for rule_id in rule_ids:
        rule = nodes[rule_id]
        targets.update(rule.get("allowed_targets") or [])
        constraint = rule.get("target_constraint") or {}
        root = constraint.get("root")
        if root:
            if constraint.get("include_descendants"):
                targets.update(descendants(anatomy, root, constraint.get("include_root", False)))
            elif constraint.get("include_root"):
                targets.add(root)
    return sorted(targets, key=lambda rid: anatomy_name(anatomy, nodes, rid).lower()), inherited_from


def finding_hierarchy(nodes, outgoing):
    finding_ids = {n["id"] for n in nodes.values() if n.get("node") == "FindingClass"}
    children = defaultdict(list)
    parents = {}
    for fid in finding_ids:
        candidates = [p for p in parent_ids(outgoing, fid) if p in finding_ids]
        if candidates:
            parent = sorted(candidates, key=lambda x: name(nodes, x).lower())[0]
            parents[fid] = parent
            children[parent].append(fid)
    for parent in children:
        children[parent].sort(key=lambda x: name(nodes, x).lower())
    top = sorted((fid for fid in finding_ids if fid not in parents), key=lambda x: name(nodes, x).lower())
    return children, parents, top


def direct_diagnosis_connections(nodes, incoming, finding_id):
    result = []
    for e in incoming.get(finding_id, []):
        source = nodes.get(e["from"], {})
        if source.get("node") == "Diagnosis" and e["edge"] in DIAGNOSIS_RELATIONS:
            result.append((e["edge"], e["from"]))
    return result


def diagnosis_connections(nodes, outgoing, incoming, finding_id):
    result = []
    visited = set()
    q = deque([(finding_id, None)])
    while q:
        current, inherited_from = q.popleft()
        if current in visited:
            continue
        visited.add(current)
        for relation, diagnosis in direct_diagnosis_connections(nodes, incoming, current):
            result.append((relation, diagnosis, inherited_from))
        for parent in parent_ids(outgoing, current):
            q.append((parent, parent))

    unique = []
    seen = set()
    for item in result:
        key = (item[0], item[1])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return sorted(unique, key=lambda x: (name(nodes, x[1]).lower(), x[0]))


def symmetric_occurs_with(outgoing, incoming, node_id):
    targets = []
    for e in outgoing.get(node_id, []):
        if e["edge"] == "OCCURS_WITH":
            targets.append(e["to"])
    for e in incoming.get(node_id, []):
        if e["edge"] == "OCCURS_WITH" and e.get("props", {}).get("symmetric"):
            targets.append(e["from"])
    return list(dict.fromkeys(targets))


def element_name_from_constraint(nodes, raw):
    if not raw:
        return None
    text = raw
    if text.startswith("has") and len(text) > 3:
        text = text[3:]
    text = re.sub(r"(?<!^)(?=[A-Z])", " ", text).strip().lower()
    for node in nodes.values():
        if node.get("node") == "DataElement" and node.get("name", "").lower() == text:
            return node["name"]
    return text


def quote_lines(lines):
    return [("> " + line) if line else ">" for line in lines]


def emit_finding(nodes, anatomy, outgoing, incoming, children, fid, level=2):
    lines = [f"{'#' * level} {name(nodes, fid)}", ""]

    connections = diagnosis_connections(nodes, outgoing, incoming, fid)
    if connections:
        lines += ["#### DIAGNOSIS_CONNECTIONS", ""]
        for relation, diagnosis, inherited_from in connections:
            suffix = f" (inherited via {name(nodes, inherited_from)})" if inherited_from else ""
            lines.append(f"- **{name(nodes, diagnosis)}** via `{DIAGNOSIS_RELATIONS[relation]}`{suffix}")
        lines.append("")

    for heading, anatomy_id, source in resolved_scopes(nodes, outgoing, fid):
        suffix = f" (inferred from {name(nodes, source)})" if source else ""
        lines += [f"**{heading}:** {name(nodes, anatomy_id)}{suffix}", ""]

    refinements, refinement_source = refinement_targets(anatomy, nodes, outgoing, fid)
    if refinements:
        lines += [f"#### {REFINEMENT_HEADING}", ""]
        for rid in refinements:
            lines.append(f"- **{anatomy_name(anatomy, nodes, rid)}**")
        lines.append("")

    for edge_name, heading in (("HAS_COMPONENT", "HAS_COMPONENT"), ("COMPONENT_OF", "COMPONENT_OF"), ("ASSESSED_BY", "ASSESSED_BY")):
        targets = edge_targets(outgoing, fid, edge_name)
        if targets:
            lines += [f"#### {heading}", ""]
            for target in sorted(targets, key=lambda x: display_name(nodes, x).lower()):
                lines.append(f"- **{display_name(nodes, target)}**")
            lines.append("")

    occurs = symmetric_occurs_with(outgoing, incoming, fid)
    if occurs:
        lines += ["#### OCCURS_WITH (seen together often enough to be worth noting, but says nothing about cause or sequence)", ""]
        for target in sorted(occurs, key=lambda x: name(nodes, x).lower()):
            lines.append(f"- **{name(nodes, target)}**")
        lines.append("")

    measurements = edge_targets(outgoing, fid, "HAS_MEASUREMENT")
    if measurements:
        lines += ["#### HAS_MEASUREMENT", ""]
        for target in sorted(measurements, key=lambda x: name(nodes, x).lower()):
            lines.append(f"- **{name(nodes, target)}**")
        lines.append("")

    element_edges = [e for e in outgoing.get(fid, []) if e["edge"] == "HAS_DATA_ELEMENT"]
    if element_edges:
        lines += ["#### HAS_DATA_ELEMENT (attributes associated directly with it)", ""]
        for e in sorted(element_edges, key=lambda x: name(nodes, x["to"]).lower()):
            target = e["to"]
            narrow = e.get("props", {}).get("narrow")
            if narrow:
                permitted = ", ".join(f"**{name(nodes, vid)}**" for vid in narrow)
                note = e.get("props", {}).get("note")
                suffix = f". _{note}_" if note else ""
                lines.append(f"- **{name(nodes, target)}** — narrowed to {permitted}{suffix}")
            else:
                lines.append(f"- **{name(nodes, target)}**")
        lines.append("")

    constraints = [e for e in outgoing.get(fid, []) if e["edge"] == "HAS_VALUE_CONSTRAINT"]
    if constraints:
        lines += ["#### HAS_VALUE_CONSTRAINT", ""]
        for e in sorted(constraints, key=lambda x: name(nodes, x["to"]).lower()):
            element = element_name_from_constraint(nodes, e.get("props", {}).get("element"))
            semantics = "defining" if e.get("props", {}).get("defining") else "fixed in alpha model (non-defining)"
            if element:
                note = e.get("props", {}).get("note")
                suffix = f". _{note}_" if note else ""
                lines.append(f"- **{element} = {name(nodes, e['to'])}** ({semantics}){suffix}")
            else:
                lines.append(f"- **{name(nodes, e['to'])}** ({semantics})")
        lines.append("")

    modalities = edge_targets(outgoing, fid, "SEEN_ON")
    if modalities:
        lines += ["#### SEEN_ON (modality)", ""]
        for target in sorted(modalities, key=lambda x: display_name(nodes, x).lower()):
            lines.append(f"- **{display_name(nodes, target)}**")
        lines.append("")

    subspecialties = edge_targets(outgoing, fid, "IN_SUBSPECIALTY")
    if subspecialties:
        lines += ["#### IN_SUBSPECIALTY", ""]
        for target in sorted(subspecialties, key=lambda x: display_name(nodes, x).lower()):
            lines.append(f"- **{display_name(nodes, target)}**")
        lines.append("")

    kids = children.get(fid, [])
    if kids:
        lines += ["#### SUBTYPES", ""]
        for child in kids:
            lines.append(f"- **{name(nodes, child)}**")
        lines.append("")
        for child in kids:
            lines += ["> **Subtype**", ">"]
            lines += quote_lines(emit_finding(nodes, anatomy, outgoing, incoming, children, child, level=3))
            lines += [">"]

    return lines


def write_findings(anatomy, nodes, outgoing, incoming):
    children, _, top = finding_hierarchy(nodes, outgoing)
    lines = [
        "# FindingClass Relationships, Scope, and Diagnosis Connections",
        "",
        "FindingClass relationships extracted from the canonical `definition-graph.json`. "
        "FindingClasses are grouped by their subtype hierarchy. Diagnosis connections include relationships asserted from Diagnosis to FindingClass, with subtype inheritance identified where applicable. "
        "`OCCURS_WITH` is expanded in both directions when the relationship is marked symmetric. "
        f"`{REFINEMENT_HEADING}` is shown only when an explicit `AnatomicRefinementRule` defines permitted targets. Predicate choice, target selection, and traversal behavior remain independent. "
        "Fixed DataElement values are shown separately as `HAS_VALUE_CONSTRAINT`; defining status and any explicit modeling-status note are preserved. Narrowing notes are likewise shown when declared. Absent relationships are omitted.",
        "",
    ]
    for idx, fid in enumerate(top):
        lines += emit_finding(nodes, anatomy, outgoing, incoming, children, fid, level=2)
        if idx != len(top) - 1:
            lines += ["---", ""]
    (HERE / "findingclass_relationships_scope_and_diagnosis.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_diagnoses(nodes, outgoing):
    diagnoses = sorted((n for n in nodes.values() if n.get("node") == "Diagnosis"), key=lambda n: n["name"].lower())
    sections = [
        ("HAS_ETIOLOGY", "HAS_ETIOLOGY", False),
        ("MAY_MANIFEST_AS", "MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)", True),
        ("MAY_CAUSE", "MAY_CAUSE (FindingClass that may occur as a consequence of the diagnosis)", True),
        ("MAY_PROGRESS_TO", "MAY_PROGRESS_TO", False),
        ("ASSESSED_BY", "ASSESSED_BY", False),
    ]
    lines = [
        "# Diagnosis Relationships and Scope",
        "",
        "Diagnosis relationships extracted from the canonical `definition-graph.json`. When scope is inherited rather than directly asserted, the nearest ancestor providing that scope is identified. Absent relationships are omitted.",
        "",
    ]
    for idx, diagnosis in enumerate(diagnoses):
        did = diagnosis["id"]
        lines += [f"## {diagnosis['name']}", ""]
        for heading, anatomy_id, source in resolved_scopes(nodes, outgoing, did):
            suffix = f" (inferred from {name(nodes, source)})" if source else ""
            lines += [f"**{heading}:** {name(nodes, anatomy_id)}{suffix}", ""]
        for edge_name, heading, show_scope in sections:
            targets = edge_targets(outgoing, did, edge_name)
            if not targets:
                continue
            lines += [f"#### {heading}", ""]
            for target in sorted(targets, key=lambda x: display_name(nodes, x).lower()):
                lines.append(f"- **{display_name(nodes, target)}**")
                if show_scope:
                    for shead, anatomy_id, source in resolved_scopes(nodes, outgoing, target):
                        suffix = f" (inferred from {name(nodes, source)})" if source else ""
                        lines.append(f"  - `{shead}`: {name(nodes, anatomy_id)}{suffix}")
            lines.append("")
        elements = edge_targets(outgoing, did, "HAS_DATA_ELEMENT")
        if elements:
            lines += ["#### HAS_DATA_ELEMENT (attributes associated directly with it)", ""]
            for target in sorted(elements, key=lambda x: name(nodes, x).lower()):
                lines.append(f"- **{name(nodes, target)}**")
            lines.append("")
        constraints = [e for e in outgoing.get(did, []) if e["edge"] == "HAS_VALUE_CONSTRAINT"]
        if constraints:
            lines += ["#### HAS_VALUE_CONSTRAINT", ""]
            for e in constraints:
                element = element_name_from_constraint(nodes, e.get("props", {}).get("element"))
                semantics = "defining" if e.get("props", {}).get("defining") else "fixed in alpha model (non-defining)"
                lines.append(f"- **{element} = {name(nodes, e['to'])}** ({semantics})")
            lines.append("")
        if idx != len(diagnoses) - 1:
            lines += ["---", ""]
    (HERE / "diagnosis_relationships_and_scope.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def compact_table_cell(names):
    return "<br/>".join(f"- {n}" for n in names) if names else ""


def write_data_elements(nodes, outgoing, incoming):
    elements = sorted((n for n in nodes.values() if n.get("node") == "DataElement"), key=lambda n: n["name"].lower())
    lines = [
        "# DataElement Concepts",
        "",
        "DataElements extracted from the canonical `definition-graph.json`. DataElements are attributes that describe a FindingClass or Diagnosis. Each section shows the allowed values defined by the model and where the DataElement is used. Scope is shown if a DataElement itself is explicitly scoped in the model.",
        "",
    ]
    for idx, element in enumerate(elements):
        eid = element["id"]
        lines += [f"## {element['name']}", ""]
        for heading, anatomy_id, source in resolved_scopes(nodes, outgoing, eid):
            suffix = f" (inferred from {name(nodes, source)})" if source else ""
            lines += [f"**{heading}:** {name(nodes, anatomy_id)}{suffix}", ""]
        values = edge_targets(outgoing, eid, "HAS_VALUE")
        if values:
            lines += ["#### VALUES", ""]
            for value in sorted(values, key=lambda x: name(nodes, x).lower()):
                lines.append(f"- **{name(nodes, value)}**")
            lines.append("")
        users = defaultdict(set)
        for e in incoming.get(eid, []):
            if e["edge"] != "HAS_DATA_ELEMENT":
                continue
            source = nodes.get(e["from"], {})
            if source.get("node") in {"Diagnosis", "FindingClass"}:
                users[source["node"]].add(source["name"])
        if users:
            dx = sorted(users["Diagnosis"], key=str.lower)
            fc = sorted(users["FindingClass"], key=str.lower)
            lines += [
                "#### USED_BY", "",
                "| Diagnosis | FindingClass |",
                "| --- | --- |",
                f"| {compact_table_cell(dx)} | {compact_table_cell(fc)} |",
                "",
            ]
        if idx != len(elements) - 1:
            lines += ["---", ""]
    (HERE / "dataelement_concepts.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def validate(nodes, outgoing, incoming):
    warnings = []
    findings = [n for n in nodes.values() if n.get("node") == "FindingClass"]
    diagnoses = [n for n in nodes.values() if n.get("node") == "Diagnosis"]
    elements = [n for n in nodes.values() if n.get("node") == "DataElement"]
    if not findings:
        warnings.append("No FindingClasses detected.")
    if not diagnoses:
        warnings.append("No Diagnoses detected.")
    if not elements:
        warnings.append("No DataElements detected.")
    missing_values = [n["name"] for n in elements if not edge_targets(outgoing, n["id"], "HAS_VALUE")]
    if missing_values:
        warnings.append("DataElements with no detected VALUES: " + ", ".join(sorted(missing_values, key=str.lower)))
    return warnings, len(findings), len(diagnoses), len(elements)


def main():
    _, anatomy, nodes, outgoing, incoming = load()
    write_findings(anatomy, nodes, outgoing, incoming)
    write_diagnoses(nodes, outgoing)
    write_data_elements(nodes, outgoing, incoming)
    warnings, nf, nd, ne = validate(nodes, outgoing, incoming)
    print(f"Source: {GRAPH.relative_to(ROOT)}")
    print(f"FindingClasses: {nf}")
    print(f"Diagnoses: {nd}")
    print(f"DataElements: {ne}")
    print("Generated:")
    print("  findingclass_relationships_scope_and_diagnosis.md")
    print("  diagnosis_relationships_and_scope.md")
    print("  dataelement_concepts.md")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")


if __name__ == "__main__":
    main()
