# FindingClass Relationships, Scope, and Diagnosis Connections

FindingClass relationships extracted from the canonical `definition-graph.json`. FindingClasses are grouped by their subtype hierarchy. Diagnosis connections include relationships asserted from Diagnosis to FindingClass, with subtype inheritance identified where applicable. `OCCURS_WITH` is expanded in both directions when the relationship is marked symmetric. `AVAILABLE_LOCATION_REFINEMENTS (example of the mechanism, not a comprehensive or confirmed set)` is shown only when an explicit `AnatomicRefinementRule` defines permitted targets. Predicate choice, target selection, and traversal behavior remain independent. Fixed DataElement values are shown separately as `HAS_VALUE_CONSTRAINT`; defining status and any explicit modeling-status note are preserved. Narrowing notes are likewise shown when declared. Absent relationships are omitted.

## acute infarct

#### DIAGNOSIS_CONNECTIONS

- **cerebral infarction** via `mayManifestAs`

**SCOPED_TO_REGION:** brain

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **interval change**
- **presence**
- **vascular territory**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Neuroradiology**

---

## adrenal nodule

#### DIAGNOSIS_CONNECTIONS

- **adrenal adenoma** via `mayManifestAs`
- **metastatic disease** via `mayManifestAs`

**SCOPED_TO_REGION:** adrenal gland

#### HAS_MEASUREMENT

- **attenuation (Hounsfield units)**
- **lesion count**
- **long-axis diameter**
- **mean diameter**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **calcification**
- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Abdominal Radiology**

---

## atelectasis

#### DIAGNOSIS_CONNECTIONS

- **lung cancer** via `mayManifestAs`
- **tension pneumothorax** via `mayManifestAs`

**SCOPED_TO_REGION:** lung

#### OCCURS_WITH (seen together often enough to be worth noting, but says nothing about cause or sequence)

- **pleural effusion**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **atelectasis mechanism**
- **atelectasis morphology**
- **extent**
- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Chest Radiology**

---

## azygos fissure

**SCOPED_TO_REGION:** upper lobe of right lung

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Chest Radiology**

---

## cerebral atrophy

#### DIAGNOSIS_CONNECTIONS

- **chronic small vessel disease** via `mayManifestAs`

**SCOPED_TO_REGION:** brain

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **interval change**
- **presence**
- **severity**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Neuroradiology**

---

## consolidation

#### DIAGNOSIS_CONNECTIONS

- **pneumonia** via `mayManifestAs`
- **pulmonary edema** via `mayManifestAs`

**SCOPED_TO_SPECIFIC:** lung parenchyma

#### OCCURS_WITH (seen together often enough to be worth noting, but says nothing about cause or sequence)

- **pleural effusion**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **distribution**
- **extent**
- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Chest Radiology**

---

## encephalomalacia

#### DIAGNOSIS_CONNECTIONS

- **cerebral infarction** via `mayCause`

**SCOPED_TO_REGION:** brain

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Neuroradiology**

---

## external carotid artery stenosis

**SCOPED_TO_SPECIFIC:** external carotid artery

#### HAS_MEASUREMENT

- **end diastolic velocity**
- **peak systolic velocity**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **ECA stenosis significance**
- **flow character**
- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Neuroradiology**

---

## ground-glass opacity

#### DIAGNOSIS_CONNECTIONS

- **pneumonia** via `mayManifestAs`
- **pulmonary edema** via `mayManifestAs`

**SCOPED_TO_SPECIFIC:** lung parenchyma

#### OCCURS_WITH (seen together often enough to be worth noting, but says nothing about cause or sequence)

- **pleural effusion**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **distribution**
- **extent**
- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Chest Radiology**

---

## hepatic mass

#### DIAGNOSIS_CONNECTIONS

- **hepatocellular carcinoma** via `mayManifestAs`
- **metastatic disease** via `mayManifestAs`

**SCOPED_TO_REGION:** liver

#### ASSESSED_BY

- **LI-RADS**

#### HAS_MEASUREMENT

- **lesion count**
- **long-axis diameter**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **calcification**
- **enhancement pattern**
- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Abdominal Radiology**

---

## hydronephrosis

**SCOPED_TO_SPECIFIC:** renal pelvis

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **interval change**
- **presence**
- **severity**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Abdominal Radiology**

---

## internal carotid artery stenosis

