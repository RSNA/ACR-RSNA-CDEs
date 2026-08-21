---
type: Reference
title: Finding Model Structured Metadata Fields
description: Reference for the structured metadata fields on FindingModelBase and FindingModelFull. Copy of the upstream gist.
resource: "https://gist.github.com/talkasab/2d366555a8c371d8f2e2316f9d39d0e0"
tags: [oifm, reference, metadata]
status: stable
retrieved: 2026-07-29
---

# Finding Model Structured Metadata Fields

Reference document for the structured metadata fields on `FindingModelBase` and `FindingModelFull`. Intended for review with colleagues who may not be looking at the code.

---

## Identity Fields

### `oifm_id` (Full only)

- **Type**: `str` matching `^OIFM_[A-Z]{3,4}_[0-9]{6}$`
- **Required?**: Yes (Full only; Base has no ID)

Globally unique registry identifier. The 3-4 letter prefix is the contributing organization code (e.g., `OIFM_MSFT_932618`). Generated with random digits.

### `name`

- **Type**: `str`, min 5 chars
- **Required?**: Yes

The canonical English name for the finding/diagnosis/measurement. Used as the primary display name and search target. Examples: "pulmonary embolism", "breast density", "anterior cruciate ligament tear".

### `description`

- **Type**: `str`, min 5 chars
- **Required?**: Yes

A textbook-style definition. Should describe what the entity IS (not how to diagnose it). Used as context for AI metadata assignment and search indexing.

### `synonyms`

- **Type**: `list[str] | null`, min 1 item if present
- **Required?**: No

Alternate names a radiologist might use in a report. Used for search matching and AI context. Examples: "PE" for pulmonary embolism, "AAA" for abdominal aortic aneurysm, "slipped disc" for lumbar disc herniation.

### `tags`

- **Type**: `list[str] | null`, min 1 item if present
- **Required?**: No

Free-text categorization tags for browsing/filtering. Not constrained to an enum. Used by `Index.browse(tags=...)` and `Index.search(tags=...)`.

---

## Structured Metadata Fields

These are the fields that the `assign_metadata()` pipeline populates. All are optional (nullable) on the model, but the pipeline aims to fill all of them.

### `body_regions`

- **Type**: `list[BodyRegion] | null`
- **Required?**: No (but pipeline treats as required)

Which gross anatomic region(s) the finding is located in. Multi-valued for findings that span regions (e.g., acute appendicitis can be `["abdomen", "pelvis"]`). Used for browse filtering and search faceting. Legacy values (title-cased, "Arm"/"Leg"/"ALL") are auto-normalized.

| Value | Meaning |
|-------|---------|
| `head` | Intracranial and extracranial head |
| `neck` | Cervical soft tissues, thyroid, etc. |
| `chest` | Thorax including lungs, mediastinum, heart |
| `breast` | Mammary/breast tissue |
| `abdomen` | Abdominal cavity organs |
| `pelvis` | Pelvic organs and structures |
| `spine` | Vertebral column (cervical through sacral) |
| `upper_extremity` | Shoulder, arm, forearm, wrist, hand |
| `lower_extremity` | Hip, thigh, knee, leg, ankle, foot |
| `whole_body` | Not anatomically localized (e.g., technique issues) |

### `subspecialties`

- **Type**: `list[Subspecialty] | null`
- **Required?**: No (but pipeline treats as required)

Which radiology subspecialty divisions would typically read/report this finding. Multi-valued. Represents the expertise needed to interpret the finding, not just who orders the study. Example: a kidney stone might be `["AB", "GU", "ER"]` because abdominal radiologists, GU radiologists, and ER radiologists all encounter it.

