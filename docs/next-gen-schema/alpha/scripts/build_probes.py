# -*- coding: utf-8 -*-
"""
A separate module of deliberate test cases. Import it, run a reasoner, and see
which ones the model catches.

Kept out of radcde-alpha.ttl on purpose: some of these are meant to be
unsatisfiable, and an ontology that ships with unsatisfiable classes is
indistinguishable from a broken one.

Group A probes should classify somewhere useful.
Group B probes should turn red. If one of them does not, the constraint it
tests is not actually being enforced.
"""
import os
import rdflib
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS

BASE = "https://radelement.org/ng/"
CDE = Namespace(BASE)
RADLEX = Namespace("http://www.radlex.org/RID/")
PROBE = Namespace(BASE + "probe/")
ONT = URIRef(BASE + "radcde-probes")


def some(g, prop, cls):
    r = BNode()
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, prop))
    g.add((r, OWL.someValuesFrom, cls))
    return r


def inter(g, members):
    c = BNode()
    g.add((c, RDF.type, OWL.Class))
    coll = rdflib.collection.Collection(g, BNode(), list(members))
    g.add((c, OWL.intersectionOf, coll.uri))
    return c


def build():
    g = Graph()
    for p, n in [("cde", CDE), ("radlex", RADLEX), ("probe", PROBE),
                 ("owl", OWL), ("skos", SKOS), ("dcterms", DCTERMS)]:
        g.bind(p, n)
    g.add((ONT, RDF.type, OWL.Ontology))
    g.add((ONT, OWL.imports, URIRef(BASE + "radcde-alpha")))
    g.add((ONT, DCTERMS.title, Literal("RadElement next-gen alpha: probes")))
    g.add((ONT, RDFS.comment, Literal(
        "Deliberate test cases. Run a reasoner over this module. Group A probes should "
        "classify under something informative. Group B probes should go red. A Group B "
        "probe that stays white means the constraint it tests is not being enforced.")))

    def probe(name, label, members, group, expect, why, primitive=False):
        # Set per probe, not guessed from the expect string. The three outcomes look
        # different in Protege and are easy to confuse: a probe whose description exactly
        # restates an existing definition comes back EQUIVALENT, which appears as a yellow
        # row in the Equivalent To box and never moves in the tree. A probe whose
        # description is narrower comes back a SUBCLASS, which does move once the hierarchy
        # dropdown is set to Inferred. Only inconsistency shows as colour.
        OUTCOME = {
          "inconsistent": "EXPECT INCONSISTENT - turns red under owl:Nothing",
          "equivalent":   "EXPECT EQUIVALENT to an existing class - yellow row in Equivalent To, "
                          "does NOT move in the tree",
          "subclass":     "EXPECT SUBCLASS of an existing class - yellow row in SubClass Of, "
                          "moves in the tree when the dropdown is set to Inferred",
          "consistent":   "EXPECT CONSISTENT and nothing further - stays where it is, no yellow rows",
        }
        VERDICT = {
          "A3": "equivalent", "A6": "subclass", "C1": "equivalent",
          "E10": "inconsistent",
          "B1": "inconsistent", "B2": "inconsistent", "B3": "inconsistent",
          "B4": "inconsistent", "B5": "consistent", "B6": "inconsistent",
          "D1": "consistent",
          "E1": "consistent", "E2": "consistent", "E5": "consistent", "E6": "inconsistent", "E7": "consistent",
          "E8": "equivalent", "E9": "equivalent",
          "E11": "inconsistent", "E12": "inconsistent",
        }
        tag = OUTCOME[VERDICT[name.split("_")[0]]]
        c = PROBE[name]
        g.add((c, RDF.type, OWL.Class))
        g.add((c, RDFS.label, Literal(f"{label.split(':')[0]} [{tag}]:{label.split(':', 1)[1]}")))
        g.add((c, RDFS.comment, Literal(
            "Deliberate test case, not part of the vocabulary. " + why + " "
            "If this probe does not do what its label says, a constraint has been lost or "
            "added. Only inconsistency shows as colour, so a probe expecting EQUIVALENT or "
            "SUBCLASS fails silently: check the Description panel, where the reasoner's "
            "conclusions appear as yellow rows, rather than looking for a colour in the tree.")))
        g.add((c, RDFS.subClassOf if primitive else OWL.equivalentClass, inter(g, members)))
        g.add((c, CDE.designNote, Literal(f"[Group {group}] expect: {expect}. {why}")))
        return c

    # ---------------- Group A: should classify -----------------------------
    probe("A3_PartSolidByAttenuation",
          "PROBE A3: a pulmonary nodule whose attenuation is part-solid",
          [CDE.PulmonaryNodule, some(g, CDE.hasAttenuation, CDE.V_000011_PartSolid)],
          "A", "subsumed by PartSolidPulmonaryNodule",
          "The condition-versus-subtype case. The subtype is defined, so nobody authors "
          "it twice and the component requirement attaches to it automatically.")

    probe("A6_CystWithMuralNodule",
          "PROBE A6: a cyst with a mural nodule component",
          [CDE.RenalCyst, some(g, CDE.hasComponent, CDE.MuralNodule)],
          "A", "subsumed by ComplexRenalCyst",
          "The second conditional-relationship case, and it fires in the opposite direction "
          "from the part-solid one. Nothing here asserts a composition value. The chain is: "
          "a mural nodule is necessarily componentOf some ComplexCyst, componentOf is "
          "functional, so the cyst holding it IS that complex cyst.")

    # ---------------- Group B: should go red -------------------------------
    probe("B1_SolidAndPartSolid",
          "PROBE B1: a nodule that is both solid and part-solid",
          [CDE.PulmonaryNodule,
           some(g, CDE.hasAttenuation, CDE.V_000010_Solid),
           some(g, CDE.hasAttenuation, CDE.V_000011_PartSolid)],
          "B", "unsatisfiable",
          "Value disjointness. Without it, a single-select element is single-select only "
          "by convention. Note this bites through someValuesFrom because the value classes "
          "are disjoint, not because of any cardinality axiom.")

    probe("B2_NoduleThatIsAMass",
          "PROBE B2: something that is both a nodule and a mass",
          [CDE.PulmonaryNodule, CDE.PulmonaryMass],
          "B", "unsatisfiable",
          "The current definition model declares PulmonaryNodule and PulmonaryMass disjoint. "
          "This probe verifies that the class distinction remains reasoner-enforced rather than "
          "only a naming convention.")

    def only_(prop, classes):
        u = BNode()
        g.add((u, RDF.type, OWL.Class))
        coll = rdflib.collection.Collection(g, BNode(), list(classes))
        g.add((u, OWL.unionOf, coll.uri))
        r = BNode()
        g.add((r, RDF.type, OWL.Restriction))
        g.add((r, OWL.onProperty, prop))
        g.add((r, OWL.allValuesFrom, u))
        return r

    probe("B3_RibFractureWithChronicAcuity",
          "PROBE B3: a rib fracture reported as chronic",
          [CDE.RibFracture,
           only_(CDE.hasAcuity, [CDE.V_000330_Acute, CDE.V_000332_Healing,
                                 CDE.V_000333_Healed, CDE.V_000335_IndeterminateAge]),
           some(g, CDE.hasAcuity, CDE.V_000334_Chronic)],
          "B", "unsatisfiable",
          "RibFracture narrows Acuity to acute, healing, healed, or indeterminate age. "
          "Chronic remains a value of the reusable Acuity DataElement but is excluded at this "
          "point of use with an allValuesFrom restriction. This probe verifies that the class-" 
          "specific narrowing is reasoner-enforced.")

    probe("B4_FindingThatIsAlsoADiagnosis",
          "PROBE B4: something that is both a FindingClass and a Diagnosis",
          [CDE.FindingClass, CDE.Diagnosis],
          "B", "unsatisfiable",
          "FindingClass and Diagnosis are intentionally disjoint node types. This probe "
          "verifies that a concept cannot simultaneously occupy both semantic roles.")

    probe("B6_SimpleCystWithMuralNodule",
          "PROBE B6: a simple cyst with a mural nodule",
          [CDE.SimpleRenalCyst, some(g, CDE.hasComponent, CDE.MuralNodule)],
          "B", "unsatisfiable",
          "The conditional actually bites. SimpleCyst fixes composition to cystic; the mural "
          "nodule forces the same cyst to be a ComplexCyst, whose composition is mixed cystic "
          "and solid. hasComposition is functional (D-02) and the two values are disjoint, so "
          "the contradiction surfaces. Note this needed three separate decisions to work: "
          "functional componentOf, functional hasComposition, and disjoint values. Remove any "
          "one and this probe goes white.")

    probe("B5_ThyroidNoduleInLung",
          "PROBE B5: a thyroid nodule located in the lung",
          [CDE.ThyroidNodule, some(g, CDE.scopedToRegion, RADLEX.RID1301)],
          "B", "SATISFIABLE - this one is expected to stay white",
          "Deliberate negative control. scopedToRegion is not functional and lung and "
          "thyroid are not declared disjoint, so nothing rules this out. It shows what "
          "the model does NOT check, which matters for the strength property: strength "
          "declares how binding a scope claim is, and no OWL axiom currently carries it.")

    # ---------------- Group C: authored progression --------------------------
    probe("C1_ParapneumonicEffusionProgressesToEmpyema",
          "PROBE C1: parapneumonic effusion may progress to empyema",
          [CDE.ParapneumonicEffusion, some(g, CDE.mayProgressTo, CDE.Empyema)],
          "C", "equivalent to ParapneumonicEffusion",
          "ParapneumonicEffusion currently authors MAY_PROGRESS_TO Empyema. Because that "
          "restriction is already part of the class definition, intersecting the class with "
          "the same progression restriction should not narrow it further. This probe verifies "
          "that the authored progression axiom remains present." )

    # ---------------- Group E: mechanisms nothing else exercises ------------
    probe("E1_KidneyPartOfUrinaryTract",
          "PROBE E1: native kidney Part_Of urinary tract relationship",
          [RADLEX.RID205, some(g, RADLEX.Part_Of, RADLEX.RID204)],
          "E", "SATISFIABLE",
          "Preserves the exact native Part_Of predicate. This probe does not authorize any "
          "application traversal or substitution with another RadLex property.")

    probe("E2_KidneyContainedInRetroperitoneum",
          "PROBE E2: native kidney Contained_In retroperitoneum relationship",
          [RADLEX.RID205, some(g, RADLEX.Contained_In, RADLEX.RID431)],
          "E", "SATISFIABLE",
          "Preserves the distinct native Contained_In fact alongside Part_Of. The CDE layer "
          "does not rewrite either predicate or use one as a proxy for the other.")

    probe("E5_MultiSelectAllowsTwoValues",
          "PROBE E5: a pulmonary nodule with popcorn and punctate calcification",
          [CDE.PulmonaryNodule,
           some(g, CDE.hasCalcification, CDE.V_000032_Popcorn),
           some(g, CDE.hasCalcification, CDE.V_000033_Punctate)],
          "E", "SATISFIABLE",
          "The counterpart to B1. Calcification is deliberately multi-select, so two patterns "
          "co-occurring must remain satisfiable. If this goes red, something has declared the "
          "element functional and a lesion can no longer carry two calcification patterns.")

    probe("E6_SingleSelectOnAcuity",
          "PROBE E6: a rib fracture that is both acute and healed",
          [CDE.RibFracture,
           some(g, CDE.hasAcuity, CDE.V_000330_Acute),
           some(g, CDE.hasAcuity, CDE.V_000333_Healed)],
          "E", "unsatisfiable",
          "Acuity is single-select. Disjoint values alone would not catch this, because two "
          "different fillers are possible; it is caught because the property is declared "
          "functional. Removing either the disjointness or the functional declaration turns "
          "this white.")

    probe("E7_AtelectasisAxesAreIndependent",
          "PROBE E7: compressive atelectasis with a rounded morphology",
          [CDE.Atelectasis,
           some(g, CDE.hasAtelectasisMechanism, CDE.V_000410_Compressive),
           some(g, CDE.hasAtelectasisMorphology, CDE.V_000420_Rounded)],
          "E", "SATISFIABLE",
          "The restructure that replaced five atelectasis subtypes with two elements rests on "
          "the axes being independent: a rounded atelectasis is characteristically compressive. "
          "If this ever goes red the two have been made to partition one another, and the "
          "subtype question reopens.")

    probe("E8_PartSolidWithItsSolidComponent",
          "PROBE E8: a part-solid nodule whose component is solid",
          [CDE.PartSolidPulmonaryNodule,
           some(g, CDE.hasComponent,
                inter(g, [CDE.SolidComponentOfPartSolidNodule,
                          some(g, CDE.hasAttenuation, CDE.V_000010_Solid)]))],
          "E", "SATISFIABLE",
          "The resolution B1 rules out on one entity. A report saying 'part-solid nodule with "
          "a 4 mm solid component' states both values, and they are consistent because they sit "
          "on two entities: the nodule is part-solid, its component is solid. Attenuation is "
          "functional and its values are disjoint, so this only works because hasComponent "
          "supplies the second entity. Read together with B1: one entity cannot hold both, two "
          "can, and the component edge is what makes them two.")

    probe("E9_BothValuesStatedResolveToTheSubtype",
          "PROBE E9: a pulmonary nodule with part-solid attenuation and a solid component",
          [CDE.PulmonaryNodule,
           some(g, CDE.hasAttenuation, CDE.V_000011_PartSolid),
           some(g, CDE.hasComponent,
                inter(g, [CDE.SolidComponentOfPartSolidNodule,
                          some(g, CDE.hasAttenuation, CDE.V_000010_Solid)]))],
          "E", "subsumed by PartSolidPulmonaryNodule",
          "The full path. Asserted at the parent class with both attenuation values present, "
          "one on the nodule and one on its component. It must stay satisfiable AND classify "
          "into the part-solid subtype. E8 shows the two values coexist; this shows the "
          "coexistence does not block the classification that A3 performs.")

    probe("E10_NoCalcificationPlusAPattern",
          "PROBE E10: a nodule with no calcification and popcorn calcification",
          [CDE.PulmonaryNodule,
           some(g, CDE.hasCalcification, CDE.V_000030_None),
           some(g, CDE.hasCalcification, CDE.V_000032_Popcorn)],
          "E", "unsatisfiable",
          "Calcification is multi-select, so value disjointness alone does not stop none being "
          "asserted alongside a pattern: two different fillers are permitted. The none value "
          "carries its own allValuesFrom restriction to close that, and this probe is what "
          "proves it. Read against E5, which asserts two real patterns together and must stay "
          "satisfiable.")

    probe("E11_EpiduralCannotBeCrescentic",
          "PROBE E11: an epidural hematoma with crescentic collection shape",
          [CDE.EpiduralHematoma,
           some(g, CDE.hasCollectionShape, CDE.V_000371_Crescentic)],
          "E", "unsatisfiable",
          "The current alpha provisionally models epidural hematoma with a fixed biconvex collection-shape constraint. "
          "Collection shape is single-select, so asserting crescentic tests whether the fixed-value mechanism makes "
          "the modeled combination inconsistent. This is a mechanism test, not a radiologist-validated clinical rule.")

    probe("E12_SubduralCannotBeBiconvex",
          "PROBE E12: a subdural hematoma with biconvex collection shape",
          [CDE.SubduralHematoma,
           some(g, CDE.hasCollectionShape, CDE.V_000370_Biconvex)],
          "E", "unsatisfiable",
          "The current alpha provisionally models subdural hematoma with a fixed crescentic collection-shape constraint. "
          "Collection shape is single-select, so asserting biconvex tests whether the fixed-value mechanism makes "
          "the modeled combination inconsistent. This is a mechanism test, not a radiologist-validated clinical rule.")

    # ---------------- Group D: what the reasoner cannot check ---------------
    probe("D1_FindingClassWithNoAnatomicAnchor",
          "PROBE D1: a finding class with no anatomic anchor",
          [CDE.FindingClass],
          "D", "SATISFIABLE - expected to stay white",
          "The requirement that a top-level FindingClass have an anatomic scope is an "
          "authoring lint rule, not an OWL axiom. A reasoner therefore should not make this "
          "primitive test class inconsistent merely because it lacks a location. This probe "
          "keeps the boundary between authoring validation and ontology semantics explicit.",
          primitive=True)

    return g


if __name__ == "__main__":
    out = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    g = build()
    g.serialize(destination=f"{out}/radcde-probes.ttl", format="turtle")
    g.serialize(destination=f"{out}/rdfxml/radcde-probes.rdf", format="xml")
    print("probe triples:", len(g))