**SCOPED_TO_SPECIFIC:** internal carotid artery

#### HAS_MEASUREMENT

- **ECST percent stenosis**
- **involved length**
- **NASCET percent stenosis**
- **residual lumen diameter**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **degree of narrowing**
- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Neuroradiology**

---

## intracranial hemorrhage

**SCOPED_TO_REGION:** head

#### HAS_MEASUREMENT

- **attenuation (Hounsfield units)**
- **volume**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **amount**
- **collection shape**
- **hemorrhage age**
- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Neuroradiology**

#### SUBTYPES

- **epidural hematoma**
- **intraparenchymal hemorrhage**
- **intraventricular hemorrhage**
- **subarachnoid hemorrhage**
- **subdural hematoma**

> **Subtype**
>
> ### epidural hematoma
>
> **SCOPED_TO_SPECIFIC:** epidural space
>
> #### HAS_DATA_ELEMENT (attributes associated directly with it)
>
> - **interval change**
> - **presence**
>
> #### HAS_VALUE_CONSTRAINT
>
> - **collection shape = biconvex** (fixed in alpha model (non-defining)). _Provisional alpha mechanism test; this fixed value has not been radiologist-validated and may change after clinical review._
>
> #### SEEN_ON (modality)
>
> - **Computed Tomography**
> - **Magnetic Resonance Imaging**
> - **Projection Radiography**
> - **Ultrasound**
>
>
> **Subtype**
>
> ### intraparenchymal hemorrhage
>
> **SCOPED_TO_REGION:** brain
>
> #### HAS_DATA_ELEMENT (attributes associated directly with it)
>
> - **collection shape** — narrowed to **conforming**, **rounded**. _Provisional alpha mechanism test; this narrowing has not been radiologist-validated and may change after clinical review._
> - **interval change**
> - **presence**
>
> #### SEEN_ON (modality)
>
> - **Computed Tomography**
> - **Magnetic Resonance Imaging**
> - **Projection Radiography**
> - **Ultrasound**
>
>
> **Subtype**
>
> ### intraventricular hemorrhage
>
> **SCOPED_TO_SPECIFIC:** cerebral ventricle
>
> #### HAS_DATA_ELEMENT (attributes associated directly with it)
>
> - **collection shape** — narrowed to **conforming**, **rounded**. _Provisional alpha mechanism test; this narrowing has not been radiologist-validated and may change after clinical review._
> - **interval change**
> - **presence**
>
> #### SEEN_ON (modality)
>
> - **Computed Tomography**
> - **Magnetic Resonance Imaging**
> - **Projection Radiography**
> - **Ultrasound**
>
>
> **Subtype**
>
> ### subarachnoid hemorrhage
>
> **SCOPED_TO_SPECIFIC:** subarachnoid space
>
> #### HAS_DATA_ELEMENT (attributes associated directly with it)
>
> - **interval change**
> - **presence**
>
> #### HAS_VALUE_CONSTRAINT
>
> - **collection shape = conforming** (fixed in alpha model (non-defining)). _Provisional alpha mechanism test; this fixed value has not been radiologist-validated and may change after clinical review._
>
> #### SEEN_ON (modality)
>
> - **Computed Tomography**
> - **Magnetic Resonance Imaging**
> - **Projection Radiography**
> - **Ultrasound**
>
>
> **Subtype**
>
> ### subdural hematoma
>
> **SCOPED_TO_SPECIFIC:** subdural space
>
> #### HAS_DATA_ELEMENT (attributes associated directly with it)
>
> - **interval change**
> - **presence**
>
> #### HAS_VALUE_CONSTRAINT
>
> - **collection shape = crescentic** (fixed in alpha model (non-defining)). _Provisional alpha mechanism test; this fixed value has not been radiologist-validated and may change after clinical review._
>
> #### SEEN_ON (modality)
>
> - **Computed Tomography**
> - **Magnetic Resonance Imaging**
> - **Projection Radiography**
> - **Ultrasound**
>
>
---

## mediastinal lymphadenopathy

#### DIAGNOSIS_CONNECTIONS

- **lung cancer** via `mayManifestAs`
- **metastatic disease** via `mayManifestAs`
- **reactive lymphadenopathy** via `mayManifestAs`

**SCOPED_TO_CLASS:** mediastinal lymph node

#### OCCURS_WITH (seen together often enough to be worth noting, but says nothing about cause or sequence)

