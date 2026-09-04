---
type: Draft Specification
title: The Finding and Diagnosis Relationship Family
description: The proposed catalog of relationships between FindingClasses and Diagnoses, with definitions, prior art, the typicality and specificity properties on manifestation edges, the differential as a derived view, and the refinements deliberately deferred.
tags: [next-gen-schema, relationships, diagnosis, edges, differential]
status: draft
generated: { by: ["human:talkasab", "claude-code/claude-opus-5"], at: 2026-09-01 }
sources:
  - id: exchange
    resource: /notes/review-exchange-2026-08-25-extract.md
    title: The review exchange whose closing request this document answers
  - id: structures
    resource: /docs/next-gen-schema/03-draft-structures.md
    title: The edge table this family extends
    author: "human:talkasab"
  - id: radlex-owl
    resource: https://github.com/RSNA/RadLex
    title: RadLex OWL source, object properties verified directly 2026-09-01
  - id: rgo
    resource: https://www.gamuts.net/about.php
    title: Radiology Gamuts Ontology, the direct predecessor for derived differentials
  - id: hpo-format
    resource: https://hpo-annotation-qc.readthedocs.io/en/latest/annotationFormat.html
    title: HPO annotation format, source of the frequency scale
  - id: orphadata
    resource: https://www.orphadata.com/docs/OrphadataScienceDataDescription.pdf
    title: Orphadata science data description, source of the pathognomonic definition
  - id: internist
    resource: https://groups.csail.mit.edu/medg/people/psz/ftp/Szolovits-Pauker78/Szolovits-Pauker78.html
    title: Szolovits and Pauker 1978, the two-axis evoking-strength and frequency precedent
---

# The Finding and Diagnosis Relationship Family

**Status:** Draft for review. This answers the request in the [25 August exchange](../../notes/review-exchange-2026-08-25-extract.md): a tentative, explicitly non-comprehensive catalog of the relationships needed between findings and diagnoses, to validate against the proposed edge object. Prior-art surveys were run 2026-09-01; primary sources are cited inline.

**Framing.** Everything here is a **class-level potential** in the vocabulary plane. Since the taxonomy is one and unrestricted (10 S1), the domain column below is the only structural thing that separates a Diagnosis from a FindingClass: a diagnosis is what can source `MAY_MANIFEST_AS`. That is a Claude observation recorded so the two-node-type decision can be revisited with it in view. A report edge between two Observations expresses a vocabulary relationship and can cite it ([03 §5](./03-draft-structures.md)); nothing here obliges any report to contain anything. With Diagnosis now agreed to be its own node type ([exchange §1](../../notes/review-exchange-2026-08-25-extract.md)), each relationship states its domain and range. F is FindingClass, D is Diagnosis, A is Assessment, G is the Grouping node type added on 2026-09-02 ([10 S8](./10-decision-record-2026-09-02.md)).

**Out of scope:** the anatomy family (`SCOPED_TO`, `ADJACENT_TO`), element bindings (`HAS_ELEMENT`), and the context edges to concept nodes ([03 §2](./03-draft-structures.md)). Those are separate families; keeping them out of this catalog is deliberate.

---

## 1. The family

Seven pairs and one escape hatch. Assertion direction is the left-hand name; tooling derives the inverse, following OIFM's registry draft ([00 §5.1](./00-current-understanding.md); note §7 below on its implementation status).

| Relationship (inverse) | From → To | Character | Meaning |
|---|---|---|---|
| `SUBTYPE_OF` (`HAS_SUBTYPE`) | F/D/G→F/D/G, either direction across the labels | transitive ⟨?⟩ ([00 Issue A](./00-current-understanding.md)) | taxonomy, more to less specific; written `rdfs:subClassOf` formally. One taxonomy over all three node types, unrestricted by the finding or diagnosis label; the earlier F→F, D→D restriction was withdrawn on 2026-09-02 ([10 S1](./10-decision-record-2026-09-02.md)) |
| `MAY_HAVE_COMPONENT` (`MAY_BE_COMPONENT_OF`) | F→F | compositional | the target can occur as a described sub-part with its own elements, and is genuinely optional in all cases; the gated case is the open conditionality question ([exchange §2](../../notes/review-exchange-2026-08-25-extract.md)) |
| `MAY_CAUSE` (`MAY_BE_CAUSED_BY`) | F/D→F/D | causal | the source can produce the target as a distinct second entity |
| `MAY_MANIFEST_AS` (`MAY_REPRESENT`) | D→F/D | evidential | the diagnosis can show itself as the target; the inverse is how a report reads, finding toward conclusion |
| `OCCURS_WITH` | F/D↔F/D | symmetric, associative | seen together; asserts and excludes nothing about causality or sequence (definition adopted from SNOMED CT, §6) |
| `MAY_PROGRESS_TO` (`MAY_PROGRESS_FROM`) | F→F, D→D | temporal | identity-preserving evolution: the same entity in a later state |
| `ASSESSED_BY` (`ASSESSES`) | F/D→A | interpretive | a standardized scheme applies to the source; which scheme applies in a given study comes from the exam object in the instance layer, not from this edge ([exchange §5](../../notes/review-exchange-2026-08-25-extract.md)) |
| `MAY_BE_RELATED_TO` | F/D↔F/D | symmetric, catch-all | an association the author cannot yet type; a triage queue, not a home. Every use is a candidate for replacement by a typed edge |

