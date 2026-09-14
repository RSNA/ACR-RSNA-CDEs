# -*- coding: utf-8 -*-
"""
Generates MECHANISMS.md: what each mechanism does and why it is there.

One row per mechanism. No decision numbers, no cross-references, no history.
If a mechanism is contested or unfinished, that is stated in its own entry
rather than pointing somewhere else.
"""
import json, datetime
import spec
from pathlib import Path

OUT = str(Path(__file__).resolve().parent.parent)

# (mechanism, what it does, why it is this way, status)
MECHANISMS = [

    # ---- identity and anchoring -------------------------------------------
    ("Binding to several terminologies without a primary designation",
     "A node may bind to several terminologies. Each binding records the terminology, code, "
     "the source terminology's own label, the SKOS match strength and the release it was "
     "resolved against. No binding is designated primary or secondary.",
     "Different terminologies may cover different kinds of concepts well. The model records "
     "the bindings that are useful without forcing a hierarchy among terminology systems. "
     "Anatomy identity is handled separately by the direct RadLex anatomy import.",
     "applied"),

    ("RadLex composition for concepts without one exact RadLex binding",
     "When a CDE concept can be represented from existing RadLex concepts rather than one "
     "pre-coordinated RadLex concept, `radlex_composition` records a base concept plus zero or "
     "more modifiers.",
     "The composition preserves useful RadLex semantics without treating absence of a single "
     "pre-coordinated term as a terminology defect.",
     "applied"),

    ("Terms RadLex discourages are not treated as synonyms",
     "Terms the source explicitly discourages are imported as `unsanctionedTerm`, never as "
     "`skos:altLabel`, and are excluded from duplicate detection.",
     "In RadLex, `Unsanctioned_Term`, `Acronym` and `Misspelling_of_term` are all "
     "subproperties of `Synonym`. Read naively, a search for 'nodule' matches 'mass' "
     "through a term RadLex explicitly rejects.",
     "applied"),

    ("Duplicate detection searches RadLex synonyms, not only labels",
     "A candidate concept is checked against preferred labels and synonym fields, filtered "
     "to English, before a CDE node is created.",
     "Of RadLex's English synonym terms, 99% match no preferred label anywhere. Two "
     "first-order concepts in this build were reachable only by synonym: renal cell "
     "carcinoma is labelled 'renal adenocarcinoma', intrapulmonary lymph node is labelled "
     "'pulmonary lymph node'.",
     "applied"),

    ("Terminology codes verified against the source at build time",
     "Every code the model uses is checked against the label the source gives it. A code that "
     "does not resolve, or whose label is unrelated to what the model calls it, fails the "
     "build.",
     "A code is opaque. Nothing about RID3554 says whether it means what the line claims, so a "
     "wrong one reads as correct and survives review indefinitely. This is a pipeline step "
     "rather than anything the graph asserts, and it is listed here because a binding is only "
     "worth what the check behind it is worth.",
     "applied"),

    ("Authoring patterns are topic checklists, not element bundles",
     "A pattern lists broad TOPICS that may help when authoring a kind of finding. It names no "
     "DataElement and inserts nothing into the ontology, definition graph, compiled model, or "
     "FindingClass. Patterns are authoring guidance only and are documented for authors; they "
     "are not ontology entities. An author may use a pattern, compose authoring considerations "
     "through `applies_with`, or use no pattern when none fits. Reuse is never forced.",
     "The two carotid stenosis classes are the case that settles it. They share a name and "
     "share nothing else: the internal carotid takes five NASCET diameter-ratio bands and two "
     "competing percentage methods, the external carotid takes two bands read from velocity, "
     "because the vessel is small and tortuous and a diameter ratio is unreliable there. "
     "Different element, different measurements, different modality. A pattern that inserted "
     "the stenosis machinery into everything called a stenosis would have put NASCET "
     "percentages on a vessel nobody measures that way. "
     "A pattern must not hold element ids and splice them into a FindingClass. That forces a "
     "shared element onto classes it does not suit, and the only way to make one fit is to "
     "widen it: a single margin element reaching nine values across three societies, so that "
     "a tendon lesion can be reported as having extra-thyroidal extension. Published elements "
     "must not move to accommodate new findings. Discoverability is the useful part; a future "
     "authoring tool may make that discoverability anatomy-aware without turning the pattern "
     "into ontology semantics.",
     "applied"),

    ("Fixed DataElement values are represented with HAS_VALUE_CONSTRAINT",
     "When membership in a FindingClass fixes an applicable DataElement to one Value, the "
     "class carries `HAS_VALUE_CONSTRAINT` to that Value and the edge records which element "
     "the value belongs to. The fixed element is not presented as a choice on that class, "
     "including when the element is inherited from a parent.",
     "This provides a semantic mechanism for a model assertion that a value is fixed, instead of "
     "leaving that assertion only in prose or presenting a choice the model says the class cannot take. Pulmonary nodule "
     "subtypes use it for attenuation: solid, part-solid and non-solid each constrain the "
     "parent attenuation element to the corresponding value. Intracranial haemorrhage uses "
     "the same mechanism in a provisional intracranial-haemorrhage test case: the current alpha "
     "models epidural as biconvex, subdural as crescentic, and subarachnoid as conforming, while "
     "intraventricular and intraparenchymal haemorrhage provisionally narrow the inherited "
     "collection-shape value set to conforming or rounded. This division is a modeling "
     "hypothesis for exercising fixed-value versus narrowing behavior, not a radiologist-backed "
     "clinical rule. It must remain open to revision after clinical review. "
     "`defining=true` is reserved for value constraints participating in a defined class "
     "equivalence; `defining=false` records a necessary fixed value without making the class "
     "necessary-and-sufficient from that value alone.",
     "applied"),

    ("Sidedness is carried by native anatomy, not a DataElement",
     "A finding does not declare a separate side element. When the resolved native RadLex "
     "anatomic location is sided, that anatomy concept carries the sidedness. More specific native "
     "anatomy may also preserve sided context through its own relationships.",
     "Duplicating the same fact as a finding attribute would create two representations of one "
     "anatomic assertion. The CDE layer therefore does not mint substitute sided anatomy, add a "
     "fallback side field, or repair missing RadLex relationships. If the configured RadLex "
     "release cannot represent the needed sided anatomy, that limitation remains visible until the "
     "native ontology supplies it.",
     "applied"),

    ("Anatomic refinement is a first-class rule with independent controls",
     "A finding may attach an `AnatomicRefinementRule` that independently records the scope "
     "being narrowed, zero or more exact native RadLex predicates, an eligible target concept "
     "set, and traversal behavior when traversal is actually authored. The pulmonary-nodule "
     "rule currently preserves the seven descendants of `RID34694` (lobe of lung) as its "
     "target set and intentionally specifies no native predicate or traversal policy.",
     "Predicate choice must not define the target set, a taxonomy set must not imply an "
     "anatomical relationship, and selecting a predicate must not silently make it recursive. "
     "Only authored RadLex relationships are represented as permitted predicates.",
     "applied; traversal vocabulary remains to be authored when needed"),

    ("Every finding is anatomically anchored",
     "A FindingClass carries a scope, or it is a component reached only through "
     "`HAS_COMPONENT`, or it is a subtype. A class with none of these does not meet the "
     "current FindingClass boundary, and the linter says so.",
     "'Hepatic lesion' is a class; 'lesion' is not. Location is what turns a shape into "
     "something reportable. Enforced for now and not yet disproved: no finding has appeared "
     "that a radiologist reports without a location. A counterexample would not simply relax "
     "the rule, it would suggest a node type this model does not have, since something "
     "reportable and placeless is not a FindingClass as defined here.",
     "applied, no counterexample yet"),

    ("Authoring checks: advisory lint, not schema",
     "Eight advisory rules, none enforced by a reasoner and none constraining what an author may "
     "write. The sharpest is that an element is never narrowed to a single value.",
     "An element every user answers the same way is not recording an observation; it is "
     "restating the class definition and belongs in the class definition instead.",
     "applied"),

    ("When a subtype earns its place",
     "A subtype must differ from its siblings through modelled semantics: a defining element "
     "value, a different scope, a required component, or its own elements. Subtypes partition "
     "on one axis; an independent second axis remains an element.",
     "Pulmonary nodule subtypes are separated by defining attenuation values, renal cyst "
     "subtypes by composition, and haemorrhage compartments by scope. Atelectasis morphology "
     "and mechanism remain elements because they are independent axes that can co-occur. "
     "NEEDS A RADIOLOGIST: whether obstructive atelectasis has sufficiently distinct causal "
     "behaviour to warrant classhood.",
     "needs confirmation"),

    ("Defined classes: subtypes a reasoner computes",
     "A class whose conditions are necessary and sufficient is computed by a reasoner rather "
     "than authored. A part-solid nodule is a pulmonary nodule whose attenuation is "
     "part-solid, and nothing about it is written twice.",
     "One necessary-and-sufficient axiom lets the reasoner compute membership and inheritance "
     "without duplicating the defining condition across the subtype hierarchy.",
     "applied"),

    ("Component relationships, asserted in either direction",
     "`HAS_COMPONENT` says the whole must have this part. `COMPONENT_OF` says this part "
     "belongs only to that whole and says nothing about whether the whole has one.",
     "A part-solid nodule has a solid component by definition. A complex cyst does not have "
     "a mural nodule by definition, but a mural nodule only occurs in one. Both are real "
     "and they need opposite axioms.",
     "applied"),

    ("Edges are addressable objects with their own identity",
     "Every edge in the canonical definition graph is CDE-authored and carries an id and a "
     "version block, so a relationship can change or be retired without either endpoint changing. "
     "Native RadLex anatomy relations remain outside this graph in the RadLex-derived index.",
     "An edge that can only be described cannot be governed.",
     "applied"),

    # ---- anatomy ----------------------------------------------------------
    ("AnatomicLocation is a CDE role over native RadLex anatomy",
     "The CDE model keeps `AnatomicLocation` as a node/role type, but the concepts occupying "
     "that role are native RadLex RIDs under RID3 (`anatomical entity`). No `AL-*` identity "
     "or CDE-owned anatomy class is minted.",
     "This keeps one concept identity. CDE can still distinguish anatomy nodes in its graph "
     "without maintaining a parallel anatomy terminology.",
     "applied"),

    ("RadLex is imported directly and native predicates are preserved",
     "The generated CDE OWL imports the configured RadLex ontology directly. Native RadLex object "
     "properties, their `rdfs:subPropertyOf` hierarchy, inverses, taxonomy and relationship "
     "assertions keep their source IRIs and are never renamed to CDE proxy predicates.",
     "Future RadLex releases can therefore add relationship types without requiring a CDE "
     "predicate mapping or semantic rewrite.",
     "applied"),

    ("Native RadLex predicates are available without a privileged traversal family",
     "The RadLex index exposes exact relationships, property definitions, subproperty metadata, "
     "inverse declarations, and exact-property one-hop traversal. It does not choose `Part_Of` "
     "or any other property family as the default CDE refinement mechanism.",
     "RadLex distinguishes `Part_Of`, `Contained_In`, `Member_Of`, `Branch_Of`, and other "
     "relations. Preserving those distinctions avoids turning an ontology hierarchy into an "
     "application traversal policy.",
     "applied"),

    ("Missing RadLex relationships remain gaps",
     "If the configured RadLex release does not supply a relationship needed to connect two "
     "anatomic concepts, the model reports the missing native path and does not author a "
     "replacement relationship.",
     "This makes upstream terminology limitations visible and avoids a second relationship "
     "layer that would have to be reconciled with later RadLex releases.",
     "applied"),

    ("Target concept sets are independent from predicates",
     "A refinement rule may define eligible targets from an exact native RadLex taxonomy root "
     "with explicit root/descendant inclusion. The same rule may independently permit one or "
     "more exact native predicates. Multiple predicates remain multiple predicates.",
     "A target taxonomy answers which concepts are eligible, not how they are anatomically "
     "related. The application therefore never infers a predicate from taxonomic membership.",
     "applied"),


    # ---- semantics --------------------------------------------------------
    ("When acuity is a value and when it is a class",
     "Acuity is an ELEMENT where it changes only what the finding looks like, and separate "
     "CLASSES where it changes which findings the diagnosis reaches. Intracranial haemorrhage "
     "takes an acuity element: acute and chronic blood are the same collection at different "
     "densities, and nothing else about the finding changes. Acute and chronic pyelonephritis "
     "are two classes: the acute picture is a striated nephrogram with perinephric stranding "
     "and an enlarged kidney, the chronic picture is cortical scarring, and they share none of "
     "it.",
     "One class with an acuity value cannot vary its manifestation edges, so it would assert "
     "that chronic pyelonephritis manifests as a striated nephrogram. There is also no "
     "unqualified parent for pyelonephritis: a radiologist always chooses a side because the "
     "two look completely different, and an ambiguous diagnosis would be unhelpful to the "
     "treating physician. The unqualified term exists for billing, not for reporting.",
     "applied"),

    ("Diagnosis scope does not govern its manifestations",
     "A diagnosis carries the anatomic seat of the disease. Its manifestations may sit "
     "anywhere, and no rule requires them to agree. Pyelonephritis is scoped to the kidney and "
     "manifests as perinephric fat stranding, which is in the perirenal space. Lung cancer is "
     "scoped to the lung and manifests as mediastinal lymphadenopathy.",
     "Widening a diagnosis scope to cover everything it can produce would scope lung cancer to "
     "the whole body and say nothing. The scope answers where the disease is; the manifestation "
     "edges answer where it can be seen. Those are different questions, nothing enforces "
     "agreement between them, and nothing should.",
     "applied"),
    ("Evidential and causal edges are separate",
     "`MAY_MANIFEST_AS` says a diagnosis can show itself as a finding. `MAY_CAUSE` says "
     "something produces a second entity. Neither is inference-bearing.",
     "Pneumonia does not show itself as a pleural effusion; it produces one. Running the "
     "two together lets an author assert production by writing evidence.",
     "applied"),

    ("Typicality and specificity on an evidential edge",
     "`typicality` reads forward: how often the diagnosis shows this finding. `specificity` "
     "reads backward: how much seeing the finding narrows the differential.",
     "The two are independent. A striated nephrogram and perinephric stranding are equally "
     "frequent in pyelonephritis, but stranding also occurs in obstruction, trauma and "
     "infarct, so it narrows far less.",
     "specificity unvalidated"),

    ("Obligate typicality instead of subtyping",
     "Where a diagnosis cannot occur without a finding, the edge carries "
     "`typicality: obligate` rather than making the diagnosis a subtype of the finding.",
     "'Empyema without effusion' is not a meaningful sentence, but empyema is still a "
     "conclusion and an effusion is still an observation. Subtyping across the two would "
     "collapse the distinction the node types exist to draw.",
     "applied"),

    ("Etiology as a deliberately coarse causal target",
     "`HAS_ETIOLOGY` points at ten broad kinds of cause.",
     "Gives causal edges somewhere to land without starting a causal taxonomy, which is a "
     "different project.",
     "deliberately coarse"),

    ("Scope kind records authoring intent, not a traversal policy",
     "`SCOPED_TO` may still carry `specific`, `region`, or `class` as the authored scope category. "
     "Those values do not select a native RadLex predicate, expand a property hierarchy, or "
     "authorize recursive traversal.",
     "Relationship semantics belong in an explicit refinement rule rather than being hidden "
     "inside a generic scope kind.",
     "applied"),

    ("Scope strength: how binding the location claim is",
     "`required`, `expected` or `unconstrained`, recorded on the scope edge.",
     "Declares how binding the claim is, so a consumer can tell a definitional scope from a "
     "usual one. This cannot be enforced as an OWL axiom: OWL is open-world, so 'required' "
     "cannot mean 'absence is invalid' without closed-world checking. That checking belongs "
     "to a future report-validation layer that checks real submitted data against "
     "compiled/*.json, once instance data exists to check. Probe B5_ThyroidNoduleInLung is "
     "the negative control already in place for this: it documents, by staying white, that "
     "no axiom currently carries scope strength.",
     "deferred to a future instance-validation layer, by design"),

    # ---- data -------------------------------------------------------------
    ("Single-select and multi-select declared on the element",
     "Single-select elements are declared functional; multi-select ones are not.",
     "Disjoint values alone do not make an element single-select: nothing stops two "
     "different fillers. No case in the corpus shows the same element single-select on one "
     "finding and multi-select on another, so cardinality is intrinsic to the element.",
     "applied"),

    ("Narrowing a value list at the point of use is advisory",
     "A finding may restrict an element to a subset of its values. In the alpha this emits "
     "as an annotation and a lint rule, not as an axiom.",
     "A hard stop does not always fit the language, and anatomy narrowing in particular is "
     "guidance because a diagnosis draws on several regions at once. Probe "
     "B3_RibFractureWithChronicAcuity already demonstrates the hard form as an "
     "owl:allValuesFrom restriction, reasoner-checked and working, but only inside the "
     "probes file. Promoting a specific narrow from advisory to enforced needs two things: "
     "an explicit per-narrow flag distinguishing hard from soft, and a change to "
     "build_owl.py to emit the real restriction for flagged cases instead of the current "
     "narrowsTo annotation. Promote a narrow when a violation would be clinically wrong "
     "rather than merely unusual, e.g. RibFracture excluding chronic acuity; leave it soft "
     "where legitimate cases can fall outside the narrowed set, e.g. anatomy narrowing "
     "against multi-region diagnoses.",
     "soft by default; hard form proven in probe B3, not yet promotable without a flag"),

    ("Ordered value lists: rank on all values or none",
     "`rank` appears on every value of an element or on none.",
     "Partial ranking is worse than none: a consumer cannot tell an unranked value from one "
     "someone forgot to rank.",
     "applied"),

    ("Measurement is its own node, because the method is the content",
     "A quantitative attribute is a Measurement carrying quantity kind, permitted units and "
     "the method by which it is taken. It is not a DataElement with a numeric range.",
     "The method is the content. Mean diameter measured on lung windows by the Fleischner "
     "convention is a different measurement from one taken any other way, and a range "
     "cannot say so.",
     "applied"),

    ("The graph records what was said, and derives nothing",
     "Where a finding can be reported two ways, both are carried and neither is computed from "
     "the other. Carotid stenosis takes an ordinal band and a percentage, and takes NASCET and "
     "ECST percentages separately. A report saying moderate gives the band and no number; one "
     "saying 55 percent gives the number and no band; one saying both gives both.",
     "Converting would be inventing. NASCET and ECST are different numbers from the same "
     "image, roughly 70 against 85 percent, so a consumer reading one as the other is wrong by "
     "a management threshold. Deriving a band from a number would also assert a convention the "
     "report may not have used. The band definitions state which convention they carry so a "
     "reader knows what the word meant, and that is documentation, not a computation rule.",
     "applied"),

    ("How a measurement is scoped, and when it is split",
     "A measurement carries anatomic scope when its METHOD only holds at that anatomy, and "
     "carries none when the method is general. Greatest pole-to-pole length is a kidney "
     "method, so that measurement is renal length scoped to the kidney. Greatest diameter on "
     "a single plane holds anywhere, so long-axis diameter is unscoped and reused freely. "
     f"{sum(1 for m in spec.MEASUREMENTS if not m.get('scoped_to_anatomy'))} of "
     f"{len(spec.MEASUREMENTS)} are unscoped.",
     "A measurement IS its method, so a generic parent with no method would carry no content, "
     "and one with several methods would not say which applied. There is therefore no shared "
     "parent and no subtype hierarchy: an organ needing a length gets its own measurement with "
     "its own method, and quantity_kind already groups every length for anyone who wants the "
     "set. The scope is what makes `measurement-scope-agrees` meaningful, since attaching a "
     "kidney method to a lung finding is then catchable. The rule allows a class scoped at or "
     "below the measurement, so carotid stenosis at the internal carotid artery may use "
     "luminal caliber scoped to artery.",
     "applied"),

    ("Measurements carry their own scope",
     "A descriptor of a normal structure is a Measurement scoped to a location, with no "
     "owning finding.",
     "Keeping the descriptor as a Measurement avoids making an external anatomy concept own "
     "the CDE descriptor set.",
     "applied"),

    ("Values are owned by one element, never shared",
     "Each element owns its values; exactly one element points at each.",
     "Most repeated value labels are homonyms rather than duplicates. 'Solid' attenuation "
     "means the nodule obscures the parenchyma; 'solid' composition means it is soft "
     "tissue. Sharing would collapse a real distinction. Where meaning is genuinely stable "
     "the reuse belongs at the element, not the value.",
     "applied"),

    # ---- extraction -------------------------------------------------------
    ("No instances: claims are made by probes, not worked examples",
     "The model carries no worked observations. Claims about what it can represent are made by "
     "class-level probes, which state a construction and check what a reasoner concludes from "
     "it, and invent no report text.",
     "An instance pairing a real sentence with a representation chosen here proves nothing: "
     "whoever writes the representation also decides the answer, and any field they supply "
     "beyond what the sentence states renders identically to one that was derived or checked. "
     "Instance-level validation needs data authored elsewhere, by a radiologist or by something "
     "that reads text. Until then the probes carry the claims, since a probe states a "
     "construction and lets the reasoner return the verdict.",
     "applied"),

    ("Compiled shapes: the flat form vendors read",
     "Each finding is emitted as one flat shape with references resolved and patterns "
     "applied, so a consumer evaluates nothing.",
     "The definition graph is for authoring and governance. A vendor should read one "
     "concrete shape, not a general shape plus conditions.",
     "applied"),
]