- **pleural effusion**

#### HAS_MEASUREMENT

- **short-axis diameter**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **FDG avidity**
- **interval change**
- **nodal architecture**
- **nodal shape**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Positron Emission Tomography**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Chest Radiology**

---

## mediastinal shift

#### DIAGNOSIS_CONNECTIONS

- **tension pneumothorax** via `mayManifestAs`

**SCOPED_TO_SPECIFIC:** mediastinum

#### HAS_MEASUREMENT

- **displacement distance**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **direction** — narrowed to **leftward**, **rightward**
- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Chest Radiology**

---

## midline shift

#### DIAGNOSIS_CONNECTIONS

- **cerebral infarction** via `mayCause`

**SCOPED_TO_REGION:** brain

#### HAS_MEASUREMENT

- **displacement distance**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **direction** — narrowed to **leftward**, **rightward**
- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Neuroradiology**

---

## mural nodule

#### COMPONENT_OF

- **complex renal cyst**

#### HAS_MEASUREMENT

- **long-axis diameter**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **enhancement pattern**
- **interval change**
- **presence**

---

## perinephric fat stranding

#### DIAGNOSIS_CONNECTIONS

- **acute pyelonephritis** via `mayManifestAs`

**SCOPED_TO_SPECIFIC:** perirenal space

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Abdominal Radiology**

---

## pleural effusion

#### DIAGNOSIS_CONNECTIONS

- **chylothorax** via `mayManifestAs`
- **empyema** via `mayManifestAs`
- **heart failure** via `mayCause`
- **hemothorax** via `mayManifestAs`
- **lung cancer** via `mayCause`
- **malignant pleural effusion** via `mayManifestAs`
- **nephrotic syndrome** via `mayCause`
- **parapneumonic effusion** via `mayManifestAs`
- **pneumonia** via `mayCause`
- **pulmonary edema** via `mayCause`
- **pulmonary embolism** via `mayCause`

**SCOPED_TO_SPECIFIC:** pleural space

#### OCCURS_WITH (seen together often enough to be worth noting, but says nothing about cause or sequence)

- **atelectasis**
- **consolidation**
- **ground-glass opacity**
- **mediastinal lymphadenopathy**

#### HAS_MEASUREMENT

- **attenuation (Hounsfield units)**
- **volume**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **amount**
- **internal complexity**
- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Chest Radiology**

---

## pneumothorax

#### DIAGNOSIS_CONNECTIONS

- **tension pneumothorax** via `mayManifestAs`

**SCOPED_TO_SPECIFIC:** pleural space

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **interval change**
- **pneumothorax size**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Chest Radiology**

---

## pulmonary artery filling defect

#### DIAGNOSIS_CONNECTIONS

- **pulmonary embolism** via `mayManifestAs`

**SCOPED_TO_SPECIFIC:** pulmonary artery

#### HAS_MEASUREMENT

- **involved length**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **interval change**
- **occlusiveness**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Chest Radiology**

---

## pulmonary mass

#### DIAGNOSIS_CONNECTIONS

- **lung cancer** via `mayManifestAs`

**SCOPED_TO_REGION:** lung

#### HAS_MEASUREMENT

- **lesion count**
- **long-axis diameter**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **calcification**
- **distribution** — narrowed to **solitary**, **scattered**, **clustered**
- **interval change**
- **presence**
- **pulmonary margin**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Chest Radiology**

---

## pulmonary nodule

#### DIAGNOSIS_CONNECTIONS

- **metastatic disease** via `mayManifestAs`

**SCOPED_TO_REGION:** lung

#### AVAILABLE_LOCATION_REFINEMENTS (example of the mechanism, not a comprehensive or confirmed set)

- **lower lobe of left lung**
- **lower lobe of lung**
- **lower lobe of right lung**
- **middle lobe of lung**
- **upper lobe of left lung**
- **upper lobe of lung**
- **upper lobe of right lung**

#### ASSESSED_BY

- **Lung-RADS**

#### HAS_MEASUREMENT

- **lesion count**
- **long-axis diameter**
- **mean diameter**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **attenuation**
- **calcification**
- **distribution**
- **FDG avidity**
- **interval change**
- **presence**
- **pulmonary margin**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Positron Emission Tomography**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Chest Radiology**

#### SUBTYPES

