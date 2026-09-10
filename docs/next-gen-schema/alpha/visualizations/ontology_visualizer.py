from rdflib import Graph, RDF, RDFS, OWL, Namespace, BNode, URIRef
from pyvis.network import Network
from collections import Counter
import math
import os
import re

# ============================================================
# 1. Load ontology
# ============================================================

file_path = ("alpha-turtle.ttl")
output_html = "ontology_map.html"

g = Graph()

print("Parsing ontology...")
g.parse(file_path, format="turtle")

CDE = Namespace("https://radelement.org/ng/")
g.bind("cde", CDE)

print(f"Loaded {len(g):,} triples")


# ============================================================
# 2. PyVis canvas
# ============================================================

net = Network(
    height="calc(100vh - 60px)",
    width="100%",
    bgcolor="#1a1a1a",
    font_color="white",
    select_menu=False,
    cdn_resources="remote",
    directed=True
)

# Physics is used only to create the initial layout.
# It is automatically disabled after stabilization.
#
# IMPORTANT:
# smooth=false keeps edges attached directly to node positions.
# This avoids the hidden support-node behavior that caused
# curved / elliptical edges after dragging nodes.
net.set_options("""
{
  "interaction": {
    "hover": true,
    "hoverConnectedEdges": false,
    "navigationButtons": true,
    "keyboard": true,
    "multiselect": true,
    "selectConnectedEdges": false,
    "zoomView": true,
    "zoomSpeed": 0.7
  },
  "nodes": {
    "chosen": false,
    "scaling": {
      "min": 10,
      "max": 60,
      "label": {
        "enabled": true,
        "min": 10,
        "max": 28,
        "maxVisible": 40,
        "drawThreshold": 0
      }
    }
  },
  "physics": {
    "enabled": true,
    "solver": "forceAtlas2Based",
    "stabilization": {
      "enabled": true,
      "iterations": 1200,
      "updateInterval": 50,
      "fit": true
    },
    "forceAtlas2Based": {
      "gravitationalConstant": -65,
      "centralGravity": 0.003,
      "springLength": 160,
      "springConstant": 0.035,
      "damping": 0.5,
      "avoidOverlap": 1.0
    }
  },
  "edges": {
    "smooth": false,
    "chosen": false,
    "font": {
      "color": "#E6E6E6",
      "strokeWidth": 3,
      "strokeColor": "#1a1a1a",
      "size": 12,
      "align": "middle"
    },
    "scaling": {
      "min": 1,
      "max": 8,
      "label": {
        "enabled": true,
        "min": 10,
        "max": 24,
        "maxVisible": 40,
        "drawThreshold": 0
      }
    }
  }
}
""")


# ============================================================
# 3. Structural ontology nodes that should not be rendered
# ============================================================
#
# These are useful in the ontology itself, but not useful as
# visible analytical nodes. Their meaning is retained through
# node styling/type rather than by drawing the metaclass.
#
# Example:
#
#   PulmonaryNodule rdfs:subClassOf FindingClass
#
# becomes:
#
#   PulmonaryNodule [styled as FindingClass]
#
# rather than:
#
#   PulmonaryNodule -> FindingClass
#

HIDDEN_STRUCTURAL_NODES = {
    CDE.FindingClass,
    CDE.Diagnosis,
    CDE.Measurement,
    CDE.Value,
    CDE.AnatomicLocation,
    CDE.Terminology,
    CDE.DataElement,
    CDE.AssessmentScheme,
    CDE.AssessmentCategory,
    CDE.Modality,
    CDE.Etiology,
    CDE.Subspecialty,
}


# ============================================================
# 4. Basic helpers
# ============================================================

def clean_name(node):
    """Prefer rdfs:label; otherwise use the URI fragment/local name."""
    label = g.value(node, RDFS.label)

    if label:
        return str(label)

    return (
        str(node)
        .split("#")[-1]
        .split("/")[-1]
        .split(":")[-1]
    )



def compact_id(node):
    """
    Return the human-facing ontology identifier rather than the full URI.

    Examples:
        https://radelement.org/ng/AL-0004 -> AL-0004
        https://radelement.org/ng/DX      -> DX
    """
    raw = str(node).rstrip("/")

    if "#" in raw:
        return raw.rsplit("#", 1)[-1]

    if "/" in raw:
        return raw.rsplit("/", 1)[-1]

    return raw.rsplit(":", 1)[-1]


