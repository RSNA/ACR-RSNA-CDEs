# -*- coding: utf-8 -*-
"""
Builds the imported anatomy module, and the imported-fact layer generally,
from RadLex.owl.

The OWL file replaces the CSV export as the source of truth. The two carry
identical content (verified field by field: 24 of 24 matching value counts),
but the OWL carries the partonomy as real axioms rather than as pipe-delimited
strings, so relations are extracted rather than reconstructed.

Three fields the CSV-based build never used are now imported:

  Unsanctioned_Term  terms RadLex explicitly discourages for a concept. These
                     are NOT synonyms and must never be emitted as skos:altLabel
                     or matched by duplicate detection.
  Anatomical_Site    RadLex's own finding-to-anatomy assertion. Where present,
                     scope is imported rather than authored.
  Replaced_by /      retirement pointers. The Obsolete flag is FALSE for every
  Preferred_Name_    concept in 4.3 while 437 carry Replaced_by, so retirement
  for_Obsolete       is tracked by the pointer, not by the flag.

Real Definition and Source values are carried too, in place of the
"Imported from RadLex" placeholder the CSV build fell back to.
"""
import re, json, os, time
from collections import OrderedDict, defaultdict
import rdflib
from rdflib import Graph, URIRef
from rdflib.namespace import RDFS, OWL
import spec

OWL_SRC = "/home/claude/work/rlowl/RadLex.owl"
NT_CACHE = "/home/claude/work/radlex.nt"
RID = "http://www.radlex.org/RID/"

PART_SENSES = OrderedDict([
    ("Part_Of", "generalPartOf"),
    ("Regional_Part_Of", "regionalPartOf"),
    ("Constitutional_Part_Of", "constitutionalPartOf"),
])

# Contained_In is imported but kept OUT of the partOf family on purpose. A kidney
# is not part of the abdomen, it is located in it. Folding the two together would
# let scope congruence chase location links.
#
# It is imported because the body-region facet needs it: kidney reaches abdomen
# only through Contained_In, so without it the facet cannot be derived and a
# separate authored IN_REGION edge becomes necessary. Traversed only for the
# facet, never for scope congruence. See DECISIONS.md D-22.
LOCATION_SENSES = OrderedDict([("Contained_In", "containedIn")])

EXCLUDED_SENSES = ["Member_Of", "Segment_Of", "Branch_Part_of"]

# Unsanctioned_Term, Acronym and Misspelling_of_term are all rdfs:subPropertyOf
# Synonym in RadLex. They must be read separately: a discouraged term is not a
# synonym, and a misspelling is not either.
ANN = ["Definition", "Source", "Synonym", "Acronym", "Unsanctioned_Term",
       "Misspelling_of_term", "Replaced_by", "Preferred_Name_for_Obsolete",
       "Comment", "Anatomical_Site", "Related_modality",
       "Radlex_version_of_class_change"]

ALL_SENSES = OrderedDict(list(PART_SENSES.items()) + list(LOCATION_SENSES.items()))


def rid_of(term):
    if not isinstance(term, URIRef):
        return None
    m = re.fullmatch(re.escape(RID) + r"(RID\d+)", str(term))
    return m.group(1) if m else None


def load():
    g = Graph()
    t = time.time()
    if os.path.exists(NT_CACHE) and os.path.getmtime(NT_CACHE) > os.path.getmtime(OWL_SRC):
        g.parse(NT_CACHE, format="nt"); src = "cache"
    else:
        g.parse(OWL_SRC, format="xml"); g.serialize(NT_CACHE, format="nt"); src = "RadLex.owl"
    print(f"loaded {len(g):,} triples from {src} in {time.time()-t:.0f}s")
    return g