`INTERPRETED_FROM` (F/D/A→binding) stays as defined in [03 §2](./03-draft-structures.md): it is the fine-grained twin of `ASSESSED_BY`, naming the specific inputs a scheme is computed from rather than the scheme itself. Its domain was widened on 2026-09-02 from assessments to any class that interprets a measurement, which [03 §9](./03-draft-structures.md) already relied on for bile duct dilation ([08 §2](./08-worked-examples.md)).

The domain of `MAY_MANIFEST_AS` extends to D→D deliberately: radiologists use findings and diagnoses loosely enough that a diagnosis can manifest as another diagnosis (neurofibromatosis manifesting as optic glioma). That makes the boundary with `MAY_CAUSE` the load-bearing definition in this family, so it gets its own section.

## 2. Keeping manifestation and causation apart

**`MAY_MANIFEST_AS` is constitutive**: the target is the source showing itself. A striated nephrogram is pyelonephritis appearing on imaging, not a second disease.

**`MAY_CAUSE` is consequential**: the target is a distinct second entity the source produced. A renal abscess is a new thing pyelonephritis made.

The test: if the target resolved, would a clinician say the source "got better," or that "a complication resolved"? The first is manifestation, the second is causation.

**`SUBTYPE_OF` is a third thing, and the finding or diagnosis label does not decide it.** Subsumption means every instance of the source is an instance of the target, and it has a plain-language test: can you say "X without Y" and mean something? "Empyema without effusion" is not a sentence, so empyema is a subtype of pleural effusion even though one is labelled a diagnosis and the other a finding. "Consolidation without pneumonia" is an ordinary sentence, so consolidation is a manifestation of pneumonia and not a subtype. An obligate manifestation edge whose target is the whole of the source is a subtype edge in disguise and should be authored as one ([10 S1](./10-decision-record-2026-09-02.md)).

`MAY_PROGRESS_TO` is neither. It asserts identity-preserving evolution: acute hemorrhage becomes chronic hemorrhage, infarct becomes encephalomalacia. The entity persists and changes state. SNOMED CT is the precedent for insisting these stay separate: its `Due to` asserts causality while agnostic about sequence, its `After` asserts sequence while agnostic about causality, and the two are never conflated (SNOMED CT Concept Model, docs.snomed.org). Progression is a third, stronger claim: sequence plus identity. An edge author who can assert only sequence has no edge in this family and should say nothing, or use `OCCURS_WITH` if co-occurrence is the actual observation.

`OCCURS_WITH` takes SNOMED's `Associated with` wording as its definition: "a clinically relevant association between concepts without either asserting or excluding a causal or sequential relationship." The explicit double negative is the point; it stops the edge from silently absorbing weak causal claims.

## 3. Properties on manifestation edges

