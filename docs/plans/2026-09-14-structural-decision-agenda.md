# Structural decision discussion and agenda

Status: active — owner working positions and proposals recorded; none should be presented as settled integration agreements. One question at a time.

## Scope

Use the reviewer's implementation approach as the foundation. Resolve structural choices through discussion with the owner, keeping clinical content and presentation separate. The earlier implementation snapshot remains on hold; the comparison is a question inventory, not evidence of the refactor's current behavior.

## Current additions and corrections, 15 September (S50–S51)

**Anatomy scope specifiers (S50).** Develop two initial families: tissue types (pulmonary parenchyma, hepatic parenchyma, subcutaneous fat) and structure types (solid organs, vessels with artery/vein subtypes, muscles, tendons, ligaments). Work out their connections to the anatomic location hierarchy. These families are the owner's direction; separate graph node types, disjoint categories, and exact relationships have not been selected.

**Exploratory connection ideas, not adopted.** Compare explicit tissue/location nodes with tissue scope specifiers linked to locations. Explore is-a classification for structure kinds and separately named part-of/location links for tissue setting. A named artery, hepatic parenchyma, and subcutaneous fat in a region could expose the difference. These are assistant-suggested illustrations, not new owner requirements or changes to the Observation model.

**Withdrawn questions and later work (S51).** The published agenda's original seven-question section mixed existing answers with future implementation work:

- Measurements are represented by Measurement nodes; the broad question did not identify a new structural difference. AssessmentScheme and its ordinary DataElements remain as discussed in S40–S41.
- Observations specify sided anatomic locations. Absence is expressed by an Observation pointing to a FindingClass with a component value referencing the presence DataElement and value "absent." Neither requires reopening the Observation model.
- "Incomplete anatomy" referred to missing taxonomy coverage; keep that within the anatomy gap work, not as an abstract new semantic question.
- Plain-list OR and explicit AND remain the owner's working position (S48), not a fresh unresolved choice. Their syntax is implementation work.
- Checking OWL mappings, export metadata, and verification belongs to later implementation work. Preserve useful analysis there without presenting it as additional structural decisions for this meeting.

The genuine new open anatomy item is how tissue/structure scope specifiers connect to the location hierarchy. Other structural discussion remains the specific apparent conflicts and explicitly labeled proposals. S49's provisional integration status remains in force.

**Communication preference:** ask questions directly in ordinary chat. Do not use queued/async question widgets; the owner reported a persistent, unusable question panel. This is workflow guidance, not domain semantics.

## Plan

1. Record this discussion process and agenda here.
2. Present one bounded structural choice at a time: the approaches, practical consequences, existing authority, and a recommendation where useful. Explicitly distinguish an observed implementation difference (with snapshot/revision identified) from an open structural contract whose implementation status has not been verified. Keep questions tied to reconciling the implementation foundation; do not imply every open question is a demonstrated defect.
3. Record each owner answer immediately, distinguishing a working preference, a proposal, an exploratory idea, and an explicitly shared agreement. Preserve historical prototype instructions without presenting them as settled requirements for the reviewer's foundation.
4. Turn unresolved items into precise questions for the reviewer, with a concrete example and the owner's preferred outcome where known.
5. Update the existing decision record and relevant document metadata when an actual decision is made; keep this agenda and the bundle log synchronized with material outcomes.
6. At completion, review the documentation and run the bundle checks; mark this discussion pass complete while leaving genuinely unresolved questions visible.

No implementation changes, renewed review of the superseded branch, commits, or uploads are part of this discussion.

## Current clarification and documentation pass (S49)

The owner clarified that inheritance, finding/diagnosis types, and the component model remain proposals to discuss with the reviewer. Nothing in this integration agenda is settled merely because it was accepted in our own discussion or implemented in our prototype. Bring useful ideas to the alpha foundation and explore compatible modifications. Earlier quotations remain historical evidence, not proof of joint agreement.

Documentation pass complete: corrected the comparison's authority labels, explained the OWL question in ordinary language, and drafted incremental export suggestions. Updated the decision record, reference status notes, glossary framing, metadata/index descriptions, and bundle log. Bundle and whitespace checks pass. The discussion remains active; no implementation work or review of the held branch was performed.

## Starting context

- The reviewer's implementation is the foundation (S38).
- Our initial proposal is that definition bindings are authored directly rather than automatically propagated through subtype edges (S3, clarified by S49). Inheritance remains a discussion item, not a rejected option for the foundation; applicability checks are a distinct question.
- The anatomy substrate is the pinned anatomic-locations overlay on RadLex (S37); do not reopen source selection.
- The preferred mat presentation and clinical-content cleanup remain separate workstreams.

## Decisions and discussion agenda

The entries below preserve the owner's working positions and original wording. "Accepted" describes the earlier owner–assistant exchange, not a settled agreement with the reviewer. Read their proposed behavior subject to S49, including references to no propagation.