def edge_label_from_property(prop):
    """
    Convert ontology property names to one consistent edge-label style.

    Examples:
        occursWith              -> OCCURS_WITH
        mayManifestAs           -> MAY_MANIFEST_AS
        scopedToSpecific        -> SCOPED_TO_SPECIFIC
        generalPartOf           -> GENERAL_PART_OF
        hasMeasurementComponent -> HAS_MEASUREMENT_COMPONENT
    """
    name = clean_name(prop)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"[^A-Za-z0-9]+", "_", name)
    return name.strip("_").upper()

def get_node_type(node):
    """
    Use explicit cde:nodeType whenever possible.
    This is more reliable than guessing from URI text.
    """
    node_type = g.value(node, CDE.nodeType)

    if node_type:
        return str(node_type)

    return None


def is_value_domain(node):
    """
    True for intermediate OWL classes that represent a DataElement's
    permitted value set.

    Examples:
        WallCharacterValue
        AttenuationValue
        MarginValue

    These are ontology implementation structures and are hidden from
    the conceptual visualization.
    """
    if not isinstance(node, URIRef):
        return False

    # Direct subclass of the structural Value class
    if (node, RDFS.subClassOf, CDE.Value) in g:
        return True

    # An OWL equivalentClass containing a unionOf is also a strong
    # indication that this is a value-domain wrapper.
    for equivalent in g.objects(node, OWL.equivalentClass):
        if g.value(equivalent, OWL.unionOf):
            return True

    # A class used as the rdfs:range of an explicitly typed DataElement
    # is also treated as a value-domain wrapper.
    for prop in g.subjects(RDFS.range, node):
        if get_node_type(prop) == "DataElement":
            return True

    return False


def is_instance_only(node):
    """
    Hide instance data from the ontology visualization.

    The Turtle file contains example observations, measurement instances,
    instantiated values/sites, terminology-binding individuals, and other
    owl:NamedIndividual resources. Those belong to the instance/data layer,
    not the knowledge-graph/schema view.

    Some ontology concepts use OWL punning and are declared BOTH owl:Class
    and owl:NamedIndividual. Those must remain visible as classes, so only
    resources that are NamedIndividuals WITHOUT also being OWL classes are
    treated as instance-only nodes.
    """
    if not isinstance(node, URIRef):
        return False

    is_named_individual = (node, RDF.type, OWL.NamedIndividual) in g
    is_class = (
        (node, RDF.type, OWL.Class) in g
        or (node, RDF.type, RDFS.Class) in g
    )

    return is_named_individual and not is_class


def is_hidden(node):
    """
    Hide implementation/meta structures and instance-level data so the
    visualization represents only the ontology knowledge graph.
    """
    if isinstance(node, BNode):
        return True

    if node in HIDDEN_STRUCTURAL_NODES:
        return True

    # ScopeResolution values such as "stated", "not stated",
    # "indeterminate", and "unresolved" are modeling/control metadata,
    # not concepts we want in the clinical knowledge-graph view.
    if get_node_type(node) == "ScopeResolution":
        return True

    if is_value_domain(node):
        return True

    if is_instance_only(node):
        return True

    return False


def infer_node_type(node):
    """
    Determine the visualization type of a node.

    Explicit cde:nodeType wins. A few safe fallbacks are used for
    concrete nodes that do not carry the annotation directly.
    """
    explicit = get_node_type(node)
    if explicit:
        return explicit

    # Concrete values are often subclasses of a hidden value domain.
    for parent in g.objects(node, RDFS.subClassOf):
        if is_value_domain(parent):
            return "Value"

        # Assessment categories are concrete selectable outcomes of an
        # assessment scheme. Hide the structural AssessmentCategory root,
        # but retain its concrete subclasses as visible category nodes.
        if parent == CDE.AssessmentCategory:
            return "AssessmentCategory"

    return "generic"


# ============================================================
# 5. Visual node styles
# ============================================================

