---
type: Reference
title: IHE IDR Phase II — Extract for the CDE Vocabulary
description: What the IHE Imaging Diagnostic Report (IDR) Phase II public-comment draft says about encoding findings as FHIR Observations — the grammar this vocabulary must fit — read directly from the supplement.
tags: [ihe, idr, fhir, observation, grammar]
status: stable
generated: { by: ["human:talkasab", "claude-code/claude-fable-5"], at: 2026-08-21 }
sources:
  - id: idr
    resource: "https://www.ihe.net/uploadedFiles/Documents/Radiology/IHE_RAD_Suppl_IDR_PhII_Rev1-2_PC_2026-03-04.pdf"
    title: IHE Radiology Technical Framework Supplement — Imaging Diagnostic Report (IDR), Phase II, Rev. 1.2, Draft for Public Comment, 4 March 2026 (72 pp.)
    author: team:ihe-radiology-technical-committee
    last_modified: 2026-03-04
---

# IHE IDR Phase II — Extract for the CDE Vocabulary

Read from the supplement directly (72 pages), 2026-08-21. Line numbers refer to the public-comment draft. This extract concentrates on how IDR encodes findings as FHIR `Observation`s, because that is the grammar our vocabulary has to fit ([00 §1.3](../docs/next-gen-schema/00-current-understanding.md)).

## 1. IDR's information model (§56.4.1.7, lines 603–629)

IDR defines its terms "heavily influenced by modelling in SNOMED and DICOM":

- **Body Structure** "encompasses both anatomical structures … and morphologic abnormalities (like a lesion, cyst, inflammation, aneurysm, fracture or abscess)." Paired anatomy has laterality.
- **(Imaging) Observation** — "a feature or characteristic that is visible in an image … may serve as the basis for determination that a finding is present and/or it may further characterize a finding." Encoded as FHIR `Observation`.
- **(Clinical) Finding** — "the determination that a clinical entity is present or absent, or the assessment that a clinical entity is normal or abnormal … with varying degrees of certainty." **Positive findings are encoded as FHIR `Condition`; negative findings as `Observation`** (FHIR Working Group policy).

Their example (line 623): "the presence of a tumor is a finding, a recorded diameter of the tumor is an observation … a determination that the tumor is benign is a finding."

**Note the vocabulary collision:** IDR's "finding" is narrower than our `FindingClass` — it is the presence/absence determination — and IDR's "observation" is what we would call a DataElement value. Our committee moved away from "observation" to avoid exactly this FHIR overlap; the mapping is in §5 below.

## 2. The Observation shape (§6.7.3.6.2, lines 1568–1615; Table B.3-1)

Every observation has a **target entity** and **content**:

| Slot | FHIR location | Rule |
|---|---|---|
| anatomy | `Observation.bodyStructure.includedStructure.structure` | "fully pre-coordinated **except for the laterality**" |
| laterality | `…includedStructure.laterality` | separate field, "if .structure is a paired structure" |
| pathologic entity | `…includedStructure.morphology` | "shall not unnecessarily pre-coordinate the associated anatomy" |
| the property | `Observation.code` | "minimal pre-coordination of the property" |
| the value | `Observation.value` | units recorded in `.value`; "Two different Observations might have the same .code but use different units" |

Table B.3-1 shows the pattern on real sentences. The rows that matter most to us:

| Report text | .structure | .laterality | .morphology | .code | .value |
|---|---|---|---|---|---|
| Pancreatic duct diameter is 2 mm | Pancreatic duct | | — | Diameter | 2 mm |
| Liver contour is smooth | Liver | | — | Contour | Smooth |
| Adrenal glands are normal in morphology | Adrenal gland | Bilateral | — | Size · Shape | Normal |
| Spiculated lesion in the lower lobe of the left lung | Lung lower lobe | Left | Lesion | Presence · Shape | Detected · Spiculated |
| Mild cardiomegaly | Heart | | Cardiomegaly | Presence · Severity | Detected · Mild |
| [CDE Set: Pulmonary Nodule] | Upper lobe of lung | Left | Nodule | **RDES195 Pulmonary Nodule**, then `.hasMember` → Presence, Composition, Size, Morphology, Plurality, Microcystic Component, Volume | |

