---
type: Review Record
title: Design Questions Raised in Review
description: Five structural design questions raised in an April–May 2026 review of the OIFM material, with the answers given and each question's open/resolved status.
tags: [next-gen-schema, cde, review]
status: stable
generated: { by: ["human:talkasab", "claude-code/claude-fable-5"], at: 2026-07-29 }
sources:
  - id: correspondence
    resource: "Private email correspondence, 2026-04-30 to 2026-05-05 (not committed; contained personal contact details)"
    title: Review correspondence
    last_modified: 2026-05-05
  - id: oifm-overview
    resource: /notes/oifm-overview.md
    title: OIFM definitions overview — one of the three documents that prompted the exchange
    author: "human:talkasab"
    last_modified: 2026-07-29
  - id: oifm-schema
    resource: /notes/oifm-schema-v2-draft.md
    title: OIFM source-format schema v2 draft — circulated with the overview
    author: "human:talkasab"
    last_modified: 2026-04-20
  - id: oifm-metadata
    resource: /notes/oifm-metadata-fields.md
    title: OIFM metadata field reference — circulated with the overview
    author: "human:talkasab"
    last_modified: 2026-07-29
---

# Design Questions Raised in Review

**Status:** Record of an exchange; most questions still open
**Date of exchange:** 30 April – 5 May 2026
**Participants:** an external reviewer and Tarik Alkasab (author)

**Provenance.** Distilled from a private email thread. The original correspondence has been removed rather than committed, since it contains personal contact details and was not written for publication. Everything substantive is preserved below; what was dropped is addressing, pleasantries, and scheduling. Direct quotations are marked and are verbatim.

**Why this matters.** These are the sharpest questions the redesign has received. They came from someone reading the OIFM material cold and asking what *structurally* follows from it — and several remain unanswered. The reviewer's framing of the disagreement is worth keeping in view:

> "I can see a lot of conceptual alignment on where we want to arrive... Where I think we may diverge is in the structure to get there."

The reviewer also flagged the diagnosis question as decisive:

> "I ask because this is where I see the clearest gap between the current model and where I think we need to go."

---

## What prompted it

Tarik shared three OIFM documents — the definitions overview, the source-structure draft, and the metadata field reference — with the caveat that they are "AI-organized distilled notes from hours of detailed interactions," intended to be further distilled into prompts rather than read as specifications. The request was for a judgement about which ideas were compatible with the reviewer's own thinking and where the two diverged.

---

## Q1 — Does `entity_type` have structural consequences?

**Asked:**

> "Is entity_type intended to change how the object behaves structurally, for example driving validation rules or restricting what attributes are allowed, or is it primarily a classification label for downstream consumers? The answer changes how I think about it architecturally."

The observation behind it: the documents describe what each `entity_type` value *means* but are not explicit about what follows from the classification.

**Answered:**

> "We haven't (yet) found a material difference between the different entity types in terms of how they're specified/defined. It's almost analogous to the 'semantic type' concept in SNOMED, which doesn't affect the concepts themselves or how you can use them as labels, but could be used as useful context in downstream apps."

**Status: open at the time; since settled.** The answer given was "label, not constraint" — later analysis showed it half-right: some values carry structural obligations and some are pure labels, and the allowed values are now fixed at seven with `grouping` and `recommendation` dropped ([01 §5](./01-what-the-vocabulary-must-express.md)). The values and what each obliges a class to carry are in [01 §5](./01-what-the-vocabulary-must-express.md); the reasoning question it left behind is [00 Issue C](./00-current-understanding.md).

---

## Q2 — How does a measurement work as a finding rather than an attribute?

**Asked:** The overview describes measurement groupings as requiring "a flexible view of what a finding is." What does that flexibility look like *structurally* — is the finding object doing something different, or is it the same structure with different attributes? And why is a measurement a finding type at all rather than an attribute?

**Answered:** An individual measurement should indeed be an attribute. But a measurement *grouping* — modelled as a Finding object — does two jobs: it gives the attribute context, and it groups related measurements.

- Simple case: width–height–depth, which "in fact, could be a sub-component finding for many findings."
- Complex case: a set of specific angular measurements in the assessment of scoliosis that are always grouped together.

**Status: settled since.** The committee decided the multi-component representation (a quantity type with components, not a grouping finding; [00 §8 Decided](./00-current-understanding.md)). The record of the exchange: [Deck slide 13](../../notes/proposed-schema-changes-deck-extract.md) models width × height × depth as a *quantity type with three components* rather than as a grouping finding — two representations of the same thing. Subsequent work also separated measurement from interpretation and identified *method* as a third component; see [01 §4](./01-what-the-vocabulary-must-express.md).

---

## Q3 — What is a "grouping"?

**Asked:** `grouping` appears both as an `entity_type` value and as a concept in the overview. Is a grouping a finding model that has been labelled as such, or will it become its own object type? If it stays a finding, does it behave like any other finding structurally, or does it exist primarily to reference other findings rather than to describe a direct observation?

