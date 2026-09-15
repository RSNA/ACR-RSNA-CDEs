import json
import math
import os
from collections import Counter, defaultdict, deque
from pathlib import Path

from pyvis.network import Network
from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL

# ============================================================
# 1. Authoritative sources
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
GRAPH_PATH = Path(os.environ.get("RADCDE_DEFINITION_GRAPH", REPO_ROOT / "graph" / "definition-graph.json"))
OUTPUT_HTML = Path(os.environ.get("RADCDE_VISUALIZER_HTML", SCRIPT_DIR / "ontology_map.html"))
RDFS_SUBCLASS = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
RADLEX_NS = "http://www.radlex.org/RID/"

ANATOMY_INDEX_PATH = Path(os.environ.get(
    "RADCDE_ANATOMY_INDEX", REPO_ROOT / "scripts" / "anatomy.json"))
CDE_ONTOLOGY_PATH = Path(os.environ.get(
    "RADCDE_ONTOLOGY", REPO_ROOT / "radcde-alpha.ttl"))
CDE_NS = "https://radelement.org/ng/"
CDE = Namespace(CDE_NS)

print(f"Loading canonical definition graph: {GRAPH_PATH}")
with GRAPH_PATH.open("r", encoding="utf-8") as fh:
    graph_data = json.load(fh)
print(f"Loading native RadLex anatomy index: {ANATOMY_INDEX_PATH}")
with ANATOMY_INDEX_PATH.open("r", encoding="utf-8") as fh:
    anatomy_index = json.load(fh)
print(f"Loading generated CDE ontology metadata: {CDE_ONTOLOGY_PATH}")
cde_ontology = Graph().parse(CDE_ONTOLOGY_PATH, format="turtle")

def predicate_key(value):
    return "".join(ch.lower() for ch in str(value) if ch.isalnum())

def screaming_snake(local_name):
    out = []
    for i, ch in enumerate(str(local_name)):
        if ch.isupper() and i and (not str(local_name)[i - 1].isupper()):
            out.append("_")
        out.append(ch.upper())
    return "".join(out)

canonical_nodes = {str(n["id"]): n for n in graph_data.get("nodes", [])}
canonical_edges = graph_data.get("edges", [])
radlex_property_metadata = anatomy_index.get("object_properties", {})

# Inverse relationships are ontology metadata, not visualizer policy. RadLex
# inverses come from anatomy.json; CDE inverses come from owl:inverseOf in the
# generated ontology. Both maps are symmetrized because either side may carry
# the declaration in the source.
radlex_inverse = {}
for iri, meta in radlex_property_metadata.items():
    for inverse_iri in meta.get("inverseOf", []):
        radlex_inverse[str(iri)] = str(inverse_iri)
        radlex_inverse[str(inverse_iri)] = str(iri)

cde_inverse_iri = {}
for prop, inverse_prop in cde_ontology.subject_objects(OWL.inverseOf):
    if str(prop).startswith(CDE_NS) and str(inverse_prop).startswith(CDE_NS):
        cde_inverse_iri[str(prop)] = str(inverse_prop)
        cde_inverse_iri[str(inverse_prop)] = str(prop)

# Resolve graph predicate spellings (for example HAS_COMPONENT) to the formal
# CDE property IRIs without maintaining a second hand-authored relationship map.
formal_cde_properties = {
    str(s) for s in cde_ontology.subjects(RDF.type, OWL.ObjectProperty)
    if str(s).startswith(CDE_NS)
}
formal_by_key = {predicate_key(iri[len(CDE_NS):]): iri for iri in formal_cde_properties}
graph_predicates = {str(e.get("edge")) for e in canonical_edges}
graph_predicate_by_formal_iri = {}
for raw in graph_predicates:
    formal = formal_by_key.get(predicate_key(raw))
    if formal:
        graph_predicate_by_formal_iri[formal] = raw

cde_inverse_graph_predicate = {}
for formal, inverse_formal in cde_inverse_iri.items():
    raw = graph_predicate_by_formal_iri.get(formal)
    inverse_raw = graph_predicate_by_formal_iri.get(inverse_formal)
    if raw and inverse_raw:
        cde_inverse_graph_predicate[raw] = inverse_raw

# Assessment categories are still authored data. The definition graph stores
# them inside each AssessmentScheme node, while the generated OWL gives them
# first-class AssessmentCategory class IRIs linked by hasCategory restrictions.
# The visualizer joins those two generated representations instead of carrying
# a hardcoded category list.
assessment_category_records = {}
assessment_category_edges = []
for scheme_id, scheme_record in canonical_nodes.items():
    if scheme_record.get("node") != "AssessmentScheme":
        continue
    scheme_classes = list(cde_ontology.subjects(CDE.localId, Literal(scheme_id)))
    if len(scheme_classes) != 1:
        raise RuntimeError(
            f"Expected exactly one OWL AssessmentScheme class for {scheme_id}; found {len(scheme_classes)}"
        )
    scheme_class = scheme_classes[0]
    authored_categories = {str(c.get("name")): c for c in scheme_record.get("categories", [])}
    owl_categories = {}
    category_property = None
    for restriction in cde_ontology.objects(scheme_class, RDFS.subClassOf):
        if (restriction, RDF.type, OWL.Restriction) not in cde_ontology:
            continue
        prop = cde_ontology.value(restriction, OWL.onProperty)
        target = cde_ontology.value(restriction, OWL.someValuesFrom)
        if prop is None or target is None:
            continue
        target_type = cde_ontology.value(target, RDFS.subClassOf)
        if target_type != CDE.AssessmentCategory:
            continue
        label = str(cde_ontology.value(target, RDFS.label) or target)
        owl_categories[label] = str(target)
        category_property = str(prop)
    if set(authored_categories) != set(owl_categories):
        raise RuntimeError(
            f"Assessment category mismatch for {scheme_id}: "
            f"definition graph={sorted(authored_categories)}, OWL={sorted(owl_categories)}"
        )
    if authored_categories and not category_property:
        raise RuntimeError(f"No OWL assessment-category property found for {scheme_id}")
    category_edge_name = screaming_snake(category_property.rsplit("/", 1)[-1]) if category_property else ""
    for category_name, category in authored_categories.items():
        category_iri = owl_categories[category_name]
        category_id = category_iri
        assessment_category_records[category_id] = {
            "node": "AssessmentCategory",
            "id": category_id,
            "iri": category_iri,
            "name": category_name,
            "rank": category.get("rank"),
            "bindings": category.get("bindings", []),
            "assessment_scheme": scheme_id,
        }
        assessment_category_edges.append({
            "edge": category_edge_name,
            "from": scheme_id,
            "to": category_id,
            "props": {"source": "generated CDE ontology"},
        })

# Enforce the canonical anatomy-reference contract at the visualization boundary.
invalid_anatomy_ids = [
    nid for nid, n in canonical_nodes.items()
    if n.get("node") == "AnatomicLocation" and not nid.startswith("RID")
]
forbidden_proxy_edges = {
    "IS_A", "PART_OF", "CONTAINED_IN", "GENERAL_PART_OF",
    "REGIONAL_PART_OF", "CONSTITUTIONAL_PART_OF"
}
invalid_proxy_edges = sorted({
    str(e.get("edge")) for e in canonical_edges
    if str(e.get("edge")) in forbidden_proxy_edges
})
if invalid_anatomy_ids or invalid_proxy_edges:
    raise RuntimeError(
        "Definition graph violates the visualizer anatomy contract. "
        f"Non-RID anatomy IDs: {invalid_anatomy_ids[:5]}; "
        f"proxy anatomy edges: {invalid_proxy_edges}."
    )

# ============================================================
# 2. Mechanical visual projection
# ============================================================
# The canonical graph contains only CDE-authored content plus explicitly
# referenced native RadLex RIDs. Display context is joined from the native
# anatomy index: taxonomy ancestry plus one exact native relationship hop around
# directly referenced anatomy. No local anatomy concepts or replacement
# predicates are created here.

canonical_anatomy_ids = {
    nid for nid, n in canonical_nodes.items() if n.get("node") == "AnatomicLocation"
}
seed_anatomy = set(canonical_anatomy_ids)

branch_classes = anatomy_index.get("classes", {})
all_taxonomy = anatomy_index.get("taxonomy", [])
all_relationships = anatomy_index.get("relationships", [])

# Reconstruct the native RID3 anatomy branch from the index so display context
# cannot spill into other RadLex branches.
children = defaultdict(list)
for e in all_taxonomy:
    if str(e.get("predicate")) == RDFS_SUBCLASS:
        children[str(e["to"])].append(str(e["from"]))
anatomy_branch = {"RID3"}
queue = deque(["RID3"])
while queue:
    parent = queue.popleft()
    for child in children.get(parent, []):
        if child not in anatomy_branch:
            anatomy_branch.add(child)
            queue.append(child)

native_taxonomy = [e for e in all_taxonomy
                   if str(e["from"]) in anatomy_branch and str(e["to"]) in anatomy_branch]
native_relationships = [e for e in all_relationships
                        if str(e["from"]) in anatomy_branch and str(e["to"]) in anatomy_branch]

parents = defaultdict(list)
for e in native_taxonomy:
    parents[str(e["from"])].append(str(e["to"]))

def add_taxonomy_ancestry(start_ids, selected):
    queue = deque(start_ids)
    while queue:
        child = queue.popleft()
        for parent in parents.get(child, []):
            if parent not in selected:
                selected.add(parent)
                queue.append(parent)