**So an observation on a normal structure — no morphology, anatomy as the target, a property as the code — is a first-class, worked pattern in IDR.** That is exactly the location-bindings proposal in [01 §3.1](../docs/next-gen-schema/01-what-the-vocabulary-must-express.md).

## 3. Finding Sets = CDE Sets (§6.7.3.6.3.1, lines 1725–1754)

- "Observation.code of the root finding shall identify the root of the finding set. **When encoding CDE Sets from radelement.org, it is preferred to use the CDE Set code here**, such as (RDES195, RadElement, 'Pulmonary Nodule')."
- "Observation.hasMember of the root finding shall reference the associated observations … expected to follow the specifications for the CDE Set on radelement.org."
- "The associated observations do not reference the root finding" — found by reverse chaining.
- **`Observation.component` is not used**: FHIR limits it to values "not useful on their own"; using it "has the potential to significantly complicate queries."

## 4. Relationships between observations (§56.4.1.8.2, §6.7.3.6.3)

| IDR relationship | Encoding | Our counterpart |
|---|---|---|
| **Finding Set** | root `.code` = set, `.hasMember` → elements | FindingClass + `HAS_ELEMENT` bindings |
| **Hierarchical Target Entity** (lines 1788–1817) — their example is *literally* "a pulmonary nodule with observations of the presence and volumes of a solid component and a non-solid component" | organized as a Finding Set; sub-observations carry a more specific `.morphology` ("nodule solid component"), each with its own `.hasMember` measurements. "This construction should be used judiciously … not intended to capture [anatomical hierarchy]." | `MAY_HAVE_COMPONENT` in the vocabulary, `HAS_COMPONENT` in the report ([03 §5](../docs/next-gen-schema/03-draft-structures.md)) |
| **Summary/Derived Observation** — "the LungRads Score is derived from the grading of one or more lung nodules" | value in the parent, children via `.derivedFrom` | `ASSESSED_BY` / `INTERPRETED_FROM` |
| **Computed Property** — ratios, volumes from diameters | `.derivedFrom` | `entity_type: measurement` (composite indices) |
| **Conclusion Support** (lines 1858–1872) — "opacity suggestive of infection" | `Condition.evidence` → Observation; for *absent* conditions, `Observation.derivedFrom` | `MAY_REPRESENT`, and the finding/diagnosis split (diagnosis ≈ `Condition`) |
| **Causal Relationship** (lines 1873–1879) — "a pneumonia infection, which manifests entities such as pleural effusion or consolidation" | **"LATER – There is currently no etiology mechanism in FHIR Core."** Points at the `condition-dueTo` extension. | `MAY_CAUSE` / `MAY_BE_CAUSED_BY` — **no FHIR home yet** |
| **Common Cause** — diverticulitis manifesting as inflammation, perforation, abscess, fistula; "might support a severity assessment" | (discussion only) | multi-finding diagnosis — the pyelonephritis example |
| **Temporal Comparison**; **Tracking UIDs** on `BodyStructure.identifier` to correlate the same entity across reports (lines 1590–1613) | DICOM (112039/112040) tracking identifiers; reclassification, merge, and split rules | longitudinal identity — not yet in our scope |
| **Compound Statement** — "liver, gallbladder, pancreas, and spleen are unremarkable" | individual observations per anatomic entity | the grouping / negation-propagation case ([00 Issue A](../docs/next-gen-schema/00-current-understanding.md)) |

## 5. Questions IDR is asking *us* (reviewer notes, lines 257–269)

IDR's open questions about RadElement are requirements on this vocabulary:

- "What extensibility should be permitted when encoding Radelement CDE Sets? Most importantly, can additional sub-observations be included?"
- "**What is the Coding System identifier for Radelement codes?**" — the URI base question in [00 Issue E](../docs/next-gen-schema/00-current-understanding.md), asked from the other side.
- "Is it helpful to have a 'Presence' value in the parent of a grouped Observation Set? … In Radelement, they have no value in the parent and Presence is the first child, but they could be encoded with Presence being the value of the Set."

## 6. Mapping our model onto IDR

