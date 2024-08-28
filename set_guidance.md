# Set Guidance

## Literature Search

Standardized observation elements and standardized values are not a new concept. The CDE initiative introduces a method for managing the data structures and ID codes, but from a clinical perspective the literature is replete with examples of content appropriate for CDEs.

Before formulating a CDE Element Set, explore the peer-reviewed literature. If there is an existing imaging classification system for a specific observation, this should be considered first before attempting to create one from scratch. A codified and validated grading system is preferred over a new and unvalidated scheme. There are many validated imaging features in the literature that have been assessed for agreement (kappa or ICC). Studies which have validated the classification scheme through interobserver analysis for a specific clinical use case are particularly valuable and should be given high priority when composing a CDE Element Set submission. 

The order of priority for existing CDE schemes include: 

1. unique classification systems with successful validation analysis, 
2. classification systems developed through expert consensus panels, 
3. other classification in use in the peer review literature and 
4. individual methods. 

In most instances provenance for a CDE element or CDE set should be citable and point to an original reference in the literature.

## Scope

Begin by deciding on an appropriate scope of Elements to be included in an Element Set. Review existing Sets on radelement.org to get a sense of typical scope patterns and to confirm the proposed set is not already adequately covered.  If an existing set covers most of your intended content, consider suggesting modifications rather than a new Element Set.  

A Set should include Elements for all the essential discrete detailed observations or properties to be recorded by a reading radiologist for a particular general finding or clinical scenario. 

CDE set scope avoids data that is mostly not obtained from images but rather from EHR.

For example:

* a Set for a pulmonary nodule would include Elements for size, location, and solidity 
* a Set for pancreatitis would include Elements for the presence of necrosis, presence of peripancreatic collections, size of peripancreatic collections, and patency of the adjacent vessels 
* a Set for acute stroke could include Elements for vascular territory, presence of hemorrhage, midline shift, and an ASPECTS score

For a simple radiology procedure, the scope may be congruent with all the observations typically reported for the entire procedure.
For more complex interpretations, image interpretation and diagnosis may involve forking paths of conditional ("If/then") logic where each finding leads to a new set of observations, such as in a flowchart. In such cases, the scope of a Set will typically correspond to one "branch" of that graph.

Note: While creation of a CDE Set addresses content, it does not define the conditional logic (see ACRCAR/DS).

Consider reviewing and having at hand a reference such as a best-practice guide, a reporting template, or an exemplary report as a basis for determining what Elements will be included in the Set. You may need to begin by identifying the discrete pieces of data implied in the narrative text of such resources.

CDEs should not include data elements that are contained elsewhere in the patient record, such as patient demographics (age, sex) and general medical history, even though this information may be included in a radiology report.

### EHR , RIS, and PACS Data - Elements in a Set

Avoid including Elements for information already captured and available within the patient’s EHR or the radiology information system. CDEs are intended to be used within such systems, so documenting these items in CDEs is duplicative and CDE’s try to avoid modelling information outside our domain. CDEs should only contain elements that capture image derived features

**Specifically Avoid:**

- Patient demographics—Age, sex, MRN, etc.
- Patient health—History or current, comorbidities, previous history of disease/surgery, pulse rate, etc. describe the patient, but aren’t derived from an imaging exam. 
- Exam description—Procedure, modality, scanner info, position, views, etc. CDEs correspond with a set of images, and those images already have a standardized way for representing what was performed. DICOM has spent a lot of time thinking about how to model this including more granular procedure steps.

There may be exception cases. It’s a matter of weighing the cost and benefit of storing this type of information in CDEs.

## Set ID

Leave Set ID codes blank at the time of submission. They are assigned as part of the publication process. This intentionally inhibits usage of sets and codes with draft semantics that might conflict with the final published semantics, which would undercut the essential purpose of CDE codes.

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
