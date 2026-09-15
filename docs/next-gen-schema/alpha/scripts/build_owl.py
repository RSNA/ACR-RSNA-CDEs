# -*- coding: utf-8 -*-
"""
Emits the generated OWL serialisation of the alpha CDE model.

RadLex is imported directly as the anatomy source of truth. AnatomicLocation
is a CDE node/role type; native RadLex class identities are referenced directly
and no parallel CDE anatomy vocabulary is generated.

Mapping from the JSON graph model to OWL:

  FindingClass node        -> owl:Class under cde:FindingClass
  Diagnosis node           -> owl:Class under cde:Diagnosis
  DataElement node         -> owl:ObjectProperty + a value-domain owl:Class
  Value node               -> owl:Class under that value domain
  Measurement node         -> owl:Class under cde:Measurement
  AnatomicLocation node    -> native RadLex owl:Class referenced directly
  AssessmentScheme node    -> owl:Class under cde:AssessmentScheme
  HAS_DATA_ELEMENT edge    -> subClassOf (prop some ValueDomain)
  narrow on that edge      -> subClassOf (prop only (V1 or V2 ...))
  HAS_VALUE edge           -> subClassOf between Value and its value domain
  SCOPED_TO {kind}         -> one of three scopedTo subproperties
  binding                  -> a cde:Binding individual + a skos mapping
  version block            -> flat annotations
"""
import json, datetime
import snomed
import rdflib
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS, DCTERMS
import spec
from pathlib import Path
from radlex_config import RADLEX_NS, RADLEX_ONTOLOGY_IRI

BASE   = "https://radelement.org/ng/"
CDE    = Namespace(BASE)
RADLEX = Namespace(RADLEX_NS)
SCT    = Namespace("http://snomed.info/id/")
TODAY  = Literal(datetime.date.today().isoformat(), datatype=XSD.date)

ONT_ALPHA = URIRef(BASE + "radcde-alpha")
RADLEX_ONTOLOGY = URIRef(RADLEX_ONTOLOGY_IRI)

ANN = [  # annotation properties the model uses
    ("localId",            "The type-prefixed identifier of the corresponding node in the definition graph."),
    ("nodeType",           "Which node type of the definition graph this entity serialises."),
    ("bindingSystem",      "Terminology identifier of a binding."),
    ("bindingCode",        "Code in that terminology."),
    ("sourceLabel",        "That terminology's label for the code, as of sourceVersion."),
    ("bindingMatch",       "SKOS mapping strength of the binding."),
    ("sourceVersion",      "Terminology release the binding was resolved against."),
    ("synonymTerm",        "An alternate term for the concept."),
    ("synonymType",        "synonym, abbreviation, acronym or eponym."),
    ("synonymScope",       "exact, narrow, broad or related. Stops a narrow synonym being treated as an exact hit."),
    ("rank",               "Position in an ordered value list. Present on every value of an element or on none."),
    ("versionNumber",      "Version of this object."),
    ("versionStatus",      "draft, proposed, published, retired or superseded."),
    ("created",            "Creation date."),
    ("lastModified",       "Last modification date."),
    ("quantityKind",       "The kind of quantity a measurement reports."),
    ("permittedUnit",      "A UCUM unit code permitted for a measurement."),
    ("measurementMethod",  "The convention by which a measurement is taken."),
    ("issuingAuthority",   "The body that issues an assessment scheme."),
    ("schemeVersion",      "The scheme's own version clock, independent of ours."),
    ("schemeScope",        "observation, exam or side."),
    ("scopeStrength",      "required, expected or unconstrained. Declares how binding a scope claim is."),
    ("modalityRestriction","Restricts an element or measurement to a subset of the modalities the finding is seen on."),
    ("criterion",          "A stated criterion carried as an annotation rather than as a defining condition."),
    ("epistemic",          "True where a relation holds between our knowledge of two things rather than between the things."),
    ("designNote",         "A note recorded during alpha construction."),
    ("sourceText",         "Report text an instance example was drawn from."),
    ("sourceRef",          "Where in the modelling corpus the example came from."),
    ("synonymOnlyHit",     "True where the RadLex binding is reachable only through the source's synonym field."),
    ("unsanctionedTerm",   "A term the source terminology explicitly discourages for this concept. "
                           "NOT a synonym: never emitted as skos:altLabel and never matched by duplicate detection."),
    ("conceptSource",      "The body the source terminology credits for the concept (Fleischner, PI-RADS, LI-RADS...)."),
    ("sourceChangeLog",    "The source terminology's own per-concept change history."),
    ("sourceDefinition",   "The source terminology's definition, kept distinct from ours."),
    ("replacedBy",         "Retirement pointer from the source terminology."),
    ("misspelling",        "A misspelling the source records for this concept. Like unsanctionedTerm, "
                           "a subproperty of the source's Synonym and therefore NOT a synonym."),
    ("isComponent",        "True where the class is reached only through HAS_COMPONENT."),
    ("mentionTerm",        "The term in the source text that a mention names."),
    ("radlexCompositionBase", "The RadLex head concept used when a CDE concept is represented compositionally."),
    ("radlexCompositionModifier", "A RadLex concept that modifies the compositional base."),
    ("typicality",         "How often the source shows the target: occasional, frequent, "
                           "very_frequent, obligate. Read forward, diagnosis to finding."),
    ("specificity",        "How much seeing the target narrows the differential: suggestive, "
                           "highly_suggestive, pathognomonic. Read backward, finding to diagnosis."),
    ("noImagingElements",  "True on a diagnosis carried only so causal edges have a target."),
    ("exclusiveValue",     "A value whose selection excludes every sibling. Used for a none "
                           "option on a multi-select element, where value disjointness alone "
                           "does not prevent none being asserted alongside a pattern."),
    ("narrowsTo",          "The subset of an element's values permitted at this point of use. "
                           "Advisory in alpha: enforced by lint, not by an axiom."),
    ("selectCardinality",  "single or multi. Single-select elements are declared owl:FunctionalProperty; "
                           "multi-select ones are not. Value disjointness alone does not give single-select."),
]

