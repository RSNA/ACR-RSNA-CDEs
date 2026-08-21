---
type: Reference
title: "Finding Models: Overview"
description: OIFM overview of finding models — why they exist, what they contain, and modelling guidance. Copy of the upstream document.
resource: "https://github.com/openimagingdata/findingmodels/blob/main/prompts/overview.md"
tags: [oifm, reference]
status: stable
retrieved: 2026-07-29
---

# Finding Models: Overview

## Why Finding Models Exist

A radiology report is unstructured text describing what a radiologist observed on a medical image. Finding models turn that unstructured language into **structured, machine-accessible observation objects** — each linked to a rich knowledge base of clinical context.

**The pipeline:** An agent reads a radiology report and identifies findings mentioned in the text. Each finding gets matched to a finding model definition, producing a structured observation object tagged with the finding type and its attributes (present/absent, changed/unchanged, larger/smaller, etc.). These Observations are then consumed by downstream systems and agents that reason about what was seen — to guide patient care, surface important patterns, or make realizations that might otherwise be buried in narrative text.

**Findings exist in time.** A radiology report is a snapshot, but the findings it describes persist across exams. A pleural effusion seen today may be the same one from last week, now larger. Finding models provide the shared vocabulary that lets observations be tracked and associated across time.

**Finding models are the knowledge base, not just labels.** The library of finding model definitions is the foundational context for understanding radiology reports. Each definition carries:
- A canonical name and synonyms that map the many ways radiologists express the same observation
- Attributes that capture how the finding is characterized — presence and change over time are near-universal, but findings are also described by size (critical in cancer imaging), severity, density, morphology, enhancement patterns, location, and many other domain-specific properties
- Links to standard ontologies (SNOMED, RadLex, GAMUTS) for interoperability
- Tags describing etiologies, anatomic context, and clinical associations
- References to related findings and to external knowledge resources

Downstream systems use these definitions to understand what an observation *means* — not just what it's called. This is why quality standards for finding models are critical: a sloppy synonym maps the wrong concept to an observation; a nonsensical attribute propagates meaningless data; a poorly scoped model conflates distinct clinical entities. Errors here don't just look bad — they cause incorrect downstream reasoning about patient care.

## What Is an Imaging Finding?

An imaging finding is **any observation a radiologist makes about an image and documents in a report.** Radiologists both **describe what they see** (descriptive observations) and **make diagnoses** (clinical interpretations) in their reports. Finding models capture both:

- A radiologist might describe "bilateral perihilar opacities" (descriptive) and also state "pulmonary edema" (diagnosis) — both are valid findings
- Diagnostic terms like "pneumonia", "cystic fibrosis", or "emphysema" are used as shorthand for recognizable patterns of radiographic appearances
- **This blending of description and diagnosis is normal and expected.** We are modeling what radiologists actually say in reports, not what we wish they would say. Diagnostic terms are first-class findings — do not question whether a diagnosis "should" be a finding

This is broader than just pathology — findings include:

- **Pathologic findings**: pneumothorax, pleural effusion, lung mass, fracture, osteophyte formation, aortic unfolding
- **Physiologic/functional observations**: pulmonary vascular engorgement, cephalization
- **Devices and hardware**: pacemakers, chest tubes, surgical clips, stents — these are important findings that radiologists must identify and assess
- **Postsurgical states**: sternotomy, thoracotomy, pneumonectomy, lung transplant
- **Anatomic variants and normal structures**: azygos fissure, cervical rib, bifid rib, costochondral calcification
- **Image quality observations**: motion artifact, overpenetration, rotated positioning, obscuration by external objects

### The "Would a radiologist report it?" Test

A finding is something a radiologist would identify and name as a distinct observation in a report — including negative observations. The test: would a radiologist write "there is [X]" or "no [X]" as a standalone statement?