NODE_STYLE = {
    # Core clinical/content nodes share one shape. Their semantic type is
    # distinguished primarily by color and size.
    "FindingClass": {
        "color": "#2563EB",  # blue
        "size": 30,
        "shape": "dot"
    },
    "Diagnosis": {
        "color": "#DC2626",  # red
        "size": 30,
        "shape": "dot"
    },
    "DataElement": {
        "color": "#16A34A",  # green
        "size": 23,
        "shape": "dot"
    },
    "Measurement": {
        "color": "#7C3AED",  # violet
        "size": 25,
        "shape": "dot"
    },

    # Terminal selectable leaves share a square shape.
    "Value": {
        "color": "#CA8A04",  # gold
        "size": 17,
        "shape": "square"
    },
    "AssessmentCategory": {
        "color": "#C2410C",  # burnt orange
        "size": 18,
        "shape": "square"
    },

    # Anatomy gets its own visual family because it represents location
    # rather than a finding/content concept or a terminal value.
    "AnatomicLocation": {
        "color": "#0891B2",  # cyan
        "size": 22,
        "shape": "triangle"
    },

    # Classification/context concepts share the diamond convention already
    # established by AssessmentScheme.
    "AssessmentScheme": {
        "color": "#0F766E",  # teal
        "size": 23,
        "shape": "diamond"
    },
    "Modality": {
        "color": "#EA580C",  # orange
        "size": 19,
        "shape": "diamond"
    },
    "Etiology": {
        "color": "#DB2777",  # magenta
        "size": 19,
        "shape": "diamond"
    },
    "Subspecialty": {
        "color": "#475569",  # slate
        "size": 19,
        "shape": "diamond"
    },

    "Terminology": {
        "color": "#64748B",
        "size": 18,
        "shape": "dot"
    },
    "generic": {
        "color": "#78716C",
        "size": 18,
        "shape": "dot"
    }
}


added_nodes = set()


def register_node(node, node_type=None):
    """
    Add a concrete ontology entity to the graph.

    Returns True if the node is visible/registered and False if it is
    intentionally hidden.
    """
    if is_hidden(node):
        return False

    node_id = str(node)

    if node_id in added_nodes:
        return True

    if node_type is None:
        node_type = infer_node_type(node)

    style = NODE_STYLE.get(node_type, NODE_STYLE["generic"])
    label = clean_name(node)
    short_id = compact_id(node)

    title = (
        f"{label}\n"
        f"Type: {node_type}\n"
        f"{node}"
    )

    net.add_node(
        node_id,
        label=label,
        title=title,
        ontologyType=node_type,
        shortId=short_id,
        color=style["color"],
        size=style["size"],
        shape=style["shape"],
        borderWidth=1.5
    )

    added_nodes.add(node_id)
    return True


# ============================================================
# 6. Edge styles and helper
# ============================================================

EDGE_STYLES = {
    "OCCURS_WITH": {
        "color": "#3498DB",
        "width": 2.4,
        "dashes": False
    },
    "SUBTYPE_OF": {
        "color": "#95A5A6",
        "width": 1.5,
        "dashes": False
    },
    "HAS_DATA_ELEMENT": {
        "color": "#2ECC71",
        "width": 2.5,
        "dashes": False
    },
    "HAS_VALUE_CONSTRAINT": {
        "color": "#F39C12",
        "width": 2.3,
        "dashes": False
    },
    "ALLOWS_VALUE": {
        "color": "#F1C40F",
        "width": 1.5,
        "dashes": True
    },
    "HAS_MEASUREMENT": {
        "color": "#9B59B6",
        "width": 2.5,
        "dashes": False
    },
    "SCOPED_TO": {
        "color": "#E67E22",
        "width": 2.2,
        "dashes": True
    },
    "HAS_COMPONENT": {
        "color": "#3498DB",
        "width": 2.5,
        "dashes": False
    },
    "DIAGNOSIS_RELATION": {
        "color": "#E74C3C",
        "width": 2.2,
        "dashes": False
    },
    "PART_OF": {
        "color": "#7F8C8D",
        "width": 1.5,
        "dashes": True
    },
    "GENERIC": {
        "color": "#BDC3C7",
        "width": 1.5,
        "dashes": False
    }
}


added_edges = set()


def add_edge(source, target, label, category="GENERIC"):
    """
    Add a semantic edge if both endpoints are visible.

    A simple de-duplication key prevents the same relationship from being
    added once through OWL restrictions and again through direct triples.
    """
    if is_hidden(source) or is_hidden(target):
        return

    if not register_node(source):
        return

    if not register_node(target):
        return

    edge_key = (str(source), str(target), label)

    if edge_key in added_edges:
        return

    style = EDGE_STYLES.get(category, EDGE_STYLES["GENERIC"])

    net.add_edge(
        str(source),
        str(target),
        title=label,
        label=label,
        arrows="to",
        color=style["color"],
        width=style["width"],
        dashes=style["dashes"],
        semanticCategory=category
    )

    added_edges.add(edge_key)


# ============================================================
# 7. Concrete subtype relationships
# ============================================================

print("Extracting concrete subtype relationships...")