| Code | Subspecialty |
|------|-------------|
| `AB` | Abdominal Radiology |
| `BR` | Breast Imaging |
| `CA` | Cardiac Radiology |
| `CH` | Chest/Thoracic Radiology |
| `ER` | Emergency Radiology |
| `GI` | Gastrointestinal Radiology |
| `GU` | Genitourinary Radiology |
| `HN` | Head and Neck Radiology |
| `IR` | Interventional Radiology |
| `MI` | Molecular Imaging / Nuclear Medicine |
| `MK` | Musculoskeletal Radiology |
| `NR` | Neuroradiology |
| `OB` | OB/GYN Radiology |
| `OI` | Oncologic Imaging |
| `PD` | Pediatric Radiology |
| `VI` | Vascular/Interventional |

### `entity_type`

- **Type**: `EntityType | null`
- **Required?**: No (but pipeline treats as required)

The semantic category of what this model represents. The most important distinction is **finding vs. diagnosis**: a finding is what you SEE on the image; a diagnosis is what you CONCLUDE from what you see. This field drives how the model is used in structured reporting workflows.

| Value | Meaning |
|-------|---------|
| `finding` | An imaging observation that requires further characterization to reach a diagnosis. The radiologist sees it but it doesn't name the underlying disease. Examples: pleural effusion, ovarian cyst, intracranial hemorrhage, FDG-avid nodule. |
| `diagnosis` | A specific pathologic entity with defined diagnostic criteria. The radiologist can name the disease from the imaging appearance. Examples: pulmonary embolism, ACL tear, hepatocellular carcinoma. |
| `grouping` | A collection of related findings described together. |
| `measurement` | A quantified imaging parameter. Not a finding or diagnosis — it's a number with clinical meaning. Examples: breast density score, ventricular diameters. |
| `assessment` | A standardized scoring/classification system applied to findings. Examples: BI-RADS category, LI-RADS category. |
| `recommendation` | A suggested follow-up action based on imaging findings. |
| `technique_issue` | An image quality or acquisition problem. Not a clinical finding. Examples: motion artifact. |

### `applicable_modalities`

- **Type**: `list[Modality] | null`
- **Required?**: No (but pipeline treats as required)

Which imaging modalities can demonstrate or diagnose this finding. Should include modalities where the finding is routinely evaluated, not every modality that could theoretically show it. Legacy values `CR` and `DX` are auto-normalized to `XR`.

| Code | Modality |
|------|----------|
| `XR` | Radiography (plain X-ray) |
| `CT` | Computed Tomography |
| `MR` | Magnetic Resonance Imaging |
| `US` | Ultrasound |
| `PET` | Positron Emission Tomography |
| `NM` | Nuclear Medicine (non-PET scintigraphy) |
| `MG` | Mammography |
| `RF` | Fluoroscopy |
| `DSA` | Digital Subtraction Angiography |

### `etiologies`

- **Type**: `list[EtiologyCode] | null`
- **Required?**: No

The pathologic mechanism(s) that cause this finding/diagnosis. Multi-valued because many entities have more than one common etiology (e.g., subdural hematoma can be `traumatic:acute` AND `vascular:hemorrhagic`). Null is valid for entities where etiology doesn't apply (e.g., breast density is a measurement, not caused by disease; ovarian cysts are physiologic). The hierarchical colon-separated coding (e.g., `neoplastic:malignant`) allows filtering at both the broad category level and the specific subtype.

