#!/usr/bin/env python3
"""
Generate conceptual Markdown documentation from the RadElement alpha Turtle ontology.

Outputs:
  - findingclass_relationships_scope_and_diagnosis.md
  - diagnosis_relationships_and_scope.md
  - dataelement_concepts.md

Usage:
    python generate_ontology_docs.py
    python generate_ontology_docs.py alpha-turtle(8).ttl

If no Turtle filename is supplied, the script selects the newest *.ttl file
in the same directory as this script.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable

from rdflib import Graph, RDF, RDFS, OWL, URIRef, BNode, Namespace


CDE = Namespace("https://radelement.org/ng/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")


def parse_args():
    p = argparse.ArgumentParser(description="Generate RadElement ontology concept Markdown files.")
    p.add_argument(
        "turtle",
        nargs="?",
        help="Turtle filename. If omitted, the newest .ttl file in the script directory is used.",
    )
    return p.parse_args()


def choose_turtle(base: Path, supplied: str | None) -> Path:
    if supplied:
        path = Path(supplied)
        if not path.is_absolute():
            path = base / path
        if not path.exists():
            raise FileNotFoundError(f"Turtle file not found: {path}")
        return path

    candidates = list(base.glob("*.ttl"))
    if not candidates:
        raise FileNotFoundError(
            f"No .ttl file found in {base}. Place the Turtle file in the same directory as this script."
        )
    return max(candidates, key=lambda p: p.stat().st_mtime)


class OntologyDocs:
    def __init__(self, turtle_path: Path):
        self.turtle_path = turtle_path
        self.g = Graph()
        self.g.parse(turtle_path, format="turtle")

        self.subject_classes = {
            s for s in self.g.subjects(RDFS.subClassOf, None)
            if isinstance(s, URIRef)
        }

        self.finding_classes = {
            s for s in self.subject_classes
            if s != CDE.FindingClass and self.subclass_of(s, CDE.FindingClass)
        }
        self.diagnoses = {
            s for s in self.subject_classes
            if s != CDE.Diagnosis and self.subclass_of(s, CDE.Diagnosis)
        }

        all_props = {
            p for p in self.g.subjects(RDFS.subPropertyOf, None)
            if isinstance(p, URIRef)
        }
        all_props |= {
            p for p in self.g.subjects(RDF.type, OWL.ObjectProperty)
            if isinstance(p, URIRef)
        }

        self.data_element_props = {
            p for p in all_props
            if p != CDE.hasDataElement and self.prop_is_subproperty(p, CDE.hasDataElement)
        }

        self.scope_props = {
            CDE.scopedToRegion: "SCOPED_TO_REGION",
            CDE.scopedToSpecific: "SCOPED_TO_SPECIFIC",
            CDE.scopedToClass: "SCOPED_TO_CLASS",
        }

    # ---------- Generic ontology helpers ----------

    def label(self, node) -> str:
        return str(
            self.g.value(node, RDFS.label)
            or self.g.value(node, SKOS.prefLabel)
            or str(node).rsplit("/", 1)[-1]
        )

    def named_parents(self, cls) -> list[URIRef]:
        return [
            p for p in self.g.objects(cls, RDFS.subClassOf)
            if isinstance(p, URIRef) and p != OWL.Thing
        ]

    def subclass_of(self, cls, ancestor) -> bool:
        if cls == ancestor:
            return True
        seen = set()
        q = deque([cls])
        while q:
            cur = q.popleft()
            if cur in seen:
                continue
            seen.add(cur)
            for parent in [
                p for p in self.g.objects(cur, RDFS.subClassOf)
                if isinstance(p, URIRef)
            ]:
                if parent == ancestor:
                    return True
                q.append(parent)
        return False

    def prop_is_subproperty(self, prop, ancestor) -> bool:
        if prop == ancestor:
            return True
        seen = set()
        q = deque([prop])
        while q:
            cur = q.popleft()
            if cur in seen:
                continue
            seen.add(cur)
            for parent in self.g.objects(cur, RDFS.subPropertyOf):
                if parent == ancestor:
                    return True
                q.append(parent)
        return False

    def restrictions(self, cls) -> list[tuple[URIRef, object]]:
        result = []
        for r in self.g.objects(cls, RDFS.subClassOf):
            if not isinstance(r, BNode):
                continue
            if (r, RDF.type, OWL.Restriction) not in self.g:
                continue
            prop = self.g.value(r, OWL.onProperty)
            filler = (
                self.g.value(r, OWL.someValuesFrom)
                or self.g.value(r, OWL.allValuesFrom)
                or self.g.value(r, OWL.hasValue)
            )
            if prop is not None and filler is not None:
                result.append((prop, filler))
        return result

    def restrictions_in_expression(self, expression, seen=None):
        """
        Recursively return OWL restrictions contained in a class expression.

        This is used for defined classes whose necessary-and-sufficient
        restrictions sit inside owl:equivalentClass / owl:intersectionOf.

        owl:unionOf is intentionally not flattened because its members are
        alternatives, not simultaneously applicable constraints.
        """
        if seen is None:
            seen = set()

        if expression in seen:
            return []

        seen.add(expression)

        if (expression, RDF.type, OWL.Restriction) in self.g:
            prop = self.g.value(expression, OWL.onProperty)
            filler = (
                self.g.value(expression, OWL.someValuesFrom)
                or self.g.value(expression, OWL.allValuesFrom)
                or self.g.value(expression, OWL.hasValue)
            )
            if prop is not None and filler is not None:
                return [(prop, filler)]
            return []

        result = []
        intersection = self.g.value(expression, OWL.intersectionOf)
        if intersection is not None:
            for member in self.rdf_list(intersection):
                result.extend(self.restrictions_in_expression(member, seen))

        return result

    def defining_restrictions(self, cls) -> list[tuple[URIRef, object]]:
        """
        Restrictions participating in owl:equivalentClass definitions.

        These are necessary-and-sufficient defining constraints.
        """
        result = []
        for expression in self.g.objects(cls, OWL.equivalentClass):
            result.extend(self.restrictions_in_expression(expression))

        output = []
        seen = set()
        for item in result:
            if item not in seen:
                seen.add(item)
                output.append(item)
        return output

    def all_restrictions_with_semantics(self, cls):
        """
        Return (property, filler, defining) tuples.

        defining=False: rdfs:subClassOf restriction, necessary only.
        defining=True: owl:equivalentClass restriction, necessary and sufficient.
        """
        result = [(p, o, False) for p, o in self.restrictions(cls)]
        result.extend((p, o, True) for p, o in self.defining_restrictions(cls))

        output = []
        seen = set()
        for item in result:
            if item not in seen:
                seen.add(item)
                output.append(item)
        return output

    def data_element_ranges(self, prop):
        return [
            r for r in self.g.objects(prop, RDFS.range)
            if isinstance(r, URIRef)
        ]

    def is_fixed_data_element_value(self, prop, target) -> bool:
        """
        True when a DataElement restriction fixes the element to a concrete
        permitted value rather than exposing its value domain.

        Example:
          hasAttenuation some AttenuationValue  -> authorable DataElement
          hasAttenuation some V_000010_Solid   -> fixed value constraint
        """
        if not isinstance(target, URIRef):
            return False

        ranges = self.data_element_ranges(prop)

        for value_range in ranges:
            if target == value_range:
                return False
            if self.subclass_of(target, value_range):
                return True

        return False

    # ---------- Scope handling ----------

    def direct_scopes(self, cls):
        return [
            (self.scope_props[p], obj)
            for p, obj in self.restrictions(cls)
            if p in self.scope_props
        ]

    def resolved_scopes(self, cls):
        direct = self.direct_scopes(cls)
        if direct:
            return [(kind, obj, None) for kind, obj in direct]

        seen = {cls}
        q = deque((p, 1) for p in self.named_parents(cls))
        nearest_depth = None
        found = []

        while q:
            anc, depth = q.popleft()
            if anc in seen:
                continue
            seen.add(anc)

            if nearest_depth is not None and depth > nearest_depth:
                break

            scopes = self.direct_scopes(anc)
            if scopes:
                nearest_depth = depth
                found.extend((kind, obj, anc) for kind, obj in scopes)
                continue

            for parent in self.named_parents(anc):
                q.append((parent, depth + 1))

        output = []
        seen_items = set()
        for item in found:
            if item not in seen_items:
                seen_items.add(item)
                output.append(item)
        return output

    # ---------- Constrained anatomy refinement ----------

    def restriction_children(self, parent, prop):
        children = set()
        for restriction in self.g.subjects(OWL.onProperty, prop):
            fillers = set(self.g.objects(restriction, OWL.someValuesFrom))
            fillers |= set(self.g.objects(restriction, OWL.allValuesFrom))
            fillers |= set(self.g.objects(restriction, OWL.hasValue))
            if parent not in fillers:
                continue
            for child in self.g.subjects(RDFS.subClassOf, restriction):
                if isinstance(child, URIRef):
                    children.add(child)
        return children

    def find_by_label(self, wanted: str):
        wanted = wanted.lower()
        nodes = set(self.g.subjects()) | set(self.g.objects())
        for node in nodes:
            if isinstance(node, URIRef) and self.label(node).lower() == wanted:
                return node
        return None

    def regional_archetypes(self):
        names = [
            "organ region",
            "organ segment",
            "anatomical lobe",
            "segment of brain",
            "region of vascular tree",
        ]
        return [n for n in (self.find_by_label(x) for x in names) if n is not None]

    def is_regional_anatomy(self, node):
        text = self.label(node).lower()

        if any(self.subclass_of(node, archetype) for archetype in self.regional_archetypes()):
            return True

        if any(p == CDE.regionalPartOf for p, _ in self.restrictions(node)):
            return True

        # Covers ontology concepts modeled under generic component classes while
        # still clearly representing regional/lobar/segmental localization.
        regional_terms = (
            " lobe", "lobe of ", "segment of ", "segmental ",
            "left ", "right ", "upper pole", "lower pole",
        )
        return any(term in text for term in regional_terms)

    def valid_location_refinements(self, root):
        """
        Conservative authoring-oriented location refinement.

        Include:
          * named subclass specializations
          * explicit regionalPartOf children
          * generalPartOf children only when the child itself is modeled as
            regional, lobar, or segmental anatomy

        Do not treat arbitrary mereological descendants as valid authoring
        locations. This intentionally excludes structures such as parenchyma or
        generic organ components solely because they are part of the scoped organ.
        """
        seen = {root}
        q = deque([root])
        results = set()

        while q:
            cur = q.popleft()

            subclass_children = {
                c for c in self.g.subjects(RDFS.subClassOf, cur)
                if isinstance(c, URIRef)
            }
            regional_children = self.restriction_children(cur, CDE.regionalPartOf)
            general_children = {
                c for c in self.restriction_children(cur, CDE.generalPartOf)
                if self.is_regional_anatomy(c)
            }

            for child in subclass_children | regional_children | general_children:
                if child not in seen:
                    seen.add(child)
                    results.add(child)
                    q.append(child)

        return results

    # ---------- Value lists ----------

    def rdf_list(self, head):
        vals = []
        seen = set()
        while head and head != RDF.nil and head not in seen:
            seen.add(head)
            first = self.g.value(head, RDF.first)
            if first is not None:
                vals.append(first)
            head = self.g.value(head, RDF.rest)
        return vals

    def values_from_resource(self, resource):
        vals = set()

        for head in self.g.objects(resource, OWL.oneOf):
            vals.update(self.rdf_list(head))

        # Explicit x_value-like predicates.
        for p, o in self.g.predicate_objects(resource):
            pname = (self.label(p) + " " + str(p)).lower()
            if "x_value" in pname or "x-value" in pname or "x value" in pname:
                if isinstance(o, BNode):
                    vals.update(self.rdf_list(o))
                else:
                    vals.add(o)

        # RDF lists attached through a blank node.
        for _, o in self.g.predicate_objects(resource):
            if isinstance(o, BNode):
                seq = self.rdf_list(o)
                if seq:
                    vals.update(seq)

        return vals

    def values_for_data_element(self, prop):
        vals = set()

        # Property range.
        for r in self.g.objects(prop, RDFS.range):
            vals.update(self.values_from_resource(r))

        # Restriction target resources/classes used by FindingClasses/Diagnoses.
        owners = self.finding_classes | self.diagnoses
        for owner in owners:
            for p, target in self.restrictions(owner):
                if p == prop:
                    vals.update(self.values_from_resource(target))

                    tname = (self.label(target) + " " + str(target)).lower()
                    if "x_value" in tname or "x-value" in tname or " value" in tname:
                        for child in self.g.subjects(RDFS.subClassOf, target):
                            if isinstance(child, URIRef):
                                vals.add(child)

        # Property-level x_value-like links.
        for pred, obj in self.g.predicate_objects(prop):
            pname = (self.label(pred) + " " + str(pred)).lower()
            if "x_value" in pname or "x-value" in pname or "x value" in pname:
                if isinstance(obj, BNode):
                    vals.update(self.rdf_list(obj))
                else:
                    vals.add(obj)

        # Keep only meaningful named/literal values.
        clean = set()
        for v in vals:
            if isinstance(v, URIRef) and v in self.data_element_props:
                continue
            lab = self.label(v).strip()
            if lab and lab.lower() not in {"value", "values"}:
                clean.add(v)

        return sorted(clean, key=lambda x: self.label(x).lower())

    # ---------- Diagnosis document ----------

    def write_diagnoses(self, path: Path):
        rels = [
            (CDE.hasEtiology, "HAS_ETIOLOGY"),
            (CDE.mayManifestAs, "MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)"),
            (CDE.mayCause, "MAY_CAUSE (FindingClass that may occur as a consequence of the diagnosis)"),
            (CDE.mayProgressTo, "MAY_PROGRESS_TO"),
            (CDE.assessedBy, "ASSESSED_BY"),
        ]

        lines = [
            "# Diagnosis Relationships and Scope",
            "",
            f"Diagnosis relationships extracted from `{self.turtle_path.name}`. "
            "When scope is inherited rather than directly asserted, the nearest ancestor providing that scope is identified. "
            "Fixed DataElement values are shown separately as HAS_VALUE_CONSTRAINT, with defining versus necessary semantics preserved. "
            "Absent relationships are omitted.",
            "",
        ]

        for idx, dx in enumerate(sorted(self.diagnoses, key=lambda x: self.label(x).lower())):
            lines += [f"## {self.label(dx)}", ""]

            for kind, anatomy, source in self.resolved_scopes(dx):
                suffix = f" (inferred from {self.label(source)})" if source else ""
                lines += [f"**{kind}:** {self.label(anatomy)}{suffix}", ""]

            r = self.restrictions(dx)

            for prop, heading in rels:
                vals = [o for p, o in r if p == prop]
                if vals:
                    lines += [f"#### {heading}", ""]
                    for v in sorted(vals, key=lambda x: self.label(x).lower()):
                        lines.append(f"- **{self.label(v)}**")
                        if v in self.finding_classes:
                            for skind, anatomy, source in self.resolved_scopes(v):
                                suffix = f" (inferred from {self.label(source)})" if source else ""
                                lines.append(f"  - `{skind}`: {self.label(anatomy)}{suffix}")
                    lines.append("")

            de_vals = [
                (p, o)
                for p, o in r
                if self.prop_is_subproperty(p, CDE.hasDataElement)
                and not self.is_fixed_data_element_value(p, o)
            ]
            if de_vals:
                lines += ["#### HAS_DATA_ELEMENT (attributes associated directly with it)", ""]
                for prop, _ in sorted(de_vals, key=lambda x: self.label(x[0]).lower()):
                    lines.append(f"- **{self.label(prop)}**")
                lines.append("")

            value_constraints = [
                (p, o, defining)
                for p, o, defining in self.all_restrictions_with_semantics(dx)
                if self.prop_is_subproperty(p, CDE.hasDataElement)
                and self.is_fixed_data_element_value(p, o)
            ]
            if value_constraints:
                lines += ["#### HAS_VALUE_CONSTRAINT", ""]
                for prop, value, defining in sorted(
                    value_constraints,
                    key=lambda x: (self.label(x[0]).lower(), self.label(x[1]).lower()),
                ):
                    semantics = "defining" if defining else "necessary"
                    lines.append(
                        f"- **{self.label(prop)} = {self.label(value)}** ({semantics})"
                    )
                lines.append("")

            if idx != len(self.diagnoses) - 1:
                lines += ["---", ""]

        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    # ---------- FindingClass document ----------

    def finding_hierarchy(self):
        children = defaultdict(list)
        parent_map = {}

        for fc in self.finding_classes:
            direct_fc_parents = [
                p for p in self.named_parents(fc)
                if p in self.finding_classes
            ]
            if direct_fc_parents:
                parent = sorted(direct_fc_parents, key=lambda x: self.label(x).lower())[0]
                children[parent].append(fc)
                parent_map[fc] = parent

        for p in children:
            children[p].sort(key=lambda x: self.label(x).lower())

        top = sorted(
            [fc for fc in self.finding_classes if fc not in parent_map],
            key=lambda x: self.label(x).lower(),
        )
        return children, parent_map, top

    def diagnosis_connections(self):
        direct = defaultdict(list)
        for dx in self.diagnoses:
            for prop, target in self.restrictions(dx):
                if target in self.finding_classes:
                    direct[target].append((prop, dx))

        result = {}
        for fc in self.finding_classes:
            vals = []
            seen_anc = set()
            stack = [fc]

            while stack:
                anc = stack.pop()
                if anc in seen_anc:
                    continue
                seen_anc.add(anc)

                for prop, dx in direct.get(anc, []):
                    vals.append((prop, dx, None if anc == fc else anc))

                stack.extend(
                    p for p in self.named_parents(anc)
                    if p in self.finding_classes
                )

            unique = []
            seen = set()
            for item in vals:
                if item not in seen:
                    seen.add(item)
                    unique.append(item)

            result[fc] = sorted(
                unique,
                key=lambda v: (self.label(v[1]).lower(), self.label(v[0]).lower()),
            )

        return result

    def occurs_with_map(self):
        result = defaultdict(set)

        for fc in self.finding_classes:
            for p, target in self.restrictions(fc):
                if p == CDE.occursWith and target in self.finding_classes:
                    result[fc].add(target)

        # Respect OWL symmetric semantics.
        if (CDE.occursWith, RDF.type, OWL.SymmetricProperty) in self.g:
            for source, targets in list(result.items()):
                for target in targets:
                    result[target].add(source)

        return result

    def write_findings(self, path: Path):
        children, _, top = self.finding_hierarchy()
        dx_connections = self.diagnosis_connections()
        occurs = self.occurs_with_map()

        def emit(fc, level=2, quoted=False):
            prefix = "> " if quoted else ""
            blank = ">" if quoted else ""
            heading = "#" * level
            arr = [prefix + f"{heading} {self.label(fc)}", blank]

            if dx_connections.get(fc):
                arr += [prefix + "#### DIAGNOSIS_CONNECTIONS", blank]
                for prop, dx, inherited_from in dx_connections[fc]:
                    suffix = (
                        f" (inherited via {self.label(inherited_from)})"
                        if inherited_from else ""
                    )
                    arr.append(
                        prefix + f"- **{self.label(dx)}** via `{self.label(prop)}`{suffix}"
                    )
                arr.append(blank)

            scopes = self.resolved_scopes(fc)
            for kind, anatomy, source in scopes:
                suffix = f" (inferred from {self.label(source)})" if source else ""
                arr += [prefix + f"**{kind}:** {self.label(anatomy)}{suffix}", blank]

            refinements = set()
            for _, anatomy, _ in scopes:
                refinements |= self.valid_location_refinements(anatomy)

            if refinements:
                arr += [prefix + "#### AVAILABLE_LOCATION_REFINEMENTS", blank]
                for node in sorted(refinements, key=lambda x: self.label(x).lower()):
                    arr.append(prefix + f"- **{self.label(node)}**")
                arr.append(blank)

            r = self.restrictions(fc)

            # COMPONENT_OF and ASSESSED_BY are directional as asserted.
            for prop, heading_text in [
                (CDE.componentOf, "COMPONENT_OF"),
                (CDE.assessedBy, "ASSESSED_BY"),
            ]:
                targets = [o for p, o in r if p == prop]
                if targets:
                    arr += [prefix + f"#### {heading_text}", blank]
                    for target in sorted(targets, key=lambda x: self.label(x).lower()):
                        arr.append(prefix + f"- **{self.label(target)}**")
                    arr.append(blank)

            if occurs.get(fc):
                arr += [
                    prefix + "#### OCCURS_WITH (seen together often enough to be worth noting, but says nothing about cause or sequence)",
                    blank,
                ]
                for target in sorted(occurs[fc], key=lambda x: self.label(x).lower()):
                    arr.append(prefix + f"- **{self.label(target)}**")
                arr.append(blank)

            measurements = [o for p, o in r if p == CDE.hasMeasurement]
            if measurements:
                arr += [prefix + "#### HAS_MEASUREMENT", blank]
                for target in sorted(measurements, key=lambda x: self.label(x).lower()):
                    arr.append(prefix + f"- **{self.label(target)}**")
                arr.append(blank)

            de_vals = [
                (p, o)
                for p, o in r
                if self.prop_is_subproperty(p, CDE.hasDataElement)
                and not self.is_fixed_data_element_value(p, o)
            ]
            if de_vals:
                arr += [prefix + "#### HAS_DATA_ELEMENT (attributes associated directly with it)", blank]
                for prop, _ in sorted(de_vals, key=lambda x: self.label(x[0]).lower()):
                    arr.append(prefix + f"- **{self.label(prop)}**")
                arr.append(blank)

            value_constraints = [
                (p, o, defining)
                for p, o, defining in self.all_restrictions_with_semantics(fc)
                if self.prop_is_subproperty(p, CDE.hasDataElement)
                and self.is_fixed_data_element_value(p, o)
            ]
            if value_constraints:
                arr += [prefix + "#### HAS_VALUE_CONSTRAINT", blank]
                for prop, value, defining in sorted(
                    value_constraints,
                    key=lambda x: (self.label(x[0]).lower(), self.label(x[1]).lower()),
                ):
                    semantics = "defining" if defining else "necessary"
                    arr.append(
                        prefix + f"- **{self.label(prop)} = {self.label(value)}** ({semantics})"
                    )
                arr.append(blank)

            seen_on = [o for p, o in r if p == CDE.seenOn]
            if seen_on:
                arr += [prefix + "#### SEEN_ON (modality)", blank]
                for target in sorted(seen_on, key=lambda x: self.label(x).lower()):
                    arr.append(prefix + f"- **{self.label(target)}**")
                arr.append(blank)

            subspecialties = [o for p, o in r if p == CDE.inSubspecialty]
            if subspecialties:
                arr += [prefix + "#### IN_SUBSPECIALTY", blank]
                for target in sorted(subspecialties, key=lambda x: self.label(x).lower()):
                    arr.append(prefix + f"- **{self.label(target)}**")
                arr.append(blank)

            kids = children.get(fc, [])
            if kids:
                arr += [prefix + "#### SUBTYPES", blank]
                for child in kids:
                    arr.append(prefix + f"- **{self.label(child)}**")
                arr.append(blank)

                for child in kids:
                    # Clear visual division and indentation for subtype content.
                    arr += [
                        prefix + "> **Subtype**" if quoted else "> **Subtype**",
                        ">" if not quoted else prefix.rstrip(),
                    ]
                    child_lines = emit(child, level=3, quoted=False)
                    for line in child_lines:
                        arr.append("> " + line if line else ">")
                    arr.append(">" if not quoted else prefix.rstrip())

            return arr

        lines = [
            "# FindingClass Relationships, Scope, and Diagnosis Connections",
            "",
            f"FindingClass relationships extracted from `{self.turtle_path.name}`. "
            "FindingClasses are grouped by their ontology subtype hierarchy. "
            "Diagnosis connections include relationships asserted from Diagnosis to FindingClass, with subtype inheritance identified where applicable. "
            "`OCCURS_WITH` is expanded in both directions when the ontology declares it symmetric. "
            "`AVAILABLE_LOCATION_REFINEMENTS` uses a conservative authoring-oriented ontology walk and does not treat arbitrary anatomical containment as a valid location option. "
            "Fixed DataElement values are shown separately as `HAS_VALUE_CONSTRAINT`; restrictions from `owl:equivalentClass` are marked defining and restrictions from `rdfs:subClassOf` are marked necessary. "
            "Absent relationships are omitted.",
            "",
        ]

        for idx, fc in enumerate(top):
            lines += emit(fc, level=2)
            if idx != len(top) - 1:
                lines += ["---", ""]

        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    # ---------- DataElement document ----------

    def data_element_scopes(self, prop):
        """
        Return scopes attached to a DataElement property.

        Supported forms:
          1. direct scope assertions on the property
          2. class-like OWL restrictions attached through rdfs:subClassOf
          3. logical rdfs:domain restrictions such as:

             hasThyroidMargin rdfs:domain [
                 a owl:Restriction ;
                 owl:onProperty scopedToRegion ;
                 owl:someValuesFrom RID7578
             ] .

        A logical domain restriction means the DataElement is applicable only
        within that scope.
        """
        values = []

        # 1. Direct property assertions.
        for scope_prop, heading in self.scope_props.items():
            for obj in self.g.objects(prop, scope_prop):
                values.append((heading, obj))

        # 2. Restriction form on the DataElement resource itself.
        for p, obj in self.restrictions(prop):
            if p in self.scope_props:
                values.append((self.scope_props[p], obj))

        # 3. Logical rdfs:domain restrictions.
        for domain in self.g.objects(prop, RDFS.domain):
            if not isinstance(domain, BNode):
                continue
            if (domain, RDF.type, OWL.Restriction) not in self.g:
                continue

            on_prop = self.g.value(domain, OWL.onProperty)
            filler = (
                self.g.value(domain, OWL.someValuesFrom)
                or self.g.value(domain, OWL.allValuesFrom)
                or self.g.value(domain, OWL.hasValue)
            )

            if on_prop in self.scope_props and filler is not None:
                values.append((self.scope_props[on_prop], filler))

        output = []
        seen = set()
        for item in values:
            if item not in seen:
                seen.add(item)
                output.append(item)
        return output


    def data_element_usage(self):
        """
        Return authorable DataElement usage only.

        Fixed value restrictions are constraints, not offered elements, so they
        are intentionally excluded from USED_BY.

        Example:
          PulmonaryNodule -> hasAttenuation some AttenuationValue
              counts as attenuation usage

          SolidPulmonaryNodule -> hasAttenuation some Solid
              does not count as attenuation usage; it is a defining constraint

          SolidComponentOfPartSolidNodule -> hasAttenuation some Solid
              does not count as attenuation usage; it is a necessary constraint
        """
        dx = defaultdict(set)
        fc = defaultdict(set)

        for owner in self.diagnoses:
            for prop, target, _ in self.all_restrictions_with_semantics(owner):
                if (
                    prop in self.data_element_props
                    and not self.is_fixed_data_element_value(prop, target)
                ):
                    dx[prop].add(owner)

        for owner in self.finding_classes:
            for prop, target, _ in self.all_restrictions_with_semantics(owner):
                if (
                    prop in self.data_element_props
                    and not self.is_fixed_data_element_value(prop, target)
                ):
                    fc[prop].add(owner)

        return dx, fc

    @staticmethod
    def compact_table_cell(names: Iterable[str]) -> str:
        names = list(names)
        if not names:
            return ""
        return "<br/>".join(f"- {name}" for name in names)

    def write_data_elements(self, path: Path):
        used_by_dx, used_by_fc = self.data_element_usage()

        lines = [
            "# DataElement Concepts",
            "",
            f"DataElements extracted from `{self.turtle_path.name}`. DataElements are attributes that describe a FindingClass or Diagnosis. "
            "Each section shows the allowed values defined by the ontology and where the DataElement is available as an authorable attribute. "
            "Fixed class value constraints are not counted as `USED_BY`. "
            "Scope is shown if a DataElement itself is explicitly or logically scoped in the ontology.",
            "",
        ]

        props = sorted(self.data_element_props, key=lambda x: self.label(x).lower())

        for idx, prop in enumerate(props):
            lines += [f"## {self.label(prop)}", ""]

            for kind, anatomy in self.data_element_scopes(prop):
                lines += [f"**{kind}:** {self.label(anatomy)}", ""]

            values = self.values_for_data_element(prop)
            if values:
                lines += ["#### VALUES", ""]
                for value in values:
                    lines.append(f"- **{self.label(value)}**")
                lines.append("")

            dx_names = [
                self.label(x)
                for x in sorted(used_by_dx[prop], key=lambda x: self.label(x).lower())
            ]
            fc_names = [
                self.label(x)
                for x in sorted(used_by_fc[prop], key=lambda x: self.label(x).lower())
            ]

            if dx_names or fc_names:
                lines += [
                    "#### USED_BY",
                    "",
                    "| Diagnosis | FindingClass |",
                    "| --- | --- |",
                    f"| {self.compact_table_cell(dx_names)} | {self.compact_table_cell(fc_names)} |",
                    "",
                ]

            if idx != len(props) - 1:
                lines += ["---", ""]

        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    # ---------- Validation ----------

    def validate(self):
        warnings = []

        if not self.finding_classes:
            warnings.append("No FindingClass descendants found.")
        if not self.diagnoses:
            warnings.append("No Diagnosis descendants found.")
        if not self.data_element_props:
            warnings.append("No DataElement properties found beneath hasDataElement.")

        if CDE.occursWith in set(self.g.subjects()) and (
            CDE.occursWith, RDF.type, OWL.SymmetricProperty
        ) not in self.g:
            warnings.append("occursWith exists but is no longer declared owl:SymmetricProperty.")

        missing_values = [
            p for p in self.data_element_props
            if not self.values_for_data_element(p)
        ]
        if missing_values:
            warnings.append(
                "DataElements with no detected VALUES: "
                + ", ".join(self.label(p) for p in sorted(missing_values, key=lambda x: self.label(x).lower()))
            )

        return warnings


def main():
    args = parse_args()
    base = Path(__file__).resolve().parent
    turtle = choose_turtle(base, args.turtle)

    docs = OntologyDocs(turtle)

    finding_path = base / "findingclass_relationships_scope_and_diagnosis.md"
    diagnosis_path = base / "diagnosis_relationships_and_scope.md"
    data_path = base / "dataelement_concepts.md"

    docs.write_findings(finding_path)
    docs.write_diagnoses(diagnosis_path)
    docs.write_data_elements(data_path)

    warnings = docs.validate()

    print(f"Source: {turtle.name}")
    print(f"FindingClasses: {len(docs.finding_classes)}")
    print(f"Diagnoses: {len(docs.diagnoses)}")
    print(f"DataElements: {len(docs.data_element_props)}")
    print()
    print("Generated:")
    print(f"  {finding_path.name}")
    print(f"  {diagnosis_path.name}")
    print(f"  {data_path.name}")

    if warnings:
        print()
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")


if __name__ == "__main__":
    main()
