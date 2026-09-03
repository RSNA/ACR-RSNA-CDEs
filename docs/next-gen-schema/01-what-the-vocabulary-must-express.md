---
type: Analysis
title: What the Vocabulary Must Express
description: What the finding vocabulary has to be able to express — what a FindingClass is, anatomic scope guidance, the breadth of what is reported on, measurement versus interpretation, and what entity_type is recording.
tags: [next-gen-schema, cde, ontology, analysis]
status: draft
generated: { by: ["human:talkasab", "claude-code/claude-fable-5"], at: 2026-08-19 }
sources:
  - id: companion
    resource: /docs/next-gen-schema/00-current-understanding.md
    title: Current understanding (companion document)
    author: "human:talkasab"
    last_modified: 2026-07-28
  - id: siim-minutes
    resource: /notes/siim-meeting-extract.md
    title: SIIM committee meeting minutes (extract)
    author: team:rsna-acr-cde-committee
    last_modified: 2026-06-12
  - id: deck
    resource: /notes/proposed-schema-changes-deck-extract.md
    title: Proposed schema changes deck (extract)
    author: team:rsna-acr-cde-committee
    last_modified: 2026-06-12
  - id: committee-notes
    resource: /notes/committee-notes-extract.md
    title: Committee meeting notes (extract)
    author: team:rsna-acr-cde-committee
  - id: recommendations-2
    resource: /notes/schema-recommendations-part2.md
    title: "CDE schema recommendations, Part II (extract)"
    author: "human:talkasab"
  - id: anatomiclocations
    resource: "https://raw.githubusercontent.com/talkasab/anatomiclocations.org/main/data/body_parts.json"
    title: AnatomicLocations.org body_parts.json, release 1.0.0-rc.1 — analyzed directly 2026-07-28
    author: "human:talkasab"
  - id: published-corpus
    resource: "https://radelement.org"
    title: The ~1000 published CDE sets (leakage-analysis corpus)
    author: team:rsna-acr-cde-committee
---
# What the Vocabulary Must Express

**Status:** Working document — reasoning in progress
**Date:** 2026-08-19
**Companion to:** [00-current-understanding.md](./00-current-understanding.md)

**Purpose:** Work out what the vocabulary has to be able to express, upstream of any technology decision. Nothing here depends on choosing a database, a schema language, or an ontology framework.

---

## 1. What a FindingClass is

**A FindingClass is a term, not a thing.** It names a kind of finding so that an Observation can point at it ([00 §1.3](./00-current-understanding.md)). What is *asserted* — that the finding is present, absent, 8 mm, unchanged — happens in the Observation, through DataElement values.

That settles something that otherwise looks paradoxical. `presence: absent` is a near-universal element in the corpus, and "no pulmonary nodule" is a clinically important statement that both the SIIM material and the OIFM guidance insist on supporting. If a FindingClass named a set of *actual nodules*, an Observation carrying `presence: absent` would be pointing at a nodule that does not exist. As a term it is unremarkable: the Observation uses "pulmonary nodule" to say that no such thing is there.

Three consequences for the vocabulary:

- **Finding versus diagnosis is not a property of the term.** [02 Q4](./02-review-questions.md) records that "sometimes a fracture is used as a finding, and sometimes as a diagnosis." That is one term used in two roles by two Observations. Whatever `entity_type` is recording (§5), it is not a fact about the bodily state.
- **The vocabulary never makes claims about patients.** A FindingClass says what *could* be said; it is never true or false of anyone. Claims live in Observations, which belong to the grammar ([00 §1.1](./00-current-understanding.md)).
- **Inference runs over the term hierarchy.** "Upper abdomen unremarkable" propagating down to more specific findings ([02 Q3](./02-review-questions.md)) is a claim about what `is-a` between *terms* licenses — vocabulary business, and [00, Issue A](./00-current-understanding.md).

---

## 2. Anatomic scope guidance

The vocabulary owes each FindingClass a statement of which anatomic locations are congruent with it ([00 §1.4](./00-current-understanding.md)). The [initial proposal](../../notes/schema-recommendations-part2.md) says what that statement ranges over: "as broad as a body region (e.g., the abdomen), a **structure type** (e.g., arteries), or as specific as a named body structure (e.g., anterior cruciate ligament)."