| Code | Category | Meaning |
|------|----------|---------|
| `inflammatory` | Inflammatory | General inflammation (non-infectious) |
| `inflammatory:infectious` | Inflammatory | Infectious etiology |
| `neoplastic:benign` | Neoplastic | Benign tumor |
| `neoplastic:malignant` | Neoplastic | Primary malignancy |
| `neoplastic:metastatic` | Neoplastic | Metastatic disease |
| `neoplastic:potential` | Neoplastic | Premalignant or uncertain malignant potential |
| `traumatic:acute` | Traumatic | Acute traumatic injury |
| `traumatic:sequela` | Traumatic | Post-traumatic chronic changes |
| `vascular:ischemic` | Vascular | Ischemic etiology |
| `vascular:hemorrhagic` | Vascular | Hemorrhagic etiology |
| `vascular:thrombotic` | Vascular | Thrombotic/embolic etiology |
| `vascular:aneurysmal` | Vascular | Aneurysmal dilation |
| `degenerative` | Degenerative | Age-related wear and degeneration |
| `metabolic` | Metabolic | Metabolic/biochemical cause |
| `congenital` | Congenital | Present from birth |
| `developmental` | Developmental | Develops during growth |
| `autoimmune` | Autoimmune | Autoimmune mechanism |
| `toxic` | Toxic | Toxic exposure |
| `mechanical` | Mechanical | Mechanical cause (e.g., annular tear, pneumothorax from rupture) |
| `iatrogenic:post-operative` | Iatrogenic | Post-surgical changes |
| `iatrogenic:post-radiation` | Iatrogenic | Radiation-induced changes |
| `iatrogenic:device` | Iatrogenic | Device-related |
| `iatrogenic:medication-related` | Iatrogenic | Drug-induced |
| `idiopathic` | Idiopathic | Unknown cause |
| `normal-variant` | Normal variant | Anatomic variant, not pathologic |

### `sex_specificity`

- **Type**: `SexSpecificity | null`
- **Required?**: No

Whether this finding is anatomically restricted to one sex. This is about whether the finding CAN occur in both sexes, not about prevalence differences. ACL tears are `sex-neutral` even though females have higher incidence. Breast density is `female-specific` because it applies to breast tissue. BPH is `male-specific` because it involves the prostate.

| Value | Meaning |
|-------|---------|
| `male-specific` | Only occurs in male anatomy (e.g., benign prostatic hyperplasia) |
| `female-specific` | Only occurs in female anatomy (e.g., ovarian cyst, breast density) |
| `sex-neutral` | Occurs in both sexes |

### `age_profile`

- **Type**: `AgeProfile | null` (a nested model)
- **Required?**: No

Two-part age characterization. `applicability` defines the age window where this finding can reasonably occur. `more_common_in` highlights where incidence peaks. Example: intracranial hemorrhage has `applicability="all_ages"` (can happen at any age) but `more_common_in=["aged"]` (most common in the elderly). Pyloric stenosis has `applicability=["newborn", "infant"]` — it simply doesn't occur outside infancy. Legacy free-text labels ("pediatric", "elderly", "any age") are auto-normalized.

**Subfields:**
- `applicability`: Either the string `"all_ages"` or a list of `AgeStage` values
- `more_common_in`: `list[AgeStage] | null` — subset where the finding is more prevalent

**AgeStage values** (MeSH-derived, disjoint bins):

| Value | Approximate Age Range |
|-------|-----------------------|
| `newborn` | Birth to 28 days |
| `infant` | 29 days to 1 year |
| `preschool_child` | 2-5 years |
| `child` | 6-12 years |
| `adolescent` | 13-17 years |
| `young_adult` | 18-24 years |
| `adult` | 25-44 years |
| `middle_aged` | 45-64 years |
| `aged` | 65+ years |

### `expected_time_course`

- **Type**: `ExpectedTimeCourse | null` (a nested model)
- **Required?**: No

How this finding behaves on serial imaging. `duration` is how long the finding is visible; `modifiers` describe the trajectory. Example: pulmonary embolism has `duration=weeks, modifiers=[resolving]` (it resolves with treatment over weeks). AAA has `duration=permanent, modifiers=[progressive]` (it never goes away and slowly grows). Ovarian cyst has `duration=weeks, modifiers=[resolving, recurrent]` (resolves each cycle but comes back). Null for entities where time course doesn't apply (e.g., BI-RADS is a point-in-time assessment).

**Subfields:**
- `duration`: `ExpectedDuration | null` — upper bound of visibility on imaging
- `modifiers`: `list[TimeCourseModifier]` — behavioral pattern over time