for child, _, parent in g.triples((None, RDFS.subClassOf, None)):

    # Restrictions are handled separately.
    if isinstance(parent, BNode):
        continue

    # Structural roots are typing metadata, not visual nodes.
    if parent in HIDDEN_STRUCTURAL_NODES:
        register_node(child)
        continue

    if child in HIDDEN_STRUCTURAL_NODES:
        continue

    # Do not draw:
    #
    #   imperceptible -> WallCharacterValue
    #   thin          -> WallCharacterValue
    #
    # The value-domain wrapper will be collapsed later into direct
    # DataElement -> ALLOWS_VALUE -> Value relationships.
    if infer_node_type(child) == "Value" and is_value_domain(parent):
        continue

    if is_value_domain(child) or is_value_domain(parent):
        continue

    add_edge(
        child,
        parent,
        "SUBTYPE_OF",
        "SUBTYPE_OF"
    )


# ============================================================
# 8. RDF-list / value-domain helpers
# ============================================================

def get_rdf_list_members(list_node):
    """Traverse an RDF collection and return its members."""
    members = []
    current = list_node

    while current and current != RDF.nil:
        first = g.value(current, RDF.first)

        if first is not None:
            members.append(first)

        current = g.value(current, RDF.rest)

    return members


def get_allowed_values(value_domain):
    """
    Resolve the concrete permitted values belonging to a value domain.

    Supports:
      1. owl:equivalentClass [ owl:unionOf (...) ]
      2. concrete Value classes rdfs:subClassOf the value domain
    """
    values = set()

    # Representation 1: equivalentClass / unionOf
    for equivalent in g.objects(value_domain, OWL.equivalentClass):
        union_list = g.value(equivalent, OWL.unionOf)

        if union_list:
            values.update(get_rdf_list_members(union_list))

    # Representation 2: Value subclasses
    for candidate in g.subjects(RDFS.subClassOf, value_domain):
        if infer_node_type(candidate) == "Value":
            values.add(candidate)

    return values


def restriction_target(restriction):
    """
    Return the filler/value used by an OWL restriction.

    Supports the restriction forms used by this ontology:
      - owl:someValuesFrom
      - owl:allValuesFrom
      - owl:hasValue
    """
    return (
        g.value(restriction, OWL.someValuesFrom)
        or g.value(restriction, OWL.allValuesFrom)
        or g.value(restriction, OWL.hasValue)
    )


def restrictions_in_expression(expression, seen=None):
    """
    Recursively yield OWL restrictions contained in a class expression.

    This is required for defined classes whose restrictions sit inside
    owl:equivalentClass / owl:intersectionOf rather than directly under
    rdfs:subClassOf.

    Example:

        SolidPulmonaryNodule
            owl:equivalentClass [
                owl:intersectionOf (
                    PulmonaryNodule
                    [
                        a owl:Restriction ;
                        owl:onProperty hasAttenuation ;
                        owl:someValuesFrom Solid
                    ]
                )
            ] .

    The helper deliberately follows intersection expressions, but does not
    flatten owl:unionOf. A union describes alternatives and must not be
    interpreted as a set of simultaneously applicable constraints.
    """
    if seen is None:
        seen = set()

    if expression in seen:
        return

    seen.add(expression)

    if (expression, RDF.type, OWL.Restriction) in g:
        yield expression
        return

    intersection_list = g.value(expression, OWL.intersectionOf)

    if intersection_list:
        for member in get_rdf_list_members(intersection_list):
            yield from restrictions_in_expression(member, seen)