**ST09a — Accepted with clarifications (S39).** Measurement is distinct from DataElement. A DataElement's value set may be ordered or unordered; the distinction must be represented explicitly. Measurement method is optional and is unspecified by default. This does not choose a serialization or settle method-specific identity rules.

Owner's words: "Yes, I'm OK with the distinction."; "DataElements set of values NEED NOT be ordered, but it COULD be, and we should distinguish them."; "BY DEFAULT, the measurement method is NOT specified."

For the reviewer: retain the type distinction; ensure unordered value sets are distinguishable from ordered ones and measurements are valid without a specified method. No implementation verification against the held branch is implied.

Documentation updated: decision record, structural comparison, requirements, draft structures, glossary, and bundle log. Older example artifacts have not been migrated.

**ST09b — Accepted with a structural change (S40).** AssessmentScheme is a separate definition type, organized more like FindingClass with edges to multiple DataElement-like descriptors. The scheme is not flattened into one category list; the scheme, its descriptive dimensions, and each dimension's values must remain distinguishable. The owner cites Lung-RADS and cancer staging systems as motivation; their clinical content is not being specified here.

Owner's words: "I actually like the idea of AssessmentScheme being a separate definition type"; "I think AssessmentScheme needs to work more like FindingClass and have edges to multiple DataElement-like things."

For the reviewer: discuss the scheme-to-descriptor structure. Exact descriptor types, binding names, reuse, result representation, and scoring rules are not settled by this decision. The FindingClass analogy does not itself choose a subtype relationship or the finding-component relationship.

**ST09c — Ordinary DataElements accepted (S41).** The descriptors linked from AssessmentScheme are ordinary DataElements; there is no distinct assessment-specific descriptor type. This resolves the descriptor-type question in S40. It does not automatically mean different schemes share the same element identity merely because labels match. The earlier suggestion about Measurements for quantitative components was not explicitly decided.

Owner's words: "I would say they should be ordinary DataElements--I don't see a need to make them distinct."

For the reviewer: retain AssessmentScheme as a distinct definition type and link it to ordinary DataElements, rather than introduce an assessment-specific descriptor type. Nesting, scoring, quantitative components, and report-result structure remain separate questions.

**ST10a — Binding-level value subsets accepted (S42).** A FindingClass–DataElement edge can restrict that use to a subset of the element's permissible values. Keep the shared DataElement and its full value set intact; other bindings are unaffected. This is a semantic restriction, not merely a display filter, and does not propagate through subtype relationships (S3).

Owner's words: "Oh, absolutely--having an edge that says, \"Takes this element, but only this subset of values\" connecting a FindingClass and a DAtaElement would be a big help in promoting reuse."

For the reviewer: preserve the binding-local subset as part of the definition contract across representations. Concrete encoding and consumer enforcement mechanisms remain implementation questions, not authorization to add report-template validation. The owner explicitly named FindingClass; other binding subjects have not been separately resolved.

**ST08a — Direct anatomy bindings accepted (S43).** AnatomicLocation can bind directly to both DataElements and Measurements. Describing normal anatomy does not require introducing a FindingClass. This selects direct bindings; it does not prohibit separately declared descriptor scope or decide new anatomy traversal rules. Existing S3/S20 distinctions between no propagation and applicability checks remain in force.

Owner's words: "I agree, we shoud be able to bind anatomic locations directly to data elements and measurements."

For the reviewer: support anatomy-originating descriptor bindings alongside finding-originating ones, referencing the agreed anatomy substrate. Exact Measurement binding names and delivery mappings remain open; no anatomy source or implementation changes are authorized here.

**ST10b — Owner proposal for discussion (S44).** Put default selection cardinality on DataElement, with possible adjustment on the binding edge. This is proposed, not a finalized cardinality contract. The proposal does not alter value ordering, introduce required report elements, or propagate relationships through taxonomy.

Owner's words: "Let's propose a default cardinality on the DataElement with possible inflection on the edge."

For the reviewer: discuss a default on the shared element and a local cardinality adjustment on an individual binding. Leave broadening versus narrowing, the cardinality vocabulary, and encoding open; do not silently interpret "inflection" as narrowing only. No implementation changes are authorized.

**ST10c — Three modality statements distinguished (S45).** A finding can be visible only on particular modalities; a descriptor can apply to a particular finding only on particular modalities; and a DataElement or Measurement can be intrinsically evaluable only on particular modalities. Record these separately at the finding, binding, and descriptor levels. The last is a hard capability limit, not the adjustable-default pattern discussed for cardinality.

Owner's words: "Some findings can only be seen on specific modalities. Some descriptors (DataElement/Measurements) only apply to findings seen on specific modalities. And some DataElement/Measurements can only EVER be evaluated on specific modalities."

For the reviewer: preserve the three meanings without turning a binding-local restriction into a global descriptor restriction. An individual use cannot override a descriptor's intrinsic limitation. Encoding and inconsistency handling remain open; omission semantics are resolved by S47 below. No subtype propagation or report-template validation is introduced.

## Parked exploratory item

