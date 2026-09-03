#!/usr/bin/env python3
"""Load, merge, validate, and normalize the canonical graph (docs/next-gen-schema/graph/*.jsonl).

Canonical form, per 03 §6.2: one JSON object per line; nodes before edges; nodes sorted
by id; edges sorted by (edge, from, to, id); keys sorted; compact separators; UTF-8.

Usage:
  graph.py check            validate every graph file and report normalization drift
  graph.py normalize        rewrite every graph file in canonical form
  graph.py dump             print the merged graph (graph files + converted specs) as JSONL

As a library: load_graph() returns a Graph with .nodes (id -> dict) and .edges (list of dicts).
"""
import json, os, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)                       # docs/next-gen-schema
GRAPH_DIR = os.path.join(BASE, "graph")
EXAMPLES_DIR = os.path.join(BASE, "examples")

NODE_TYPES = {"FindingClass", "Diagnosis", "Grouping", "DataElement", "Value",
              "AnatomicLocation", "Concept", "RelationshipType"}
EXTERNAL_EDGES = {"exactMatch", "closeMatch"}      # targets are SYSTEM:code strings, not nodes
BINDING_TARGET_EDGES = {"INTERPRETED_FROM"}        # targets may be a reified HAS_ELEMENT edge id


def dumps(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sort_key(obj):
    if "node" in obj:
        return (0, obj["id"], "", "", "")
    return (1, obj["edge"], obj["from"], obj["to"], obj.get("id", ""))


def canonical_text(objs):
    return "".join(dumps(o) + "\n" for o in sorted(objs, key=sort_key))


def read_jsonl(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}:{n}: bad JSON: {e}")
    return out


def graph_files():
    return sorted(glob.glob(os.path.join(GRAPH_DIR, "*.jsonl")))


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.origin = {}          # node id -> file the node was defined in

    def add_node(self, node, origin, prio=1):
        nid = node["id"]
        if nid in self.nodes:
            old, oldp = self.nodes[nid], self.origin[nid][1]
            if prio > oldp:
                merged = dict(old); merged.update({k: v for k, v in node.items() if v not in (None, "", [])})
                self.nodes[nid] = merged; self.origin[nid] = (origin, prio)
            else:
                for k, v in node.items():
                    if k not in old or old[k] in (None, "", []):
                        old[k] = v
        else:
            self.nodes[nid] = dict(node); self.origin[nid] = (origin, prio)

    def add_edge(self, edge):
        self.edges.append(dict(edge))

    def objects(self):
        return list(self.nodes.values()) + self.edges

    # ---- indexes
    def out_edges(self, nid):
        return [e for e in self.edges if e["from"] == nid]

    def in_edges(self, nid):
        return [e for e in self.edges if e["to"] == nid]

    def edge_by_id(self, eid):
        for e in self.edges:
            if e.get("id") == eid:
                return e
        return None

    def by_type(self, t):
        return sorted((n for n in self.nodes.values() if n["node"] == t), key=lambda n: n["id"])


def load_graph(include_specs=True):
    g = Graph()
    for path in graph_files():
        rel = os.path.relpath(path, BASE)
        for obj in read_jsonl(path):
            if "node" in obj:
                g.add_node(obj, rel, prio=2)
            else:
                g.add_edge(obj)
    if include_specs:
        sys.path.insert(0, HERE)
        from spec_to_graph import convert_all
        for obj, origin in convert_all(EXAMPLES_DIR):
            if "node" in obj:
                g.add_node(obj, origin, prio=1)
            else:
                g.add_edge(obj)
    # dedupe identical edges (a spec and a graph file may both state a binding)
    seen, uniq = set(), []
    for e in g.edges:
        k = dumps(e)
        if k not in seen:
            seen.add(k); uniq.append(e)
    g.edges = uniq
    return g


def validate(g):
    errs = []
    reltypes = {n["id"] for n in g.nodes.values() if n["node"] == "RelationshipType"}
    edge_ids = {e["id"] for e in g.edges if e.get("id")}
    for nid, n in g.nodes.items():
        if n["node"] not in NODE_TYPES:
            errs.append(f"node {nid}: unknown node type {n['node']!r}")
        if not n.get("name"):
            errs.append(f"node {nid}: no name")
        if nid in edge_ids:
            errs.append(f"id {nid} is used by both a node and an edge")
    for e in g.edges:
        t = e["edge"]
        if t not in reltypes:
            errs.append(f"edge {t} {e['from']}->{e['to']}: relationship type not declared")
        if e["from"] not in g.nodes:
            errs.append(f"edge {t}: source {e['from']} is not a node")
        if t in EXTERNAL_EDGES:
            if ":" not in e["to"]:
                errs.append(f"edge {t} from {e['from']}: target {e['to']} should be SYSTEM:code")
        elif t in BINDING_TARGET_EDGES:
            if e["to"] not in g.nodes and e["to"] not in edge_ids:
                errs.append(f"edge {t} from {e['from']}: target {e['to']} is neither a node nor a binding id")
        elif e["to"] not in g.nodes:
            errs.append(f"edge {t} from {e['from']}: target {e['to']} is not a node")
    # reified ids unique
    seen = {}
    for e in g.edges:
        if e.get("id"):
            if e["id"] in seen:
                errs.append(f"edge id {e['id']} used twice")
            seen[e["id"]] = e
    return errs


def check_normalized():
    drift = []
    for path in graph_files():
        objs = read_jsonl(path)
        if open(path, encoding="utf-8").read() != canonical_text(objs):
            drift.append(os.path.relpath(path, BASE))
    return drift


def normalize_files():
    for path in graph_files():
        objs = read_jsonl(path)
        with open(path, "w", encoding="utf-8") as f:
            f.write(canonical_text(objs))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "normalize":
        normalize_files(); print("normalized", len(graph_files()), "files")
    elif cmd == "dump":
        g = load_graph(); sys.stdout.write(canonical_text(g.objects()))
    else:
        g = load_graph()
        errs = validate(g)
        drift = check_normalized()
        for d in drift: print(f"NOT CANONICAL: graph/{os.path.basename(d)} (run graph.py normalize)")
        for e in errs: print("ERROR:", e)
        print(f"{len(g.nodes)} nodes, {len(g.edges)} edges, {len(errs)} errors, {len(drift)} files not canonical")
        sys.exit(1 if errs or drift else 0)
