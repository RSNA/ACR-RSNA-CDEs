---
type: Analysis
title: Ontology Background Research and Follow-up Questions
description: Primary-source background and proposed worked examples for target identity, assertion context, negation, formal semantics, terminology mappings, and diagnostic reasoning in the next-generation CDE vocabulary.
tags: [next-gen-schema, research, ontology, observations, semantics]
status: draft
generated: { by: ["codex", "gpt-5.6-sol"], at: 2026-09-04 }
sources:
  - id: dicom-tracking
    resource: https://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_tid_4108.html
    title: DICOM PS3.16, TID 4108 Tracking Identifier
  - id: phenopackets
    resource: https://phenopacket-schema.readthedocs.io/en/latest/phenotype.html
    title: GA4GH Phenopacket Schema 2.0, PhenotypicFeature
  - id: fhir-observation
    resource: https://hl7.org/fhir/R5/observation-definitions.html
    title: FHIR R5 Observation definitions
  - id: owl-primer
    resource: https://www.w3.org/TR/owl2-primer/
    title: OWL 2 Primer, Second Edition
  - id: owl-semantics
    resource: https://www.w3.org/TR/owl2-direct-semantics/
    title: OWL 2 Direct Semantics, Second Edition
  - id: shacl
    resource: https://www.w3.org/TR/shacl/
    title: Shapes Constraint Language, W3C Recommendation
  - id: skos
    resource: https://www.w3.org/TR/skos-reference/
    title: SKOS Reference, W3C Recommendation
  - id: hpo-frequency
    resource: https://obophenotype.github.io/human-phenotype-ontology/annotations/frequency/
    title: HPO frequency annotations and negative annotations
  - id: lirical
    resource: https://pmc.ncbi.nlm.nih.gov/articles/PMC7477017/
    title: Interpretable Clinical Genomics with a Likelihood Ratio Paradigm, LIRICAL
  - id: rgo
    resource: https://doi.org/10.1148/rg.341135036
    title: Radiology Gamuts Ontology, Differential Diagnosis for the Semantic Web
  - id: aim
    resource: https://doi.org/10.1007/s10278-014-9710-3
    title: The AIM Foundation Model
  - id: snomed-context
    resource: https://docs.snomed.org/implementation-guides/context-representation-implementation-guide/4-snomed-ct-and-context/4.1-clinical-findings-with-explicit-context
    title: SNOMED CT Clinical Findings with Explicit Context
  - id: ihe-idr
    resource: https://www.ihe.net/uploadedFiles/Documents/Radiology/IHE_RAD_Suppl_IDR_PhII_Rev1-2_PC_2026-03-04.pdf
    title: IHE IDR Phase II, Rev. 1.2 public-comment draft, 4 March 2026
---

# Ontology Background Research and Follow-up Questions

Research requested on 4 September 2026, with a GPT-5.6 Sol subagent conducting a targeted web survey and the main agent reviewing the branch and checking selected sources. These are recommendations for discussion, not committee decisions or changes to the graph. The research emphasizes primary specifications and original work. Historical standards remain useful where their semantics are stable; the FHIR material cited here is specifically R5.

Search accounting: the subagent requested 115 Exa results across four research themes and selected 12 primary sources. The main agent requested 10 additional search results and checked selected source passages. These counts describe requested search results, not unique publications read. The main agent also added OWL Direct Semantics to the evidence base. Exa's truncated fetches were supplemented by direct page access.

The most useful development would be a few worked examples that state both what a consumer may conclude and what remains unknown. They can clarify the vocabulary's contract without taking ownership of the report grammar or an instance store.

## 1. Give the observed target an identity distinct from each assertion