- **non-solid pulmonary nodule**
- **part-solid pulmonary nodule**
- **solid pulmonary nodule**

> **Subtype**
>
> ### non-solid pulmonary nodule
>
> #### DIAGNOSIS_CONNECTIONS
>
> - **lung cancer** via `mayManifestAs`
> - **metastatic disease** via `mayManifestAs` (inherited via pulmonary nodule)
>
> **SCOPED_TO_REGION:** lung (inferred from pulmonary nodule)
>
> #### AVAILABLE_LOCATION_REFINEMENTS (example of the mechanism, not a comprehensive or confirmed set)
>
> - **lower lobe of left lung**
> - **lower lobe of lung**
> - **lower lobe of right lung**
> - **middle lobe of lung**
> - **upper lobe of left lung**
> - **upper lobe of lung**
> - **upper lobe of right lung**
>
> #### HAS_DATA_ELEMENT (attributes associated directly with it)
>
> - **interval change**
> - **presence**
>
> #### HAS_VALUE_CONSTRAINT
>
> - **attenuation = non-solid** (defining)
>
> #### SEEN_ON (modality)
>
> - **Computed Tomography**
> - **Magnetic Resonance Imaging**
> - **Projection Radiography**
> - **Ultrasound**
>
>
> **Subtype**
>
> ### part-solid pulmonary nodule
>
> #### DIAGNOSIS_CONNECTIONS
>
> - **lung cancer** via `mayManifestAs`
> - **metastatic disease** via `mayManifestAs` (inherited via pulmonary nodule)
>
> **SCOPED_TO_REGION:** lung (inferred from pulmonary nodule)
>
> #### AVAILABLE_LOCATION_REFINEMENTS (example of the mechanism, not a comprehensive or confirmed set)
>
> - **lower lobe of left lung**
> - **lower lobe of lung**
> - **lower lobe of right lung**
> - **middle lobe of lung**
> - **upper lobe of left lung**
> - **upper lobe of lung**
> - **upper lobe of right lung**
>
> #### HAS_COMPONENT
>
> - **solid component of part-solid pulmonary nodule**
>
> #### HAS_DATA_ELEMENT (attributes associated directly with it)
>
> - **interval change**
> - **presence**
>
> #### HAS_VALUE_CONSTRAINT
>
> - **attenuation = part-solid** (defining)
>
> #### SEEN_ON (modality)
>
> - **Computed Tomography**
> - **Magnetic Resonance Imaging**
> - **Projection Radiography**
> - **Ultrasound**
>
>
> **Subtype**
>
> ### solid pulmonary nodule
>
> #### DIAGNOSIS_CONNECTIONS
>
> - **intrapulmonary lymph node** via `mayManifestAs`
> - **lung cancer** via `mayManifestAs`
> - **metastatic disease** via `mayManifestAs` (inherited via pulmonary nodule)
> - **pulmonary granuloma** via `mayManifestAs`
> - **pulmonary hamartoma** via `mayManifestAs`
>
> **SCOPED_TO_REGION:** lung (inferred from pulmonary nodule)
>
> #### AVAILABLE_LOCATION_REFINEMENTS (example of the mechanism, not a comprehensive or confirmed set)
>
> - **lower lobe of left lung**
> - **lower lobe of lung**
> - **lower lobe of right lung**
> - **middle lobe of lung**
> - **upper lobe of left lung**
> - **upper lobe of lung**
> - **upper lobe of right lung**
>
> #### HAS_DATA_ELEMENT (attributes associated directly with it)
>
> - **interval change**
> - **presence**
>
> #### HAS_VALUE_CONSTRAINT
>
> - **attenuation = solid** (defining)
>
> #### SEEN_ON (modality)
>
> - **Computed Tomography**
> - **Magnetic Resonance Imaging**
> - **Projection Radiography**
> - **Ultrasound**
>
>
---

## renal cortical scarring

#### DIAGNOSIS_CONNECTIONS

- **chronic pyelonephritis** via `mayManifestAs`

**SCOPED_TO_REGION:** kidney

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Abdominal Radiology**

---

## renal cyst

**SCOPED_TO_REGION:** kidney

#### ASSESSED_BY

- **Bosniak classification**

#### HAS_MEASUREMENT

- **lesion count**
- **long-axis diameter**
- **wall thickness**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **composition**
- **interval change**
- **presence**
- **wall character**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Abdominal Radiology**