selected_anatomy = set(seed_anatomy)
add_taxonomy_ancestry(seed_anatomy, selected_anatomy)

relationship_neighbors = set()
for e in native_relationships:
    s, t = str(e["from"]), str(e["to"])
    if s in seed_anatomy or t in seed_anatomy:
        relationship_neighbors.update((s, t))
selected_anatomy.update(relationship_neighbors)
add_taxonomy_ancestry(relationship_neighbors, selected_anatomy)

def anatomy_record(rid):
    if rid in canonical_nodes:
        return canonical_nodes[rid]
    nd = branch_classes[rid]
    return {
        "node": "AnatomicLocation",
        "id": rid,
        "iri": nd.get("iri") or (RADLEX_NS + rid),
        "name": nd.get("label") or rid,
        "definition": nd.get("definition"),
        "source": "RADLEX",
    }

all_nodes = dict(canonical_nodes)
all_nodes.update(assessment_category_records)
for rid in selected_anatomy:
    if rid in branch_classes:
        all_nodes[rid] = anatomy_record(rid)

all_edges = list(canonical_edges) + assessment_category_edges
for e in native_taxonomy:
    s, t = str(e["from"]), str(e["to"])
    if s in selected_anatomy and t in selected_anatomy:
        all_edges.append({
            "edge": str(e["predicate"]), "from": s, "to": t,
            "props": {"source": "RADLEX", "source_form": e.get("source_form")}
        })
for e in native_relationships:
    s, t = str(e["from"]), str(e["to"])
    if s in selected_anatomy and t in selected_anatomy:
        all_edges.append({
            "edge": str(e["predicate"]), "from": s, "to": t,
            "props": {"source": "RADLEX", "forms": e.get("forms", [])}
        })

visible_nodes = all_nodes
visible_edges = all_edges

print(
    f"Canonical definition graph: {len(canonical_nodes):,} nodes / {len(canonical_edges):,} edges\n"
    f"Visualizer projection: {len(visible_nodes):,} nodes / {len(visible_edges):,} edges "
    f"({len(selected_anatomy):,} native RadLex anatomy nodes after joining display context; "
    f"{len(assessment_category_records):,} assessment categories joined from generated model data)"
)

# ============================================================
# 3. PyVis canvas and styles
# ============================================================

net = Network(
    height="calc(100vh - 60px)", width="100%", bgcolor="#1a1a1a",
    font_color="white", select_menu=False, cdn_resources="in_line", directed=True
)
net.set_options(r'''{
  "interaction": {"hover": true, "hoverConnectedEdges": false, "navigationButtons": true,
    "keyboard": true, "multiselect": true, "selectConnectedEdges": false,
    "zoomView": true, "zoomSpeed": 0.7},
  "nodes": {"chosen": false, "scaling": {"min": 10, "max": 60,
    "label": {"enabled": true, "min": 10, "max": 28, "maxVisible": 40, "drawThreshold": 0}}},
  "physics": {"enabled": true, "solver": "forceAtlas2Based",
    "stabilization": {"enabled": true, "iterations": 1200, "updateInterval": 50, "fit": true},
    "forceAtlas2Based": {"gravitationalConstant": -65, "centralGravity": 0.003,
      "springLength": 160, "springConstant": 0.035, "damping": 0.5, "avoidOverlap": 1.0}},
  "edges": {"smooth": false, "chosen": false,
    "font": {"color": "#E6E6E6", "strokeWidth": 3, "strokeColor": "#1a1a1a", "size": 12, "align": "middle"},
    "scaling": {"min": 1, "max": 8, "label": {"enabled": true, "min": 10, "max": 24, "maxVisible": 40, "drawThreshold": 0}}}
}''')

NODE_STYLE = {
    "FindingClass": {"color": "#2563EB", "size": 30, "shape": "dot"},
    "Diagnosis": {"color": "#DC2626", "size": 30, "shape": "dot"},
    "DataElement": {"color": "#16A34A", "size": 23, "shape": "dot"},
    "Measurement": {"color": "#7C3AED", "size": 25, "shape": "dot"},
    "Value": {"color": "#CA8A04", "size": 17, "shape": "square"},
    "AssessmentCategory": {"color": "#C2410C", "size": 18, "shape": "square"},
    "AnatomicLocation": {"color": "#0891B2", "size": 22, "shape": "triangle"},
    "AnatomicRefinementRule": {"color": "#6D28D9", "size": 21, "shape": "hexagon"},
    "AssessmentScheme": {"color": "#0F766E", "size": 23, "shape": "diamond"},
    "Modality": {"color": "#EA580C", "size": 19, "shape": "diamond"},
    "Etiology": {"color": "#DB2777", "size": 19, "shape": "diamond"},
    "Subspecialty": {"color": "#475569", "size": 19, "shape": "diamond"},
    "Terminology": {"color": "#64748B", "size": 18, "shape": "dot"},
    "generic": {"color": "#78716C", "size": 18, "shape": "dot"},
}

EDGE_STYLES = {
    "OCCURS_WITH": {"color": "#3498DB", "width": 2.4, "dashes": False},
    "SUBTYPE_OF": {"color": "#95A5A6", "width": 1.5, "dashes": False},
    "HAS_DATA_ELEMENT": {"color": "#2ECC71", "width": 2.5, "dashes": False},
    "HAS_VALUE_CONSTRAINT": {"color": "#F39C12", "width": 2.3, "dashes": False},
    "HAS_VALUE": {"color": "#F1C40F", "width": 1.5, "dashes": True},
    "HAS_CATEGORY": {"color": "#D97706", "width": 1.8, "dashes": False},
    "HAS_MEASUREMENT": {"color": "#9B59B6", "width": 2.5, "dashes": False},
    "SCOPED_TO": {"color": "#E67E22", "width": 2.2, "dashes": True},
    "REFINEMENT_RULE": {"color": "#8B5CF6", "width": 2.0, "dashes": True},
    "HAS_COMPONENT": {"color": "#3498DB", "width": 2.5, "dashes": False},
    "DIAGNOSIS_RELATION": {"color": "#E74C3C", "width": 2.2, "dashes": False},
    "RADLEX_RELATION": {"color": "#7F8C8D", "width": 1.5, "dashes": True},
    "RADLEX_TAXONOMY": {"color": "#95A5A6", "width": 1.3, "dashes": False},
    "GENERIC": {"color": "#BDC3C7", "width": 1.5, "dashes": False},
}

def edge_label(raw):
    raw = str(raw)
    if raw == RDFS_SUBCLASS:
        return "rdfs:subClassOf"
    if raw.startswith(RADLEX_NS):
        return raw[len(RADLEX_NS):]
    return raw.rsplit("/", 1)[-1].rsplit("#", 1)[-1]

def edge_category(raw):
    raw = str(raw)
    if raw == RDFS_SUBCLASS:
        return "RADLEX_TAXONOMY"
    if raw.startswith(RADLEX_NS):
        return "RADLEX_RELATION"
    if raw in {"SCOPED_TO", "SCOPED_TO_CLASS", "SCOPED_TO_REGION", "SCOPED_TO_SPECIFIC"}:
        return "SCOPED_TO"
    if raw in {"HAS_ANATOMIC_REFINEMENT_RULE", "REFINES_SCOPE", "TARGET_TAXONOMY_ROOT", "ALLOWED_ANATOMIC_TARGET"}:
        return "REFINEMENT_RULE"
    if raw == "HAS_CATEGORY":
        return "HAS_CATEGORY"
    if raw in {"HAS_COMPONENT", "COMPONENT_OF"}:
        return "HAS_COMPONENT"
    if raw in {"HAS_MEASUREMENT", "HAS_MEASUREMENT_COMPONENT", "DERIVED_FROM_MEASUREMENT"}:
        return "HAS_MEASUREMENT"
    if raw in {"MAY_MANIFEST_AS", "MAY_CAUSE", "MAY_BE_CAUSED_BY", "CAUSES_FINDING", "MAY_PROGRESS_TO", "MAY_BE_RELATED_TO"}:
        return "DIAGNOSIS_RELATION"
    return raw if raw in EDGE_STYLES else "GENERIC"

# Add nodes directly from the canonical graph. AnatomicLocation is a role;
# its identifier remains the native RID.
for nid, record in visible_nodes.items():
    node_type = str(record.get("node") or "generic")
    style = NODE_STYLE.get(node_type, NODE_STYLE["generic"])
    label = str(record.get("name") or nid)
    definition = str(record.get("definition") or "Not provided").strip()
    title = f"{label}\nType: {node_type}\nDefinition: {definition}"
    if node_type == "AssessmentCategory":
        scheme_id = str(record.get("assessment_scheme") or "")
        scheme_name = str(all_nodes.get(scheme_id, {}).get("name") or scheme_id)
        rank = record.get("rank")
        bindings = []
        for b in record.get("bindings", []):
            code = b.get("code")
            system = b.get("system")
            if code and system:
                bindings.append(f"{system}: {code}")
        title = (f"{label}\nType: AssessmentCategory\nAssessment scheme: {scheme_name}"
                 f"\nRank: {rank if rank is not None else 'Not specified'}"
                 f"\nBindings: {', '.join(bindings) if bindings else 'None'}")
    if node_type == "AnatomicRefinementRule":
        scope = str(record.get("scope") or "")
        scope_name = str(all_nodes.get(scope, {}).get("name") or scope or "None")
        exact = [str(all_nodes.get(r, {}).get("name") or r) + f" ({r})"
                 for r in record.get("allowed_targets", [])]
        tc = record.get("target_constraint")
        if tc:
            root = str(tc.get("root") or "")
            root_name = str(all_nodes.get(root, {}).get("name") or root)
            taxonomy_text = (f"{root_name} ({root}); include root={bool(tc.get('include_root'))}; "
                             f"include descendants={bool(tc.get('include_descendants'))}")
        else:
            taxonomy_text = "None"
        predicates = []
        for iri in record.get("allowed_predicates", []):
            meta = radlex_property_metadata.get(iri, {})
            predicates.append(f"{meta.get('label') or meta.get('name') or edge_label(iri)} ({iri})")
        traversal = record.get("traversal")
        title = (f"{label}\nType: {node_type}\nRefines scope: {scope_name} ({scope})"
                 f"\nExact targets: {', '.join(exact) if exact else 'None'}"
                 f"\nTaxonomy target set: {taxonomy_text}"
                 f"\nAllowed RadLex predicates: {', '.join(predicates) if predicates else 'None'}"
                 f"\nTraversal: {traversal if traversal is not None else 'Not specified'}")
    net.add_node(
        nid, label=label, title=title, ontologyType=node_type, shortId=nid,
        nativeIri=str(record.get("iri") or (RADLEX_NS + nid if node_type == "AnatomicLocation" else "")),
        color=style["color"], size=style["size"], shape=style["shape"], borderWidth=1.5
    )