It is **guidance, not a location**. A `clavicle fracture` class records `clavicle`; an actual fracture is at `left clavicle`. The class-level value is deliberately more general than any instance value and is doing a different job — suggesting and constraining the value space rather than stating where anything is. Laterality in particular is carried by the location node, not by the guidance and not by a DataElement ([00 §2.6](./00-current-understanding.md)).

The three kinds behave differently, and only two are about *where* anything is:

| Guidance | Example | How congruence is checked |
|---|---|---|
| named structure | anterior cruciate ligament | identity, or descendant of |
| region | abdomen | containment |
| **structure type** | arteries; tendons; lymph nodes | **is-a — not spatial at all** |

So calling the field `Location`, as deck slide 19 does, is wrong beyond nomenclature: it invites the containment reading, which fails for the third row. Tendons are scattered across the body and share no common container. **Anatomic scope**, not location — and the guidance should record *which kind* it is rather than leaving a consumer to infer it from the node.

### 2.1 Not every place is a structure

An anatomic **structure** and an anatomic **location** are different things: the thyroid gland is a structure; "in the thyroid gland" is that structure being used to say where something is. The places a finding can be are wider than the structures RadLex names:

| Kind of place | Example |
|---|---|
| structure | right upper lobe |
| potential space | pleural space (pleural effusion) |
| cavity | peritoneal cavity (pneumoperitoneum) |
| region or zone | lung periphery; upper zone |
| interface or junction | gastroesophageal junction |
| position relative to a landmark | 3 cm from the hilum; anterior to the trachea |

A vocabulary in which location means "a pointer to an anatomic structure" cannot express the rest — and authors will do what they did last time: invent a value-set element and fill it with ungrounded strings (the failure documented in [deck slide 14](../../notes/proposed-schema-changes-deck-extract.md)). The last row is what the remaining location-flavoured DataElements are for: shading on top of a location code, not a restatement of it. Which of these places the anatomy substrate can currently name is tracked in [04-anatomy-gaps.md](./04-anatomy-gaps.md).

### 2.2 Guidance must be machine-resolvable

Scope guidance does two jobs: it **suggests** — offering an author or a tool the locations that make sense for this kind of finding — and at the strong end it **constrains**, making some pairings detectable as errors. Enforcement is a grammar concern ([00 §1.1](./00-current-understanding.md)); what the vocabulary owes is guidance a downstream check *can* act on — a resolvable value, a declared kind, and a declared strength.

Two of the three kinds resolve today by plain traversal. Run against AnatomicLocations.org on 2026-07-28:

```
lung  →  thorax  →  whole body
toe   →  ankle   →  lower extremity  →  whole body
```

The paths diverge immediately, so `lung` guidance rejects a toe location with a tree walk. The resource carries two distinct hierarchies — physical containment and functional part-of — so any such walk must declare which it means ([00 §2.6](./00-current-understanding.md)). The third kind, structure type, resolves once the is-a relation being added upstream lands.

### 2.3 Guidance strength varies

This cannot be a single "allowed location" field:

| Finding | Guidance | Strength |
|---|---|---|
| pulmonary nodule | lung | definitional — violation is an error |
| rib fracture | ribs | definitional |
| metastasis | almost anywhere | very weak |
| foreign body | anywhere | none |
| free air | air where air should not be | **not anatomic at all** |

So guidance records its strength — required / expected / unconstrained — since that is the difference between rejecting and warning.

### 2.4 Class-level scope versus value-level location

For "pulmonary nodule," the scope guidance and the class's *identity* are arguably the same fact stated twice: it is called pulmonary because it is in the lung. That reopens the "subtypes vs. generic findings with location attributes" discussion in the [SIIM minutes](../../notes/siim-meeting-extract.md) and the too-broad/too-narrow tension in the OIFM guidance ("mass where? lung mass, mediastinal mass, renal mass are findings"). Since the grammar always carries location as its own pointer, the presumption should lean toward the general class — `nodule` scoped to lung — with `pulmonary nodule` as a distinct FindingClass only when it is a genuinely different kind of thing rather than the same thing somewhere else.

**This is the highest-frequency modelling decision in the corpus.** Not yet resolved; the smoke test's thyroid-nodule case exists to exercise it.

---

## 3. FindingClasses must cover more than abnormalities

The obvious reading — that a FindingClass names a kind of abnormality — is too narrow.