- **"There is cardiomegaly"** — yes, cardiomegaly is a finding
- **"No fracture"** — yes, "chest wall fracture" is a finding (with presence: absent)
- **"Upper abdomen is unremarkable"** — yes, "upper abdominal abnormality" is a finding (with presence: absent)
- **"Stable cardiac silhouette"** — no, "stable" is a change-from-prior value on a cardiac finding, not a finding itself
- **"Large pleural effusion"** — no, "large" is a size attribute on "pleural effusion", not a separate finding

### What is NOT a Finding

- **A state of a finding.** "Stable cardiac silhouette" is not a finding — "stable" is an attribute value. No one reports "there is stable cardiac silhouette."
- **A qualified version of another finding.** "Large pleural effusion" is not a separate finding — "large" is an attribute on "pleural effusion."
- **Normal anatomy.** "Cardiac silhouette" is anatomy, not a finding. The finding is when something is abnormal about it ("cardiac silhouette abnormality", "cardiomegaly").
- **Radiographic signs, interpretation techniques, and descriptors:**
  - "silhouette sign" — an interpretation technique, not an observation. The finding is what it reveals ("obscuration of hemidiaphragm").
  - "air-fluid level", "hematocrit level" — characteristics of a finding (effusion, cavity), not standalone observations. These belong as attributes on the parent finding.
  - "double density sign" — a radiographic sign pointing to a finding (left atrial enlargement), not a finding itself.
- **Exam metadata**: projection type (AP, PA, lateral), patient positioning (supine, upright) — these describe how the image was acquired, not what the radiologist observes
- **Clinical history**: reason for exam, patient symptoms
- **Recommendations**: suggested follow-up actions

A generic descriptor can become a finding when combined with anatomic context that makes it a specific, reportable observation. "Air-fluid level" alone is a characteristic of another finding, but "air-fluid levels in bowel" is a distinct observation that a radiologist would report.

Similarly, a descriptor+entity combination *can* become its own finding when the combined term carries distinct meaning. The test: **does a radiologist mean something different when they say "calcified nodule" versus "nodule with calcifications"?** For that example, yes — "calcified nodule" implies a benign, fully calcified lesion, while "nodule with calcifications" implies a nodule that has some calcium but may still warrant follow-up. When the combined phrase has its own clinical meaning beyond the sum of its parts, it earns its own model.

### Specificity and Scope

**A finding must be at the right level of specificity.** The guiding principle: **a finding is a noun phrase; everything else is an attribute.** A finding should be a stable noun phrase that gets the same characterizing attributes regardless of the specific instance. Every pleural effusion gets described by size, laterality, and character. Every pulmonary nodule gets size, location, and density. The finding is the thing being described; how it's described is captured in attributes.

**Too broad** — not an imaging observation, or too vague without anatomic scope:
- "infection" — a clinical category that manifests as many different imaging findings (pneumonia, abscess, osteomyelitis)
- "mass" — mass where? "lung mass", "mediastinal mass", "renal mass" are findings
- "calcification" — calcification of what? "aortic calcification", "mitral annular calcification" are findings
- "fluid" — fluid where? "pleural effusion", "pericardial effusion", "ascites" are findings
- "hardware" — what kind? "pacemaker", "spinal fixation", "sternotomy wires" are findings
- "degenerative changes" — of what? "degenerative change of the thoracic spine" is a finding

**Too narrow** — bakes attributes (size, location, laterality, acuity, change status) into the finding name:
- "bibasilar consolidation" — location is an attribute on "airspace consolidation"
- "large right pleural effusion" — size and laterality are attributes on "pleural effusion"
- "acute left lower lobe pneumonia" — acuity, laterality, and lobe are attributes on "pneumonia"
- "new right subclavian central venous catheter" — "new" is change-from-prior, "right subclavian" is location, on "central venous catheter"
- "worsening interstitial edema" — "worsening" is a change-from-prior value on "interstitial pulmonary edema"
- "mildly displaced rib fracture" — severity and displacement are attributes on "rib fracture"