OBJ_PROPS = [
    ("scopedTo",               None, "Relates a definition to an AnatomicLocation.", {}),
    ("scopedToSpecific",       "scopedTo", "Scope checked by identity or subsumption. kind=specific.", {}),
    ("scopedToRegion",         "scopedTo", "Regional anatomic scope. The kind records authoring intent; no native RadLex predicate or traversal is implied.", {}),
    ("scopedToClass",          "scopedTo", "Scope checked taxonomically. kind=class.", {}),
    ("hasDataElement",         None, "Parent of every element property. Each DataElement is a subproperty.", {}),
    ("hasMeasurement",         None, "Relates a FindingClass or Diagnosis to a Measurement.", {}),
    ("hasMeasurementComponent",None, "Relates a Measurement to a component Measurement.", {}),
    ("derivedFromMeasurement", None, "Relates a Measurement to the measurements it is computed from.", {}),
    ("hasComponent",           None, "Relates a FindingClass to a sub-finding with no standalone meaning.", {}),
    ("componentOf",            None,
     "Inverse of hasComponent. Functional: a sub-finding with no standalone meaning belongs "
     "to exactly one whole. This is what lets a conditional relationship be carried on the "
     "component rather than asserted as a requirement on the whole.",
     dict(inverse="hasComponent", functional=True)),
    ("mayManifestAs",          None,
     "Evidential. The diagnosis can show itself as the target. Carries typicality (how often) "
     "and specificity (how much seeing it narrows the differential). Annotation-only.",
     dict(epistemic=True)),
    ("mayRepresent",           None,
     "Inverse of mayManifestAs. How a report reads: finding toward conclusion.",
     dict(inverse="mayManifestAs", epistemic=True)),
    ("mayCause",               None,
     "Causal. The source can produce the target as a distinct second entity. Distinct from "
     "mayManifestAs, which is about evidence rather than production.",
     dict(inference=False)),
    ("mayBeCausedBy",          None, "Inverse of mayCause.",
     dict(inverse="mayCause")),
    ("occursWith",             None,
     "Symmetric and associative. Seen together; asserts and excludes nothing about causality "
     "or sequence.", dict(symmetric=True)),
    ("mayBeRelatedTo",         None,
     "Symmetric catch-all for an association the author cannot yet type. A triage queue, not "
     "a home; every use is a candidate for replacement by a typed edge.",
     dict(symmetric=True)),
    ("hasEtiology",            None, "Relates a definition to the kind of cause behind it.", {}),
    ("assessedBy",             None, "Relates a FindingClass or Diagnosis to an AssessmentScheme.", {}),
    ("hasCategory",            None, "Relates an AssessmentScheme to one of its categories.", {}),
    ("seenOn",                 None, "The imaging techniques a finding is seen on.", {}),
    ("inSubspecialty",         None, "The radiology subspecialty a finding belongs to.", {}),
    # behaviour toward adjacent structures - the dominant content of the mass corpus
    ("actsOn",                 None, "A mass-effect relation between a finding and an adjacent structure.", {}),
    ("encases",                "actsOn", "Surrounds a structure circumferentially.", {}),
    ("invades",                "actsOn", "Extends into and disrupts a structure.", {}),
    ("displaces",              "actsOn", "Moves a structure from its expected position.", {}),
    ("obstructs",              "actsOn", "Occludes the lumen of a structure.", {}),
    ("erodes",                 "actsOn", "Destroys the substance of a structure.", {}),
    ("abuts",                  "actsOn", "Contacts a structure without disrupting it.", {}),
    ("causesFinding",          None, "A finding downstream of another finding.", dict(epistemic=False)),
    ("mayProgressTo",          None,
     "Identity-preserving evolution: the same entity in a later state. The relationship is "
     "authored explicitly; no additional temporal identity inference is asserted.",
     dict(epistemic=False)),
    ("mayProgressFrom",        None, "Inverse of mayProgressTo.",
     dict(inverse="mayProgressTo")),
]


# --------------------------------------------------------------------------
def new_graph():
    g = Graph()
    for p, n in [("cde", CDE), ("radlex", RADLEX), ("sct", SCT),
                 ("skos", SKOS), ("owl", OWL), ("dcterms", DCTERMS)]:
        g.bind(p, n)
    return g


def version_block(g, subj, number=1, status="draft"):
    g.add((subj, CDE.versionNumber, Literal(number)))
    g.add((subj, CDE.versionStatus, Literal(status)))
    g.add((subj, CDE.created, TODAY))
    g.add((subj, CDE.lastModified, TODAY))


MATCH_PROP = {"exactMatch": SKOS.exactMatch, "closeMatch": SKOS.closeMatch,
              "broadMatch": SKOS.broadMatch, "narrowMatch": SKOS.narrowMatch,
              "relatedMatch": SKOS.relatedMatch}


def add_sct(g, subj, key, table, slug):
    """Add a SNOMED CT binding. Codes are supplied, never written from memory."""
    if key not in table:
        return
    code, label, match = table[key]
    add_binding(g, subj, code, label, match, system="SNOMEDCT", slug=slug)


