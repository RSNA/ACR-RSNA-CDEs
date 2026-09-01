---
type: Review Record
title: Schema Review Exchange, 25 August 2026 — Extract
description: Sanitized extract of the 25 August 2026 email exchange on the next-generation schema, covering the Diagnosis node and its relationship types, conditional relationships versus subtype classes, bilaterality, anatomic scope for scored slots, and how study indication selects an assessment.
tags: [committee, review, next-gen-schema, diagnosis, conditionality, laterality]
status: stable
generated: { by: "claude-code/claude-opus-5", at: 2026-08-31 }
verified: [{ by: "claude-code/claude-opus-5", at: 2026-08-31 }]
sources:
  - id: thread
    resource: raw_sources/schema_exchange_2026-08-25.txt
    title: Email thread, 21 to 26 August 2026 (internal; kept out of the public repo)
    last_modified: 2026-08-26
  - id: memo
    resource: /notes/conditional-relationships-memo.md
    title: The attachment to the final message in the thread
    author: "human:external-reviewer"
  - id: call
    resource: /notes/working-group-call-2026-08-20-extract.md
    title: The call this exchange continues
sanitization: Participants other than the repo owner (Tarik Alkasab) are referred to by role. Addressing, signatures, contact details, affiliations, scheduling, and corporate disclaimers removed. Obvious typographical slips in quoted text are silently corrected; nothing else in a quotation is altered.
---

# Schema Review Exchange, 25 August 2026

**Status:** Record of an exchange. Five topics raised, five answered, three items left owing.
**Dates:** 21 to 26 August 2026.
**Participants:** Tarik Alkasab and the external reviewer drafting the model.

**Provenance.** Distilled from a private email thread, following the precedent set by [`docs/next-gen-schema/02-review-questions.md`](../docs/next-gen-schema/02-review-questions.md): the original correspondence is not committed, since it carries contact details and was not written for publication. Everything substantive is preserved. What was dropped is addressing, pleasantries, scheduling, and disclaimer boilerplate. Direct quotations are marked and are verbatim.

**What prompted it.** Tarik pushed the analysis bundle to `next-gen-2026` on 21 August and invited comment. The reviewer read it and replied with five structural questions on 25 August. This continues the working-group call of 20 August ([call extract](working-group-call-2026-08-20-extract.md)) and, further back, the review round recorded as [02](../docs/next-gen-schema/02-review-questions.md).

---

## 0. The reviewer's overall read

Broad agreement on shape. Verbatim:

> "the node types you modeled and edge names mostly align and make sense with my understanding of the proposed shape."

One methodological criticism, worth keeping because it is actionable:

> "I see some slight mismatch between worked out examples and some items listed as decided/defined"

Specifically, the edge properties declared in the [03 §2](../docs/next-gen-schema/03-draft-structures.md) edge table have not been carried into the worked examples, so the examples understate what the model already says an edge can hold. The reviewer read this as working notes catching up with fast decisions rather than as disagreement, and noted that the edge-property direction is the one she would have argued for anyway.

**This is a real repository defect, not a misreading.** It belongs on the housekeeping list.

---

## 1. The Diagnosis node

Agreed on the 20 August call that Diagnosis needs to be worked out separately from Finding ([call §4.4](working-group-call-2026-08-20-extract.md)). The reviewer deferred the clinical validity of that split to Tarik and asked what follows structurally.

**Answered.** Yes, a separate node type. Verbatim:

> "I'm pretty confident we can create a separate kind of diagnosis node that will be useful, although I think it may end up looking quite similar to our finding node. I don't think we need to let that bother us."

**Bearing on the documents.** [01 §5](../docs/next-gen-schema/01-what-the-vocabulary-must-express.md) currently models `diagnosis` as one of seven values of `entity_type` on a single `FindingClass` node type, and argues that a term shifts between the finding and diagnosis roles by context. Separate node types is a different answer and supersedes it.

### 1.1 Can a Diagnosis carry its own DataElements?

**Asked.** Expected yes, on the evidence of existing published Sets that represent diagnoses and carry qualifiers such as severity that attach to the diagnosis rather than to any one finding.

**Answered: yes.** A diagnosis points at its own data elements.

### 1.2 Relationship types for Diagnosis

**Asked.** A starting catalogue, with inverses, and one design question about how to express a finding that is required for a diagnosis:

| Proposed pair | Meaning |
|---|---|
| `MAY_CAUSE` / `MAY_BE_CAUSED_BY` | one entity causes another, or is a complication of it, rather than being evidence for it |
| `MAY_BE_REPRESENTED_BY` / `MAY_REPRESENT` | a finding supports a diagnosis without establishing it; the diagnosis can hold without this finding |
| `MUST_HAVE_FINDING` / `IS_KEY_FINDING_OF` (proposed new) | the diagnosis does not hold without this finding |

The design question: should the required case be its own edge pair, or should it reuse `MAY_REPRESENT` with `required: true` on the edge? The reviewer argued for the separate pair:

> "the edge name is the strongest signal for anything reading the graph, and a required flag alongside MAY_ is both easy to miss and reads oddly."

She also asked for the full catalogue to be identified now even if alpha does not implement all of it, including differential relations between diagnoses:

> "with named edges, anything we miss risks being expressed as one of the existing edges with a note, which is the pattern I hope we can move away from."

**Answered.** The relationship types for diagnosis are potentially different from a finding's, and that difference is itself the argument for making diagnosis its own node type. There will be considerably more of them than the three pairs proposed, both diagnosis to diagnosis and diagnosis to finding.

**The `MUST_HAVE_FINDING` pair is rejected**, on clinical grounds rather than modelling ones. Verbatim:

> "I think that too often it's going to be the case that we are going to have what amount to unadorned or unsupported diagnoses. That is, diagnoses with no associated finding at all in the report itself. I don't think we can require anything associated with a finding."

This is the same observation recorded as pattern 1 in [02 Q4](../docs/next-gen-schema/02-review-questions.md), a diagnosis asserted directly with no findings described. Note the scope: it rules out a *report-level* obligation. Whether the vocabulary may still record that a finding is criterial for a diagnosis, without obliging any report to contain it, was not separated out in the answer.

**Owing: Tarik.** A tentative, explicitly non-comprehensive list of the diagnosis-to-finding and diagnosis-to-diagnosis relationships that need to exist, so the reviewer can validate it against the proposed edge object. Requested 26 August.

---

## 2. Conditional relationships

The largest topic, and the one still open.

**Asked.** Conditionality between elements is currently deferred to the template layer ([00 §4.1](../docs/next-gen-schema/00-current-understanding.md), [03 §8](../docs/next-gen-schema/03-draft-structures.md)). The reviewer accepted that the *display* problem the legacy flat sets had is largely dissolved by structurally consistent findings and an explicit `presence: absent`. She argued a different problem remains: **relationships gated by the value of another element on the same finding.**

The case: `MAY_HAVE_COMPONENT` from `pulmonary nodule` to `solid component` applies only when attenuation is part-solid. Her argument, in four parts:

1. **Missing is ambiguous.** Without a condition, an absent solid-component observation could mean the nodule was solid so there was nothing to describe, or that it was part-solid and the component was not measured. Those are different facts and pooled data cannot separate them.
2. **It invites a nonsense assertion.** Nothing stops an extractor recording solid component `presence: absent`, which is a claim about something that was never there to have a presence.
3. **The condition is already asserted, just not structurally.** The `MAY_HAVE_COMPONENT` note in the spec reads "finding - sub-finding of a part-solid nodule, with its own size". Prose in a note is not actionable downstream, which also blocks generating a consistent resolved artifact for vendors. **Verified: this note text is exactly as quoted, in [`examples/pulmonary-nodule.neighborhood.json`](../docs/next-gen-schema/examples/pulmonary-nodule.neighborhood.json).**
4. **It is not template-varying.** The condition holds in every template, which is what makes deferring it to the template layer look like the wrong home for it.

The practical consequence she draws: with a condition, a solid nodule compiles to a shape carrying no component fields at all, so there is nothing for an extractor to fill in wrongly. Without one, every nodule carries the component fields and the extractor decides whether they apply, which is close to the legacy pattern of listing everything and leaving the inapplicable blank.

A second candidate offered tentatively: a `calcification pattern` element applying only when internal features include calcification. She flagged this one as speculative and asked for clinical judgement on whether real cases justify the mechanism.

**Answered: counter-proposal, not agreement.** Conditions may be too complicated. Instead, define **multiple finding classes** for the family: `pulmonary nodule` with sub-finding classes `solid pulmonary nodule`, `part-solid pulmonary nodule`, and so on. `HAS_COMPONENT` is then required on the part-solid class and absent from the others. Offered as a general rule:

> "This might be a general pattern. When deciding between attribute and subtype, if the distinction would affect the relationships, then use a subtype."

Separately confirmed: a `MAY_HAVE_COMPONENT` relationship type does make sense, **but only where the component is genuinely optional in all cases**, with nothing gating it.

**Follow-up.** The reviewer replied with a written engineering comparison of the two options, committed as [`conditional-relationships-memo.md`](conditional-relationships-memo.md). Its recommendation is a condition on the edge, on the grounds that subtyping without inheritance duplicates finding-level structure that nothing prevents from drifting, while subtyping *with* inheritance means building a resolution mechanism broader than the condition property it would replace. It offers a test for choosing between them: if the relationship in question were removed, would the distinction still warrant its own FindingClass? If yes, subtype; if no, condition.

**Status: open.** A genuine fork in the model, with a written argument on each side and no decision.

---

## 3. Laterality and bilaterality

**Asked.** The notes drop laterality as a DataElement, since AnatomicLocations.org carries left, right, and unsided as distinct nodes and IDR has its own laterality field ([03 §7](../docs/next-gen-schema/03-draft-structures.md)). The reviewer flagged that this **supersedes the committee's agreed reusable-element list** ([committee notes](committee-notes-extract.md)) but agreed with the change, seeing inheritance from the anatomy hierarchy as a gain.

Her open question: how is **bilateral** represented? If laterality lives on the location, is a bilateral finding two instances rather than one instance with a bilateral value? Should instantiating both be default behaviour? And how is the difference handled between findings that differ on each side and findings where both sides share a characteristic the report states once?

She noted the question generalizes past laterality, arising at other levels of anatomic granularity where characteristics differ only in some regions, and argued that whatever resolves it should be a general mechanism rather than a laterality rule.

**Answered.** Both, depending on the case, and the choice is clinical rather than mechanical:

- An Observation must be allowed to occur in **multiple locations**. Multifocal pneumonia in both left lung and right lung is one Observation with two location pointers.
- But sometimes bilaterality means **separate findings**, one per side. Bilateral adrenal nodules are two findings, not one.

**Bearing on the documents.** This is a constraint on the grammar, not on the vocabulary: it requires the IDR Observation to accept more than one anatomic target. Nothing in [00 §1.3](../docs/next-gen-schema/00-current-understanding.md) or the [IDR extract](ihe-idr-extract.md) records whether it does. It should be checked against the supplement and added to the IHE list if it does not. The generalization the reviewer asked for, a mechanism covering shared characteristics across anatomic granularity, was not addressed.

---

## 4. Positional references, and whether scoring needs anything special

**Asked.** A clarification of a point the reviewer had put poorly on the call as a "location property on edge". The real cases are **assessments with internal structure**: the Curie Score's ten scored anatomic segments summing to a total, or Coronary CTA's nine named vessel segments. In the legacy sets the anatomy for each slot sits in the element name or in free-text definition, so it is not queryable.

Her proposed resolution: `SCOPED_TO` on each child makes the anatomy reachable, and the slot identity is already carried by the name the standard gives it. She asked whether that is how it is intended to work, and whether other scoring methods need anything beyond it.

**Answered: yes, and it extends further.** It should be possible to tie **data element definitions** to specific anatomic locations where they are specific to them, and `SCOPED_TO` is likely the right way.

**Bearing on the documents.** [03 §2](../docs/next-gen-schema/03-draft-structures.md) currently types `SCOPED_TO` as FindingClass to AnatomicLocation only. The answer extends its domain to DataElement. That is an edit to the edge table, and it sits close to the existing normal-structure mechanism, where `HAS_ELEMENT` already takes an AnatomicLocation as its subject ([03 §9](../docs/next-gen-schema/03-draft-structures.md)).

---

## 5. Assessment and study indication

**Asked.** The pulmonary nodule points `ASSESSED_BY` at both Fleischner recommendation and Lung-RADS category, distinguished only by free-text notes reading "assessment - incidental" and "assessment - screening". **Verified: exactly as described in the spec.** The reviewer read this as deliberate looseness rather than an oversight, but asked whether it generalizes: if other findings turn out to carry competing schemes keyed to different circumstances, the selector may need to be structural rather than accumulating in notes. Since a nodule is not itself a screening concept, she suggested the selector is a qualifier on *which assessment applies*, and asked whether it belongs as a property on the `ASSESSED_BY` edge.