**Evidence.** DICOM explicitly distinguishes the Tracking UID of an object across reports from the Observation UID of one observation; one tracked object can have many observations. This is a direct precedent for keeping target identity separate from assertion identity. [DICOM TID 4108](https://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_tid_4108.html).

**Branch connection.** The report examples currently identify individual Observations and their vocabulary subjects. The [IDR extract](ihe-idr-extract.md) already records tracking identifiers on BodyStructure, so this is an opportunity to exercise a known consumer requirement.

**Proposed example.** Follow two nodules in the same lobe through two reports. One grows and acquires a different interpretation. Show which identities remain stable: the vocabulary concept, the tracked target, and each new assertion. Then add a second reader's different measurement of the same target. Location plus class must not accidentally merge the two nodules. A class change must not necessarily create a new target.

An absent-abscess assertion makes the boundary especially clear: recording that assertion must not itself assert the existence of an abscess. A target reference may identify the examined kidney or a previously tracked lesion; it cannot require a newly existing abnormality for every negative statement. This is a proposed consumer contract, not a proposal to add patient objects to the definition graph.

The [AIM Foundation Model](https://doi.org/10.1007/s10278-014-9710-3) offers complementary background on image annotations, observations, calculations, inferences, and longitudinal comparison. Its entity categories do not map directly onto this proposal. The [March 2026 IDR draft](https://www.ihe.net/uploadedFiles/Documents/Radiology/IHE_RAD_Suppl_IDR_PhII_Rev1-2_PC_2026-03-04.pdf) is the closer interoperability target; this research does not establish that it is the latest IDR release. Also document the naming collision: this branch's Observation `subject` means a vocabulary class, whereas FHIR's `subject` identifies the patient or other record subject.

## 2. Work through polarity, assessability, and certainty together

**Evidence.** Phenopackets uses `excluded` for a feature specifically sought and found absent. FHIR R5's `dataAbsentReason` explains why an expected result value is missing. FHIR also explicitly permits exceptional results in a value set, so it does not mandate one representation for this project. [Phenopackets](https://phenopacket-schema.readthedocs.io/en/latest/phenotype.html); [FHIR Observation](https://hl7.org/fhir/R5/observation-definitions.html#Observation.dataAbsentReason).

**Branch connection.** The [presence element](../docs/next-gen-schema/examples/presence.element.json) mixes `present`, `possible`, `absent`, `indeterminate`, and `unknown`; `unknown` combines not assessed with not recorded. Meanwhile the [pyelonephritis report](../docs/next-gen-schema/examples/pyelonephritis.report.jsonl) separately records `confidence`, and the effusion report uses presence `present` with confidence `possible` for heart failure.

**Proposed example.** Model these phrases side by side: "abscess present", "possible abscess", "no abscess", "cannot assess for abscess", and a report that says nothing about abscess. Specify which distinctions are recoverable and which combinations are contradictory. Decide whether certainty stays partly encoded in presence or is expressed separately; avoid two independently editable fields that say the same thing. Preserve the radiologist's wording. If extraction confidence is later added, define it separately from the radiologist's certainty.

[SNOMED's explicit-context model](https://docs.snomed.org/implementation-guides/context-representation-implementation-guide/4-snomed-ct-and-context/4.1-clinical-findings-with-explicit-context) supplies another useful precedent: associated finding, finding context, temporal context, and subject relationship context are distinct. It does not settle radiology assessment scope for us.

## 3. Separate explicit negative scope from assumptions about missing data

**Evidence.** OWL subclass semantics is set inclusion. Therefore, under a fixed scope, an explicit assertion that there are no instances of a superclass excludes instances of its subclasses without needing a complete catalogue of subclasses. This is our logical application of the standard. Inferring absence merely because no positive assertion exists is a different operation. [OWL 2 Direct Semantics, class expressions and axioms](https://www.w3.org/TR/owl2-direct-semantics/).

**Branch connection.** [00 Issue A](../docs/next-gen-schema/00-current-understanding.md) and the renal-abnormality example currently tie the negative sweep to closed-world completeness. That wording conflates the logical inference with the clinical interpretation of the initial negative assertion. Also, an Observation with the ordinary value `absent` acquires no OWL negation semantics automatically; the mapping must state what it means.

**Proposed example.** Compare "right kidney unremarkable", "no right renal mass", and "right kidney poorly visualized". State the anatomy, time, and assessment scope within which each negative can be used. Test that it cannot negate a left-sided finding or a prior study's finding. Test that adding a newly named subtype does not change the original report into a stronger clinical claim. Deriving absence of a parent from negatives on selected children would require additional coverage assumptions.

## 4. Write a small formal-semantics contract before expanding the graph

**Evidence.** OWL's domain and range declarations support inference; they are not document validation checks. Punning allows a name to be used as both class and individual, but their interpretations remain separate under OWL 2 Direct Semantics. SHACL supplies explicit graph validation, including `sh:in` for permitted values. [OWL 2 Primer, sections 4.6 and 9](https://www.w3.org/TR/owl2-primer/); [SHACL](https://www.w3.org/TR/shacl/).

**Branch connection.** [03](../docs/next-gen-schema/03-draft-structures.md) names `rdfs:range` as the DataElement-to-value-domain edge, while [00](../docs/next-gen-schema/00-current-understanding.md) leaves class-versus-individual modeling open. The final export needs to decide whether an element denotes a property, a governed definition object, or deliberately linked representations. Likewise a class-level `MAY_MANIFEST_AS` assertion must not accidentally become a claim that every disease instance has an existing manifestation. An annotation on an existential axiom does not weaken the axiom's truth conditions.

**Proposed deliverable.** Use one diagnosis, two findings, a shared element, and sided anatomy to document expected entailments, non-entailments, and validation failures. Include these cases:

- An anatomic subtype satisfies a compatible scope.
- A subtype does not acquire an unasserted element binding, preserving decision S3.
- A potential manifestation creates no patient finding.
- An absent finding creates an assertion without creating a positive disease instance.
- An invalid supplied value fails validation; an omitted optional element is allowed.

This can also clarify the conditional-component debate: distinguish a clinical meaning constraint from a requirement that a report actually include a component. Defining part-solid nodule semantics need not make a solid-component Observation mandatory in every report. No choice between the two proposed authoring mechanisms is made here.

## 5. Correct the terminology-mapping rule before scaling lookup work

**Evidence.** SKOS mappings express relationships between meanings. `exactMatch` denotes strong interchangeability across retrieval applications, and is transitive; `closeMatch` denotes weaker interchangeability. Broader and narrower mappings have their own predicates. Neither exactness nor closeness is a string-matching grade. [SKOS Reference, section 10](https://www.w3.org/TR/skos-reference/#mapping).

**Branch connection.** [03 section 2.1](../docs/next-gen-schema/03-draft-structures.md) currently calls an `exactMatch` an exact-label hit and uses `closeMatch` for broader or narrower concepts. That is a concrete correction to make in a subsequent edit.

**Proposed deliverable.** A short mapping rubric with examples of equivalent meaning despite different labels, identical labels with different scopes, and a broader external concept. Preserve lookup candidates separately from accepted semantic mappings, and record the external release and mapping rationale. The clinical appropriateness of each existing mapping still requires review; this research does not recode the graph.

## 6. Separate differential retrieval, heuristic ranking, and probabilistic evidence

**Evidence.** The [Radiology Gamuts Ontology](https://doi.org/10.1148/rg.341135036) is a direct precedent for ontology-supported differential lookup. It supports the candidate-retrieval direction; it does not establish the calibration of this branch's proposed ranking.

[HPO frequency guidance](https://obophenotype.github.io/human-phenotype-ontology/annotations/frequency/) prefers cohort counts when available and distinguishes expert negative annotations from a feature seen in zero members of a sampled cohort. The distinction between `0/2` and `0/200` matters. Its guidance is about disease manifestations; adopting the same bins for causal consequences remains an extrapolation to review.

[LIRICAL](https://pmc.ncbi.nlm.nih.gov/articles/PMC7477017/) makes the computational assumptions explicit: a likelihood ratio compares the feature's frequency under a disease with its frequency under alternatives, and combining features uses an independence assumption. Its rare-disease setting does not provide a ready-made background population for general radiology.

**Branch connection.** [07 section 3.2](../docs/next-gen-schema/07-relationship-family.md) suggests deriving numerical specificity from typicality plus prevalence. That is incomplete: disease prevalence supplies prior odds; it does not by itself supply the feature frequency among competing diagnoses. In notation, `LR = P(F | D) / P(F | not D)`. Similarly, ranking by specificity then typicality is an interpretable heuristic, not automatically a calibrated probability. The example edge weights are already labeled hypothetical in the decision record.

**Proposed example.** Retrieve a differential for a small finding set, show the existing qualitative ordering, and explain each contribution. Then add a correlated finding derived from the same appearance or measurement and ask whether the score should change. Preserve cohort counts, study context, citations, and evidence type where known. Do not collapse a sampled zero into a universal exclusion or let one observation contribute evidence twice under different descriptions.

## Suggested order

Start with the longitudinal target example and the assertion-state matrix; they make the consumer objects concrete. Next write the small semantics contract and the mapping rubric, using expected inferences and validation outcomes to assess export options. Finally develop a differential example with explicit evidence assumptions. These are proposed follow-ups, not implementation phases authorized by this research request.

The existing decision record remains authoritative for provenance. No recommendation here changes the no-required-elements rule, creates automatic element-binding inheritance, or adds pointers from report edges to definition edges. Documentation review found older statements about required bindings and report-edge `expresses` pointers alongside newer decisions in 00, 03, 07, and the IDR extract; the existing cleanup work should reconcile them before they are treated as current requirements.
