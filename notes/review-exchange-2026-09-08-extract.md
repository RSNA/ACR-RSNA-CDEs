---
type: Review Record
title: Schema Review Exchange, 8 September 2026 — Extract
description: Sanitized extract of the 8 September 2026 email exchange on the next-generation schema, covering a cystic lesion with a mural nodule as a second component case, the boundary between a FindingClass and a DataElement, how vendors will consume the definitions, and whether to wrap RadLex anatomy in a local layer.
tags: [committee, review, next-gen-schema, component, sub-finding, consumption, anatomy, radlex]
status: stable
generated: { by: "claude-code/claude-fable-5.1", at: 2026-09-10 }
sources:
  - id: thread
    resource: raw_sources/ (email thread of 8 September 2026; internal file, not named here)
    title: Email thread of 8 September 2026, three messages (internal; kept out of the public repo)
    last_modified: 2026-09-10
  - id: prior
    resource: /notes/review-exchange-2026-08-25-extract.md
    title: The 25 August exchange this one continues
  - id: viewer
    resource: /notes/viewer-review-2026-09-08.md
    title: The reviewer's viewer, received the same day
sanitization: Participants other than the repo owner (Tarik Alkasab) are referred to by role. Greetings, sign-offs, and the name of the reviewer's AI assistant removed. Direct quotations are verbatim, including the owner's capitals and dashes; nothing else in a quotation is altered.
---

# Schema Review Exchange, 8 September 2026

**Status:** Record of an exchange. Four topics raised, four answered, several items left open.
**Date:** 8 September 2026, three messages: the reviewer, the owner, the reviewer.
**Participants:** Tarik Alkasab and the external reviewer drafting the model.

**Provenance.** Distilled from a private email thread, following the precedent of the [25 August extract](review-exchange-2026-08-25-extract.md): the original is not committed. Everything substantive is preserved. The reviewer's viewer, reviewed the same day ([viewer review](viewer-review-2026-09-08.md)), is the artifact behind several of her remarks.

---

## 1. A cystic lesion with a mural nodule: a second component case

**Asked.** A report phrase, "cystic lesion with a mural nodule", stumped the reviewer. Her first thought was an associated finding with a spatial relationship to the cyst wall; on reflection she wondered whether the mural nodule is a *component* of the cystic lesion, on the pattern of the solid component of a part-solid pulmonary nodule. RadLex gave little help beyond the definition of complicated cyst (RID3890), which says a complicated cyst has no solid mural nodule and that a discrete solid component makes the lesion a complex mass; complex mass was itself a dead end. She asked how the owner conceptualizes it clinically, whether similar cases should be an expected pattern in the model, and mentioned vegetation as a possible analog that she had leaned toward treating as an associated finding rather than a component.

**Answered.** The owner made four points. Verbatim where it matters:

1. A generic cystic lesion is not a FindingClass; site-specific ones are. "We could imagine FindingClass definitions for 'ovarian cystic lesion', 'thyroid cystic lesion', 'pancreatic cystic lesion,' 'renal cystic lesion,' etc., but a generic 'cystic lesion' definition really wouldn't make sense because the clinical context and modeling needs for any actual cystic lesion vary so widely." This is the pattern rule of the decision record (lesion is a pattern applied at a location, not a node) applied again.
2. Whether the mural nodule is an associated finding, an attribute, or a subtype is context-dependent: "do we treat a lesion with a mural nodule completely differently from its absence (like a part-solid pulmonary nodule vs a solid pulmonary nodule)?"
3. The test for a component: caring about more than presence. "if we care about more than merely the presence of a mural nodule (in which case it can be a simple attribute/element), then I would definitely think we want to model the nodule itself as a distinct observation pointing to an appropriate FindingClass definition and with some kind of 'component of' relationship between the containing cyst and the nodule. In the plane of the definitions, I think we would want the definition of the mural nodule itself to be distinct from a generic finding, maybe labeled as a 'sub-finding' or something like that, and an edge connecting it to the larger findings it might be associated with. This pattern is the same as I think we would do for the solid component of a part-solid pulmonary nodule."
4. Component versus associated finding is not a real distinction: "My take is that we'd say that it's an associated finding, but the association is 'component of'."

The owner offered to draw a diagram.

**Reviewer's follow-up.** She had not meant the phrase as a FindingClass. "Associated finding" was her generic phrase for a Finding that references another Finding, chosen to avoid saying "component" before knowing it was right. She has already modeled renal cyst and cysts at other locations separately, with simple and complex subtypes, and sees simple versus complex as a relevant axis. Her synthetic-data experiments showed the failure mode she fears: her AI assistant reverted to `renal cyst HAS_DATA_ELEMENT mural nodule = present/absent`, which "seems to work against the duplicate-reduction goal". What she wants preserved is that descriptors of the nodule that are meaningful *in relation to the cyst* stay machine-readable: `Finding HAS_COMPONENT Finding` rather than two unrelated findings. Conclusion on both sides: the same pattern as the part-solid nodule and its solid component.

**Bearing on the documents.** Three things.