#### SUBTYPES

- **complex renal cyst**
- **simple renal cyst**

> **Subtype**
>
> ### complex renal cyst
>
> #### DIAGNOSIS_CONNECTIONS
>
> - **renal cell carcinoma** via `mayManifestAs`
>
> **SCOPED_TO_REGION:** kidney (inferred from renal cyst)
>
> #### HAS_DATA_ELEMENT (attributes associated directly with it)
>
> - **calcification**
> - **interval change**
> - **presence**
>
> #### HAS_VALUE_CONSTRAINT
>
> - **composition = mixed cystic and solid** (defining)
>
> #### SEEN_ON (modality)
>
> - **Computed Tomography**
> - **Magnetic Resonance Imaging**
> - **Projection Radiography**
> - **Ultrasound**
>
>
> **Subtype**
>
> ### simple renal cyst
>
> **SCOPED_TO_REGION:** kidney (inferred from renal cyst)
>
> #### HAS_DATA_ELEMENT (attributes associated directly with it)
>
> - **interval change**
> - **presence**
>
> #### HAS_VALUE_CONSTRAINT
>
> - **composition = cystic** (defining)
>
> #### SEEN_ON (modality)
>
> - **Computed Tomography**
> - **Magnetic Resonance Imaging**
> - **Projection Radiography**
> - **Ultrasound**
>
>
---

## renal enlargement

#### DIAGNOSIS_CONNECTIONS

- **acute pyelonephritis** via `mayManifestAs`

**SCOPED_TO_REGION:** kidney

#### HAS_MEASUREMENT

- **renal length**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Abdominal Radiology**

---

## renal lesion

**SCOPED_TO_REGION:** kidney

#### HAS_MEASUREMENT

- **lesion count**
- **long-axis diameter**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **calcification**
- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Abdominal Radiology**

---

## renal mass

#### DIAGNOSIS_CONNECTIONS

- **renal cell carcinoma** via `mayManifestAs`

**SCOPED_TO_REGION:** kidney

#### HAS_MEASUREMENT

- **lesion count**
- **long-axis diameter**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **calcification**
- **enhancement pattern**
- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Abdominal Radiology**

---

## rib fracture

**SCOPED_TO_CLASS:** rib

#### HAS_MEASUREMENT

- **displacement distance**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **acuity** — narrowed to **acute**, **healing**, **healed**, **indeterminate age**
- **comminution**
- **fracture displacement**
- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Chest Radiology**

---

## solid component of part-solid pulmonary nodule

#### COMPONENT_OF

- **part-solid pulmonary nodule**

#### HAS_MEASUREMENT

- **solid component diameter**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

#### HAS_VALUE_CONSTRAINT

- **attenuation = solid** (fixed in alpha model (non-defining)). _fixed by the authored class model, not offered as an element_

#### SEEN_ON (modality)

- **Computed Tomography**

---

## striated nephrogram

#### DIAGNOSIS_CONNECTIONS

- **acute pyelonephritis** via `mayManifestAs`

**SCOPED_TO_SPECIFIC:** kidney

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Abdominal Radiology**

---

## tendon lesion

**SCOPED_TO_CLASS:** tendon

#### HAS_MEASUREMENT

- **lesion count**
- **long-axis diameter**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

---

## thyroid nodule

**SCOPED_TO_REGION:** thyroid gland

#### ASSESSED_BY

- **ACR TI-RADS**

#### HAS_MEASUREMENT

- **lesion count**
- **long-axis diameter**
- **mean diameter**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **echogenic foci**
- **echogenicity**
- **interval change**
- **presence**
- **thyroid composition**
- **thyroid margin**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Head and Neck**

---

## ventricular shunt catheter

**SCOPED_TO_SPECIFIC:** lateral ventricle

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **device integrity**
- **interval change**
- **presence**
- **tip position status**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Neuroradiology**

---

## white matter hyperintensity

#### DIAGNOSIS_CONNECTIONS

- **chronic small vessel disease** via `mayManifestAs`

**SCOPED_TO_SPECIFIC:** cerebral white matter

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **interval change**
- **presence**

#### SEEN_ON (modality)

- **Computed Tomography**
- **Magnetic Resonance Imaging**
- **Projection Radiography**
- **Ultrasound**

#### IN_SUBSPECIALTY

- **Neuroradiology**