**Answered: no, and deliberately so.** It is true that one finding type may be assessed by different schemes in different situations, but the selector comes from the **exam**, which is a separate object in the instance layer that the Observation links to, and which carries the indication. It should not be embedded in this part of the data model.

**Bearing on the documents.** This introduces an instance-layer object nothing in the bundle currently names. [03 §5](../docs/next-gen-schema/03-draft-structures.md) draws two planes, vocabulary and report; the exam is a third thing the report plane needs and does not have. It should also be checked against IDR, which presumably has an imaging-study context already.

---

## 6. Test cases requested

The reviewer asked to work both approaches through **two or three existing published Sets**, with clinical judgement on whether each is a legitimate conditional case or merely a badly modelled one. Her candidates, with the condition written into element names rather than expressed structurally:

- **ECMO Cannula (RDES332).** Cannulation site appears to gate three elements: "Vein approach (if venous)", "Artery approach (if arterial)", and "Distal tip location (venous)". The arterial case has no distal tip element at all.
- **Ventricular Shunt Catheter (RDES329).** "Valve Setting (if programmable)" carries a "not applicable" value that appears to be doing the work a condition would do.

She flagged that these may not survive migration as good examples and invited replacements.

---

## Appendix. Verification against the published sets

Checked against the live RadElement API on 31 August 2026. The reviewer's readings are accurate, one identifier in the memo is wrong, and the sets contain two further conditional patterns she did not cite.

**RDES332, Extracorporeal membrane oxygenation (ECMO) Cannula.** Confirmed. Eight elements:

| Element | Values |
|---|---|
| RDE2310 Presence | present, absent, indeterminate, unknown |
| RDE2311 Status | new placement, unchanged, retracted, removed, advanced |
| **RDE2312 Cannulation Site** | **venous, arterial** |
| RDE2313 Appropriate location | no, yes |
| RDE2314 Side | left, right, **not applicable (na)** |
| RDE2315 Vein approach (if venous) | internal jugular, external jugular, subclavian, femoral |
| RDE2316 Artery approach (if arterial) | femoral, subclavian, carotid |
| RDE2317 Distal tip location (venous) | right atrium, superior vena cava (SVC), inferior vena cava (IVC) |

Cannulation Site does gate all three, and there is indeed no arterial distal tip element. Note also that `Side` carries a "not applicable" value, the same evasion the reviewer identified in the shunt set.

**RDES329, Ventricular Shunt Catheter.** Confirmed, and it carries a second, cleaner conditional the reviewer did not mention. Nine elements:

| Element | Values |
|---|---|
| RDE2278 Presence | absent, present |
| RDE2279 Status | new placement, unchanged, complication, removed |
| **RDE2280 Shunt Type** | **ventriculoperitoneal (VP), ventriculoatrial (VA), ventriculopleural** |
| RDE2281 Appropriate location | no, yes |
| RDE2282 Proximal tip location | right lateral ventricle, left lateral ventricle, third ventricle, not identified |
| **RDE2283 Distal tip location** | **peritoneal cavity, right atrium, pleural cavity** |
| **RDE2284 Valve Type** | **programmable, fixed pressure** |
| RDE2285 Valve Setting (if programmable) | specify setting, **not applicable** |
| RDE2286 Complications | none, catheter fracture, tip migration |

Two observations beyond the reviewer's:

1. **Shunt Type gates the legal values of Distal tip location**, one to one: VP with peritoneal cavity, VA with right atrium, ventriculopleural with pleural cavity. This is a **value-level** condition, not a relationship-level one, and neither the condition-on-edge proposal nor the subtype counter-proposal addresses it as stated. It is the sharper test case of the two sets.
2. **RDE2285's value set is degenerate.** "specify setting" is a prompt, not a value, and "not applicable" is the condition in disguise. Under the new model this is a quantitative element whose applicability is gated by Valve Type, and both of its current values disappear.

**Identifier correction.** The memo lists the second candidate as "RDES118 - Ventricular Shunt Catheter". RDES118 is a different published set, **Ventriculoperitoneal Shunt Assessment** (elements RDE770 Programmable valve setting, RDE772 Shunt catheter status, RDE773 Abandoned shunt catheters, RDE1594 Presence). The email body's **RDES329** is the correct identifier for the set described. RDES118 overlaps it substantially and is itself worth looking at as a duplication and migration case.
