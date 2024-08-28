---
title: Set Standards
---
## Set ID

Set IDs are assigned by radelement.org during the review and publication process. This intentionally eliminates ID conflicts and conflicting draft and final semantics, which would undercut the essential purpose of CDE codes. If authoring in JSON, the validation allows TO_BE_DETERMINEDnnn.

## Set Definition
Describe the full semantics of the Set, specifically the nature of the finding or assessment, and the context of use. Include references when the Set is based on established scientific literature. During the Review Process, this definition will also serve as a basis for assessing the completeness of the Elements in the Set.

## Set Name
Name the Set to indicate the finding or assessment being captured. Focus on the finding/assessment in question. Often will include the anatomical context (body region, body part, organ, etc) and clinical context (e.g. post-operative) since the same feature in another context might be assessed differently.  Metadata fields can help with searching.  

Use the following component format: 

> (Modality) (Body region) (Region of interest) (Finding or reason for study/observation) (Setting or specialty)

Example: CT Chest Rib Fracture Identification - Emergency Setting

A component may be omitted to indicate that the Set is not specific to a particular value for that component, e.g., when the Set is not specific to a particular modality or setting. In some instances, a component may be omitted when it has a single value that can be uniquely derived from another component, e.g., CT Stroke is sufficient and concise, whereas CT Head Stroke would be redundant.

## Modality
Express Modality using the acronym field of the corresponding RadLex code or DICOM modality code.  

- CT: Computed Tomography
- FL: Fluoroscopy
- MR: Magnetic Resonance Imaging
- NM: Nuclear Medicine
- PET: Positron Emission Tomography
- US: Ultrasound
- XR: Projection Radiography

## Speciality
Express setting or specialty using MARVAL codes.

- AB: Abdominal Radiology
- BR: Breast Imaging
- CA: Cardiac Radiology
- CH: Chest Radiology
- ER: Emergency Radiology
- GI: Gastrointestinal Radiology
- GU: Genitourinary Radiology
- HN: Head and Neck
- IR: Interventional Radiology
- MI: Molecular Imaging
- MK: Musculoskeletal Radiology
- NR: Neuroradiology
- OB: OB/GYN Radiology
- OI: Oncologic Imaging
- OT: Other
- PD: Pediatric Radiology
- QI: Quality Improvement
- RS: Research
- VI: Vascular Imaging

## Set Usage
Each Set also has several metadata fields to encode aspects of the intended use of the set, such as characteristics of the procedures and patients for which it is intended to be used. These fields facilitate searching for Sets relevant to a particular case. The values are informative in that they represent the intention of the Set authors. Usage of the Set for procedures and patients beyond those constraints is at the discretion of the physician.

Usage Metadata includes: 

- Modality
- Specialty
- Body Region
- Region of Interest
- Procedure??(LOINC Playbook)
- Indication
- Minimum Patient Age
- Maximum Patient Age
- Assigned Sex at Birth

Usage Metadata may be multi-valued. If no values are given for a usage metadata element, the Set is presumed to apply broadly.