# mechanisms considered and not adopted
NOT_ADOPTED = [
    ("Grouping node",
     "A node asserted only in the negative, so that 'no renal abnormality' has something to "
     "point at. Never used positively.",
     "Unresolved rather than rejected. Negating a named finding already works, with presence "
     "absent on the finding itself; what has no answer is negating a category, where nothing is "
     "named to carry the value. What would need settling: whether one "
     "negative node per organ scales, and how remainder negation works, since 'no other "
     "significant adenopathy' needs a scope over what was examined rather than a node to "
     "point at."),
    ("IN_REGION edge",
     "Coarse body region authored alongside the scope edge.",
     "Not adopted. The model keeps exact native RadLex relationships available from the scope "
     "target rather than authoring a second regional assertion. Any use of those relationships "
     "for refinement requires an explicit rule."),
    ("MAY_PROGRESS_TO",
     "Identity-preserving evolution: the same entity in a later state.",
     "Used for explicitly authored progression between Diagnosis classes. The relationship "
     "records the stated progression pair without adding a separate temporal identity model."),
    ("INTERPRETED_FROM",
     "Relates an interpretation to what it was read from.",
     "Meaning shifts depending on how many things it points at and which are present."),
    ("Diagnosis as a subtype of a finding",
     "Empyema as a kind of pleural effusion.",
     "Collapses the observation and conclusion layers. Obligate typicality says the same "
     "thing without it."),
    ("Size as a defining condition",
     "Nodule and mass separated by a measured threshold.",
     "Class membership would follow a measured value, so a lesion followed over time would "
     "change class silently with no author present. The threshold is recorded as prose on "
     "the organ-specific pair where the evidence for it actually is."),
    ("Requiredness on elements",
     "Marking some elements mandatory.",
     "No case needs it. Absence of a value is already carried by the presence element."),
    ("Demographic and temporal applicability",
     "Sex, age range and time course as edges.",
     "Deferred. Nothing in the current content needs them."),
]