def add_binding(g, subj, code, source_label, match="exactMatch",
                system="RADLEX", slug=None):
    """Binding as an individual (W3C n-ary pattern) plus a plain SKOS mapping.

    For RadLex, sourceLabel is always the configured terminology's preferred
    English label rather than the CDE display term.
    """
    if not code:
        return
    if system == "RADLEX":
        try:
            ap = Path(__file__).with_name("anatomy.json")
            if ap.exists():
                ai = json.load(open(ap, encoding="utf-8"))
                source_label = ai.get("classes", {}).get(code, {}).get("label") or source_label
        except Exception:
            pass
    b = CDE[f"binding-{slug or str(subj).rsplit('/',1)[-1]}-{system}-{code}"]
    g.add((b, RDF.type, OWL.NamedIndividual))
    g.add((b, RDF.type, CDE.Binding))
    g.add((b, CDE.bindingSystem, Literal(system)))
    g.add((b, CDE.bindingCode, Literal(code)))
    g.add((b, CDE.sourceLabel, Literal(source_label)))
    g.add((b, CDE.bindingMatch, Literal(match)))
    g.add((b, CDE.sourceVersion, Literal(spec.RADLEX_VERSION)))
    version_block(g, b)
    g.add((subj, CDE.hasBinding, b))
    ns = RADLEX if system == "RADLEX" else SCT
    g.add((subj, MATCH_PROP.get(match, SKOS.closeMatch), ns[code]))


def add_synonyms(g, subj, syns, scopes=None):
    scopes = scopes or {}
    for term, typ in syns or []:
        s = BNode()
        g.add((subj, CDE.hasSynonym, s))
        g.add((s, CDE.synonymTerm, Literal(term)))
        g.add((s, CDE.synonymType, Literal(typ)))
        g.add((s, CDE.synonymScope, Literal(scopes.get(term, "exact"))))
        g.add((subj, SKOS.altLabel, Literal(term)))


def some(g, prop, cls):
    r = BNode()
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, prop))
    g.add((r, OWL.someValuesFrom, cls))
    return r


def only(g, prop, classes):
    if len(classes) == 1:
        target = classes[0]
    else:
        target = BNode()
        g.add((target, RDF.type, OWL.Class))
        coll = rdflib.collection.Collection(g, BNode(), list(classes))
        g.add((target, OWL.unionOf, coll.uri))
    r = BNode()
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, prop))
    g.add((r, OWL.allValuesFrom, target))
    return r


def intersection(g, members):
    c = BNode()
    g.add((c, RDF.type, OWL.Class))
    coll = rdflib.collection.Collection(g, BNode(), list(members))
    g.add((c, OWL.intersectionOf, coll.uri))
    return c


def annotate_axiom(g, subj, pred, obj, anns):
    """OWL 2 axiom annotation. A bare triple on a restriction bnode is RDF-legal
    but OWL tools drop it, so annotated axioms are reified as owl:Axiom."""
    ax = BNode()
    g.add((ax, RDF.type, OWL.Axiom))
    g.add((ax, OWL.annotatedSource, subj))
    g.add((ax, OWL.annotatedProperty, pred))
    g.add((ax, OWL.annotatedTarget, obj))
    for p_, v in anns:
        g.add((ax, p_, v))
    return ax


def disjoint(g, classes):
    for i in range(len(classes)):
        for j in range(i + 1, len(classes)):
            g.add((classes[i], OWL.disjointWith, classes[j]))


# ==========================================================================
# AUTHORED ALPHA MODULE
# ==========================================================================
def value_domain_name(de):
    return de["prop"][3:] + "Value" if de["prop"].startswith("has") else de["prop"] + "Value"


