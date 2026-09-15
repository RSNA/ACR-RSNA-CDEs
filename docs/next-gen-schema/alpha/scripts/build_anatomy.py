# -*- coding: utf-8 -*-
"""Build a read-only native RadLex index used by the alpha.

This file intentionally does not create a CDE anatomy ontology. RadLex class
IRIs and RadLex object-property IRIs are preserved exactly. Equivalent direct
RDF assertions and OWL restriction expressions are represented once, with the
source expression forms retained as provenance.
"""
from __future__ import annotations
import json, re
from collections import OrderedDict
from pathlib import Path
from lxml import etree
from radlex_config import RADLEX_OWL, RADLEX_VERSION, RADLEX_NS, RADLEX_ONTOLOGY_IRI

ROOT = Path(__file__).resolve().parent.parent

RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
OWL = "http://www.w3.org/2002/07/owl#"
XML = "http://www.w3.org/XML/1998/namespace"

Q_ABOUT = f"{{{RDF}}}about"
Q_RESOURCE = f"{{{RDF}}}resource"
Q_TYPE = f"{{{RDF}}}type"
Q_CLASS = f"{{{OWL}}}Class"
Q_OBJPROP = f"{{{OWL}}}ObjectProperty"
Q_DESC = f"{{{RDF}}}Description"
Q_LABEL = f"{{{RDFS}}}label"
Q_SUBCLASS = f"{{{RDFS}}}subClassOf"
Q_SUBPROP = f"{{{RDFS}}}subPropertyOf"
Q_INVERSE = f"{{{OWL}}}inverseOf"
Q_DOMAIN = f"{{{RDFS}}}domain"
Q_RANGE = f"{{{RDFS}}}range"
Q_EQUIVCLASS = f"{{{OWL}}}equivalentClass"
Q_RESTRICTION = f"{{{OWL}}}Restriction"
Q_ONPROP = f"{{{OWL}}}onProperty"
PROPERTY_CHARACTERISTICS = {
    OWL + "TransitiveProperty": "transitive",
    OWL + "FunctionalProperty": "functional",
    OWL + "InverseFunctionalProperty": "inverseFunctional",
    OWL + "SymmetricProperty": "symmetric",
    OWL + "AsymmetricProperty": "asymmetric",
    OWL + "ReflexiveProperty": "reflexive",
    OWL + "IrreflexiveProperty": "irreflexive",
}

FILLERS = {
    f"{{{OWL}}}someValuesFrom": "someValuesFrom",
    f"{{{OWL}}}allValuesFrom": "allValuesFrom",
    f"{{{OWL}}}hasValue": "hasValue",
    f"{{{OWL}}}onClass": "onClass",
}

RID_RE = re.compile(re.escape(RADLEX_NS) + r"(RID\d+)$")

def rid_from_iri(iri):
    if not iri:
        return None
    m = RID_RE.match(str(iri))
    return m.group(1) if m else None


def local_name(iri):
    return str(iri).rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def english_text(el):
    lang = el.get(f"{{{XML}}}lang")
    return (el.text or "").strip() if lang in (None, "en") else None


def _subject_kind(el):
    if el.tag == Q_CLASS:
        return "class"
    if el.tag == Q_OBJPROP:
        return "object_property"
    if el.tag == Q_DESC:
        for c in el:
            if c.tag == Q_TYPE:
                r = c.get(Q_RESOURCE)
                if r == OWL + "Class": return "class"
                if r == OWL + "ObjectProperty": return "object_property"
    return None