Radiologists routinely characterize **perfectly normal structures**, giving measurements with no claim that anything is wrong. Common bile duct calibre, ovarian volume, bladder volume, endometrial thickness. A large fraction of ultrasound reporting is exactly this.

So the vocabulary must supply terms for at least:

| Kind of thing reported on | Example |
|---|---|
| an abnormality | pulmonary nodule |
| a **normal structure** | common bile duct caliber — via bindings on the location, not a FindingClass (§3.1) |
| a physiologic quantity | peak systolic velocity at the renal artery ostium |
| a device | pacemaker lead position |
| the image itself | motion artifact |
| a **normal variant** (?) | cervical rib, azygos fissure |

The last row is unsettled.

### 3.1 Normal structures: no FindingClass at all — proposal

Since DataElements have life independent of FindingClasses, and the anatomy vocabulary already names almost every normal structure, **a normal structure needs no FindingClass**. The descriptors of a structure — caliber, wall thickness, length, volume, echogenicity, patency — are DataElements **bound directly to the AnatomicLocation node**: `common bile duct (RID199) HAS_ELEMENT caliber`. An Observation describing the structure then points at the *location* as its subject, rather than at a FindingClass, and carries the relevant element values. Worked through in [03 §9](./03-draft-structures.md).

What this buys:

- The structure-vs-property question (`common bile duct` with a `caliber` element, or `bile duct caliber` as a class?) dissolves — there is no class, and the paired-structure test passes trivially: renal length is `kidney (RID205) HAS_ELEMENT length`, observed on `left kidney (RID29663)`.
- **Bindings inherit down the anatomy.** Bind `length` to the unsided `kidney` and the laterality triad gives it to both sides; bind `diameter` to the structure type `artery` once the is-a relation lands ([04](./04-anatomy-gaps.md)) and every artery has it. One binding covers hundreds of structures.
- The abnormality stays a FindingClass: `bile duct dilation` is a `diagnosis`, `INTERPRETED_FROM` the caliber binding — the measurement/interpretation split of §4 made concrete.

What it requires, to be taken to the committee and to IHE:

- ~~The grammar's Observation subject must be a FindingClass or an AnatomicLocation.~~ **Already so**: IDR encodes observations on anatomic entities with no morphology and a property code — its own examples include "pancreatic duct diameter is 2 mm" ([`notes/ihe-idr-extract.md` §2](../../notes/ihe-idr-extract.md)). No grammar change needed.
- We attach `HAS_ELEMENT` edges to nodes we do not own. That is already true of `SCOPED_TO`; the bindings are ours, the nodes are RadLex's, and their lifecycle propagates.
- `entity_type: measurement` shrinks to composite indices that are not one structure's property (cardiothoracic ratio); most former "measurement classes" become location bindings (§5).

**Normal variants are not affected**: a cervical rib or azygos fissure remains a FindingClass with `entity_type: normal_variant` (§5). The location treatment is for the *descriptors of normal anatomy*, not for variant anatomy.

---

## 4. Measurement, method, and interpretation are separate things

"Peak systolic velocity at the renal artery ostium is 350 cm/s" and "this represents hemodynamically significant stenosis" are **two assertions**, with different truth conditions, different provenance, and different failure modes. One is measured, on an occasion, with a technique. The other is inferred, by a person, against a threshold, from a guideline.

### 4.1 Thresholds move; measurands and methods do not

**Thresholds move; measurands and methods do not.**

Store "severe stenosis" and the criteria are later revised: the stored data is now wrong and unrecoverable. Store the velocity plus a separate interpretive assertion citing which criteria it applied: the interpretation can be re-derived and the change audited.

For a corpus intended to support longitudinal analytics across decades, this is not a nicety. It is demonstrated in miniature by Keats & Sistrom's *Atlas of Radiologic Measurement* (2001) — twenty-five years on it remains the reference for *what and how* to measure, while some of its *thresholds* have moved.

### 4.2 Corollaries

- **Confidence belongs to interpretation.** The committee notes propose confidence values (definite / probable / possible). One does not *possibly* measure 350 cm/s; one possibly concludes stenosis.
- **Measurements must stand alone.** §3 establishes that measurements frequently carry no interpretation at all. So the measurement assertion has to be independently well-formed — which argues for interpretation being a *separate linked assertion* rather than a field on the measurement.
- **This principle is already written down, in a narrower form.** The OIFM guidance separates a pulmonary nodule model from a Lung-RADS model "because different radiologists might describe the same nodule but assign different risk categories." Finding-vs-assessment is one instance of observation-vs-interpretation.