def process_owl_restriction(host, restriction, defining=False):
    """
    Materialize one OWL restriction into the conceptual graph.

    `defining=False` means the restriction came from rdfs:subClassOf and is
    necessary only.

    `defining=True` means the restriction came from owl:equivalentClass and
    participates in a necessary-and-sufficient class definition.

    DataElement restrictions are handled specially:

      host -> HAS_DATA_ELEMENT -> DataElement

    when the filler is the DataElement's value domain, versus:

      host -> HAS_VALUE_CONSTRAINT -> fixed Value

    when the filler is a concrete Value.

    This prevents a fixed class-defining value such as
    `hasAttenuation some solid` from being displayed as though attenuation
    were an authorable element on that class.
    """
    prop = g.value(restriction, OWL.onProperty)

    if prop is None:
        return

    target = restriction_target(restriction)

    if target is None:
        return

    prop_type = get_node_type(prop)

    register_node(host)

    # --------------------------------------------------------
    # DataElement restriction
    # --------------------------------------------------------
    if prop_type == "DataElement":
        register_node(prop, "DataElement")

        # A concrete Value filler is a fixed value constraint, not an
        # offered/authorable DataElement.
        if infer_node_type(target) == "Value":
            register_node(target, "Value")

            add_edge(
                host,
                target,
                "HAS_VALUE_CONSTRAINT",
                "HAS_VALUE_CONSTRAINT"
            )
            return

        # A value-domain filler means the class carries the DataElement
        # without fixing it to one concrete value.
        add_edge(
            host,
            prop,
            "HAS_DATA_ELEMENT",
            "HAS_DATA_ELEMENT"
        )
        return

    # --------------------------------------------------------
    # Measurements
    # --------------------------------------------------------
    if prop == CDE.hasMeasurement:
        add_edge(
            host,
            target,
            "HAS_MEASUREMENT",
            "HAS_MEASUREMENT"
        )
        return

    if prop in {
        CDE.derivedFromMeasurement,
        CDE.hasMeasurementComponent
    }:
        add_edge(
            host,
            target,
            edge_label_from_property(prop),
            "HAS_MEASUREMENT"
        )
        return

    # --------------------------------------------------------
    # Anatomy / scope
    # --------------------------------------------------------
    if prop in {
        CDE.scopedTo,
        CDE.scopedToClass,
        CDE.scopedToRegion,
        CDE.scopedToSpecific
    }:
        add_edge(
            host,
            target,
            edge_label_from_property(prop),
            "SCOPED_TO"
        )
        return

    # --------------------------------------------------------
    # Components
    # --------------------------------------------------------
    if prop in {
        CDE.hasComponent,
        CDE.componentOf
    }:
        add_edge(
            host,
            target,
            edge_label_from_property(prop),
            "HAS_COMPONENT"
        )
        return

    # --------------------------------------------------------
    # Diagnosis / clinical relationships
    # --------------------------------------------------------
    if prop in {
        CDE.mayManifestAs,
        CDE.mayCause,
        CDE.mayBeCausedBy,
        CDE.causesFinding,
        CDE.mayProgressTo,
        CDE.occursWith,
        CDE.mayBeRelatedTo
    }:
        edge_label = edge_label_from_property(prop)
        edge_category = (
            "OCCURS_WITH"
            if prop == CDE.occursWith
            else "DIAGNOSIS_RELATION"
        )

        add_edge(
            host,
            target,
            edge_label,
            edge_category
        )
        return

    # --------------------------------------------------------
    # Anatomical containment / partonomy
    # --------------------------------------------------------
    if prop in {
        CDE.generalPartOf,
        CDE.regionalPartOf,
        CDE.constitutionalPartOf,
        CDE.containedIn
    }:
        add_edge(
            host,
            target,
            edge_label_from_property(prop),
            "PART_OF"
        )
        return

    # --------------------------------------------------------
    # All other meaningful restrictions
    # --------------------------------------------------------
    add_edge(
        host,
        target,
        edge_label_from_property(prop),
        "GENERIC"
    )


# ============================================================
# 9. OWL restrictions
# ============================================================

print("Extracting OWL restrictions...")

# Necessary restrictions attached through rdfs:subClassOf.
for host, _, restriction in g.triples((None, RDFS.subClassOf, None)):
    if not isinstance(restriction, BNode):
        continue

    if (restriction, RDF.type, OWL.Restriction) not in g:
        continue

    process_owl_restriction(
        host,
        restriction,
        defining=False
    )


# Necessary-and-sufficient restrictions contained in defined classes.
#
# These commonly appear as:
#
#   owl:equivalentClass [
#       owl:intersectionOf (
#           ParentClass
#           [ a owl:Restriction ; ... ]
#       )
#   ]
#
# They must be traversed recursively rather than treated as a direct
# equivalentClass -> Restriction edge.
print("Extracting owl:equivalentClass defining restrictions...")

for host, _, expression in g.triples((None, OWL.equivalentClass, None)):
    if is_hidden(host):
        continue

    for restriction in restrictions_in_expression(expression):
        process_owl_restriction(
            host,
            restriction,
            defining=True
        )