GAPS = [
    ("The subject of a statement",
     "One lesion, several, a cluster, innumerable. The model can describe a finding and "
     "cannot say how many there are or that an attribute applies to all of them.",
     "This is the largest gap and it is upstream of three others: negation, remainder "
     "negation and bilateral involvement all turn on what the statement is about."),
    ("Negation beyond a named finding",
     "'No renal abnormality' names no finding, so nothing carries a presence value. 'No other "
     "significant adenopathy' is a claim about everything examined and not mentioned.",
     "Negating a named finding is handled: presence absent. These two are not. The second needs "
     "a scope over what was looked at, which no node or element can carry."),
    ("Certainty",
     "'Compatible with', 'concerning for', 'cannot exclude' are not carried.",
     "Undecided. Needs a mechanism if it belongs in the vocabulary."),

    ("Extra-thyroidal extension filed under margin",
     "ACR TI-RADS scores it in the margin category, so the thyroid margin element carries it. "
     "It is a claim about invasion of adjacent tissue rather than about the interface.",
     "Matching the scheme keeps scoring straightforward and puts a behaviour claim on a "
     "morphology axis. NEEDS A RADIOLOGIST: whether to follow the scheme here or move it to an "
     "actsOn edge and reconstruct the score."),

    ("Measurements that reference a landmark elsewhere",
     "A measurement may be defined against a landmark outside the anatomy it is taken at. "
     "NASCET divides the residual lumen at the stenosis by the diameter of the normal distal "
     "internal carotid, which is a different segment. The model carries one scope per "
     "measurement and cannot say the denominator sits somewhere else.",
     "Not worked out. The scope mechanism assumes a measurement belongs at one place, and a "
     "landmark reference is a second place in a different role. Expressing it would need a new "
     "edge rather than another scope, since a second SCOPED_TO would read as the measurement "
     "being taken at both. `element-scope-agrees` is written as though one scope is the whole "
     "story, and would need revisiting."),

    ("Procedure reference",
     "Nothing represents a procedure, so a finding attributable to one cannot say which, and "
     "there is nothing against which to judge whether an appearance is expected.",
     "Post-procedural findings are common in reports and none is expressible."),
    ("Decomposing a pre-coordinated terminology concept",
     "Scope points at the concept the source names. Where that concept is pre-coordinated, as "
     "'left lung' or 'upper lobe of right lung' are, there is no way to ask for the structure "
     "and the modifier separately.",
     "A consumer wanting structure plus a side field, rather than the concept as named, has "
     "nothing to read. The same applies to any pre-coordinated axis the source builds in, not "
     "including sidedness. `radlex_composition` decomposes a CDE concept represented compositionally from RadLex; "
     "it says nothing about a concept that already has a direct terminology binding."),

    ("Comparison to a named prior",
     "Interval change is coarse and carries no reference to which study was compared.",
     ""),
]