def build_alpha_graph(anat):
    def anat_uri(x):
        if not isinstance(x, str) or not x.startswith("RID"):
            raise ValueError(f"Anatomic references must be native RadLex RIDs, got {x!r}")
        if x not in anat.get("classes", {}):
            raise KeyError(f"RadLex anatomy reference {x} is not present in the configured source")
        return URIRef(anat["classes"][x]["iri"])

    g = new_graph()
    g.add((ONT_ALPHA, RDF.type, OWL.Ontology))
    g.add((ONT_ALPHA, OWL.imports, RADLEX_ONTOLOGY))
    g.add((ONT_ALPHA, DCTERMS.title, Literal("RadElement next-gen alpha: generated CDE definition layer")))
    g.add((ONT_ALPHA, OWL.versionInfo, Literal("alpha-0.1")))
    g.add((ONT_ALPHA, RDFS.comment, Literal(
        "A first-pass OWL rendering of the next-generation RadElement definition layer, "
        "built to test modelling decisions rather than to publish content. Clinical "
        "content is provisional and unvalidated. Every RadLex code was verified against "
        "the RadLex %s export." % spec.RADLEX_VERSION)))

    for name, comment in ANN:
        g.add((CDE[name], RDF.type, OWL.AnnotationProperty))
        g.add((CDE[name], RDFS.comment, Literal(comment)))
    g.add((CDE.hasBinding, RDF.type, OWL.AnnotationProperty))
    g.add((CDE.hasSynonym, RDF.type, OWL.AnnotationProperty))

    # ---- node-type classes
    for nt, comment in [
        ("DefinitionEntity", "Root of every entity in the definition layer."),
        ("FindingClass", "A discrete observable entity."),
        ("Diagnosis", "What a radiologist may conclude."),
        ("Value", "A single coded permissible answer for a DataElement."),
        ("Measurement", "A quantitative attribute, carrying method and conventions."),
        ("AssessmentScheme", "A named assessment scheme with an issuing authority and its own version clock."),
        ("AssessmentCategory", "One category of an assessment scheme."),
        ("Modality", "An imaging technique."),
        ("Subspecialty", "A radiology subspecialty."),
        ("Etiology", "A kind of cause. Target for hasEtiology."),
        ("Binding", "A terminology binding from a CDE concept to a code in another terminology."),
        ("AnatomicRefinementRule", "An explicit rule separating eligible anatomy targets, native RadLex predicates, and traversal behavior."),
    ]:
        g.add((CDE[nt], RDF.type, OWL.Class))
        g.add((CDE[nt], RDFS.comment, Literal(comment)))
        if nt not in ("DefinitionEntity", "Binding", "AssessmentCategory", "AnatomicRefinementRule"):
            g.add((CDE[nt], RDFS.subClassOf, CDE.DefinitionEntity))
    # AnatomicLocation is a CDE role/type, not a second anatomy vocabulary.
    # Native RadLex classes occupy this role in the graph; the generated CDE OWL does
    # not assert new subclass axioms on RadLex subjects.
    g.add((CDE.AnatomicLocation, RDF.type, OWL.Class))
    g.add((CDE.AnatomicLocation, RDFS.comment, Literal(
        "Application/model role for native RadLex anatomical concepts; no local anatomy concepts are created.")))
    disjoint(g, [CDE.FindingClass, CDE.Diagnosis, CDE.Value,
                 CDE.Measurement, CDE.AssessmentScheme, CDE.AnatomicRefinementRule])

    # ---- object properties
    for pname, parent, comment, opts in OBJ_PROPS:
        p = CDE[pname]
        g.add((p, RDF.type, OWL.ObjectProperty))
        g.add((p, RDFS.comment, Literal(comment)))
        if parent:
            g.add((p, RDFS.subPropertyOf, CDE[parent]))
        if opts.get("transitive"):
            g.add((p, RDF.type, OWL.TransitiveProperty))
        if opts.get("functional"):
            g.add((p, RDF.type, OWL.FunctionalProperty))
        if opts.get("symmetric"):
            g.add((p, RDF.type, OWL.SymmetricProperty))
        if opts.get("inverse"):
            g.add((p, OWL.inverseOf, CDE[opts["inverse"]]))
        if opts.get("epistemic"):
            g.add((p, CDE.epistemic, Literal(True)))

    # Refinement-rule fields are independent. Native RadLex properties are referenced
    # as vocabulary resources rather than redefined as CDE predicates.
    for ap, comment in [
        (CDE.hasAnatomicRefinementRule, "Links a definition class to a first-class anatomic refinement rule."),
        (CDE.refinesScope, "The authored scope entry narrowed by the rule."),
        (CDE.targetTaxonomyRoot, "Native RadLex taxonomy root used only to define eligible target concepts."),
        (CDE.allowedAnatomicTarget, "One exact native RadLex concept explicitly permitted as a refinement target."),
        (CDE.allowedRadLexPredicate, "One exact native RadLex object property permitted by the rule; multiple values remain distinct."),
        (CDE.traversalSpecification, "Explicit traversal behavior when authored; absence means no traversal behavior has been specified."),
        (CDE.includeTargetRoot, "Whether the taxonomy root itself is an eligible target."),
        (CDE.includeTargetDescendants, "Whether native rdfs:subClassOf descendants are eligible targets."),
    ]:
        g.add((ap, RDF.type, OWL.AnnotationProperty))
        g.add((ap, RDFS.comment, Literal(comment)))

    g.add((CDE.mayRepresent, CDE.designNote, Literal(
        "Inverse evidential reading from finding toward diagnostic conclusion. It covers "
        "direct appearances and indirect signs alike and carries no formal inference semantics.")))

    # ---- etiology
    et_uri = {}
    for eid, cls, name, rid, defn in spec.ETIOLOGIES:
        c = CDE[cls]
        et_uri[eid] = c
        g.add((c, RDF.type, OWL.Class))
        g.add((c, RDFS.subClassOf, CDE.Etiology))
        g.add((c, RDFS.label, Literal(name)))
        g.add((c, SKOS.definition, Literal(defn)))
        g.add((c, CDE.localId, Literal(eid)))
        g.add((c, CDE.nodeType, Literal("Etiology")))
        if rid:
            add_binding(g, c, rid, name, "closeMatch", slug=cls)
        add_sct(g, c, eid, snomed.ETIOLOGY, cls)
        version_block(g, c, status="proposed")

    # ---- modalities and subspecialties
    for mid, code, label, rid in spec.MODALITIES:
        c = CDE[code]
        g.add((c, RDF.type, OWL.Class))
        g.add((c, RDFS.subClassOf, CDE.Modality))
        g.add((c, RDFS.label, Literal(label)))
        g.add((c, CDE.localId, Literal(mid)))
        g.add((c, CDE.nodeType, Literal("Modality")))
        add_binding(g, c, rid, label, "exactMatch", slug=code)
        add_sct(g, c, mid, snomed.MODALITY, code)
        version_block(g, c, status="published")
    sp_uri = {}
    for sid, short, label in spec.SUBSPECIALTIES:
        c = CDE["SP_" + short.replace(" ", "")]
        sp_uri[sid] = c
        g.add((c, RDF.type, OWL.Class))
        g.add((c, RDFS.subClassOf, CDE.Subspecialty))
        g.add((c, RDFS.label, Literal(label)))
        g.add((c, CDE.localId, Literal(sid)))
        g.add((c, CDE.nodeType, Literal("Subspecialty")))
        version_block(g, c, status="published")
    md_uri = {m[0]: CDE[m[1]] for m in spec.MODALITIES}

    # ---- data elements: object property + value-domain class + value classes
    de_by_id, val_uri = {}, {}
    for de in spec.DATA_ELEMENTS:
        p = CDE[de["prop"]]
        vd = CDE[value_domain_name(de)]
        de_by_id[de["id"]] = dict(prop=p, domain=vd, spec=de)

        g.add((p, RDF.type, OWL.ObjectProperty))
        g.add((p, RDFS.subPropertyOf, CDE.hasDataElement))
        g.add((p, RDFS.label, Literal(de["name"])))
        g.add((p, RDFS.range, vd))
        g.add((p, SKOS.definition, Literal(de["definition"])))
        g.add((p, CDE.localId, Literal(de["id"])))
        g.add((p, CDE.nodeType, Literal("DataElement")))
        if de.get("scope_note"):
            g.add((p, CDE.designNote, Literal(de["scope_note"])))
        if de.get("local_note"):
            g.add((p, CDE.designNote, Literal(de["local_note"])))
        if de.get("multi_select"):
            g.add((p, CDE.selectCardinality, Literal("multi")))
            g.add((p, CDE.designNote, Literal(de.get("cardinality_note", ""))))
        else:
            g.add((p, RDF.type, OWL.FunctionalProperty))
            g.add((p, CDE.selectCardinality, Literal("single")))
        add_synonyms(g, p, de.get("synonyms"))
        if de.get("radlex"):
            add_binding(g, p, de["radlex"], de["name"], "closeMatch", slug=de["prop"])
        version_block(g, p, status="proposed")

        g.add((vd, RDF.type, OWL.Class))
        g.add((vd, RDFS.subClassOf, CDE.Value))
        g.add((vd, RDFS.label, Literal(de["name"] + " value")))
        g.add((vd, RDFS.comment, Literal(
            "Permitted answers for the '%s' element. The HAS_VALUE edges of the definition "
            "graph appear here as subclasses." % de["name"])))

        # Scope and modality belong to the ELEMENT, never to its values. A value is an
        # answer, not something seen; if an element is bound to one modality then every
        # answer it offers is available on that modality, and saying so per value adds
        # nothing. These are annotations on the property rather than class restrictions,
        # because the element is rendered as an object property and a property carries no
        # subClassOf.
        # Same convention as FindingClass and Diagnosis: a real scopedToRegion
        # restriction on the same property, not an annotation. A DataElement renders
        # as an object property and a property takes no subClassOf, so the restriction
        # goes on its DOMAIN: anything carrying a thyroid margin is scoped to the
        # thyroid gland. That is an axiom a reasoner acts on, and it says exactly what
        # the SCOPED_TO edge in the graph says.
        for rid in de.get("scoped_to", []):
            g.add((p, RDFS.domain, some(g, CDE.scopedToRegion, anat_uri(rid))))
        for mcode in de.get("modality", []):
            g.add((p, RDFS.domain, some(g, CDE.seenOn, CDE[mcode])))

        vclasses = []
        for vid, vname, vrid, vdef, vrank in de["values"]:
            cn = "V_" + vid.split("-")[1] + "_" + "".join(
                ch if ch.isalnum() else "" for ch in vname.title())
            c = CDE[cn]
            val_uri[vid] = c
            vclasses.append(c)
            g.add((c, RDF.type, OWL.Class))
            g.add((c, RDFS.subClassOf, vd))
            g.add((c, RDFS.label, Literal(vname)))
            g.add((c, SKOS.prefLabel, Literal(vname)))
            g.add((c, SKOS.definition, Literal(vdef)))
            g.add((c, CDE.localId, Literal(vid)))
            g.add((c, CDE.nodeType, Literal("Value")))
            if vrank is not None:
                g.add((c, CDE.rank, Literal(vrank)))
            if vrid:
                add_binding(g, c, vrid, vname, "exactMatch", slug=cn)
            add_sct(g, c, vid, snomed.VALUES, cn)
            version_block(g, c, status="proposed")
        disjoint(g, vclasses)
        # An exclusive none: selecting it excludes every sibling. Disjointness between
        # the values is not enough, because the element is multi-select and nothing
        # otherwise stops "none" being asserted alongside a pattern.
        exn = de.get("exclusive_none")
        if exn:
            none_uri = val_uri[exn]
            others = [v for k, v in val_uri.items()
                      if k in {x[0] for x in de["values"]} and k != exn]
            if others:
                # A general class axiom, not a constraint on the value itself: anything
                # whose calcification is none has ONLY none. Putting the restriction on
                # the value class would say something about the value, which is not the
                # thing being constrained.
                lhs = some(g, CDE[de["prop"]], none_uri)
                rhs = only(g, CDE[de["prop"]], [none_uri])
                g.add((lhs, RDFS.subClassOf, rhs))
                g.add((none_uri, CDE.exclusiveValue, Literal(
                    "Selecting this excludes every other value of %s." % de["name"])))
        # closed value list
        u = BNode()
        g.add((u, RDF.type, OWL.Class))
        coll = rdflib.collection.Collection(g, BNode(), vclasses)
        g.add((u, OWL.unionOf, coll.uri))
        g.add((vd, OWL.equivalentClass, u))

    # ---- measurements
    ms_uri = {}
    for ms in spec.MEASUREMENTS:
        c = CDE[ms["cls"]]
        ms_uri[ms["id"]] = c
        g.add((c, RDF.type, OWL.Class))
        g.add((c, RDFS.subClassOf, CDE.Measurement))
        g.add((c, RDFS.label, Literal(ms["name"])))
        g.add((c, SKOS.definition, Literal(ms["definition"])))
        g.add((c, CDE.localId, Literal(ms["id"])))
        g.add((c, CDE.nodeType, Literal("Measurement")))
        g.add((c, CDE.quantityKind, Literal(ms["quantity_kind"])))
        for u_ in ms["permitted_units"]:
            g.add((c, CDE.permittedUnit, Literal(u_)))
        g.add((c, CDE.measurementMethod, Literal(ms["method"])))
        if ms.get("note"):
            g.add((c, CDE.designNote, Literal(ms["note"])))
        version_block(g, c, status="proposed")
    for ms in spec.MEASUREMENTS:
        c = ms_uri[ms["id"]]
        for comp in ms.get("components", []):
            g.add((c, RDFS.subClassOf, some(g, CDE.hasMeasurementComponent, ms_uri[comp])))
        for d in ms.get("derived_from", []):
            g.add((c, RDFS.subClassOf, some(g, CDE.derivedFromMeasurement, ms_uri[d])))
        if ms.get("scoped_to_anatomy"):
            # normal-structure descriptor: scope on the measurement, no owning finding
            g.add((c, RDFS.subClassOf, some(g, CDE.scopedToClass,
                                            anat_uri(ms.get("scope_target", "RID478")))))
            g.add((c, CDE.designNote, Literal(
                "Carries anatomic scope directly and belongs to no FindingClass. This is the "
                "alternative to letting HAS_MEASUREMENT originate from an AnatomicLocation. "
                "")))

    # ---- assessment schemes
    as_uri = {}
    for a in spec.ASSESSMENT_SCHEMES:
        c = CDE[a["cls"]]
        as_uri[a["id"]] = c
        g.add((c, RDF.type, OWL.Class))
        g.add((c, RDFS.subClassOf, CDE.AssessmentScheme))
        g.add((c, RDFS.label, Literal(a["name"])))
        g.add((c, CDE.localId, Literal(a["id"])))
        g.add((c, CDE.nodeType, Literal("AssessmentScheme")))
        g.add((c, CDE.issuingAuthority, Literal(a["authority"])))
        g.add((c, CDE.schemeVersion, Literal(a["scheme_version"])))
        g.add((c, CDE.schemeScope, Literal(a["scope"])))
        if a.get("radlex"):
            add_binding(g, c, a["radlex"], a["name"], "exactMatch", slug=a["cls"])
        version_block(g, c, status="proposed")
        cats = []
        for cname, crid, crank in a["categories"]:
            cn = a["cls"] + "_" + "".join(ch if ch.isalnum() else "_" for ch in cname)
            cc = CDE[cn]
            cats.append(cc)
            g.add((cc, RDF.type, OWL.Class))
            g.add((cc, RDFS.subClassOf, CDE.AssessmentCategory))
            g.add((cc, RDFS.label, Literal(cname)))
            g.add((cc, CDE.rank, Literal(crank)))
            if crid:
                add_binding(g, cc, crid, cname, "exactMatch", slug=cn)
            g.add((c, RDFS.subClassOf, some(g, CDE.hasCategory, cc)))
        disjoint(g, cats)

    # ---- finding classes
    fc_uri = {}
    for fc in spec.FINDING_CLASSES:
        fc_uri[fc["cls"]] = CDE[fc["cls"]]
    dx_uri = {d["cls"]: CDE[d["cls"]] for d in spec.DIAGNOSES}

    for fc in spec.FINDING_CLASSES:
        c = fc_uri[fc["cls"]]
        g.add((c, RDF.type, OWL.Class))
        g.add((c, RDFS.label, Literal(fc["name"])))
        g.add((c, SKOS.prefLabel, Literal(fc["name"])))
        g.add((c, SKOS.definition, Literal(fc["definition"])))
        g.add((c, CDE.localId, Literal(fc["id"])))
        g.add((c, CDE.nodeType, Literal("FindingClass")))
        g.add((c, RDFS.subClassOf, fc_uri[fc["parent"]] if fc.get("parent") else CDE.FindingClass))
        if fc.get("radlex"):
            add_binding(g, c, fc["radlex"], fc["name"], fc.get("match", "exactMatch"), slug=fc["cls"])
        add_sct(g, c, fc["name"], snomed.FINDINGS, fc["cls"])
        add_synonyms(g, c, fc.get("synonyms"), fc.get("synonym_scope"))
        if fc.get("note"):
            g.add((c, CDE.designNote, Literal(fc["note"])))
        if fc.get("criterion"):
            g.add((c, CDE.criterion, Literal(fc["criterion"])))
        if fc.get("radlex_composition"):
            comp = fc["radlex_composition"]
            if comp.get("base"):
                g.add((c, CDE.radlexCompositionBase, RADLEX[comp["base"][0]]))
            for code, lbl in comp.get("modifiers", []):
                g.add((c, CDE.radlexCompositionModifier, RADLEX[code]))
        if fc.get("component"):
            g.add((c, CDE.isComponent, Literal(True)))
        version_block(g, c, status="proposed")

        eff_el, eff_ms, eff_mod = spec.expand(fc)
        for deid in eff_el:
            d = de_by_id[deid]
            r = some(g, d["prop"], d["domain"])
            g.add((c, RDFS.subClassOf, r))
        # Narrowing is advisory by default in alpha: an annotation plus a lint rule,
        # not an allValuesFrom axiom. Probe B3_RibFractureWithChronicAcuity proves
        # the hard form in the probes file. Promoting an authored narrow to an OWL
        # restriction requires an explicit per-narrow hard/soft flag and generator
        # support for flagged cases; no such flag exists in the authoring model yet.
        for deid, allowed in (fc.get("narrow") or {}).items():
            d = de_by_id[deid]
            g.add((c, CDE.narrowsTo, Literal(
                "%s: %s" % (d["spec"]["name"],
                            ", ".join(val_uri[v].split("/")[-1] for v in allowed)))))
        for msid in eff_ms:
            r = some(g, CDE.hasMeasurement, ms_uri[msid])
            g.add((c, RDFS.subClassOf, r))
        for asid in fc.get("assessed_by", []):
            g.add((c, RDFS.subClassOf, some(g, CDE.assessedBy, as_uri[asid])))
        for m in eff_mod:
            g.add((c, RDFS.subClassOf, some(g, CDE.seenOn, md_uri[m])))
        for s in fc.get("in_subspecialty", []):
            g.add((c, RDFS.subClassOf, some(g, CDE.inSubspecialty, sp_uri[s])))
        for target in fc.get("occurs_with", []):
            g.add((c, RDFS.subClassOf, some(g, CDE.occursWith, fc_uri[target])))
        for rule in fc.get("anatomic_refinement_rules", []):
            rule_uri = CDE[rule["id"].replace("-", "_")]
            g.add((rule_uri, RDF.type, OWL.NamedIndividual))
            g.add((rule_uri, RDF.type, CDE.AnatomicRefinementRule))
            g.add((c, CDE.hasAnatomicRefinementRule, rule_uri))
            g.add((rule_uri, CDE.refinesScope, anat_uri(rule["scope"])))
            if rule.get("target_root"):
                g.add((rule_uri, CDE.targetTaxonomyRoot, anat_uri(rule["target_root"])))
                g.add((rule_uri, CDE.includeTargetRoot, Literal(bool(rule.get("include_root", False)))))
                g.add((rule_uri, CDE.includeTargetDescendants, Literal(bool(rule.get("include_descendants", True)))))
            for target in rule.get("allowed_targets", []):
                g.add((rule_uri, CDE.allowedAnatomicTarget, anat_uri(target)))
            for predicate in rule.get("allowed_predicates", []):
                g.add((rule_uri, CDE.allowedRadLexPredicate, URIRef(predicate)))
            if rule.get("traversal") is not None:
                g.add((rule_uri, CDE.traversalSpecification, Literal(str(rule["traversal"]))))
        for prop, vid in fc.get("fixed", []):
            g.add((c, RDFS.subClassOf, some(g, CDE[prop], val_uri[vid])))
        for compname in fc.get("components", []):
            r = some(g, CDE.hasComponent, fc_uri[compname])
            g.add((c, RDFS.subClassOf, r))
        if fc.get("component_of"):
            g.add((c, RDFS.subClassOf, some(g, CDE.componentOf, fc_uri[fc["component_of"]])))
        for deid, mods in (fc.get("modality_scoped") or {}).items():
            g.add((de_by_id[deid]["prop"], CDE.modalityRestriction,
                   Literal("%s on %s: %s" % (fc["cls"], de_by_id[deid]["spec"]["name"],
                                             ", ".join(m.split("-")[-1] for m in mods)))))
        for sc in fc.get("scoped_to", []):
            rid, kind, strength = sc[0], sc[1], sc[2]
            prop = {"specific": CDE.scopedToSpecific, "region": CDE.scopedToRegion,
                    "class": CDE.scopedToClass}[kind]
            r = some(g, prop, anat_uri(rid))
            g.add((c, RDFS.subClassOf, r))
            anns = [(CDE.scopeStrength, Literal(strength)),
                    (CDE.designNote, Literal("SCOPED_TO kind=%s" % kind))]
            annotate_axiom(g, c, RDFS.subClassOf, r, anns)

    # defining conditions, applied after every class exists
    for fc in spec.FINDING_CLASSES:
        if not fc.get("defined"):
            continue
        c, members = fc_uri[fc["cls"]], [fc_uri[fc["parent"]]]
        for prop, target in fc["differentia"]:
            if prop.startswith("scopedTo"):
                members.append(some(g, CDE[prop], anat_uri(target)))
            else:                                   # any DataElement property
                members.append(some(g, CDE[prop], val_uri[target]))
        g.add((c, OWL.equivalentClass, intersection(g, members)))
        g.add((c, CDE.designNote, Literal(
            "Defined class: conditions are necessary and sufficient, so a reasoner classifies "
            "into it. Nothing about it is authored twice.")))

    for fc in spec.FINDING_CLASSES:
        for other in fc.get("disjoint_with", []):
            g.add((fc_uri[fc["cls"]], OWL.disjointWith, fc_uri[other]))

    for cls, rid, kind, strength in spec.SCOPE_ASSERTIONS:
        prop = {"specific": CDE.scopedToSpecific, "region": CDE.scopedToRegion,
                "class": CDE.scopedToClass}[kind]
        r = some(g, prop, anat_uri(rid))
        g.add((fc_uri[cls], RDFS.subClassOf, r))
        annotate_axiom(g, fc_uri[cls], RDFS.subClassOf, r,
                       [(CDE.scopeStrength, Literal(strength)),
                        (CDE.designNote, Literal("SCOPED_TO kind=%s" % kind))])

    # ---- diagnoses
    for dx in spec.DIAGNOSES:
        c = dx_uri[dx["cls"]]
        g.add((c, RDF.type, OWL.Class))
        g.add((c, RDFS.subClassOf, CDE.Diagnosis))
        g.add((c, RDFS.label, Literal(dx["name"])))
        g.add((c, SKOS.prefLabel, Literal(dx["name"])))
        g.add((c, SKOS.definition, Literal(dx["definition"])))
        g.add((c, CDE.localId, Literal(dx["id"])))
        g.add((c, CDE.nodeType, Literal("Diagnosis")))
        if dx.get("radlex"):
            add_binding(g, c, dx["radlex"], dx.get("source_label", dx["name"]),
                        dx.get("match", "exactMatch"), slug=dx["cls"])
        add_sct(g, c, dx["name"], snomed.DIAGNOSES, dx["cls"])
        if dx.get("synonym_only_hit"):
            g.add((c, CDE.synonymOnlyHit, Literal(True)))
        add_synonyms(g, c, dx.get("synonyms"))
        if dx.get("note"):
            g.add((c, CDE.designNote, Literal(dx["note"])))
        if dx.get("radlex_composition"):
            comp = dx["radlex_composition"]
            if comp.get("base"):
                g.add((c, CDE.radlexCompositionBase, RADLEX[comp["base"][0]]))
            for code, lbl in comp.get("modifiers", []):
                g.add((c, CDE.radlexCompositionModifier, RADLEX[code]))
        if dx.get("no_imaging_elements"):
            g.add((c, CDE.noImagingElements, Literal(True)))
        for target, typ, spec_ in dx.get("manifests_as", []):
            t = fc_uri.get(target) or dx_uri.get(target)
            r = some(g, CDE.mayManifestAs, t)
            g.add((c, RDFS.subClassOf, r))
            annotate_axiom(g, c, RDFS.subClassOf, r,
                           [(CDE.typicality, Literal(typ)),
                            (CDE.specificity, Literal(spec_))])
        for target, typ in dx.get("causes", []):
            t = fc_uri.get(target) or dx_uri.get(target)
            r = some(g, CDE.mayCause, t)
            g.add((c, RDFS.subClassOf, r))
            annotate_axiom(g, c, RDFS.subClassOf, r, [(CDE.typicality, Literal(typ))])
        for target in dx.get("progresses_to", []):
            g.add((c, RDFS.subClassOf, some(g, CDE.mayProgressTo, dx_uri[target])))
        for target in dx.get("occurs_with", []):
            g.add((c, RDFS.subClassOf, some(g, CDE.occursWith, dx_uri[target])))
        for et in dx.get("etiology", []):
            g.add((c, RDFS.subClassOf, some(g, CDE.hasEtiology, et_uri[et])))
        for sc in dx.get("scoped_to", []):
            rid, kind = sc[0], sc[1]
            prop = {"region": CDE.scopedToRegion, "specific": CDE.scopedToSpecific,
                    "class": CDE.scopedToClass}[kind]
            g.add((c, RDFS.subClassOf, some(g, prop, anat_uri(rid))))
        for deid in dx.get("elements", []):
            d = de_by_id[deid]
            g.add((c, RDFS.subClassOf, some(g, d["prop"], d["domain"])))
        for asid in dx.get("assessed_by", []):
            g.add((c, RDFS.subClassOf, some(g, CDE.assessedBy, as_uri[asid])))
        version_block(g, c, status="proposed")

    # ---- worked instance examples, as individuals
    for ex in spec.INSTANCE_EXAMPLES:
        i = CDE[ex["id"]]
        g.add((i, RDF.type, OWL.NamedIndividual))
        g.add((i, RDF.type, fc_uri[ex["finding"]]))
        g.add((i, RDFS.label, Literal(ex["id"])))
        g.add((i, CDE.sourceText, Literal(ex["source_text"])))
        g.add((i, CDE.sourceRef, Literal(ex["source_ref"])))
        if ex.get("note"):
            g.add((i, CDE.designNote, Literal(ex["note"])))
        if ex.get("asserted_note"):
            g.add((i, CDE.designNote, Literal(ex["asserted_note"])))
        if ex.get("location"):
            g.add((i, CDE.scopedToRegion, anat_uri(ex["location"])))
        for prop, vid in ex.get("values", {}).items():
            vi = CDE[ex["id"] + "_" + prop]
            g.add((vi, RDF.type, OWL.NamedIndividual))
            g.add((vi, RDF.type, val_uri[vid]))
            g.add((i, CDE[prop], vi))
        for msid, (val, unit) in ex.get("measurements", {}).items():
            mi = CDE[ex["id"] + "_" + msid.replace("-", "_")]
            g.add((mi, RDF.type, OWL.NamedIndividual))
            g.add((mi, RDF.type, ms_uri[msid]))
            g.add((mi, CDE.measuredValue, Literal(val)))
            g.add((mi, CDE.measuredUnit, Literal(unit)))
            g.add((i, CDE.hasMeasurement, mi))
        for n_, comp in enumerate(ex.get("components", []), 1):
            ci = CDE[f"{ex['id']}_component{n_}"]
            g.add((ci, RDF.type, OWL.NamedIndividual))
            g.add((ci, RDF.type, fc_uri[comp["finding"]]))
            g.add((i, CDE.hasComponent, ci))
            for prop, vid in comp.get("values", {}).items():
                cvi = CDE[f"{ex['id']}_component{n_}_{prop}"]
                g.add((cvi, RDF.type, OWL.NamedIndividual))
                g.add((cvi, RDF.type, val_uri[vid]))
                g.add((ci, CDE[prop], cvi))
            for msid, (val, unit) in comp.get("measurements", {}).items():
                mi = CDE[f"{ex['id']}_component{n_}_{msid.replace('-', '_')}"]
                g.add((mi, RDF.type, OWL.NamedIndividual))
                g.add((mi, RDF.type, ms_uri[msid]))
                g.add((mi, CDE.measuredValue, Literal(val)))
                g.add((mi, CDE.measuredUnit, Literal(unit)))
                g.add((ci, CDE.hasMeasurement, mi))
        if ex.get("diagnosis"):
            di = CDE[ex["id"] + "_dx"]
            g.add((di, RDF.type, OWL.NamedIndividual))
            g.add((di, RDF.type, dx_uri[ex["diagnosis"]]))
            g.add((i, CDE.mayRepresent, di))
        if ex.get("assessment"):
            scheme, cat = ex["assessment"]
            cat_iri = scheme + "_" + "".join(ch if ch.isalnum() else "_" for ch in cat)
            g.add((i, CDE.assessedByCategory, CDE[cat_iri]))
    for p in ["measuredValue", "measuredUnit"]:
        g.add((CDE[p], RDF.type, OWL.DatatypeProperty))
    g.add((CDE.assessedByCategory, RDF.type, OWL.ObjectProperty))

    return g, dict(fc=fc_uri, dx=dx_uri, de=de_by_id, val=val_uri,
                   ms=ms_uri, asch=as_uri, md=md_uri, sp=sp_uri)