# ============================================================
# 9b. DataElement scope/applicability encoded in rdfs:domain
# ============================================================
#
# DataElements in this ontology are OWL object properties.
# Their applicability constraints can therefore be represented
# as anonymous OWL restrictions under rdfs:domain, for example:
#
#   hasThyroidMargin
#       rdfs:domain [
#           owl:onProperty scopedToRegion ;
#           owl:someValuesFrom anatomy:RID7578
#       ] .
#
# For the conceptual visualization, materialize that restriction as:
#
#   hasThyroidMargin -> SCOPED_TO_REGION -> RID7578
#
# Only scope predicates are extracted here. Other rdfs:domain
# restrictions retain their OWL semantics and are not converted
# into conceptual graph edges unless explicitly supported.
#

print("Extracting DataElement domain scope restrictions...")

SCOPE_PROPERTIES = {
    CDE.scopedTo,
    CDE.scopedToClass,
    CDE.scopedToRegion,
    CDE.scopedToSpecific,
}

for data_element, _, domain in g.triples((None, RDFS.domain, None)):

    if get_node_type(data_element) != "DataElement":
        continue

    if not isinstance(domain, BNode):
        continue

    if (domain, RDF.type, OWL.Restriction) not in g:
        continue

    scope_prop = g.value(domain, OWL.onProperty)

    if scope_prop not in SCOPE_PROPERTIES:
        continue

    scope_target = (
        g.value(domain, OWL.someValuesFrom)
        or g.value(domain, OWL.allValuesFrom)
        or g.value(domain, OWL.hasValue)
    )

    if scope_target is None:
        continue

    register_node(data_element, "DataElement")

    add_edge(
        data_element,
        scope_target,
        edge_label_from_property(scope_prop),
        "SCOPED_TO"
    )


# ============================================================
# 10. Direct semantic object-property assertions
# ============================================================

print("Extracting direct semantic relationships...")

DIRECT_RELATIONS = {
    CDE.hasComponent:
        ("HAS_COMPONENT", "HAS_COMPONENT"),

    CDE.componentOf:
        ("COMPONENT_OF", "HAS_COMPONENT"),

    CDE.derivedFromMeasurement:
        ("DERIVED_FROM_MEASUREMENT", "HAS_MEASUREMENT"),

    CDE.hasMeasurementComponent:
        ("HAS_MEASUREMENT_COMPONENT", "HAS_MEASUREMENT"),

    CDE.mayManifestAs:
        ("MAY_MANIFEST_AS", "DIAGNOSIS_RELATION"),

    CDE.mayCause:
        ("MAY_CAUSE", "DIAGNOSIS_RELATION"),

    CDE.mayBeCausedBy:
        ("MAY_BE_CAUSED_BY", "DIAGNOSIS_RELATION"),

    CDE.causesFinding:
        ("CAUSES_FINDING", "DIAGNOSIS_RELATION"),

    CDE.mayProgressTo:
        ("MAY_PROGRESS_TO", "DIAGNOSIS_RELATION"),

    CDE.occursWith:
        ("OCCURS_WITH", "OCCURS_WITH"),

    CDE.mayBeRelatedTo:
        ("MAY_BE_RELATED_TO", "DIAGNOSIS_RELATION"),

    CDE.assessedBy:
        ("ASSESSED_BY", "GENERIC"),

    CDE.seenOn:
        ("SEEN_ON", "GENERIC"),

    CDE.inSubspecialty:
        ("IN_SUBSPECIALTY", "GENERIC"),

    CDE.scopedTo:
        ("SCOPED_TO", "SCOPED_TO"),

    CDE.scopedToClass:
        ("SCOPED_TO_CLASS", "SCOPED_TO"),

    CDE.scopedToRegion:
        ("SCOPED_TO_REGION", "SCOPED_TO"),

    CDE.scopedToSpecific:
        ("SCOPED_TO_SPECIFIC", "SCOPED_TO"),

    CDE.generalPartOf:
        ("GENERAL_PART_OF", "PART_OF"),

    CDE.regionalPartOf:
        ("REGIONAL_PART_OF", "PART_OF"),

    CDE.constitutionalPartOf:
        ("CONSTITUTIONAL_PART_OF", "PART_OF"),

    CDE.containedIn:
        ("CONTAINED_IN", "PART_OF"),
}


for prop, (label, category) in DIRECT_RELATIONS.items():

    for source, _, target in g.triples((None, prop, None)):

        if not isinstance(target, URIRef):
            continue

        add_edge(
            source,
            target,
            label,
            category
        )