| Ours | IDR / FHIR |
|---|---|
| FindingClass (`finding`) | `bodyStructure.includedStructure.morphology` on the target, and the root `Observation.code` of a Finding Set |
| FindingClass (`diagnosis`) | **Open.** IDR's model says positive clinical findings go to `Condition`; our working default is that **every assertion in a radiology report, diagnoses included, is encoded as an `Observation`** — see §8 |
| FindingClass (`assessment`) | Summary/Derived Observation, `.derivedFrom` |
| FindingClass (`device`) | Physical Object Entity target (§6.7.3.6.2.3) |
| DataElement | `Observation.code` (measured property / assessed characteristic) |
| Value | `Observation.value` (CodeableConcept or Quantity with units) |
| AnatomicLocation (sided node) | `.structure` (unsided, pre-coordinated) **+** `.laterality` — IDR keeps laterality as a separate field; our sided RIDs map to (unsided RID, laterality) |
| normal-structure descriptor bound to a location | target = anatomic entity, no morphology, `.code` = the element — **directly supported** |
| `HAS_ELEMENT` binding | "associated observations are expected to follow the specifications for the CDE Set" |
| `MAY_HAVE_COMPONENT` → report `HAS_COMPONENT` | Hierarchical Target Entity via `.hasMember` — untyped; our `expresses` would need an extension |
| `MAY_BE_CAUSED_BY` in a report | **no mechanism** — IDR defers to a FHIR extension |

## 7. What this changes for us

1. The normal-structure proposal needs **no grammar change**: IDR already encodes observations whose target is an anatomic entity with a property code. The open item in [00 Issue G](../docs/next-gen-schema/00-current-understanding.md) is resolved in our favour.
2. The part-solid nodule case is IDR's own worked example of a Hierarchical Target. Our vocabulary edge gives it the potential it currently lacks; the report side is `.hasMember`, untyped, so citing the vocabulary relationship needs an extension.
3. **Causation has no FHIR home.** Our `MAY_BE_CAUSED_BY` report edge is something to raise with IHE, not something to assume.
4. IDR's model would route positive diagnoses to `Condition`. It is not at all clear which things that are technically diagnoses in a radiology report should become Conditions — "consistent with pneumonia" is a radiologist's assertion, not an established clinical condition. **Working default: every assertion in a radiology report, diagnoses included, is encoded as an `Observation`.** Open with IHE (§8).
5. IDR wants a coding-system identifier for RadElement codes and an answer on extensibility of CDE Sets — both are ours to give, and the `RDE2` URI base is the first.

## 8. To discuss with IHE

Items where our vocabulary and IDR either diverge or where IDR has no answer yet; to be raised during public comment / trial implementation:

1. **Observation vs. Condition for diagnoses.** IDR routes positive clinical findings to `Condition`. Radiology reports assert diagnoses with graded confidence ("consistent with", "likely represents", "cannot exclude"); which of these, if any, should be a `Condition` is unclear. **Our default until resolved: all assertions, including diagnoses, are `Observation`s**, with confidence carried on the observation. `Condition.evidence` as the finding→diagnosis link then has no place to attach; we need an Observation-to-Observation equivalent.
2. **Causal relationships between observations.** IDR: "LATER — no etiology mechanism in FHIR Core." Our report-level `MAY_BE_CAUSED_BY` needs a home; the `condition-dueTo` extension IDR points at presupposes Conditions (item 1).
3. **Typed, citable relationships.** `.hasMember` and `.derivedFrom` are untyped. A report edge that *expresses* an identified vocabulary relationship (`RDE2_000900`) needs an extension to carry the type and the reference ([03 §5](../docs/next-gen-schema/03-draft-structures.md)).
4. **Coding-system identifier for RadElement codes** — IDR's own question; answered by the `RDE2` URI base once settled ([00 Issue E](../docs/next-gen-schema/00-current-understanding.md)).
5. **Extensibility of CDE Sets** — IDR's own question ("can additional sub-observations be included?"). Our answer should follow from the binding model: elements bound to the class are expected; additional observations are permitted but are not part of the set.
6. **Presence in the parent or as the first child.** IDR notes RadElement puts presence as the first child with no value in the parent, but that a set "could be encoded with Presence being the value of the Set." The vocabulary should state a preference.
7. **Laterality representation.** IDR keeps laterality as a separate field on an unsided structure code; our anatomy nodes are sided. A stated mapping (sided RID ↔ unsided RID + laterality) is needed so both directions round-trip.