**ExpectedDuration values:**

| Value | Meaning |
|-------|---------|
| `hours` | Resolves or changes within hours |
| `days` | Resolves or changes within days |
| `weeks` | Resolves or changes within weeks |
| `months` | Resolves or changes within months |
| `years` | Slowly changing over years |
| `permanent` | Does not resolve; persists indefinitely |

**TimeCourseModifier values:**

| Value | Meaning |
|-------|---------|
| `progressive` | Gets worse / grows over time |
| `stable` | Remains unchanged |
| `evolving` | Changes in character/appearance (not necessarily worse) |
| `resolving` | Getting better / shrinking |
| `intermittent` | Comes and goes |
| `fluctuating` | Changes unpredictably |
| `recurrent` | Resolves but reappears |

---

## Ontology and Anatomy Fields (Full only)

### `index_codes`

- **Type**: `list[IndexCode] | null`, min 1 item if present
- **Required?**: No

Canonical ontology codes that are exact matches or clinically substitutable equivalents for this finding model. NOT broader/narrower/related concepts — those go in the enrichment review artifact. The metadata assignment pipeline discovers candidates via BioOntology search and has the classifier select which are truly canonical.

**IndexCode subfields:**
- `system`: `str` — The ontology system (e.g., `"SNOMEDCT"`, `"RADLEX"`, `"LOINC"`)
- `code`: `str` — The concept code within that system
- `display`: `str | null` — Human-readable display name

### `anatomic_locations`

- **Type**: `list[IndexCode] | null`, min 1 item if present
- **Required?**: No

RadLex anatomic location codes identifying where this finding is located. Uses the same `IndexCode` format as `index_codes` but with `system="ANATOMICLOCATIONS"`. Codes come from our anatomic-locations database (RadLex-derived). Examples: `RID1301` (lung), `RID2781` (anterior cruciate ligament), `RID122` (pylorus). Null for entities without a specific anatomic location (e.g., motion artifact).

---

## Contributor Fields (Full only)

### `contributors`

- **Type**: `list[Person | Organization] | null`
- **Required?**: No
- **Person subfields**: `github_username`, `email`, `name`, `organization_code`, `url`
- **Organization subfields**: `name`, `code` (3-4 letter uppercase), `url`

Who authored or contributed to this finding model definition. Not populated by the metadata assignment pipeline — this is editorial metadata set by humans during model authorship.

---

## Attributes

### `attributes` (on Base: `list[Attribute]`; on Full: `list[AttributeIded]`)

- **Type**: Discriminated union of `ChoiceAttribute | NumericAttribute` (Base) or `ChoiceAttributeIded | NumericAttributeIded` (Full)
- **Required?**: Yes, min 1

Attributes define the structured data elements a radiologist would fill out when characterizing this finding in a report. They are NOT metadata about the finding model itself — they are the clinical characterization axes. Examples: "severity" (choice: mild/moderate/severe), "size" (numeric: mm), "laterality" (choice: right/left/bilateral). The metadata assignment pipeline does NOT modify attributes — they are authored content.

#### Choice Attributes
- `name`: 3-100 chars, descriptive English name
- `description`: Optional, 5-500 chars
- `type`: `"choice"` (discriminator)
- `values`: List of `ChoiceValue` (min 2), each with `name` and optional `description`
- `required`: Whether the attribute is always used
- `max_selected`: Max selections (default 1; `"all"` auto-corrected to count of values)
- (Full only) `oifma_id`: `OIFMA_{ORG}_{6digits}` registry ID
- (Full only) `index_codes`: Ontology codes for the attribute concept itself

#### Numeric Attributes
- `name`, `description`, `type` (`"numeric"`), `required`: Same as choice
- `minimum`, `maximum`: Numeric bounds (int or float)
- `unit`: Unit of measure string (e.g., "mm", "mL")
- (Full only) `oifma_id`, `index_codes`: Same as choice