if __name__ == "__main__":
    anat = json.load(open(Path(__file__).with_name("anatomy.json"), encoding="utf-8"))
    root = Path(__file__).resolve().parent.parent
    out = root
    (out / "rdfxml").mkdir(exist_ok=True)

    gb, idx = build_alpha_graph(anat)
    gb.serialize(destination=str(out / "radcde-alpha.ttl"), format="turtle")
    gb.serialize(destination=str(out / "rdfxml" / "radcde-alpha.rdf"), format="xml")

    source_ref = Path(anat["source"]["path"])
    src_path = (source_ref if source_ref.is_absolute() else root / source_ref).resolve()
    try:
        bundled_rel = src_path.relative_to(root)
    except ValueError:
        bundled_rel = None

    for d, ext in ((out, "ttl"), (out / "rdfxml", "rdf")):
        if bundled_rel is not None:
            rel = bundled_rel if d == out else Path("..") / bundled_rel
            radlex_catalog_uri = rel.as_posix()
        else:
            radlex_catalog_uri = src_path.as_uri()
        with open(d / "catalog-v001.xml", "w", encoding="utf-8") as f:
            f.write(
                '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
                '<catalog prefer="public" xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">\n'
                f'    <uri id="radlex" name="{RADLEX_ONTOLOGY}" uri="{radlex_catalog_uri}"/>\n'
                f'    <uri id="radcde-alpha" name="{ONT_ALPHA}" uri="radcde-alpha.{ext}"/>\n'
                '</catalog>\n')

    print("alpha triples  :", len(gb))