def main():
    g = json.load(open(f"{OUT}/graph/definition-graph.json"))
    L = []
    w = L.append
    w("# Mechanisms")
    w("")
    w("What each mechanism does and why it is there. One entry each, no history.")
    w("")
    w("Status **applied** means the mechanism is in the model and in use. It does not mean")
    w("anyone outside this work has agreed with it.")
    w("")
    w(f"Generated {datetime.date.today().isoformat()} by `scripts/build_mechanisms.py`.")
    w("`SHAPE.md` is the schema; `README.md` is how to run it.")
    w("")
    w("---")
    w("")
    w("## In the model")
    w("")
    w("| Mechanism | What it does | Why | Status |")
    w("|---|---|---|---|")
    for nm, does, why, st in MECHANISMS:
        w(f"| **{nm}** | {does} | {why} | {st} |")
    w("")
    w("## Considered, not adopted")
    w("")
    w("| Mechanism | Would be | Why not |")
    w("|---|---|---|")
    for nm, would, why in NOT_ADOPTED:
        w(f"| **{nm}** | {would} | {why} |")
    w("")
    w("## Gaps")
    w("")
    w("Things a radiologist can say that the model cannot hold.")
    w("")
    w("| Gap | What is missing | Note |")
    w("|---|---|---|")
    for nm, what, note in GAPS:
        w(f"| **{nm}** | {what} | {note or '—'} |")
    w("")
    w("---")
    w("")
    w("Clinical content is provisional. Ordinal scales were assembled from report language "
      "rather than a society standard.")
    open(f"{OUT}/MECHANISMS.md", "w").write("\n".join(L) + "\n")
    print(f"MECHANISMS.md: {len(L)} lines | {len(MECHANISMS)} mechanisms, "
          f"{len(NOT_ADOPTED)} not adopted, {len(GAPS)} gaps")


if __name__ == "__main__":
    main()