- The owner's statements settle, in his words, that the report plane carries a distinct Observation for the component and a "component of" relationship between the containing finding's Observation and the component's, and that the definitions plane carries a distinct FindingClass for the component with an edge to the larger findings it can belong to. That is what the [part-solid nodule plan](../docs/plans/2026-09-08-part-solid-nodule.md) builds; it now has a second case to build after it.
- Two forms appear across the two cases. The solid component of a part-solid nodule exists by definition (the owner's ruling of 9 September, decision record S30). A mural nodule in a renal cyst is optional, and the reviewer's simple-versus-complex subtypes are the same subtype-versus-attribute choice as the nodule's composition, now with the component as the distinguishing relationship. The relationship catalog will need both the definitional form and the optional form, and the naming of the two is open (to-do item 4 of 10 September).
- The word "sub-finding" was floated by the owner for the component class ("maybe labeled as a 'sub-finding' or something like that"). Whether that is a label on the class, a fact derived from being the target of a component edge, or nothing at all is open; the decision record's rule that patterns are not written into the graph (S7) bears on it.

## 2. The boundary between a FindingClass and a DataElement

**Asked (in the follow-up).** Because the model technically allows `mural nodule` as a present/absent element on the cyst, authors and AI-assisted authoring will revert to it. The reviewer wants the boundary defined well enough that they do not.

**Not answered in the thread.** The owner's component test in §1 (more than presence wanted, therefore a class and a component Observation) is the nearest thing to a rule.

**Bearing on the documents.** This is queue item 2 of the handoff (patterns as an authoring guide and a lint check) gaining its first concrete rule: an entity that can carry its own descriptors is a FindingClass, and its relation to the containing finding is a component edge, never a presence element on the container. The owner's ruling on nodule composition (S30) gives the other half of the same guide: a distinction that changes the relationships, or matters clinically, is a subtype, not a value.

## 3. Intended consumption of the definitions

**Asked.** Is the graph itself to be public and consumed directly by vendors, or will vendors consume flat generated JSON? The boundary affects which mechanisms are safe to keep internal: something resolved implicitly in the authoring layer could leave the semantics ambiguous for anyone consuming the graph directly. In the follow-up she added that she has been building the alpha as an OWL representation, so knowing the graph may be a consumption artifact is useful context.

**Answered.** "This is a tricky question, and one we've avoided so far. I do think we need to make a JSON representation available, but we should also have some kind of graph representation. What form this takes isn't obvious to me (DuckDB? Postgres dump?), but I'm sure we could figure something out. Maybe we need to just commit and publish an RDF/OWL file? That would really lean into the ontology nature of what we're doing/promoting." And: "it would be very helpful for there to be 'official' access libraries for the definitions that make them accessible as TypeScript and Python objects with appropriate connections."

**Bearing on the documents.** The architecture sketch in the current-understanding document already lists JSON and JSON-LD for vendors and an OWL release as publication outputs, with the store as a derived view. The owner's answer adds three things that are not yet decided anywhere: that a graph form is a deliverable and not only an internal store; that an RDF/OWL file may be the published graph form; and that official TypeScript and Python libraries are wanted. The reviewer's warning is the important structural point: if the graph is consumed directly, nothing may be resolved only in the authoring layer. That is an argument against any condition mechanism that a compiler resolves away, and for explicit edges. It belongs on the list of decisions for the committee.

## 4. RadLex anatomy: known issues, gaps, and a local layer

**Asked.** The RadLex release notes have carried a known issue for at least two releases: the part relations for anatomy may be incomplete or duplicated, because the anatomy was built as a part-of hierarchy and converted to is-a, with some inadvertent is-a categorizations and a duplicating FMA import. Traversing RadLex's taxonomy and partonomy directly therefore looks risky. She proposed wrapping the anatomy relationships we depend on in a local layer: maintain them explicitly while still referencing RadLex concepts, insulate the model from release cadence and breaking changes, keep provenance of which RadLex version each mapping came from, and allow a local placeholder when something is missing upstream.

**Answered.** No separate project. Verbatim: "RadLex is moving this in exactly the right direction for our purposes"; "To the extent that we need something else from RadLex anatomy, we can have it"; "A 'safety layer' has already been created and is in the process of being reintegrated into RadLex itself. In terms of preserving any historical provenance—we don't really need to worry about it. (If people want FMA, they know where to find it.) We do NOT need to launch our own project on this—we can build on the existing effort." The owner proposed connecting specifically on the anatomy project soon.

**Reviewer's follow-up.** She is mindful of not creating a parallel anatomy ontology; her concern is genuine gaps that would block modeling while upstream work evolves. Two examples: in RadLex the adrenal gland has no upward relationship, and lung parenchyma is not connected to the lung, so anything scoped to those concepts derives no body region and fails scope checks "in a way that looks like a bug in our model". Her experiments are gap-filling, not replacement. She will push content to GitHub and offered a call; her first pass makes assumptions needing clinical confirmation and all its content is synthetic.

**Bearing on the documents.** The bundle already does what the owner described: anatomy comes from AnatomicLocations.org, not from RadLex's own partonomy, so the known issue she cites does not reach our traversals; gaps are logged in the anatomy-gaps document for upstream proposal; a stub id convention exists for a concept that is missing. Her two examples should be checked against the AnatomicLocations.org data and logged there if they are gaps. Her viewer's structured record on a locally held node (source, status, upstream request number) is the one piece of her proposal worth adopting into the stub convention. Her GitHub push, when it lands, is a new raw source to review.

## 5. Items left open

For the owner and the reviewer:

- The names and definitions of the two component relationships, definitional and optional, and how the simple-versus-complex cyst subtypes relate to them.
- Whether a component class carries a label such as "sub-finding", or is recognizable only by the edges pointing at it.
- Whether a component class is site-specific (ovarian mural nodule, renal mural nodule) or shared across the site-specific cystic lesion classes, given that a generic cystic lesion is not a class.
- Vegetation, and other candidates: which are components and which are merely associated.
- The FindingClass-versus-DataElement boundary as an authoring rule and a check.
- The consumption boundary: which forms are published (JSON, a graph form, RDF/OWL), and the consequence that nothing may be resolved only in the authoring layer.
- Official access libraries in TypeScript and Python.
- A call on the anatomy project; the reviewer's forthcoming GitHub content; the adrenal gland and lung parenchyma gaps.
- The owner's offered diagram of the component pattern, which the part-solid nodule example is positioned to be.