def build(src=RADLEX_OWL):
    src = Path(src)
    classes = OrderedDict()
    object_properties = OrderedDict()
    taxonomy = []
    rel_acc = OrderedDict()
    unindexed = []
    unresolved = set()

    # First pass: collect declared class/property identities and metadata from all
    # top-level serializations. lxml lets us safely clear only completed subjects.
    context = etree.iterparse(str(src), events=("end",), huge_tree=True)
    for _, el in context:
        parent = el.getparent()
        if parent is None or parent.getparent() is not None:
            continue
        about = el.get(Q_ABOUT)
        if not about:
            el.clear(); continue
        kind = _subject_kind(el)
        rid = rid_from_iri(about)
        # RadLex serializes much class metadata in later rdf:Description blocks
        # without repeating rdf:type owl:Class. A RID subject is still the same
        # native class identity and its metadata must be merged.
        if rid and el.tag == Q_DESC and kind is None:
            kind = "class"
        if kind == "class" and rid:
            nd = classes.setdefault(rid, {
                "iri": about, "label": None, "definition": None,
                "synonyms": [], "acronyms": [], "unsanctioned": [],
                "source": [], "radlex_version": RADLEX_VERSION,
            })
            for c in el:
                if c.tag == Q_LABEL:
                    t = english_text(c)
                    if t: nd["label"] = t
                elif c.tag.startswith("{" + RADLEX_NS + "}"):
                    name = etree.QName(c).localname
                    t = english_text(c)
                    if not t: continue
                    if name == "Definition" and not nd["definition"]: nd["definition"] = t
                    elif name == "Synonym" and t not in nd["synonyms"]: nd["synonyms"].append(t)
                    elif name == "Acronym" and t not in nd["acronyms"]: nd["acronyms"].append(t)
                    elif name == "Unsanctioned_Term" and t not in nd["unsanctioned"]: nd["unsanctioned"].append(t)
                    elif name == "Source" and t not in nd["source"]: nd["source"].append(t)
        elif kind == "object_property" and about.startswith(RADLEX_NS):
            pd = object_properties.setdefault(about, {
                "iri": about, "name": local_name(about), "label": None,
                "subPropertyOf": [], "inverseOf": [], "domain": [], "range": [],
                "characteristics": []
            })
            for c in el:
                if c.tag == Q_LABEL:
                    t = english_text(c)
                    if t: pd["label"] = t
                elif c.tag == Q_SUBPROP and c.get(Q_RESOURCE):
                    x = c.get(Q_RESOURCE)
                    if x not in pd["subPropertyOf"]: pd["subPropertyOf"].append(x)
                elif c.tag == Q_INVERSE and c.get(Q_RESOURCE):
                    x = c.get(Q_RESOURCE)
                    if x not in pd["inverseOf"]: pd["inverseOf"].append(x)
                elif c.tag == Q_DOMAIN and c.get(Q_RESOURCE):
                    x = c.get(Q_RESOURCE)
                    if x not in pd["domain"]: pd["domain"].append(x)
                elif c.tag == Q_RANGE and c.get(Q_RESOURCE):
                    x = c.get(Q_RESOURCE)
                    if x not in pd["range"]: pd["range"].append(x)
                elif c.tag == Q_TYPE and c.get(Q_RESOURCE) in PROPERTY_CHARACTERISTICS:
                    x = PROPERTY_CHARACTERISTICS[c.get(Q_RESOURCE)]
                    if x not in pd["characteristics"]: pd["characteristics"].append(x)
        el.clear()
        while el.getprevious() is not None:
            del el.getparent()[0]

    prop_iris = set(object_properties)

    # Second pass: native taxonomy and native RID-to-RID object-property assertions.
    context = etree.iterparse(str(src), events=("end",), huge_tree=True)
    for _, el in context:
        parent = el.getparent()
        if parent is None or parent.getparent() is not None:
            continue
        about = el.get(Q_ABOUT)
        rid = rid_from_iri(about)
        if not rid:
            el.clear(); continue
        if rid not in classes:
            unresolved.add(rid)
        for c in el:
            if c.tag in (Q_SUBCLASS, Q_EQUIVCLASS):
                direct = rid_from_iri(c.get(Q_RESOURCE))
                if direct:
                    if c.tag == Q_SUBCLASS:
                        taxonomy.append({"from": rid, "to": direct,
                                         "predicate": RDFS + "subClassOf",
                                         "source_form": "subClassOf"})
                    continue
                for r in c.iter(Q_RESTRICTION):
                    on = r.find(Q_ONPROP)
                    if on is None or not on.get(Q_RESOURCE):
                        unindexed.append({"subject": rid, "reason": "restriction missing onProperty"}); continue
                    pred = on.get(Q_RESOURCE)
                    filler = None; form = None
                    for ch in r:
                        if ch.tag in FILLERS and ch.get(Q_RESOURCE):
                            filler = rid_from_iri(ch.get(Q_RESOURCE)); form = FILLERS[ch.tag]; break
                    if filler and pred in prop_iris:
                        key = (rid, pred, filler)
                        rec = rel_acc.setdefault(key, {"from": rid, "predicate": pred, "to": filler, "forms": []})
                        srcform = "restriction:" + form
                        if srcform not in rec["forms"]: rec["forms"].append(srcform)
                    else:
                        unindexed.append({"subject": rid, "predicate": pred,
                                          "reason": "unsupported or non-RID restriction filler"})
            else:
                pred = etree.QName(c).namespace + etree.QName(c).localname if isinstance(c.tag, str) and c.tag.startswith("{") else None
                # etree namespace reconstruction above omits separator only because namespace includes trailing '/'.
                target = rid_from_iri(c.get(Q_RESOURCE))
                if pred in prop_iris and target:
                    key = (rid, pred, target)
                    rec = rel_acc.setdefault(key, {"from": rid, "predicate": pred, "to": target, "forms": []})
                    if "direct" not in rec["forms"]: rec["forms"].append("direct")
        el.clear()
        while el.getprevious() is not None:
            del el.getparent()[0]

    # Merge duplicate taxonomy serializations, while retaining only semantic assertions.
    t_seen = set(); tax2 = []
    for e in taxonomy:
        k=(e["from"],e["to"])
        if k not in t_seen:
            t_seen.add(k); tax2.append(e)

    for rid, nd in classes.items():
        if not nd["label"]: nd["label"] = rid

    try:
        source_path = str(src.relative_to(ROOT))
    except ValueError:
        source_path = str(src)
    out = {
        "source": {"path": source_path, "ontology_iri": RADLEX_ONTOLOGY_IRI, "version": RADLEX_VERSION},
        "classes": classes,
        "object_properties": object_properties,
        "taxonomy": tax2,
        "relationships": list(rel_acc.values()),
        "unindexed_restrictions": unindexed,
        "unresolved_rids": sorted(unresolved),
    }
    out["stats"] = {
        "classes": len(classes), "object_properties": len(object_properties),
        "taxonomy_assertions": len(tax2), "relationships": len(out["relationships"]),
        "relationship_source_expressions": sum(len(r["forms"]) for r in out["relationships"]),
        "unindexed_restrictions": len(unindexed), "unresolved_rids": len(unresolved),
    }
    return out

if __name__ == "__main__":
    out = build()
    dest = Path(__file__).with_name("anatomy.json")
    dest.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["stats"], indent=2))
    print("wrote", dest)