### 4.3 Method belongs in the definition

A measurement reference entry separates three things:

1. **the measurand** — what is measured, on what structure
2. **the method** — plane, landmarks, phase, angle correction, caliper placement
3. **the threshold** — what the value means

We had (1) and (3). **Method is constitutive, not contextual.** A common bile duct measured in the wrong plane is not the same measurement. Renal artery PSV depends on angle correction. Two "sizes" obtained by different techniques are not comparable, and treating them as one number is how longitudinal analytics quietly go wrong.

The [SIIM minutes](../../notes/siim-meeting-extract.md) treat this as optional — "the schema will allow for optional specification of measurement context, such as plane or axis." On the evidence of the measurement literature, that understates it: for many measurements the method is part of what the measurement *is*, and belongs in the class definition.

---

## 5. `entity_type`: allowed values

`entity_type` has resisted definition — its values are not mutually exclusive, and [02 Q1 and Q5](./02-review-questions.md) ask what structural consequences it has and how two of its values differ at all. The resolution: keep the values radiologists recognize, drop the two that are not kinds of finding, and make explicit what each value obliges a FindingClass to carry.

| Value | Meaning | A class of this type must carry |
|---|---|---|
| `finding` | what you SEE — requires further characterization to reach a diagnosis | value sets for its DataElements |
| `diagnosis` | what you CONCLUDE — a nameable pathologic entity | ~~confidence; the criteria applied~~ — struck 2026-09-02: confidence belongs to the report-plane assertion, for findings just as much as diagnoses ([10 S4](./10-decision-record-2026-09-02.md)); Diagnosis is now its own node type rather than an `entity_type` value ([exchange §1](../../notes/review-exchange-2026-08-25-extract.md)) |
| `measurement` | a quantified index not belonging to one structure (cardiothoracic ratio) — single-structure measurements are location bindings (§3.1) | quantity type, permitted units, method (§4.3) |
| `assessment` | a standardized score or category applied to findings | the scale, and what it is computed from |
| `normal_variant` | present and unusual, typically not pathological | — |
| `device` | a device, its position or integrity | — |
| `technique_issue` | a property of the study itself | — |

The finding/diagnosis definitions are OIFM's, unchanged: a finding is what you see; a diagnosis is what you can name from the imaging appearance. The same real-world entity can appear under both — "sometimes a fracture is used as a finding, and sometimes as a diagnosis" ([02 Q4](./02-review-questions.md)) — because `entity_type` classifies the *term as used*, not the bodily state (§1).

**Dropped from the OIFM enum:**

- `recommendation` — a suggested follow-up is not a finding. It has no subject in the patient, and under the IHE grammar it is a different element of the report, not an Observation pointing at a FindingClass.
- `grouping` — (superseded 2026-09-02: a narrow `Grouping` **node type** returns for the negative-only nodes such as `renal abnormality`, which cannot be a FindingClass or a Diagnosis once those are separate types and the node parents both; [10 S8](./10-decision-record-2026-09-02.md). The argument below still holds for positively reportable classes.) "a collection of related findings described together" is a structural role, not a kind of finding. `upper abdominal abnormality` is a `finding` that happens to sit above others in the is-a hierarchy; whether a class is a grouping falls out of its relationships. Making it also an `entity_type` value would state the same fact twice. (The inference question it raises is [00, Issue A](./00-current-understanding.md).)

**Third column is the point.** The values differ in what they structurally require, which is what [02 Q1](./02-review-questions.md) was asking after: for `measurement`, `diagnosis`, and `assessment` the answer to "does entity_type have structural consequences" is yes; for the rest it is a classification label. To be tested against the published sets in the smoke test.

## 6. What this settles in [00](./00-current-understanding.md)

- **Issue H** — location is a grammar-level pointer; what the vocabulary owes is anatomic scope guidance over three kinds of value, with a declared kind and strength (§2).
- **New requirement** — the anatomy substrate must be able to name structure *types*; being added upstream ([04](./04-anatomy-gaps.md)).
- **New requirement** — measurement method as a first-class part of quantitative definitions (§4.3).
- **`entity_type`** — allowed values fixed; `grouping` and `recommendation` dropped (§5).
- **Modelling guidance** — presumption toward general FindingClasses with location carried separately (§2.4).