**ST09d — Exploratory idea: multi-component measurements.** Put forward the possibility of a Measurement with multiple components, instead of advancing the assistant's suggestion to retain derived-measurement input links. This is an idea for discussion, not a proposal, adopted model, or rejection of derivation links.

Owner's words: "Can we... \"propose\" is too strong--put forward the idea of instead having multi-component measurements?"

For the reviewer: explore whether grouping multiple components within a Measurement better expresses the intended structure. Component identity and types, nesting, and the relationship between composition and calculation remain open. Do not assume each component is a separately defined Measurement or a required report value. The earlier inventory mentions both component measurements and derivation links; this is a question about their meaning and organization, not a claim that the current implementation lacks components. No new implementation review or work is authorized.

## Resolved follow-up

**ST10d — Missing modality means no information (S47).** An omitted modality constraint means no information about modality applicability, not unrestricted or pan-modality applicability. Omission alone also does not assert that no modality applies. Preserve explicit constraints at all three S45 levels; absence at another level does not remove them.

Owner's words: "I think not specifying modality contraint should just be \"no information\"." The owner notes that truly pan-modality findings are uncommon as the rationale; this discussion does not curate particular findings' modality lists.

For the reviewer: preserve unspecified applicability in authoring and published representations without replacing it with "all modalities." The representation of explicit unrestricted applicability, empty lists, and downstream UI behavior is not decided here. No parent-derived default is introduced.

## Latest clarification

**ST10e — Question withdrawn as framed; categorization alternatives clarified (S46).** For the same categorization in the same model, use either A with a categorizing DataElement E, or A with named subtypes B, C, D, without that categorizing E. The assistant's "B is exactly A with E = V" question combined those alternatives and was challenged by the owner. Different contexts may choose different representations, as S30 already records. Other descriptors remain possible on the classes; nothing is inherited.

Owner's words: "You should have EITHER the categorizing DataElement OR a taxonomy, right?"

For the reviewer: preserve the choice between the two models rather than duplicating a class-identity distinction as a categorizing element. The discussion does not adopt equivalence rules or decide the vocabulary's entire formal-logic capability. No clinical examples or implementation artifacts are changed.

## Deferred lifecycle topic

**ST13a — Versioning deferred by the owner.** "Leave versioning for now." No choice was made about immutable, individually addressable published revisions or any other versioning mechanism. The shared lineage identifier direction in 00 Issue E remains unchanged. Return to versioning in a separate discussion; do not treat the assistant's suggested reference model as adopted.

## Scope combination decision

**ST07a — Any-match lists and explicit all-match conditions accepted (S48).** Support both. By default a plain list of scope targets matches any one target (OR). Explicit combinations can require multiple conditions to hold together (AND). Named anatomy concepts remain usable; scope is not limited to a single pre-coordinated target. This settles the intended semantics, not an expression syntax or arbitrary Boolean language.

Owner's words: "by default, if you jsut have a list, it needs to match any ONE of those. But you should ALSO be able to specify must-match-multiple-conditions."

Evidence status: this was an open structural contract raised by the comparison, not a verified defect in the current foundation. The assistant should have labeled it that way before asking. S48 records the owner's working position to bring to the reviewer, not a jointly adopted requirement or evidence that an implementation change is already needed.

For the reviewer: confirm plain-list OR and explicit AND semantics agree across authoring, JSON, OWL, and access libraries. A candidate matching A but not B satisfies the plain list [A, B] but not an explicit all-match condition containing both. Combination logic must not silently change permitted anatomy traversal paths, source ownership, or no-propagation rules. No implementation work is authorized.

## Proposals to bring to the reviewer

- **Inheritance:** explore classification without automatic propagation of definition bindings. Establish what the alpha's inheritance is intended to accomplish before choosing how to represent those meanings.
- **Finding/diagnosis types:** explore a taxonomy that can cross these labels while retaining useful distinctions in definition types. Determine whether the labels describe records, clinical entities, or roles before deciding disjointness or permissible subtype links.
- **Finding components:** bring forward one component relationship with minimum/maximum counts and optional component-of scope to a finding family. These are potentially useful modifications, not an already adopted replacement for the alpha. Multi-component measurements remain a separate exploratory idea.
- **OWL mapping, later implementation work (S51):** check that exports preserve the definition/Observation distinction. The earlier broad OWL question is withdrawn from the structural meeting agenda; it did not establish a new domain-model decision.
- **Exports:** discuss preserving binding detail, reference coverage, explicit missingness, a short description of each export's intended contents, and small cross-format semantic examples. See [ST12's draft suggestions](../next-gen-schema/12-alpha-structural-comparison.md#st12-establish-what-is-canonical-and-what-each-deliverable-promises). Apply new structural fields only if their proposals are adopted; leave versioning deferred.

## References

- [Structural comparison](../next-gen-schema/12-alpha-structural-comparison.md)
- [Decision record](../next-gen-schema/10-decision-record-2026-09-02.md)
- [Current anatomy agreement](../next-gen-schema/11-anatomy-axis.md)