# ============================================================
# 11. Connect each DataElement directly to its allowed values
# ============================================================
#
# This is the key collapse:
#
# Ontology representation:
#
#   wall character
#       rdfs:range
#           WallCharacterValue
#              |
#              +-- imperceptible
#              +-- thin
#              +-- thickened
#              +-- enhancing
#
# Visualization:
#
#   wall character --ALLOWS_VALUE--> imperceptible
#                  --ALLOWS_VALUE--> thin
#                  --ALLOWS_VALUE--> thickened
#                  --ALLOWS_VALUE--> enhancing
#
# WallCharacterValue itself is never rendered.
#

print("Extracting DataElement allowed values...")

for data_element, node_type in g.subject_objects(CDE.nodeType):

    if str(node_type) != "DataElement":
        continue

    value_domain = g.value(data_element, RDFS.range)

    if value_domain is None:
        continue

    allowed_values = get_allowed_values(value_domain)

    if not allowed_values:
        continue

    register_node(data_element, "DataElement")

    def value_sort_key(value):
        rank = g.value(value, CDE.rank)

        try:
            rank_value = int(rank)
        except (TypeError, ValueError):
            rank_value = 999999

        return (
            rank_value,
            clean_name(value).lower()
        )

    for value in sorted(allowed_values, key=value_sort_key):

        register_node(value, "Value")

        add_edge(
            data_element,
            value,
            "ALLOWS_VALUE",
            "ALLOWS_VALUE"
        )


# ============================================================
# 12. Degree-aware spacing for dense / highly reused concepts
# ============================================================
#
# The ontology contains heavily reused concepts such as DataElements,
# Measurements, and AnatomicLocations. A single global spring length
# makes those hubs visually congested while wasting space in sparse
# parts of the graph.
#
# Instead:
#
#   1. Compute visible-node degree.
#   2. Give edges connected to highly reused nodes more preferred length.
#   3. Give highly reused nodes additional physical mass so surrounding
#      concepts receive more breathing room during initial stabilization.
#   4. Weight reuse by semantic role so DataElements, Measurements, and
#      AnatomicLocations spread more strongly than Values.
#
# Physics still turns off after initial stabilization, so this only
# influences the starting layout. Manual rearrangement remains free.
#

print("Applying degree-aware spacing...")

degree = Counter()

for edge in net.edges:
    degree[edge["from"]] += 1
    degree[edge["to"]] += 1


# Semantic importance for layout spacing.
#
# Higher values mean reuse of that node type should create more local
# breathing room. Values remain relatively compact because a DataElement
# with a large allowed-value set should not push apart the ontology as
# aggressively as a highly reused semantic concept.
LAYOUT_ROLE_WEIGHT = {
    "DataElement": 1.45,
    "Measurement": 1.35,
    "AnatomicLocation": 1.30,
    "FindingClass": 1.20,
    "Diagnosis": 1.20,
    "AssessmentScheme": 1.15,
    "Modality": 1.05,
    "Etiology": 1.05,
    "Subspecialty": 1.05,
    "Terminology": 0.95,
    "Value": 0.60,
    "generic": 1.00,
}


# Build a quick lookup for each visible node's semantic role.
visible_node_type = {}

for node in net.nodes:
    node_id = node["id"]

    try:
        rdf_node = URIRef(node_id)
        node_type = infer_node_type(rdf_node)
    except Exception:
        node_type = "generic"

    visible_node_type[node_id] = node_type


def weighted_degree(node_id):
    """
    Degree adjusted by semantic role.

    A DataElement reused 15 times should have more layout influence than
    a Value node connected within a large value set.
    """
    raw_degree = degree[node_id]
    node_type = visible_node_type.get(node_id, "generic")
    role_weight = LAYOUT_ROLE_WEIGHT.get(
        node_type,
        LAYOUT_ROLE_WEIGHT["generic"]
    )

    return raw_degree * role_weight


# ------------------------------------------------------------
# Edge length
# ------------------------------------------------------------
#
# Sparse branches stay fairly compact.
# Edges attached to highly reused nodes become progressively longer.
# log2 prevents extremely connected hubs from exploding the layout.
#
# Typical behavior:
#
# degree ~1-2    -> ~190-220 px
# degree ~5      -> ~250-290 px
# degree ~20     -> ~330-380 px
#
# Values are down-weighted through weighted_degree().
#

for edge in net.edges:
    source_score = weighted_degree(edge["from"])
    target_score = weighted_degree(edge["to"])

    hub_score = max(source_score, target_score)

    edge["length"] = int(
        145 + 48 * math.log2(1 + hub_score)
    )