Two independent axes, both optional, at most one value from each axis per edge (SNOMED's self-grouping rule, adopted as an authoring constraint). They answer the reviewer's question about expressing that a finding is criterial for a diagnosis without any report-level obligation, which was rejected on clinical grounds: unadorned diagnoses, asserted with no supporting finding in the report, are common and must stay legal ([exchange §1.2](../../notes/review-exchange-2026-08-25-extract.md)).

### 3.1 Typicality: how often the diagnosis shows this finding

The HPO/Orphanet frequency scale, adopted verbatim with its percentage anchors (HPO annotation format; Orphadata science data description):

| Value | Range |
|---|---|
| `obligate` | 100% |
| `very_frequent` | 80 to 99% |
| `frequent` | 30 to 79% |
| `occasional` | 5 to 29% |
| `very_rare` | 1 to 4% |
| `excluded` | 0% |

An exact cohort ratio (`7/13`) or percentage may be given instead of a bin, exactly as HPO permits, since either restates an observed proportion a curator can cite. The defined ranges make every annotation auditable against literature; this scale has been exercised across hundreds of thousands of disease-to-phenotype annotations.

**`excluded` is the negative assertion.** An edge carrying it states the finding is essentially never seen with the diagnosis, which supports rule-out reasoning as a single open-world assertion on one edge, with none of the closed-world machinery of [00 Issue A](./00-current-understanding.md). It does sit oddly on an edge named `MAY_MANIFEST_AS`; the alternative is a separate negative edge type. Keeping it as a bin means one mechanism and matches Orphanet's practice, but the naming tension is real and flagged for review.

### 3.2 Specificity: how strongly the finding points to the diagnosis

Three ordered values, **omitted entirely when uninformative**. There is no `nonspecific` value: an absent property means no judgment is recorded, and judged-versus-unjudged is curation state, which lives in the governance layer, not the semantic one. Orphanet works the same way, only ever adding its flags when true.

| Value | Meaning |
|---|---|
| `pathognomonic` | seeing the finding is by itself sufficient to make the diagnosis. Orphanet's definition: "a sign whose presence indicates that a particular disease is present beyond any doubt"; also the top anchor of INTERNIST-1's evoking strength, "5 means that the manifestation is pathognomonic for the diagnosis" (Szolovits and Pauker 1978) |
| `highly_suggestive` | strongly narrows the differential toward this diagnosis but is not independently conclusive; roughly Orphanet's "major diagnostic criterion" territory |
| `suggestive` | meaningfully raises suspicion relative to a coincidental finding, without strongly narrowing the differential on its own |

Three levels, not five: INTERNIST-1/QMR and DXplain hand-scored exactly this axis on finer scales with small full-time teams, and DXplain's own group documented that curators disagreed about what the middle of the scale meant. A distributed committee annotating over years needs fewer, plainer rungs.

**No numeric escape hatch on this axis**, and the asymmetry with typicality is principled: a percentage restates one published cohort proportion, which is transcription, while a defensible likelihood ratio requires the finding's rate in the diagnosis and across the background population, which is research. The strongest structured precedent, LIRICAL, computes likelihood ratios downstream from frequency data rather than asking curators for them. If a numeric axis is ever wanted, derive it the same way from typicality plus prevalence.

Membership in published diagnostic criteria needs no fourth level: an edge already carries references, and a `highly_suggestive` edge citing the criteria publication expresses "major criterion of" more auditably than a flag would. Note the register trap: report-language certainty lexicons ("diagnostic of," "may represent," the Panicek and Hricak line of work) grade one radiologist's confidence in one instance. That is a different axis, and its phrases should not be borrowed for these values.

Whether the causal pair also takes typicality (how often pyelonephritis causes abscess) is left open for the reviewer's edge object to answer; nothing structural prevents it.

## 4. The differential is a derived view, not an edge

The differential of a finding is the set of diagnoses reachable over `MAY_REPRESENT`, together with its diagnosis subtypes now that the taxonomy crosses the label ([10 S1](./10-decision-record-2026-09-02.md)), filtered by the context edges (age stage, modality, anatomic scope), ranked by specificity then typicality. The differential of a diagnosis is its siblings under shared findings. No `DIFFERENTIAL_OF` edge type exists.

The precedent is direct. The Radiology Gamuts Ontology, the ontology-backed successor to Reeder and Felson, carries 55,000+ links using exactly two relation types, is-a and may-cause, and produces every differential by traversing incoming causal links to a finding (Budovec, Lam, and Kahn, RadioGraphics 2014; gamuts.net). No source surveyed, across RGO, HPO/Orphanet, SNOMED CT, UMLS, Radiopaedia, and STATdx, stores differentials as diagnosis-to-diagnosis edges; the curated ranked lists in practitioner references are editorial products keyed to one page, which is what a sort key over derived results reproduces.

Two consequences:

- **Mimics need no relationship type.** A mimic is a competitor in the derived differential whose `entity_type` is `normal_variant` or `technique_issue`. The mechanism carries the concept.
- **A missing direct edge is a signal, not a gap.** If two diagnoses are habitually confused and no shared finding connects them, the graph is saying a FindingClass is missing. Author the finding, not a workaround edge.

## 5. Deferred refinements, and why deferring is safe

Relationship types form their own hierarchy: a later, finer type can be declared a subproperty (`rdfs:subPropertyOf`) of a broader one, so queries over the broad type still find the fine assertions, and nothing authored today needs migration. Deferred on this basis:

- **`MAY_COMPLICATE`**, a future subproperty of `MAY_CAUSE`, adding the adverse-sequela connotation.
- **`PREDISPOSES_TO`**, weaker than causation (emphysema and pneumothorax), likely a subproperty of a broad association type.
- **An obscuration relation.** Class-level pairwise "X obscures Y" would be combinatorial and is not the real fact anyway; what is bounded and true is technique-issue-to-region ("beam hardening limits evaluation of the posterior fossa"), which is `SCOPED_TO` doing another job. Per-study limitation statements belong to the Observation layer, and whether the IHE IDR grammar can express "evaluation limited" is an open question for the IHE list ([`notes/ihe-idr-extract.md` §8](../../notes/ihe-idr-extract.md)).
- **A dedicated exclusion edge**: not needed, `typicality: excluded` covers the per-edge negative (§3.1).

## 6. Prior art anchors

| This family | RGO/Gamuts | RadLex 4.3 OWL | UMLS SN | SNOMED CT | HPO/Orphanet | INTERNIST-1/QMR |
|---|---|---|---|---|---|---|
| `SUBTYPE_OF` | is-a | is_a | isa | Is a | is_a | – |
| `MAY_HAVE_COMPONENT` | – | Has_Part (anatomy) | part_of | – | part_of | – |
| `MAY_CAUSE` | may-cause | **May_Cause** | causes | Due to | – | – |
| `MAY_MANIFEST_AS` | (folded into may-cause) | – | manifestation_of | – | the disease-to-phenotype annotation itself | the scored link itself |
| `OCCURS_WITH` | – | – | co-occurs_with | Associated with | – | – |
| `MAY_PROGRESS_TO` | – | – | precedes (weaker) | After (weaker) | – | – |
| `ASSESSED_BY` | – | – | evaluation_of | Interprets pair | – | – |
| typicality | – | – | degree_of (name only) | – | **frequency scale, adopted** | frequency 1 to 5 |
| specificity | – | – | – | – | pathognomonic flag (Orphanet/HOOM) | evoking strength 0 to 5 |

**RadLex verification, 2026-09-01.** `RadLex.owl` (github.com/RSNA/RadLex, 52MB) declares 52 object properties. `May_Cause` and `May_Be_Caused_By` exist, are declared `owl:inverseOf` each other, and carry roughly 850 assertion pairs; the remaining properties are anatomical and spatial, plus `Related_modality`. Two consequences: `MAY_CAUSE`/`MAY_BE_CAUSED_BY` align with RadLex naming exactly, satisfying the check-before-minting rule of [03 §2.1](./03-draft-structures.md), and the claim in [00 §2.4](./00-current-understanding.md) that the relation axioms were unverified is now closed in the affirmative. RGO folds what this family splits into manifestation and causation into a single may-cause; the split is justified by the separate Diagnosis node type, and §2 is what keeps it from collapsing back.

**A correction to [00 §5.1](./00-current-understanding.md):** OIFM's relationship registry exists only in the v2 draft schema ([`notes/oifm-schema-v2-draft.md`](../../notes/oifm-schema-v2-draft.md)); the live findingmodels repository implements no relationship mechanism at all (verified against the repo, 2026-09-01). OIFM is therefore a potential consumer of this family rather than prior art to reconcile with, and its models already plan GAMUTS index codes, which is a ready-made crosswalk seed.

## 7. Open questions for review

1. Does `OCCURS_WITH` need an association-strength property, or is untyped co-occurrence enough for alpha?
2. Does the causal pair take typicality (§3.2, last paragraph)? Assumed yes in the worked examples so they could be written (10 S18, a Claude default); still not decided.
3. `typicality: excluded` on an edge named `MAY_MANIFEST_AS` (§3.1): live with the naming tension, or split a negative edge type?
4. The conditionality fork ([exchange §2](../../notes/review-exchange-2026-08-25-extract.md), [`conditional-relationships-memo`](../../notes/conditional-relationships-memo.md)) is unresolved and constrains `MAY_HAVE_COMPONENT`; this catalog takes no position.
5. Whether relation types themselves carry mappings to their prior-art counterparts (e.g. `MAY_CAUSE` skos:exactMatch RadLex `May_Cause`) or the table above stays documentation.

**Consequential edits owed elsewhere once this is reviewed:** the [03 §2](./03-draft-structures.md) edge table gains the manifest and progression pairs and the two properties; [00 §2.4](./00-current-understanding.md) and [00 §5.1](./00-current-understanding.md) take the §6 corrections; the ten-exemplar-sets request and the workflow push from the [20 August call](../../notes/working-group-call-2026-08-20-extract.md) remain outstanding.