def index(g):
    # The vocabulary is not multilingual. RadLex carries German labels and German
    # synonyms; both are dropped on import. Latin synonyms are kept, because Latin
    # anatomical nomenclature is an alternate term for the structure rather than a
    # translation for display.
    label_en = {}
    ann = defaultdict(lambda: defaultdict(list))
    for s, _, o in g.triples((None, RDFS.label, None)):
        r = rid_of(s)
        if r and getattr(o, "language", None) in ("en", None):
            label_en[r] = str(o)
    # Synonym is language-tagged in the OWL (en 17,402 / la 4,117 / de 2,244).
    # The CSV export flattens all three into one untagged column, so a term-match
    # check built on it silently compares English against Latin and German.
    for a in ANN:
        for s, _, o in g.triples((None, URIRef(RID + a), None)):
            r = rid_of(s)
            if not r:
                continue
            lang = getattr(o, "language", None)
            if a in ("Synonym", "Acronym", "Unsanctioned_Term", "Misspelling_of_term") \
                    and lang not in ("en", None):
                if lang == "la":
                    ann[r][a + "_la"].append(str(o))
                continue
            v = rid_of(o) or str(o)
            if v not in ann[r][a]:
                ann[r][a].append(v)

    parents, parts = defaultdict(list), defaultdict(list)
    for s, _, o in g.triples((None, RDFS.subClassOf, None)):
        r = rid_of(s)
        if not r:
            continue
        t = rid_of(o)
        if t:
            if t not in parents[r]:
                parents[r].append(t)
            continue
        if not isinstance(o, rdflib.BNode):
            continue
        prop, fill = g.value(o, OWL.onProperty), g.value(o, OWL.someValuesFrom)
        if prop is None or fill is None:
            continue
        pn, tf = str(prop).rsplit("/", 1)[-1], rid_of(fill)
        if pn in ALL_SENSES and tf:
            parts[r].append((ALL_SENSES[pn], tf))
    return label_en, dict(ann), parents, parts