added_edges = set()
for e in visible_edges:
    s, t, raw = str(e["from"]), str(e["to"]), str(e["edge"])
    label = edge_label(raw)
    key = (s, t, raw)
    if key in added_edges:
        continue
    cat = edge_category(raw)
    style = EDGE_STYLES.get(cat, EDGE_STYLES["GENERIC"])
    vocabulary = "RADLEX" if (raw == RDFS_SUBCLASS or raw.startswith(RADLEX_NS)) else "CDE"
    if raw.startswith(RADLEX_NS):
        meta = radlex_property_metadata.get(raw, {})
        p_label = meta.get("label") or meta.get("name") or label
        title = f"{p_label}\nVocabulary: RadLex\nPredicate: {raw}"
    elif raw == RDFS_SUBCLASS:
        title = f"rdfs:subClassOf\nVocabulary: RadLex taxonomy"
    else:
        props = e.get("props") or {}
        display_label = label
        title_lines = [label, "Vocabulary: CDE model"]
        narrow_values = []
        if raw == "HAS_DATA_ELEMENT" and props.get("narrow"):
            narrow_values = [str(v) for v in props.get("narrow", [])]
            narrow_names = [str(all_nodes.get(v, {}).get("name") or v) for v in narrow_values]
            display_label = f"{label} (narrowed)"
            title_lines.append("Narrowed to: " + ", ".join(narrow_names))
        if raw == "HAS_VALUE_CONSTRAINT":
            defining = props.get("defining")
            if defining is not None:
                title_lines.append("Defining: " + ("true" if defining else "false"))
            element = props.get("element")
            if element:
                title_lines.append("DataElement property: " + str(element))
            note = props.get("note")
            if note:
                title_lines.append("Note: " + str(note))
        title = "\n".join(title_lines)
        label = display_label
    inverse_predicate = None
    if raw.startswith(RADLEX_NS):
        inverse_predicate = radlex_inverse.get(raw)
    else:
        inverse_predicate = cde_inverse_graph_predicate.get(raw)
    edge_kwargs = dict(
        title=title, label=label, arrows="to", color=style["color"],
        width=style["width"], dashes=style["dashes"], semanticCategory=cat,
        vocabulary=vocabulary, nativePredicate=raw,
        inversePredicate=inverse_predicate or ""
    )
    if not (raw == RDFS_SUBCLASS or raw.startswith(RADLEX_NS)):
        props = e.get("props") or {}
        if raw == "HAS_DATA_ELEMENT" and props.get("narrow"):
            edge_kwargs["narrowValues"] = [str(v) for v in props.get("narrow", [])]
        if raw == "HAS_VALUE_CONSTRAINT":
            edge_kwargs["constraintDefining"] = props.get("defining")
            edge_kwargs["constraintNote"] = str(props.get("note") or "")
            edge_kwargs["constraintElement"] = str(props.get("element") or "")
    net.add_edge(s, t, **edge_kwargs)
    added_edges.add(key)

# ============================================================
# 5. Degree-aware spacing
# ============================================================

degree = Counter()
for edge in net.edges:
    degree[edge["from"]] += 1
    degree[edge["to"]] += 1

LAYOUT_ROLE_WEIGHT = {
    "DataElement": 1.45, "Measurement": 1.35, "AnatomicLocation": 1.30,
    "AnatomicRefinementRule": 1.25,
    "FindingClass": 1.20, "Diagnosis": 1.20, "AssessmentScheme": 1.15,
    "Modality": 1.05, "Etiology": 1.05, "Subspecialty": 1.05,
    "Terminology": 0.95, "Value": 0.60, "generic": 1.00,
}
visible_node_type = {str(n["id"]): str(n.get("ontologyType") or "generic") for n in net.nodes}
def weighted_degree(node_id):
    return degree[node_id] * LAYOUT_ROLE_WEIGHT.get(visible_node_type.get(node_id, "generic"), 1.0)
for edge in net.edges:
    edge["length"] = int(145 + 48 * math.log2(1 + max(weighted_degree(edge["from"]), weighted_degree(edge["to"]))))
for node in net.nodes:
    node["mass"] = min(8.0, 1.0 + 0.75 * math.log2(1 + weighted_degree(node["id"])))

# Pattern nodes are retained if the canonical graph eventually emits them;
# no pattern semantics are reconstructed independently here.
pattern_nodes_added = set()
print(f"Rendering {len(visible_nodes):,} base nodes and {len(added_edges):,} base edges...")
print("Added 0 independently reconstructed pattern groups.")
net.save_graph(str(OUTPUT_HTML))
output_html = str(OUTPUT_HTML)


# ============================================================
# 15. JavaScript interaction layer
# ============================================================
#
# Behavior:
#
# 1. Physics arranges the graph on initial load.
# 2. Physics turns completely off after stabilization.
# 3. Nodes remain freely draggable.
# 4. Dragged nodes stay where they are placed.
# 5. Straight edges remain attached to their endpoints.
# 6. Physics can be re-enabled manually when desired.
#