# ------------------------------------------------------------
# Node mass
# ------------------------------------------------------------
#
# More reused ontology concepts push their neighbors apart more strongly
# during stabilization without changing the visual node size.
#
# Mass is capped so the layout remains stable even for extreme hubs.
#

for node in net.nodes:
    node_id = node["id"]
    score = weighted_degree(node_id)

    node["mass"] = min(
        8.0,
        1.0 + 0.75 * math.log2(1 + score)
    )


# ============================================================
# 13. Focus-only reusable pattern groups
# ============================================================
#
# cde:appliesPattern is intentionally NOT shown in the normal graph.
#
# Instead, each pattern is represented by a hidden node and hidden
# APPLIES_PATTERN edges. The JavaScript focus logic reveals only the
# pattern(s) associated with a selected FindingClass and the peer
# FindingClasses that share those same patterns.
#
# Because these nodes/edges are added AFTER degree-aware spacing, they
# do not affect the initial physics layout or hub-density calculations.
#

pattern_nodes_added = set()
pattern_edge_counter = 0

for finding, _, pattern_literal in g.triples(
    (None, CDE.appliesPattern, None)
):
    if get_node_type(finding) != "FindingClass":
        continue

    # Make sure the concrete Finding exists in the base graph.
    register_node(finding, "FindingClass")

    pattern_name = str(pattern_literal).strip()

    if not pattern_name:
        continue

    pattern_id = f"__pattern__::{pattern_name}"

    if pattern_id not in pattern_nodes_added:
        net.add_node(
            pattern_id,
            label=pattern_name,
            title=f"Reusable pattern: {pattern_name}",
            ontologyType="Pattern",
            shortId="",
            patternName=pattern_name,
            isPatternNode=True,
            hidden=True,
            physics=False,
            shape="box",
            color="#48C9B0",
            font={"color": "#FFFFFF"},
            borderWidth=2,
            size=20,
            chosen=False
        )
        pattern_nodes_added.add(pattern_id)

    pattern_edge_counter += 1
    pattern_edge_id = (
        f"__pattern_edge__::{pattern_edge_counter}"
    )

    net.add_edge(
        str(finding),
        pattern_id,
        id=pattern_edge_id,
        label="APPLIES_PATTERN",
        title="APPLIES_PATTERN",
        patternName=pattern_name,
        isPatternEdge=True,
        hidden=True,
        physics=False,
        arrows="to",
        color="#48C9B0",
        width=2,
        dashes=True,
        chosen=False
    )


# ============================================================
# 14. Save HTML
# ============================================================

print(
    f"Rendering {len(added_nodes):,} base nodes "
    f"and {len(added_edges):,} base edges..."
)

print(
    f"Added {len(pattern_nodes_added):,} focus-only pattern groups."
)

net.save_graph(output_html)


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
    width: 330px;
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
            return String(edge.label || edge.title || "")
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


        function isDataElementValueEdge(edge, dataElementId) {
            var neighbor = otherEnd(edge, dataElementId);

            return (
                nodeTypeOf(neighbor) === "Value" &&
                normalizedLabel(edge) === "ALLOWS_VALUE"
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
                                "ALLOWS_VALUE"
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
                                "ALLOWS_VALUE"
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
                                        "ALLOWS_VALUE"
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
                                    includeEdge(
                                        result,
                                        edge
                                    );
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
        // Existing clean IDs are preserved, but descriptive URI suffixes
        // are removed:
        //
        //     V_000142_Increased -> V_000142: increased
        //
        // Nodes without a usable intrinsic ID receive a stable type-based
        // alias:
        //
        //     MuralNodule -> DE_0001: mural nodule
        //     anatomy/RIDxxxx -> AL-0001: artery
        //
        // Pattern nodes participate in this system as P_0001, P_0002, ...
        //

        var DISPLAY_PREFIX_BY_TYPE = {
            "FindingClass": "FC",
            "Diagnosis": "DX",
            "Measurement": "M",
            "DataElement": "DE",
            "Value": "V",
            "AnatomicLocation": "AL",
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
            //   AL-0042_Artery -> AL-0042
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

                // Preserve the previously established AL-000X convention
                // for anatomy; use PREFIX_000X for all other generated IDs.
                var separator =
                    type === "AnatomicLocation"
                        ? "-"
                        : "_";

                displayIdByNode[node.id] =
                    prefix +
                    separator +
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
                network.focus(entry.id, {scale:1.15, animation:{duration:600, easingFunction:"easeInOutQuad"}});
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
                        scale: 1.15,
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

os.system(f'open "{output_html}"')
