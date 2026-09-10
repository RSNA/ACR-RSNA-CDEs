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
from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS, DCTERMS

BASE = "https://radelement.org/ng/"
CDE = Namespace(BASE)
ANAT = Namespace(BASE + "anatomy/")
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
    for p, n in [("cde", CDE), ("anat", ANAT), ("probe", PROBE),
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
          "unrelated":    "EXPECT UNRELATED to its pair - neither equivalent nor a subclass of it",
        }
        VERDICT = {
          "A1": "subclass", "A2": "subclass", "A3": "equivalent", "A4": "subclass",
          "A5": "subclass", "A6": "subclass",
          "E10": "inconsistent",
          "B1": "inconsistent", "B2": "inconsistent", "B3": "inconsistent",
          "B4": "inconsistent", "B5": "consistent", "B6": "inconsistent",
          "C1": "consistent", "C2": "inconsistent", "C3": "consistent",
          "D1": "consistent",
          "E1": "unrelated", "E2": "consistent", "E3": "subclass", "E4": "consistent",
          "E5": "consistent", "E6": "inconsistent", "E7": "consistent",
          "E8": "equivalent", "E9": "equivalent",
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
    probe("A1_NoduleInRightUpperLobe",
          "PROBE A1: a nodule in the right upper lobe",
          [CDE.PulmonaryNodule, some(g, CDE.scopedToRegion, ANAT.RID1303)],
          "A", "subsumed by PulmonaryNodule",
          "The differentia for PulmonaryNodule is scope to lung. The right upper lobe "
          "reaches lung by two partOf steps, so this fires only if the property chain "
          "scopedToRegion o partOf is working. This is decision-register item 3 made testable.")

    probe("A2_NoduleInSuperiorSegmentRLL",
          "PROBE A2: a nodule in the superior segment of the right lower lobe",
          [CDE.PulmonaryNodule, some(g, CDE.scopedToRegion, ANAT.RID1316)],
          "A", "subsumed by PulmonaryNodule",
          "Three partOf steps: segment -> lower lobe -> right lung, then one subsumption "
          "step right lung -> lung. The mixed chain named in classifier-placement-considerations.md.")

    probe("A3_PartSolidByAttenuation",
          "PROBE A3: a pulmonary nodule whose attenuation is part-solid",
          [CDE.PulmonaryNodule, some(g, CDE.hasAttenuation, CDE.V_000011_PartSolid)],
          "A", "subsumed by PartSolidPulmonaryNodule",
          "The condition-versus-subtype case. The subtype is defined, so nobody authors "
          "it twice and the component requirement attaches to it automatically.")

    probe("A4_NoduleInLocalSubpleuralRegion",
          "PROBE A4: a nodule in the locally coined subpleural region",
          [CDE.PulmonaryNodule, some(g, CDE.scopedToRegion, ANAT["AL_L0002"])],
          "A", "subsumed by PulmonaryNodule",
          "The scope path runs through two locally authored partOf edges before it reaches "
          "imported RadLex structure. Tests that local gap-fill edges participate in closure.")

    probe("A5_NoduleInThyroidLobe",
          "PROBE A5: a nodule in the left lobe of the thyroid gland",
          [CDE.ThyroidNodule, some(g, CDE.scopedToRegion, ANAT.RID7579)],
          "A", "subsumed by ThyroidNodule",
          "Same mechanism in a second organ, to check the pattern is not lung-specific.")

    probe("A6_CystWithMuralNodule",
          "PROBE A6: a cyst with a mural nodule component",
          [CDE.RenalCyst, some(g, CDE.hasComponent, CDE.MuralNodule)],
          "A", "subsumed by ComplexRenalCyst",
          "The second conditional-relationship case, and it fires in the opposite direction "
          "from the part-solid one. Nothing here asserts a composition value. The chain is: "
          "a mural nodule is necessarily componentOf some ComplexCyst, componentOf is "
          "functional, so the cyst holding it IS that complex cyst. This is the case "
          "03-conditional-relationships.md asks for under its TODO.")

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
          "The 30 mm boundary is carried as disjointness, not as a size condition. "
          "See DECISIONS.md D-07 for why the criterion itself is an annotation.")

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
          "PulmonaryNodule narrows margin to smooth, lobulated, irregular, spiculated. "
          "Narrowing at the point of use is an allValuesFrom axiom rather than an edge "
          "property, so a reasoner enforces it. This is the FHIR-profile behaviour named "
          "in 02-data-element.md, made checkable.")

    probe("B4_FindingThatIsAlsoADiagnosis",
          "PROBE B4: something that is both a FindingClass and a Diagnosis",
          [CDE.FindingClass, CDE.Diagnosis],
          "B", "unsatisfiable",
          "The node types are declared disjoint. This is what stops a named cyst drifting "
          "between the two layers, which 02-modeling-case-cyst.md raises as an open question.")

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
          [CDE.ThyroidNodule, some(g, CDE.scopedToRegion, ANAT.RID1301)],
          "B", "SATISFIABLE - this one is expected to stay white",
          "Deliberate negative control. scopedToRegion is not functional and lung and "
          "thyroid are not declared disjoint, so nothing rules this out. It shows what "
          "the model does NOT check, which matters for the strength property: strength "
          "declares how binding a scope claim is, and no OWL axiom currently carries it.")

    # ---------------- Group C: the proposed MAY_PROGRESS_TO edge ------------
    probe("C1_NoduleProgressingToMass",
          "PROBE C1: a nodule with a mayProgressTo edge to a mass",
          [CDE.PulmonaryNodule, some(g, CDE.mayProgressTo, CDE.PulmonaryMass)],
          "C", "SATISFIABLE",
          "The edge as a plain relation between two individuals is fine. Nothing is "
          "contradicted, because the nodule and the mass are two different individuals. "
          "This is the edge read as sequence only, and at that reading it carries no "
          "identity claim and no more force than an annotation.")

    probe("C2_IdentityPreservingProgression",
          "PROBE C2: one entity that is both the earlier and the later state",
          [CDE.PulmonaryNodule, CDE.PulmonaryMass],
          "C", "unsatisfiable",
          "This is what 'identity-preserving' means in a model with no time: the same "
          "individual instantiates both endpoints. It is probe B2 under another name. "
          "Progression edges characteristically join disjoint classes (acute/chronic, "
          "infarct/encephalomalacia), so this is not special to nodule and mass. It is "
          "what the edge costs whenever it is inference-bearing.")

    probe("C3_ProgressionWithinOneClass",
          "PROBE C3: a cyst that may progress to a cyst",
          [CDE.RenalCyst, some(g, CDE.mayProgressTo, CDE.RenalCyst)],
          "C", "SATISFIABLE",
          "The shape that actually works: progression within one class, where what changes "
          "is the value of an attribute rather than the class. RadLex models acute and "
          "chronic this way, as children of temporal descriptor RID5716, and carries no "
          "'acute hemorrhage' or 'chronic hemorrhage' concept at all.")

    # ---------------- Group E: mechanisms nothing else exercises ------------
    probe("E1_ScopeDoesNotTravelAlongContainedIn",
          "PROBE E1: a finding scoped to the kidney",
          [CDE.FindingClass, some(g, CDE.scopedToRegion, ANAT.RID205)],
          "E", "NOT subsumed by E2, which is expected to stay separate",
          "Deliberate negative. The kidney reaches the abdomen only through Contained_In, and "
          "scope congruence chases partOf alone, so this must NOT classify under a class scoped "
          "to the abdomen. If the two ever merge, containedIn has leaked into the partOf family "
          "and a scope claim can travel along a location link.")

    probe("E2_ScopedToAbdomen",
          "PROBE E2: a finding scoped to the abdomen",
          [CDE.FindingClass, some(g, CDE.scopedToRegion, ANAT.RID56)],
          "E", "SATISFIABLE, and must not subsume E1",
          "The other half of E1.")

    probe("E3_ScopeTravelsAlongLocalGapFill",
          "PROBE E3: a finding scoped to the lung parenchyma",
          [CDE.FindingClass, some(g, CDE.scopedToRegion, ANAT.RID35739)],
          "E", "subsumed by E4",
          "RadLex gives lung parenchyma exactly one edge, IS_A parenchyma, and never connects "
          "it to the lung. A local gap-fill partOf edge supplies that. If this stops "
          "classifying under E4, the gap-fill has been lost and everything scoped to lung "
          "parenchyma has quietly detached from the lung.")

    probe("E4_ScopedToLung",
          "PROBE E4: a finding scoped to the lung",
          [CDE.FindingClass, some(g, CDE.scopedToRegion, ANAT.RID1301)],
          "E", "SATISFIABLE, and should subsume E3",
          "The other half of E3.")

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

    # ---------------- Group D: what the reasoner cannot check ---------------
    probe("D1_FindingClassWithNoAnatomicAnchor",
          "PROBE D1: a finding class with no anatomic anchor",
          [CDE.FindingClass],
          "D", "SATISFIABLE - expected to stay white",
          "The lint rules that replace inheritance are not axioms. Nothing here is "
          "contradictory, and no reasoner will object to a class with no location, no "
          "pattern applied, or an element authored twice. Those checks live in "
          "scripts/spec.py lint() and run at authoring time, which is exactly what the "
          "pattern decision commits to: consistency by generation and linting rather than "
          "by inheritance. D1 staying white is the point. Knowing where a constraint "
          "cannot live is the difference between a rule and a hope.",
          primitive=True)

    return g


if __name__ == "__main__":
    out = "/mnt/user-data/outputs/radcde-alpha"
    g = build()
    g.serialize(destination=f"{out}/radcde-probes.ttl", format="turtle")
    g.serialize(destination=f"{out}/rdfxml/radcde-probes.rdf", format="xml")
    print("probe triples:", len(g))