CUSTOM_HTML = r"""
<style>
html,
body {
    width: 100%;
    height: 100%;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden;
}

#mynetwork {
    width: 100% !important;
    height: calc(100vh - 59px) !important;
    margin: 0 !important;
}

#ontology-toolbar {
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    gap: 8px;
    width: 100%;
    box-sizing: border-box;
    height: 59px;
    padding: 10px 16px;
    background: #f8f9fa;
    border-bottom: 1px solid #d7dce1;
    font-family: Arial, sans-serif;
}

#ontology-search-wrap {
    position: relative;
    flex: 1 1 auto;
    width: min(58vw, 900px);
    min-width: 520px;
    max-width: 900px;
}

#ontology-search {
    width: 100%;
    height: 38px;
    box-sizing: border-box;
    padding: 0 12px;
    font-size: 14px;
    border: 1px solid #ced4da;
    border-radius: 4px;
}

#ontology-search-results {
    display: none;
    position: absolute;
    left: 0;
    right: 0;
    top: calc(100% + 3px);
    z-index: 3000;
    max-height: 320px;
    overflow-y: auto;
    background: #fff;
    border: 1px solid #ced4da;
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0,0,0,.16);
}

#ontology-search-results.open { display: block; }

.ontology-search-result {
    display: block;
    width: 100%;
    padding: 9px 12px;
    border: 0;
    border-bottom: 1px solid #eef1f4;
    background: #fff;
    color: #212529;
    text-align: left;
    cursor: pointer;
}

.ontology-search-result:hover, .ontology-search-result.active { background: #eef5ff; }
.ontology-search-empty { padding: 10px 12px; color: #6c757d; }

#ontology-controls {
    position: static;
    display: inline-flex;
    align-items: center;
    flex: 0 0 auto;
    gap: 6px;
    margin: 0;
    padding: 0;
    background: transparent;
    border: 0;
    font-family: Arial, sans-serif;
    white-space: nowrap;
}

#ontology-controls button,
.ontology-reset-selection {
    box-sizing: border-box;
    height: 38px;
    padding: 0 12px !important;
    margin: 0 !important;
    font-size: 14px !important;
    line-height: 36px !important;
    font-weight: 400 !important;
    border-radius: 4px !important;
    cursor: pointer;
    white-space: nowrap;
    vertical-align: middle;
}

/* Keep Reset Selection visually primary, like the native PyVis control. */
.ontology-reset-selection {
    color: #fff !important;
    background: #0d6efd !important;
    border: 1px solid #0d6efd !important;
}

.ontology-reset-selection:hover {
    background: #0b5ed7 !important;
    border-color: #0a58ca !important;
}

/* Secondary graph controls remain neutral rather than all using the same blue. */
#ontology-controls button {
    color: #212529;
    background: #f8f9fa;
    border: 1px solid #ced4da;
}

#ontology-controls button:hover {
    background: #e9ecef;
    border-color: #adb5bd;
}

#ontology-type-filter button {
    background: #333;
    color: white;
    border: 1px solid #666;
    border-radius: 4px;
    padding: 5px 7px;
    margin: 0;
    cursor: pointer;
}

#ontology-type-filter button:hover {
    background: #555;
}

#ontology-type-filter {
    position: absolute;
    right: 15px;
    bottom: 15px;
    z-index: 1000;
    background: rgba(30, 30, 30, 0.94);
    border: 1px solid #555;
    border-radius: 6px;
    padding: 8px;
    width: 350px;
    max-width: calc(100vw - 30px);
    font-family: Arial, sans-serif;
}

#ontology-type-filter-title {
    color: #ddd;
    font-size: 12px;
    font-weight: bold;
    margin: 2px 2px 6px 2px;
}

#ontology-type-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}

#ontology-type-buttons button {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    padding: 5px 7px;
    margin: 0;
}

#ontology-type-buttons button.active {
    border-color: white;
    box-shadow: 0 0 0 1px white inset;
    background: #555;
}

.ontology-type-symbol {
    display: inline-block;
    width: 10px;
    height: 10px;
    flex: 0 0 auto;
}

.ontology-type-symbol.shape-dot {
    border-radius: 50%;
}

.ontology-type-symbol.shape-square {
    border-radius: 0;
}

.ontology-type-symbol.shape-diamond {
    clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%);
}

.ontology-type-symbol.shape-triangle {
    clip-path: polygon(50% 0, 100% 100%, 0 100%);
}
</style>

<div id="ontology-toolbar">
    <div id="ontology-search-wrap">
        <input id="ontology-search" type="text" autocomplete="off" placeholder="Search nodes by name or ID" aria-label="Search nodes by name or ID">
        <div id="ontology-search-results" role="listbox"></div>
    </div>
    <button id="resetSelection" class="ontology-reset-selection">Reset Selection</button>
    <div id="ontology-controls">
        <button id="fitGraph">Fit graph</button>
        <button id="physicsToggle">Enable physics</button>
        <button id="resetFocus">Reset focus</button>
    </div>
</div>

<div id="ontology-type-filter">
    <div id="ontology-type-filter-title">Highlight node type</div>
    <div id="ontology-type-buttons"></div>
</div>

<script type="text/javascript">
(function () {

    function initializeOntologyControls() {

        if (typeof network === "undefined") {
            setTimeout(initializeOntologyControls, 100);
            return;
        }

        var nodeDataSet = network.body.data.nodes;
        var edgeDataSet = network.body.data.edges;

        // PyVis preserves arbitrary edge metadata in current releases, but the
        // rendered label must not depend on that implementation detail alone.
        // Re-apply narrowed DataElement presentation from either the serialized
        // narrowValues field or the canonical tooltip text after the DataSet is live.
        var narrowedEdgeUpdates = [];
        edgeDataSet.get().forEach(function (edge) {
            var narrowValues =
                Array.isArray(edge.narrowValues)
                    ? edge.narrowValues.map(String)
                    : [];

            if (
                String(edge.nativePredicate || "").toUpperCase() ===
                    "HAS_DATA_ELEMENT" &&
                (
                    narrowValues.length ||
                    String(edge.title || "").indexOf("Narrowed to:") !== -1
                )
            ) {
                narrowedEdgeUpdates.push({
                    id: edge.id,
                    label: "HAS_DATA_ELEMENT (narrowed)",
                    narrowValues: narrowValues,
                    isNarrowedDataElement: true
                });
            }
        });
        if (narrowedEdgeUpdates.length) {
            edgeDataSet.update(narrowedEdgeUpdates);
        }

        var searchInput =
            document.getElementById("ontology-search");
        var searchResults =
            document.getElementById("ontology-search-results");
        var resetSelectionButton =
            document.getElementById("resetSelection");
        var fitGraphButton =
            document.getElementById("fitGraph");
        var physicsButton =
            document.getElementById("physicsToggle");
        var resetFocusButton =
            document.getElementById("resetFocus");

        if (
            !searchInput ||
            !searchResults ||
            !resetSelectionButton ||
            !fitGraphButton ||
            !physicsButton ||
            !resetFocusButton
        ) {
            console.error(
                "Ontology toolbar controls were not found in the DOM."
            );
            return;
        }

        var physicsEnabled = true;
        var initialStabilizationPending = true;

        // Shared interaction state. These must be declared before any
        // legend/search/click handler can read them.
        var focusedNodeId = null;
        var focusedNodeType = null;


        var originalNodeOpacity = {};
        var originalNodeHidden = {};
        var originalEdgeColor = {};
        var originalEdgeHidden = {};

        nodeDataSet.get().forEach(function (node) {
            originalNodeOpacity[node.id] =
                node.opacity !== undefined
                    ? node.opacity
                    : 1;

            originalNodeHidden[node.id] =
                node.hidden === true;
        });

        edgeDataSet.get().forEach(function (edge) {
            originalEdgeColor[edge.id] = edge.color;

            originalEdgeHidden[edge.id] =
                edge.hidden === true;
        });


        function nodeTypeOf(nodeId) {
            var node = nodeDataSet.get(nodeId);

            if (!node) {
                return "generic";
            }

            if (node.ontologyType) {
                return String(node.ontologyType).trim();
            }

            return "generic";
        }


        function buildEdgeIndex() {
            var byNode = {};

            nodeDataSet.getIds().forEach(function (nodeId) {
                byNode[nodeId] = [];
            });

            edgeDataSet.get().forEach(function (edge) {
                if (!byNode[edge.from]) {
                    byNode[edge.from] = [];
                }

                if (!byNode[edge.to]) {
                    byNode[edge.to] = [];
                }

                byNode[edge.from].push(edge);
                byNode[edge.to].push(edge);
            });

            return byNode;
        }


        function otherEnd(edge, nodeId) {
            return edge.from === nodeId
                ? edge.to
                : edge.from;
        }


        function normalizedLabel(edge) {
            return String(edge.nativePredicate || edge.label || edge.title || "")
                .trim()
                .toUpperCase();
        }


        function semanticCategoryOf(edge) {
            return String(edge.semanticCategory || "")
                .trim()
                .toUpperCase();
        }


        function makeFocusResult() {
            return {
                nodes: {},
                edges: {}
            };
        }


        function includeNode(result, nodeId) {
            if (nodeId !== undefined && nodeId !== null) {
                result.nodes[nodeId] = true;
            }
        }


        function includeEdge(result, edge) {
            if (!edge) {
                return;
            }

            result.edges[edge.id] = true;
            includeNode(result, edge.from);
            includeNode(result, edge.to);
        }


        function predicateOf(edge) {
            return String(edge.nativePredicate || edge.label || "").trim();
        }


        function inversePredicateOf(edge) {
            return String(edge.inversePredicate || "").trim();
        }


        function collapseReciprocalInversesForSelection(
            result,
            selectedNodeId
        ) {
            // Prefer the relationship authored in the direction that leaves the
            // selected node. Suppress only an exact reciprocal edge whose
            // predicate is formally declared as the inverse. No inverse is
            // guessed and no missing edge is synthesized.
            var relevantEdges = Object.keys(result.edges)
                .map(function (edgeId) {
                    return edgeDataSet.get(edgeId);
                })
                .filter(function (edge) {
                    return !!edge;
                });

            var outbound = {};

            relevantEdges.forEach(function (edge) {
                if (edge.from !== selectedNodeId) {
                    return;
                }

                var key = [
                    String(edge.to),
                    predicateOf(edge)
                ].join("||");

                outbound[key] = true;
            });

            relevantEdges.forEach(function (edge) {
                if (edge.to !== selectedNodeId) {
                    return;
                }

                var inverse = inversePredicateOf(edge);

                if (!inverse) {
                    return;
                }

                var reciprocalKey = [
                    String(edge.from),
                    inverse
                ].join("||");

                if (outbound[reciprocalKey]) {
                    delete result.edges[edge.id];
                }
            });

            return result;
        }


        function isDataElementValueEdge(edge, dataElementId) {
            var neighbor = otherEnd(edge, dataElementId);

            return (
                nodeTypeOf(neighbor) === "Value" &&
                normalizedLabel(edge) === "HAS_VALUE"
            );
        }


        function isHostDataElementEdge(edge, hostId) {
            var neighbor = otherEnd(edge, hostId);
            var hostType = nodeTypeOf(hostId);

            return (
                (
                    hostType === "FindingClass" ||
                    hostType === "Diagnosis"
                ) &&
                nodeTypeOf(neighbor) === "DataElement" &&
                normalizedLabel(edge) === "HAS_DATA_ELEMENT"
            );
        }


        // ----------------------------------------------------
        // Node-type legend / filter
        // ----------------------------------------------------
        //
        // Selecting a node type highlights:
        //   1. every node of that ontology type,
        //   2. every edge incident to one of those nodes,
        //   3. the immediate nodes reached by those edges.
        //
        // Connected nodes are kept as context but are visually secondary.
        // The filter does not recursively expand through those neighbors.
        //

        function colorValue(node) {
            if (!node || !node.color) {
                return "#7F8C8D";
            }

            if (typeof node.color === "string") {
                return node.color;
            }

            if (node.color.background) {
                return node.color.background;
            }

            return "#7F8C8D";
        }


        function clearTypeButtonState() {
            var buttons =
                document.querySelectorAll(
                    "#ontology-type-buttons button"
                );

            buttons.forEach(function (button) {
                button.classList.remove("active");
            });
        }


        function applyTypeFocus(selectedType) {
            var primaryNodes = {};
            var contextNodes = {};
            var relevantEdges = {};

            nodeDataSet.get().forEach(function (node) {
                if (
                    node.isPatternNode !== true &&
                    nodeTypeOf(node.id) === selectedType
                ) {
                    primaryNodes[node.id] = true;
                }
            });

            if (Object.keys(primaryNodes).length === 0) {
                return;
            }

            focusedNodeId = null;
            focusedNodeType = selectedType;

            edgeDataSet.get().forEach(function (edge) {
                // Pattern relationships are UI-only context and should
                // not appear in ontology-type filtering.
                if (edge.isPatternEdge === true) {
                    return;
                }

                if (
                    primaryNodes[edge.from] ||
                    primaryNodes[edge.to]
                ) {
                    relevantEdges[edge.id] = true;

                    if (!primaryNodes[edge.from]) {
                        contextNodes[edge.from] = true;
                    }

                    if (!primaryNodes[edge.to]) {
                        contextNodes[edge.to] = true;
                    }
                }
            });

            var nodeUpdates = [];
            var edgeUpdates = [];

            nodeDataSet.get().forEach(function (node) {
                var isPrimary = !!primaryNodes[node.id];
                var isContext = !!contextNodes[node.id];
                var isPattern = node.isPatternNode === true;

                nodeUpdates.push({
                    id: node.id,
                    hidden:
                        isPattern
                            ? true
                            : false,
                    opacity:
                        isPrimary
                            ? 1
                            : (
                                isContext
                                    ? 0.32
                                    : 0.025
                            )
                });
            });

            edgeDataSet.get().forEach(function (edge) {
                var isRelevant =
                    !!relevantEdges[edge.id];

                edgeUpdates.push({
                    id: edge.id,
                    hidden: !isRelevant,
                    color:
                        edgeColorAtOpacity(
                            edge.id,
                            1
                        )
                });
            });

            nodeDataSet.update(nodeUpdates);
            edgeDataSet.update(edgeUpdates);

            clearTypeButtonState();

            var activeButton =
                document.querySelector(
                    '#ontology-type-buttons button[data-node-type="' +
                    selectedType.replace(/"/g, '\\"') +
                    '"]'
                );

            if (activeButton) {
                activeButton.classList.add("active");
            }
        }


        function buildTypeFilterButtons() {
            var container =
                document.getElementById(
                    "ontology-type-buttons"
                );

            if (!container) {
                return;
            }

            var typeInfo = {};

            nodeDataSet.get().forEach(function (node) {
                var type = nodeTypeOf(node.id);

                if (
                    node.isPatternNode === true ||
                    type === "Pattern" ||
                    type.toLowerCase() === "generic"
                ) {
                    return;
                }

                if (!typeInfo[type]) {
                    typeInfo[type] = {
                        color: colorValue(node),
                        shape: node.shape || "dot",
                        count: 0
                    };
                }

                typeInfo[type].count += 1;
            });

            Object.keys(typeInfo)
                .sort()
                .forEach(function (type) {
                    var info = typeInfo[type];
                    var button =
                        document.createElement(
                            "button"
                        );

                    button.type = "button";
                    button.dataset.nodeType = type;
                    button.title =
                        "Highlight all " +
                        type +
                        " nodes and their direct relationships";

                    var symbol =
                        document.createElement(
                            "span"
                        );
                    symbol.className =
                        "ontology-type-symbol shape-" +
                        info.shape;
                    symbol.style.backgroundColor =
                        info.color;

                    var label =
                        document.createElement(
                            "span"
                        );
                    label.textContent =
                        type +
                        " (" +
                        info.count +
                        ")";

                    button.appendChild(symbol);
                    button.appendChild(label);

                    button.addEventListener(
                        "click",
                        function () {
                            if (focusedNodeType === type) {
                                resetFocus();
                            } else {
                                applyTypeFocus(type);
                            }
                        }
                    );

                    container.appendChild(button);
                });
        }


        function semanticNeighborhood(startNodeId) {
            var edgeIndex = buildEdgeIndex();
            var result = makeFocusResult();
            var startType = nodeTypeOf(startNodeId);

            includeNode(result, startNodeId);


            // ------------------------------------------------
            // DataElement
            // ------------------------------------------------
            //
            // Show ONLY:
            //   DataElement -> Value
            //   FindingClass -> DataElement
            //   Diagnosis -> DataElement
            //   DataElement -> direct scope / AnatomicLocation
            //
            // Do not expose relationships beyond those direct endpoints.
            //
            if (startType === "DataElement") {

                (edgeIndex[startNodeId] || []).forEach(
                    function (edge) {
                        var neighbor =
                            otherEnd(edge, startNodeId);

                        var neighborType =
                            nodeTypeOf(neighbor);

                        if (
                            neighborType === "Value" &&
                            normalizedLabel(edge) ===
                                "HAS_VALUE"
                        ) {
                            includeEdge(result, edge);
                            return;
                        }

                        if (
                            (
                                neighborType === "FindingClass" ||
                                neighborType === "Diagnosis"
                            ) &&
                            normalizedLabel(edge) ===
                                "HAS_DATA_ELEMENT"
                        ) {
                            includeEdge(result, edge);
                            return;
                        }

                        var edgeLabel =
                            normalizedLabel(edge);

                        if (
                            edgeLabel === "SCOPED_TO" ||
                            edgeLabel === "SCOPED_TO_CLASS" ||
                            edgeLabel === "SCOPED_TO_REGION" ||
                            edgeLabel === "SCOPED_TO_SPECIFIC"
                        ) {
                            includeEdge(result, edge);
                            return;
                        }
                    }
                );

                return result;
            }


            // ------------------------------------------------
            // Value
            // ------------------------------------------------
            //
            // Show:
            //   selected Value <-> associated DataElement
            //   that DataElement -> sibling Values
            //   FindingClasses -> that DataElement
            //   Diagnoses -> that DataElement
            //
            // Critically, do not show any other edges belonging to the
            // sibling Values, host nodes, or DataElement.
            //
            if (startType === "Value") {

                var associatedDataElements = [];

                (edgeIndex[startNodeId] || []).forEach(
                    function (edge) {
                        var neighbor =
                            otherEnd(edge, startNodeId);

                        if (
                            nodeTypeOf(neighbor) ===
                                "DataElement" &&
                            normalizedLabel(edge) ===
                                "HAS_VALUE"
                        ) {
                            includeEdge(result, edge);
                            associatedDataElements.push(
                                neighbor
                            );
                            return;
                        }

                        if (
                            (
                                nodeTypeOf(neighbor) ===
                                    "FindingClass" ||
                                nodeTypeOf(neighbor) ===
                                    "Diagnosis"
                            ) &&
                            normalizedLabel(edge) ===
                                "HAS_VALUE_CONSTRAINT"
                        ) {
                            includeEdge(result, edge);
                        }
                    }
                );

                associatedDataElements.forEach(
                    function (dataElementId) {

                        (edgeIndex[dataElementId] || [])
                            .forEach(function (edge) {

                                var neighbor =
                                    otherEnd(
                                        edge,
                                        dataElementId
                                    );

                                var neighborType =
                                    nodeTypeOf(neighbor);

                                if (
                                    neighborType === "Value" &&
                                    normalizedLabel(edge) ===
                                        "HAS_VALUE"
                                ) {
                                    includeEdge(
                                        result,
                                        edge
                                    );
                                    return;
                                }

                                if (
                                    (
                                        neighborType ===
                                            "FindingClass" ||
                                        neighborType ===
                                            "Diagnosis"
                                    ) &&
                                    normalizedLabel(edge) ===
                                        "HAS_DATA_ELEMENT"
                                ) {
                                    includeEdge(
                                        result,
                                        edge
                                    );
                                }
                            });
                    }
                );

                return result;
            }


            // ------------------------------------------------
            // FindingClass
            // ------------------------------------------------
            //
            // Show ONLY:
            //   Finding <-> directly related Finding
            //   Finding <-> Diagnosis
            //   Finding <-> Assessment
            //   Finding <-> AnatomicLocation
            //   Finding <-> Modality
            //   Finding <-> Subspecialty
            //   Finding -> DataElement
            //   those DataElements -> Values
                        //
            // A reused DataElement may connect to many other Findings.
            // Those other Finding edges are NOT part of this focus.
            //
            if (startType === "FindingClass") {

                var findingDataElements = [];
                var findingDataElementNarrows = {};

                (edgeIndex[startNodeId] || []).forEach(
                    function (edge) {
                        var neighbor =
                            otherEnd(edge, startNodeId);

                        var neighborType =
                            nodeTypeOf(neighbor);

                        if (
                            neighborType === "Diagnosis" ||
                            neighborType ===
                                "AssessmentScheme" ||
                            neighborType ===
                                "AssessmentCategory" ||
                            neighborType ===
                                "AnatomicLocation" ||
                            neighborType ===
                                "Modality" ||
                            neighborType ===
                                "Subspecialty" ||
                            neighborType ===
                                "FindingClass"
                        ) {
                            includeEdge(result, edge);
                            return;
                        }

                        if (
                            neighborType === "DataElement" &&
                            normalizedLabel(edge) ===
                                "HAS_DATA_ELEMENT"
                        ) {
                            includeEdge(result, edge);

                            findingDataElements.push(
                                neighbor
                            );
                            var narrowValues =
                                Array.isArray(edge.narrowValues)
                                    ? edge.narrowValues.map(String)
                                    : [];

                            if (!narrowValues.length) {
                                var titleText = String(edge.title || "");
                                var narrowLine = titleText
                                    .split("\n")
                                    .filter(function (line) {
                                        return line.indexOf("Narrowed to:") === 0;
                                    })[0];
                                if (narrowLine) {
                                    var names = narrowLine
                                        .replace("Narrowed to:", "")
                                        .split(",")
                                        .map(function (name) { return name.trim(); });
                                    nodeDataSet.get().forEach(function (candidate) {
                                        if (
                                            nodeTypeOf(candidate.id) === "Value" &&
                                            names.indexOf(String(candidate.label || "").trim()) !== -1
                                        ) {
                                            narrowValues.push(String(candidate.id));
                                        }
                                    });
                                }
                            }

                            if (narrowValues.length) {
                                findingDataElementNarrows[neighbor] = {};
                                narrowValues.forEach(function (valueId) {
                                    findingDataElementNarrows[neighbor][String(valueId)] = true;
                                });
                            }
                            return;
                        }

                        if (
                            neighborType === "Value" &&
                            normalizedLabel(edge) ===
                                "HAS_VALUE_CONSTRAINT"
                        ) {
                            includeEdge(result, edge);
                            return;
                        }

                    }
                );

                findingDataElements.forEach(
                    function (dataElementId) {

                        (edgeIndex[dataElementId] || [])
                            .forEach(function (edge) {

                                if (
                                    isDataElementValueEdge(
                                        edge,
                                        dataElementId
                                    )
                                ) {
                                    var allowed =
                                        findingDataElementNarrows[dataElementId];
                                    var valueId =
                                        otherEnd(edge, dataElementId);

                                    if (
                                        !allowed ||
                                        allowed[String(valueId)]
                                    ) {
                                        includeEdge(
                                            result,
                                            edge
                                        );
                                    }
                                }
                            });
                    }
                );

                // ----------------------------------------
                // Assessment categories
                // ----------------------------------------
                //
                // If the Finding is connected to an AssessmentScheme,
                // also show that scheme's possible AssessmentCategory
                // values. This mirrors DataElement -> Value expansion:
                //
                //   Finding -> AssessmentScheme -> AssessmentCategory
                //
                // Do NOT expand the categories into anything else.
                //
                var findingAssessmentSchemes = {};

                (edgeIndex[startNodeId] || []).forEach(
                    function (edge) {
                        var neighbor =
                            otherEnd(edge, startNodeId);

                        if (
                            nodeTypeOf(neighbor) ===
                            "AssessmentScheme"
                        ) {
                            findingAssessmentSchemes[
                                neighbor
                            ] = true;
                        }
                    }
                );

                Object.keys(
                    findingAssessmentSchemes
                ).forEach(function (schemeId) {
                    (edgeIndex[schemeId] || []).forEach(
                        function (edge) {
                            var neighbor =
                                otherEnd(edge, schemeId);

                            if (
                                nodeTypeOf(neighbor) ===
                                "AssessmentCategory"
                            ) {
                                includeEdge(
                                    result,
                                    edge
                                );
                            }
                        }
                    );
                });


                // ----------------------------------------
                // Reusable modeling patterns
                // ----------------------------------------
                //
                // Pattern nodes/edges are hidden in the normal graph.
                // When a Finding is selected:
                //
                //   selected Finding -> Pattern
                //   peer Finding     -> same Pattern
                //
                // Peer Findings are context only. Their DataElements,
                // Values, Diagnoses, etc. are NOT expanded.
                //
                var selectedPatternIds = {};

                (edgeIndex[startNodeId] || []).forEach(
                    function (edge) {
                        if (
                            edge.isPatternEdge === true
                        ) {
                            var patternNodeId =
                                otherEnd(
                                    edge,
                                    startNodeId
                                );

                            selectedPatternIds[
                                patternNodeId
                            ] = true;

                            includeEdge(
                                result,
                                edge
                            );
                        }
                    }
                );

                Object.keys(
                    selectedPatternIds
                ).forEach(function (patternNodeId) {

                    (edgeIndex[patternNodeId] || [])
                        .forEach(function (edge) {

                            if (
                                edge.isPatternEdge !== true
                            ) {
                                return;
                            }

                            var peerFindingId =
                                otherEnd(
                                    edge,
                                    patternNodeId
                                );

                            if (
                                nodeTypeOf(
                                    peerFindingId
                                ) === "FindingClass"
                            ) {
                                includeEdge(
                                    result,
                                    edge
                                );
                            }
                        });
                });

                return result;
            }


            // ------------------------------------------------
            // Diagnosis
            // ------------------------------------------------
            //
            // Show the Diagnosis semantic neighborhood:
            //   Diagnosis <-> associated Diagnosis
            //   Diagnosis <-> associated Finding
            //   Diagnosis <-> associated Assessment
            //   Diagnosis <-> associated Modality
            //   Diagnosis <-> associated Subspecialty
            //   Diagnosis -> directly attached DataElement
            //   those direct DataElements -> Values
                        //
            // Do not expand DataElements belonging to associated Findings.
            // Only DataElements directly connected to this Diagnosis are
            // included.
            //
            if (startType === "Diagnosis") {

                var diagnosisDataElements = [];

                (edgeIndex[startNodeId] || []).forEach(
                    function (edge) {
                        var neighbor =
                            otherEnd(edge, startNodeId);

                        var neighborType =
                            nodeTypeOf(neighbor);

                        if (
                            neighborType === "Diagnosis" ||
                            neighborType === "FindingClass" ||
                            neighborType ===
                                "AssessmentScheme" ||
                            neighborType ===
                                "AssessmentCategory" ||
                            neighborType ===
                                "Modality" ||
                            neighborType ===
                                "Subspecialty"
                        ) {
                            includeEdge(result, edge);
                            return;
                        }

                        if (
                            neighborType === "DataElement" &&
                            normalizedLabel(edge) ===
                                "HAS_DATA_ELEMENT"
                        ) {
                            includeEdge(result, edge);
                            diagnosisDataElements.push(
                                neighbor
                            );
                            return;
                        }

                        if (
                            neighborType === "Value" &&
                            normalizedLabel(edge) ===
                                "HAS_VALUE_CONSTRAINT"
                        ) {
                            includeEdge(result, edge);
                            return;
                        }

                        var edgeLabel =
                            normalizedLabel(edge);

                        if (
                            edgeLabel === "SCOPED_TO" ||
                            edgeLabel === "SCOPED_TO_CLASS" ||
                            edgeLabel === "SCOPED_TO_REGION" ||
                            edgeLabel === "SCOPED_TO_SPECIFIC"
                        ) {
                            includeEdge(result, edge);
                            return;
                        }

                    }
                );

                // Expand only DataElements that are directly attached
                // to the selected Diagnosis. Their allowed Values are
                // shown, but no other hosts of those reused DataElements
                // are pulled into this Diagnosis-focused view.
                diagnosisDataElements.forEach(
                    function (dataElementId) {
                        (edgeIndex[dataElementId] || [])
                            .forEach(function (edge) {
                                if (
                                    isDataElementValueEdge(
                                        edge,
                                        dataElementId
                                    )
                                ) {
                                    includeEdge(
                                        result,
                                        edge
                                    );
                                }
                            });
                    }
                );

                // If the Diagnosis is directly connected to an
                // AssessmentScheme, also show that scheme's possible
                // AssessmentCategory values. Do not expand further.
                var diagnosisAssessmentSchemes = {};

                (edgeIndex[startNodeId] || []).forEach(
                    function (edge) {
                        var neighbor =
                            otherEnd(edge, startNodeId);

                        if (
                            nodeTypeOf(neighbor) ===
                            "AssessmentScheme"
                        ) {
                            diagnosisAssessmentSchemes[
                                neighbor
                            ] = true;
                        }
                    }
                );

                Object.keys(
                    diagnosisAssessmentSchemes
                ).forEach(function (schemeId) {
                    (edgeIndex[schemeId] || []).forEach(
                        function (edge) {
                            var neighbor =
                                otherEnd(edge, schemeId);

                            if (
                                nodeTypeOf(neighbor) ===
                                "AssessmentCategory"
                            ) {
                                includeEdge(
                                    result,
                                    edge
                                );
                            }
                        }
                    );
                });

                return result;
            }


            // ------------------------------------------------
            // Measurement
            // ------------------------------------------------
            //
            // A Measurement is reusable. Show every direct semantic
            // relationship attached to the selected Measurement, including
            // all FindingClass and Diagnosis hosts that use it and any
            // Measurement-to-Measurement component/derivation relationships.
            //
            if (startType === "Measurement") {

                (edgeIndex[startNodeId] || []).forEach(
                    function (edge) {
                        includeEdge(result, edge);
                    }
                );

                return result;
            }


            // ------------------------------------------------
            // AssessmentScheme / AssessmentCategory
            // ------------------------------------------------
            //
            // Show the assessment's direct semantic neighborhood:
            //   AssessmentScheme <-> AssessmentCategory
            //   Assessment <-> Finding
            //   Assessment <-> Diagnosis
            //
            // Do not expand connected Findings into DataElements,
            // Values, anatomy, or any other relationships.
            //
            if (
                startType === "AssessmentScheme" ||
                startType === "AssessmentCategory"
            ) {

                (edgeIndex[startNodeId] || []).forEach(
                    function (edge) {
                        var neighbor =
                            otherEnd(edge, startNodeId);

                        var neighborType =
                            nodeTypeOf(neighbor);

                        if (
                            neighborType === "FindingClass" ||
                            neighborType === "Diagnosis" ||
                            neighborType === "AssessmentScheme" ||
                            neighborType === "AssessmentCategory"
                        ) {
                            includeEdge(result, edge);
                        }
                    }
                );

                return result;
            }


            // ------------------------------------------------
            // Fallback for other node types
            // ------------------------------------------------
            //
            // No generic focus-depth control is used anymore.
            // For node types without a dedicated semantic rule, show
            // only the node's direct relationships. This keeps focus
            // behavior local and predictable without reintroducing a
            // generic multi-hop traversal.
            //
            (edgeIndex[startNodeId] || []).forEach(
                function (edge) {
                    includeEdge(result, edge);
                }
            );

            return result;
        }


        function edgeColorAtOpacity(edgeId, opacity) {
            var original = originalEdgeColor[edgeId];

            if (typeof original === "string") {
                return {
                    color: original,
                    opacity: opacity
                };
            }

            if (original && original.color) {
                return {
                    color: original.color,
                    highlight:
                        original.highlight || original.color,
                    hover:
                        original.hover || original.color,
                    inherit:
                        original.inherit !== undefined
                            ? original.inherit
                            : false,
                    opacity: opacity
                };
            }

            return {
                color: "#A0A0A0",
                opacity: opacity
            };
        }


        function resetFocus() {
            focusedNodeId = null;
            focusedNodeType = null;
            clearTypeButtonState();

            var nodeUpdates = [];
            var edgeUpdates = [];

            nodeDataSet.get().forEach(function (node) {
                nodeUpdates.push({
                    id: node.id,
                    hidden:
                        originalNodeHidden[node.id],
                    opacity:
                        originalNodeOpacity[node.id]
                });
            });

            edgeDataSet.get().forEach(function (edge) {
                edgeUpdates.push({
                    id: edge.id,
                    hidden:
                        originalEdgeHidden[edge.id],
                    color:
                        originalEdgeColor[edge.id]
                });
            });

            nodeDataSet.update(nodeUpdates);
            edgeDataSet.update(edgeUpdates);
        }


        function restoreDirectMeasurementsForHost(
            startNodeId
        ) {
            var selectedType =
                nodeTypeOf(startNodeId);

            if (
                selectedType !== "FindingClass" &&
                selectedType !== "Diagnosis"
            ) {
                return;
            }

            var connectedEdgeIds =
                network.getConnectedEdges(
                    startNodeId
                );

            var measurementEdgeUpdates = [];
            var measurementNodeUpdates = [];
            var restoredNodeIds = {};

            connectedEdgeIds.forEach(
                function (edgeId) {
                    var edge =
                        edgeDataSet.get(edgeId);

                    if (!edge) {
                        return;
                    }

                    var edgeCategory =
                        semanticCategoryOf(edge);

                    var edgeLabel =
                        normalizedLabel(edge);

                    if (
                        edgeCategory !==
                            "HAS_MEASUREMENT" &&
                        edgeLabel !==
                            "HAS_MEASUREMENT"
                    ) {
                        return;
                    }

                    measurementEdgeUpdates.push({
                        id: edge.id,
                        hidden: false,
                        color:
                            edgeColorAtOpacity(
                                edge.id,
                                1
                            )
                    });

                    var endpointIds = [
                        edge.from,
                        edge.to
                    ];

                    endpointIds.forEach(
                        function (nodeId) {
                            if (
                                restoredNodeIds[nodeId]
                            ) {
                                return;
                            }

                            restoredNodeIds[nodeId] =
                                true;

                            measurementNodeUpdates.push({
                                id: nodeId,
                                hidden: false,
                                opacity: 1
                            });
                        }
                    );
                }
            );

            if (
                measurementNodeUpdates.length
            ) {
                nodeDataSet.update(
                    measurementNodeUpdates
                );
            }

            if (
                measurementEdgeUpdates.length
            ) {
                edgeDataSet.update(
                    measurementEdgeUpdates
                );
            }
        }


        function applyFocus(startNodeId) {
            focusedNodeId = startNodeId;
            focusedNodeType = null;
            clearTypeButtonState();

            var focus =
                semanticNeighborhood(
                    startNodeId
                );

            collapseReciprocalInversesForSelection(
                focus,
                startNodeId
            );

            var nodeUpdates = [];
            var edgeUpdates = [];

            nodeDataSet.get().forEach(function (node) {
                var isRelevant =
                    !!focus.nodes[node.id];

                var isPattern =
                    node.isPatternNode === true;

                nodeUpdates.push({
                    id: node.id,

                    // Pattern nodes exist only during a Finding focus
                    // that explicitly includes them.
                    hidden:
                        isPattern
                            ? !isRelevant
                            : false,

                    opacity:
                        isRelevant
                            ? 1
                            : 0.025
                });
            });

            edgeDataSet.get().forEach(function (edge) {
                var isRelevant =
                    !!focus.edges[edge.id];

                edgeUpdates.push({
                    id: edge.id,

                    // Strict semantic focus:
                    // an edge is either part of the selected rule or
                    // it is not rendered at all.
                    hidden:
                        !isRelevant,

                    color:
                        edgeColorAtOpacity(
                            edge.id,
                            1
                        )
                });
            });

            nodeDataSet.update(nodeUpdates);
            edgeDataSet.update(edgeUpdates);

            // FindingClass/Diagnosis -> Measurement is restored only
            // after all normal focus hiding has completed. This uses
            // vis-network's actual connected-edge list for the selected
            // node, so the relationship cannot be dropped by the
            // semantic-neighborhood filtering above.
            restoreDirectMeasurementsForHost(
                startNodeId
            );

            // Hidden focus-only pattern nodes do not participate in
            // physics, so position any revealed pattern nodes near the
            // selected Finding for a readable local grouping.
            if (
                nodeTypeOf(startNodeId) ===
                "FindingClass"
            ) {
                var selectedPosition =
                    network.getPosition(
                        startNodeId
                    );

                var patternIndex = 0;

                nodeDataSet.get().forEach(
                    function (node) {
                        if (
                            node.isPatternNode === true &&
                            focus.nodes[node.id]
                        ) {
                            var xOffset =
                                180 +
                                (patternIndex % 2) * 80;

                            var yOffset =
                                -160 -
                                Math.floor(
                                    patternIndex / 2
                                ) * 110;

                            network.moveNode(
                                node.id,
                                selectedPosition.x +
                                    xOffset,
                                selectedPosition.y +
                                    yOffset
                            );

                            patternIndex += 1;
                        }
                    }
                );
            }
        }


        // ----------------------------------------------------
        // Human-facing ontology identifiers
        // ----------------------------------------------------
        //
        // Search/display IDs are a presentation layer independent of the
        // full RDF URI. Every node follows the same convention:
        //
        //     DISPLAY_ID: human-readable label
        //
        // Intrinsic coded IDs are preserved; descriptive suffixes are removed:
        //
        //     V_000142_Increased -> V_000142: increased
        //
        // Nodes without a usable intrinsic ID receive a stable type-based
        // alias:
        //
        //     MuralNodule -> DE_0001: mural nodule
        //     RID6434 -> RID6434: brain
        //
        // Pattern nodes participate in this system as P_0001, P_0002, ...
        //

        var DISPLAY_PREFIX_BY_TYPE = {
            "FindingClass": "FC",
            "Diagnosis": "DX",
            "Measurement": "M",
            "DataElement": "DE",
            "Value": "V",
            "AssessmentScheme": "AS",
            "AssessmentCategory": "AC",
            "Modality": "MOD",
            "Etiology": "ET",
            "Subspecialty": "SS",
            "Terminology": "T",
            "Pattern": "P",
            "generic": "N"
        };

        function intrinsicDisplayId(node) {
            var raw = String(node.shortId || "").trim();

            if (!raw) {
                return "";
            }

            // Keep an intrinsic identifier only when the URI local name
            // actually begins with an identifier-like code. Descriptive
            // suffixes are intentionally dropped.
            //
            // Examples:
            //   V_000142_Increased -> V_000142
            //   DE_0012_MuralNodule -> DE_0012
            //   RID6434 -> RID6434
            var match = raw.match(
                /^([A-Za-z][A-Za-z0-9]*[-_]\d+)/
            );

            if (match) {
                return match[1];
            }

            // Diagnosis is intentionally allowed to use the class-level
            // compact marker DX when no numbered code exists.
            if (
                node.ontologyType === "Diagnosis" &&
                /^DX$/i.test(raw)
            ) {
                return "DX";
            }

            return "";
        }

        var displayIdByNode = {};
        var nodesByType = {};

        nodeDataSet.get().forEach(function (node) {
            var type =
                String(
                    node.ontologyType || "generic"
                ).trim();

            if (!nodesByType[type]) {
                nodesByType[type] = [];
            }

            nodesByType[type].push(node);
        });

        Object.keys(nodesByType).forEach(function (type) {
            var nodes = nodesByType[type];

            nodes.sort(function (a, b) {
                return String(a.label || "").localeCompare(
                    String(b.label || ""),
                    undefined,
                    {
                        numeric: true,
                        sensitivity: "base"
                    }
                );
            });

            var generatedIndex = 1;

            nodes.forEach(function (node) {
                var intrinsic =
                    intrinsicDisplayId(node);

                if (intrinsic) {
                    displayIdByNode[node.id] =
                        intrinsic;
                    return;
                }

                var prefix =
                    DISPLAY_PREFIX_BY_TYPE[type] ||
                    DISPLAY_PREFIX_BY_TYPE.generic;

                // Anatomy retains its native RadLex RID. Other nodes without
                // an intrinsic code receive a presentation-only alias.
                if (type === "AnatomicLocation" && /^RID\d+$/.test(String(node.shortId || ""))) {
                    displayIdByNode[node.id] = String(node.shortId);
                    return;
                }

                displayIdByNode[node.id] =
                    prefix +
                    "_" +
                    String(generatedIndex).padStart(
                        4,
                        "0"
                    );

                generatedIndex += 1;
            });
        });

        function compactSearchId(node) {
            return (
                displayIdByNode[node.id] ||
                ""
            );
        }

        function searchDisplayText(node) {
            var label =
                String(node.label || "").trim();

            var id =
                compactSearchId(node);

            if (!id) {
                return label;
            }

            return id + ": " + label;
        }

        var searchableNodes =
            nodeDataSet.get()
                .map(function (node) {
                    var display =
                        searchDisplayText(node);

                    return {
                        id: node.id,
                        display: display,
                        searchText:
                            (
                                compactSearchId(node) +
                                " " +
                                String(node.label || "") +
                                " " +
                                display
                            ).toLowerCase()
                    };
                })
                .sort(function (a, b) {
                    return a.display.localeCompare(
                        b.display,
                        undefined,
                        {
                            numeric: true,
                            sensitivity: "base"
                        }
                    );
                });

        var currentSearchMatches = [];
        var activeSearchIndex = -1;

        function closeSearchResults() {
            searchResults.classList.remove("open");
            searchResults.innerHTML = "";
            currentSearchMatches = [];
            activeSearchIndex = -1;
        }

        function chooseSearchResult(entry) {
            if (!entry) return;
            searchInput.value = entry.display;
            closeSearchResults();
            applyFocus(entry.id);
            network.selectNodes([entry.id], false);
            setTimeout(function () {
                network.focus(entry.id, {scale:0.32, animation:{duration:600, easingFunction:"easeInOutQuad"}});
            }, 0);
        }

        function renderSearchResults(query) {
            var term = String(query || "").trim().toLowerCase();
            searchResults.innerHTML = "";
            activeSearchIndex = -1;
            if (!term) { closeSearchResults(); return; }

            currentSearchMatches = searchableNodes.filter(function (entry) {
                return entry.searchText.indexOf(term) !== -1;
            }).slice(0, 30);

            if (!currentSearchMatches.length) {
                var empty = document.createElement("div");
                empty.className = "ontology-search-empty";
                empty.textContent = "No matching nodes";
                searchResults.appendChild(empty);
                searchResults.classList.add("open");
                return;
            }

            currentSearchMatches.forEach(function (entry) {
                var button = document.createElement("button");
                button.type = "button";
                button.className = "ontology-search-result";
                button.textContent = entry.display;
                button.addEventListener("mousedown", function (event) {
                    event.preventDefault();
                    chooseSearchResult(entry);
                });
                searchResults.appendChild(button);
            });
            searchResults.classList.add("open");
        }

        searchInput.addEventListener("input", function () { renderSearchResults(this.value); });
        searchInput.addEventListener("focus", function () { if (this.value.trim()) renderSearchResults(this.value); });
        searchInput.addEventListener("keydown", function (event) {
            if (event.key === "Escape") { closeSearchResults(); return; }
            if (!currentSearchMatches.length) return;
            var buttons = searchResults.querySelectorAll(".ontology-search-result");
            if (event.key === "ArrowDown") {
                event.preventDefault();
                activeSearchIndex = Math.min(activeSearchIndex + 1, currentSearchMatches.length - 1);
            } else if (event.key === "ArrowUp") {
                event.preventDefault();
                activeSearchIndex = Math.max(activeSearchIndex - 1, 0);
            } else if (event.key === "Enter") {
                event.preventDefault();
                chooseSearchResult(currentSearchMatches[activeSearchIndex >= 0 ? activeSearchIndex : 0]);
                return;
            } else return;
            buttons.forEach(function (b, i) { b.classList.toggle("active", i === activeSearchIndex); });
        });

        document.addEventListener("mousedown", function (event) {
            var wrap = document.getElementById("ontology-search-wrap");
            if (wrap && !wrap.contains(event.target)) closeSearchResults();
        });

        resetSelectionButton.addEventListener(
            "click",
            function () {
                searchInput.value = "";
                closeSearchResults();
                network.unselectAll();
                resetFocus();
            }
        );


        // ----------------------------------------------------
        // Graph controls
        // ----------------------------------------------------

        function updatePhysicsButton() {
            physicsButton.textContent =
                physicsEnabled
                    ? "Disable physics"
                    : "Enable physics";
        }


        function setPhysicsEnabled(enabled) {
            physicsEnabled = !!enabled;

            network.setOptions({
                physics: {
                    enabled: physicsEnabled
                }
            });

            updatePhysicsButton();
        }


        function finishInitialStabilization() {
            if (!initialStabilizationPending) {
                return;
            }

            initialStabilizationPending = false;
            setPhysicsEnabled(false);
        }


        // PyVis/vis-network versions can emit either or both of these
        // stabilization events. The guard above makes the operation
        // idempotent.
        network.once(
            "stabilizationIterationsDone",
            finishInitialStabilization
        );

        network.once(
            "stabilized",
            finishInitialStabilization
        );


        physicsButton.addEventListener(
            "click",
            function () {
                // Once the user explicitly touches the physics control,
                // stabilization is no longer allowed to override their
                // choice later.
                initialStabilizationPending = false;

                setPhysicsEnabled(
                    !physicsEnabled
                );
            }
        );


        fitGraphButton.addEventListener(
            "click",
            function () {
                // Fit only currently visible nodes. This makes the button
                // behave correctly both in the full graph and while a
                // semantic focus/filter is active.
                var visibleNodeIds =
                    nodeDataSet.get()
                        .filter(function (node) {
                            return node.hidden !== true;
                        })
                        .map(function (node) {
                            return node.id;
                        });

                if (!visibleNodeIds.length) {
                    return;
                }

                network.fit({
                    nodes: visibleNodeIds,
                    animation: {
                        duration: 500,
                        easingFunction:
                            "easeInOutQuad"
                    }
                });
            }
        );


        resetFocusButton.addEventListener(
            "click",
            function () {
                resetFocus();
            }
        );


        // Match the label to the actual initial PyVis configuration.
        updatePhysicsButton();


        network.on("click", function (params) {
            if (params.nodes.length === 1) {
                var clickedNodeId =
                    params.nodes[0];

                // Pattern nodes are contextual grouping labels.
                // Clicking them does not replace the current focus.
                if (
                    nodeTypeOf(
                        clickedNodeId
                    ) === "Pattern"
                ) {
                    return;
                }

                applyFocus(
                    clickedNodeId
                );
                return;
            }

            if (
                params.nodes.length === 0 &&
                params.edges.length === 0
            ) {
                resetFocus();
            }
        });


        buildTypeFilterButtons();


        network.on(
            "doubleClick",
            function (params) {
                if (params.nodes.length !== 1) {
                    return;
                }

                var nodeId = params.nodes[0];

                applyFocus(nodeId);

                network.focus(
                    nodeId,
                    {
                        scale: 0.32,
                        animation: {
                            duration: 450,
                            easingFunction:
                                "easeInOutQuad"
                        }
                    }
                );
            }
        );


    }

    initializeOntologyControls();

})();
</script>
</body>
"""