**Answered:** Acknowledged as "somewhat unfortunately nebulous." The motivating case is the radiologist who writes *"Upper abdomen unremarkable."*

That is currently modelled as a finding `upper abdominal abnormality` with `presence: absent`. This reflects what was said, but what it is really doing is referring to a larger basket of more specific findings — probably a hierarchy of them — and attaching "negative" to all of them by implication.

The proposed mechanism, quoted because the inference structure matters:

> "Then you could create an 'is-a' relationship between 'upper abdominal abnormality' and (among many, many others) 'hypodense liver lesion' (probably with a 'liver lesion' intervening sub-group). Then, if you had some specific application that was assessing a report for 'hypodense liver lesions' could do a sweep for its ancestors being 'negative' and pull that relevant fact."

**Status: open, and load-bearing.** This is the single motivating use case for inference in the whole design. It requires `is-a` to be genuine transitive subsumption, which is in tension with the SIIM minutes' statement that subtypes inherit nothing — see [00, Issue A](./00-current-understanding.md). It also carries a closed-world assumption: the sweep is only sound if the hierarchy beneath the class is complete *and* the radiologist actually assessed all of it. See [01 §1](./01-what-the-vocabulary-must-express.md).

---

## Q4 — How is a diagnosis represented?

**Asked:** The overview states that diagnostic terms are first-class findings. That reads cleanly for a diagnosis mapping to a single observation with its own attributes — pulmonary embolism being a good example, where presence, clot burden, proximity, and lobar involvement all sit naturally as attributes on one object.

Less clear is a diagnosis formed by *multiple* findings. Taking COVID-19 chest CT: if it is a Finding with `entity_type: diagnosis`, where do Ground Glass Opacity, Consolidation, Pleural Effusion, and Classification live? Attributes, sub-findings, or independent Finding objects connected by a relationship? And if the last, what does that relationship look like structurally?

**Answered — how radiologists actually state diagnoses.** Three patterns, with the examples given:

1. **Diagnosis asserted directly**, with no associated findings described: *"Pneumonia in the right lower lobe."* · *"Mild, uncomplicated sigmoid diverticulitis."*
2. **Findings described, then attributed to a diagnosis** (ideally in the impression): *"Right lower lobe opacity, consistent with pneumonia."* · *"Focal fat stranding and mural thickening in the distal sigmoid colon without organized collection or frank perforation, representing uncomplicated sigmoid diverticulitis."*
3. **Findings described, then a differential offered**: *"Right lower lobe opacity is likely atelectasis, but could represent pneumonia or aspiration in the appropriate clinical context."*

A further observation, which later turned out to be significant:

> "Note that the relationship can be contextual — sometimes a fracture is used as a finding, and sometimes as a diagnosis!"

**Answered — the proposed COVID-19 structure.** Layered:

- An **assessment-finding** representing the COVID-19 score, carrying a `Classification` attribute.
- Optionally an **"associated findings" multi-choice attribute** indicating the presence of potentially associated findings (opacity, pleural effusion, and so on).
- *Also* an **"associated with" relationship** between the COVID-19 classification and those potentially associated findings.
- At the observation layer, multiple observation objects — the classification, an opacity if present, a pleural effusion if present — with those becoming components of the classification observation while remaining first-class observation objects in their own right.

**Status: partially resolved.** The contextual finding/diagnosis shift is explained once a FindingClass is understood as a term rather than a thing: one term, used in two roles by two Observations ([01 §1](./01-what-the-vocabulary-must-express.md)). The structural question — attributes, sub-findings, or related objects — is still open, and note that the answer proposes *both* an attribute and a relationship for the same information, which is the kind of redundancy the decoupling work is meant to remove.

---

## Q5 — What distinguishes a multi-finding diagnosis from a grouping?

**Asked:**

> "If a diagnosis is defined entirely by a constellation of findings and has no direct attributes of its own, what separates it from a grouping structurally?"

**Status: unanswered in the exchange; since addressed.** The later resolution: neither is an `entity_type` at all — a grouping is a structural role visible in the `is-a` relationships, and a multi-finding diagnosis is a `diagnosis` whose definition lives in its relationships to finding classes ([01 §5](./01-what-the-vocabulary-must-express.md)). The original record: It is arguably the sharpest question in the thread: it asks whether two `entity_type` values are structurally distinguishable at all, which is Q1 restated as a concrete test case.

A possible line of attack from later work: if `entity_type` is really two questions — what is reported on, and what kind of statement it is — then diagnosis and grouping differ on the second, not the first ([01 §5](./01-what-the-vocabulary-must-express.md)). The smoke test's upper-abdominal-abnormality case exercises it.

---

## Where the exchange left off

The reviewer proposed stopping the written exchange and moving to a live compare-and-contrast, on the grounds that the examples had clarified how terminology needs to stay flexible enough to reflect real reporting patterns, and had surfaced structural questions better worked through together.

**Open items carried forward:** Q1, Q2, Q3, and Q5 in full; Q4 in part. The reviewer's own notes on the diagnosis modelling gap were offered but not yet shared at the close of the thread.