**Right level** — distinct imaging observations that radiologists name as units:
- Pathology: "pleural effusion", "pneumothorax", "cardiomegaly", "atelectasis", "pulmonary nodule", "lung mass"
- Devices: "pacemaker", "chest tube", "central venous catheter"
- Osseous: "rib fracture", "compression fracture", "clavicle fixation"
- Technique: "motion artifact", "patient rotation", "overpenetration"
- Scoped broad findings: "chest wall fracture" (for "no fracture" assertions), "upper abdominal abnormality" (for "unremarkable" assertions)

**Findings can exist at multiple levels of specificity.** "Cardiac silhouette abnormality" (broad) and "cardiomegaly" (specific) can both be valid finding models — they're different levels of the same observation. The decision of which to model is a judgment call based on how radiologists actually report. If a term is used as a standalone observation in practice, it warrants its own model.

**Findings must cover negative assertions.** When a radiologist states "no fracture" or "upper abdomen is unremarkable," that's an active observation of absence that needs to be captured. Finding models need to exist at the level where radiologists make these assertions — including broad anatomic-scope findings like "upper abdominal abnormality" or "chest wall fracture." The `presence: absent` observation is clinically meaningful — it means the finding was looked for and not found.

**Broad findings should be scoped to assessable anatomy.** The scope of a finding model should match what's assessable on a given exam type — not broader. "Fracture" is too broad (spans the whole body). "Chest wall fracture" is appropriately scoped (what's visible on a chest radiograph). "Upper abdominal abnormality" is appropriately scoped for chest CT (the upper abdomen is included in the field of view).

**Finding names should be self-describing.** Someone scanning a list of models should be able to tell what each one is about from the name alone. Include enough anatomic or organ-system context for readability: "pulmonary linear opacity" not "linear opacity", "pulmonary mass" not "mass", "osteosclerosis" not "sclerosis." The short form should be kept as a synonym. Some findings are appropriately broad ("fracture", "osseous abnormality") where anatomy is an attribute. See `prompts/conventions.md` for detailed rules.

**Scoring systems and structured assessments are valid findings**, but should be modeled separately from the observations they assess. A "pulmonary nodule" finding model captures what the nodule looks like (size, morphology, location). A "Lung-RADS category" finding model captures the risk assessment assigned to it. These are separate because different radiologists might describe the same nodule but assign different risk categories — and systems need to reason about both independently. Similarly, TI-RADS, PI-RADS, ESCC scores, and other standardized assessments are valid finding models in their own right.

**Measurement groupings are valid findings.** Some finding models capture a coherent group of related measurements rather than a single visual observation — for example, emphysema quantification (density scores, lobar volumes) or brain volume measurements. These require a flexible view of what a finding is: the "finding" is the act of performing a structured quantitative assessment, and the attributes are the measurements within it.

## Anatomy of a Finding Model

A finding model definition includes:

- **Name**: the canonical, lowercase, descriptive term for the finding (acronyms expanded, eponyms minimized, no brand names)
- **Description**: 1-2 concise clinical sentences describing the finding for a radiologist audience
- **Synonyms**: alternative terms that mean the exact same thing at the same level of specificity — the different ways a radiologist might express this same observation in a report
- **Tags**: clinical categories (anatomy, modality, etiology) for organization and retrieval
- **Attributes**: structured properties that characterize the finding:
  - **presence** (required, first): absent, present, indeterminate, unknown
  - **change from prior** (required, second): unchanged, stable, new, resolved, plus clinically appropriate direction-of-change pairs (larger/smaller for masses, worsened/improved for diseases, increased/decreased for quantities)
  - **Domain-specific attributes**: size, location, severity, density, morphology, enhancement pattern, and any other properties relevant to describing or classifying this particular finding
- **Index codes**: links to standard ontologies (SNOMED, RadLex, GAMUTS) for interoperability
- **Contributors**: people and organizations who created or contributed to the definition
- **Unique IDs**: OIFM ID for the finding, OIFMA IDs for each attribute, value codes for each choice value — these are machine-generated and never created manually