def build(max_depth=12):
    g = load()
    label_en, ann, parents, parts = index(g)
    print(f"indexed: {len(label_en):,} English labels, {len(ann):,} annotated concepts, "
          f"{sum(len(v) for v in parents.values()):,} subClassOf, "
          f"{sum(len(v) for v in parts.values()):,} part-of axioms")

    seeds = list(dict.fromkeys(spec.ANATOMY_SEEDS))
    keep, frontier, depth = set(seeds), list(seeds), 0
    while frontier and depth < max_depth:
        nxt = []
        for r in frontier:
            for t in parents.get(r, []) + [t for _, t in parts.get(r, [])]:
                if t not in keep:
                    keep.add(t); nxt.append(t)
        frontier, depth = nxt, depth + 1

    nodes, n, retired = OrderedDict(), 0, []
    for r in sorted(keep, key=lambda x: int(x[3:])):
        if r not in label_en:
            continue
        n += 1
        a = ann.get(r, {})
        defn = a.get("Definition", [None])[0]
        nd = dict(al_id=f"AL-{n:06d}", rid=r, name=label_en[r], source_label=label_en[r],
                  definition=defn or f"Imported from RadLex {spec.RADLEX_VERSION}: {label_en[r]}.",
                  has_real_definition=bool(defn),
                  concept_source=a.get("Source", [None])[0],
                  source="imported", seed=(r in seeds),
                  synonyms=a.get("Synonym", [])[:6],
                  synonyms_la=a.get("Synonym_la", [])[:3],
                  acronyms=a.get("Acronym", []),
                  misspellings=a.get("Misspelling_of_term", []),
                  unsanctioned=a.get("Unsanctioned_Term", []),
                  change_log=a.get("Radlex_version_of_class_change", []))
        if a.get("Replaced_by") or a.get("Preferred_Name_for_Obsolete"):
            nd["replaced_by"] = a.get("Replaced_by", [])
            nd["obsolete_name"] = a.get("Preferred_Name_for_Obsolete", [])
            retired.append(r)
        nodes[r] = nd

    is_a, part_of, dup = [], [], 0
    for r in nodes:
        for p in parents.get(r, []):
            if p in nodes:
                is_a.append(dict(frm=r, to=p, source="imported", system="RADLEX",
                                 source_version=spec.RADLEX_VERSION))
        by_target = defaultdict(list)
        for sense, t in parts.get(r, []):
            if t in nodes:
                by_target[t].append(sense)
        for t, senses in by_target.items():
            if senses == ["containedIn"]:
                part_of.append(dict(frm=r, to=t, prop="containedIn", family="location",
                                    source="imported", system="RADLEX",
                                    source_version=spec.RADLEX_VERSION))
                continue
            mereo = [x for x in senses if x != "containedIn"]
            specific = [x for x in mereo if x != "generalPartOf"]
            if specific and "generalPartOf" in mereo:
                dup += 1
            part_of.append(dict(frm=r, to=t,
                                prop=(specific[0] if specific else "generalPartOf"),
                                family="mereology",
                                source="imported", system="RADLEX",
                                source_version=spec.RADLEX_VERSION))
            if "containedIn" in senses:
                part_of.append(dict(frm=r, to=t, prop="containedIn", family="location",
                                    source="imported", system="RADLEX",
                                    source_version=spec.RADLEX_VERSION))

    local_nodes, local_edges = OrderedDict(), []
    for la in spec.LOCAL_ANATOMY:
        local_nodes[la["local"]] = dict(
            al_id=la["local"], rid=None, name=la["name"], definition=la["definition"],
            source="local", source_status=la["source_status"], request=la.get("request"),
            note=la.get("note"), synonyms=[], unsanctioned=[])
        local_edges.append(dict(frm=la["local"], to=la["part_of"], prop="generalPartOf",
                                family="mereology",
                                source="local", source_status=la["source_status"],
                                request=la.get("request")))
    for ge in getattr(spec, "LOCAL_ANATOMY_EDGES", []):
        if ge["frm"] in nodes and ge["to"] in nodes:
            local_edges.append(dict(frm=ge["frm"], to=ge["to"], prop=ge["prop"],
                                    family=ge["family"], source="local",
                                    source_status=ge["source_status"],
                                    request=ge.get("request"), note=ge.get("note"),
                                    gap_fill=True))

    imported_facts = {}
    bound = ([f.get("radlex") for f in spec.FINDING_CLASSES] +
             [d.get("radlex") for d in spec.DIAGNOSES] +
             [a.get("radlex") for a in spec.ASSESSMENT_SCHEMES] +
             [d.get("radlex") for d in spec.DATA_ELEMENTS] +
             [v[2] for d in spec.DATA_ELEMENTS for v in d["values"]] +
             [m[3] for m in spec.MODALITIES])
    for r in [x for x in dict.fromkeys(bound) if x]:
        a, f = ann.get(r, {}), {}
        if a.get("Anatomical_Site"):
            f["anatomical_site"] = a["Anatomical_Site"]
        if a.get("Unsanctioned_Term"):
            f["unsanctioned"] = a["Unsanctioned_Term"]
        if a.get("Related_modality"):
            f["related_modality"] = a["Related_modality"]
        if a.get("Definition"):
            f["source_definition"] = a["Definition"][0]
        if a.get("Source"):
            f["concept_source"] = a["Source"][0]
        if a.get("Replaced_by") or a.get("Preferred_Name_for_Obsolete"):
            f["retired"] = True
            f["replaced_by"] = a.get("Replaced_by", [])
        if a.get("Synonym"):
            f["source_synonyms"] = a["Synonym"]
        if f:
            f["label"] = label_en.get(r)
            imported_facts[r] = f

    stats = dict(source="RadLex.owl", seeds=len(seeds), imported_nodes=len(nodes),
                 local_nodes=len(local_nodes), is_a_edges=len(is_a),
                 part_of_edges=len(part_of), local_edges=len(local_edges),
                 duplicate_part_assertions_dropped=dup, excluded_senses=EXCLUDED_SENSES,
                 anatomy_with_real_definition=sum(1 for v in nodes.values() if v["has_real_definition"]),
                 anatomy_with_unsanctioned_terms=sum(1 for v in nodes.values() if v["unsanctioned"]),
                 anatomy_retired=len(retired),
                 bound_concepts_with_imported_facts=len(imported_facts))
    return nodes, local_nodes, is_a, part_of, local_edges, imported_facts, stats


if __name__ == "__main__":
    nodes, local_nodes, is_a, part_of, local_edges, facts, stats = build()
    json.dump(dict(nodes=nodes, local_nodes=local_nodes, is_a=is_a, part_of=part_of,
                   local_edges=local_edges, imported_facts=facts, stats=stats),
              open("anatomy.json", "w"), indent=1)
    print(json.dumps(stats, indent=2))
    by = defaultdict(int)
    for e in part_of:
        by[e["prop"]] += 1
    print("part-of by sense:", dict(by))
    print("\nimported facts on bound concepts:")
    for r, f in facts.items():
        print(f"  {r:9s} {f.get('label','?'):46s} {[k for k in f if k!='label']}")