with open(output_html, "r", encoding="utf-8") as f:
    content = f.read()

# ------------------------------------------------------------
# Insert the custom UI into the actual PyVis layout.
#
# Do NOT append the complete block at </body>. The toolbar belongs
# directly above the graph; only its JavaScript should be appended
# after PyVis initializes the network.
#
# Split the custom block into:
#   1. CSS -> <head>
#   2. toolbar/filter markup -> immediately before #mynetwork
#   3. JavaScript -> end of <body>
# ------------------------------------------------------------

style_start = CUSTOM_HTML.find("<style>")
style_end = CUSTOM_HTML.find("</style>") + len("</style>")

script_start = CUSTOM_HTML.find('<script type="text/javascript">')
script_end = CUSTOM_HTML.find("</script>", script_start) + len("</script>")

if (
    style_start == -1 or
    style_end == -1 or
    script_start == -1 or
    script_end == -1
):
    raise RuntimeError("Could not split custom ontology UI block.")

custom_style = CUSTOM_HTML[style_start:style_end]
custom_markup = CUSTOM_HTML[style_end:script_start].strip()
custom_script = CUSTOM_HTML[script_start:script_end]

# Put styles in the document head.
if "</head>" not in content:
    raise RuntimeError("Generated PyVis HTML has no </head> tag.")

content = content.replace(
    "</head>",
    custom_style + "\n</head>",
    1
)

# Put the search bar and buttons directly above the graph.
network_marker = '<div id="mynetwork"'

if network_marker not in content:
    raise RuntimeError(
        "Generated PyVis HTML does not contain #mynetwork."
    )

content = content.replace(
    network_marker,
    custom_markup + "\n" + network_marker,
    1
)

# Initialize controls only after PyVis has created `network`.
if "</body>" not in content:
    raise RuntimeError("Generated PyVis HTML has no </body> tag.")

content = content.replace(
    "</body>",
    custom_script + "\n</body>",
    1
)

with open(output_html, "w", encoding="utf-8") as f:
    f.write(content)


print(f"\nSuccess: {output_html}")
print("Physics will turn off after the initial layout.")
print("Value-domain wrapper classes are hidden.")
print("Instance-level owl:NamedIndividual resources are hidden.")
print("Dense, highly reused concepts receive degree-aware spacing.")
print("DataElements connect directly to their allowed values.")
print("AssessmentScheme categories are joined from generated graph/OWL model data.")
print("Reciprocal inverse edges collapse toward the selected node using ontology inverse metadata.")

