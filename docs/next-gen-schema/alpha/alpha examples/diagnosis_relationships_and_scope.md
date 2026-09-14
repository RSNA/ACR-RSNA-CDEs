# Diagnosis Relationships and Scope

- Diagnosis relationships and scope extracted from the canonical `definition-graph.json`. 
- Only explicitly asserted scope relationships are shown. 
- Absent relationships are omitted.

## acute pyelonephritis

**SCOPED_TO_REGION:** kidney

#### HAS_ETIOLOGY

- **infectious**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **perinephric fat stranding**
  - `SCOPED_TO_SPECIFIC`: perirenal space
- **renal enlargement**
  - `SCOPED_TO_REGION`: kidney
- **striated nephrogram**
  - `SCOPED_TO_SPECIFIC`: kidney

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**
- **severity**

---

## adrenal adenoma

**SCOPED_TO_SPECIFIC:** cortex of adrenal gland

#### HAS_ETIOLOGY

- **neoplastic**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **adrenal nodule**
  - `SCOPED_TO_REGION`: adrenal gland

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## cerebral infarction

**SCOPED_TO_REGION:** brain

#### HAS_ETIOLOGY

- **vascular**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **acute infarct**
  - `SCOPED_TO_REGION`: brain

#### MAY_CAUSE (FindingClass that may occur as a consequence of the diagnosis)

- **encephalomalacia**
  - `SCOPED_TO_REGION`: brain
- **midline shift**
  - `SCOPED_TO_REGION`: brain

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## chronic pyelonephritis

**SCOPED_TO_REGION:** kidney

#### HAS_ETIOLOGY

- **infectious**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **renal cortical scarring**
  - `SCOPED_TO_REGION`: kidney

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## chronic small vessel disease

**SCOPED_TO_REGION:** brain

#### HAS_ETIOLOGY

- **vascular**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **cerebral atrophy**
  - `SCOPED_TO_REGION`: brain
- **white matter hyperintensity**
  - `SCOPED_TO_SPECIFIC`: cerebral white matter

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**
- **severity**

---

## chylothorax

**SCOPED_TO_SPECIFIC:** pleural space

#### HAS_ETIOLOGY

- **iatrogenic**
- **traumatic**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **pleural effusion**
  - `SCOPED_TO_SPECIFIC`: pleural space

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## empyema

**SCOPED_TO_SPECIFIC:** pleural space

#### HAS_ETIOLOGY

- **infectious**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **pleural effusion**
  - `SCOPED_TO_SPECIFIC`: pleural space

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## heart failure

#### MAY_CAUSE (FindingClass that may occur as a consequence of the diagnosis)

- **pleural effusion**
  - `SCOPED_TO_SPECIFIC`: pleural space
- **pulmonary edema**
  - `SCOPED_TO_REGION`: lung

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## hemothorax

**SCOPED_TO_SPECIFIC:** pleural space

#### HAS_ETIOLOGY

- **iatrogenic**
- **traumatic**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **pleural effusion**
  - `SCOPED_TO_SPECIFIC`: pleural space

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## hepatocellular carcinoma

**SCOPED_TO_REGION:** liver

#### HAS_ETIOLOGY

- **neoplastic**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **hepatic mass**
  - `SCOPED_TO_REGION`: liver

#### ASSESSED_BY

- **LI-RADS**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## intrapulmonary lymph node

**SCOPED_TO_REGION:** lung

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **solid pulmonary nodule**
  - `SCOPED_TO_REGION`: lung (inferred from pulmonary nodule)

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## lung cancer

**SCOPED_TO_REGION:** lung

#### HAS_ETIOLOGY

- **neoplastic**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **atelectasis**
  - `SCOPED_TO_REGION`: lung
- **mediastinal lymphadenopathy**
  - `SCOPED_TO_CLASS`: mediastinal lymph node
- **non-solid pulmonary nodule**
  - `SCOPED_TO_REGION`: lung (inferred from pulmonary nodule)
- **part-solid pulmonary nodule**
  - `SCOPED_TO_REGION`: lung (inferred from pulmonary nodule)
- **pulmonary mass**
  - `SCOPED_TO_REGION`: lung
- **solid pulmonary nodule**
  - `SCOPED_TO_REGION`: lung (inferred from pulmonary nodule)

#### MAY_CAUSE (FindingClass that may occur as a consequence of the diagnosis)

- **pleural effusion**
  - `SCOPED_TO_SPECIFIC`: pleural space

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## malignant neoplastic disease

#### HAS_ETIOLOGY

- **neoplastic**

#### MAY_CAUSE (FindingClass that may occur as a consequence of the diagnosis)

- **malignant pleural effusion**
  - `SCOPED_TO_SPECIFIC`: pleural space

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## malignant pleural effusion

**SCOPED_TO_SPECIFIC:** pleural space

#### HAS_ETIOLOGY

- **neoplastic**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **pleural effusion**
  - `SCOPED_TO_SPECIFIC`: pleural space

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## metastatic disease

#### HAS_ETIOLOGY

- **neoplastic**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **adrenal nodule**
  - `SCOPED_TO_REGION`: adrenal gland
- **hepatic mass**
  - `SCOPED_TO_REGION`: liver
- **mediastinal lymphadenopathy**
  - `SCOPED_TO_CLASS`: mediastinal lymph node
- **pulmonary nodule**
  - `SCOPED_TO_REGION`: lung

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## nephrotic syndrome

#### MAY_CAUSE (FindingClass that may occur as a consequence of the diagnosis)

- **pleural effusion**
  - `SCOPED_TO_SPECIFIC`: pleural space

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## parapneumonic effusion

**SCOPED_TO_SPECIFIC:** pleural space

#### HAS_ETIOLOGY

- **infectious**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **pleural effusion**
  - `SCOPED_TO_SPECIFIC`: pleural space

#### MAY_PROGRESS_TO

- **empyema**

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## pneumonia

**SCOPED_TO_SPECIFIC:** lung parenchyma

#### HAS_ETIOLOGY

- **infectious**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **consolidation**
  - `SCOPED_TO_SPECIFIC`: lung parenchyma
- **ground-glass opacity**
  - `SCOPED_TO_SPECIFIC`: lung parenchyma

#### MAY_CAUSE (FindingClass that may occur as a consequence of the diagnosis)

- **pleural effusion**
  - `SCOPED_TO_SPECIFIC`: pleural space

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## pulmonary edema

**SCOPED_TO_REGION:** lung

#### HAS_ETIOLOGY

- **vascular**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **consolidation**
  - `SCOPED_TO_SPECIFIC`: lung parenchyma
- **ground-glass opacity**
  - `SCOPED_TO_SPECIFIC`: lung parenchyma

#### MAY_CAUSE (FindingClass that may occur as a consequence of the diagnosis)

- **pleural effusion**
  - `SCOPED_TO_SPECIFIC`: pleural space

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**
- **severity**

---

## pulmonary embolism

**SCOPED_TO_SPECIFIC:** pulmonary artery

#### HAS_ETIOLOGY

- **vascular**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **pulmonary artery filling defect**
  - `SCOPED_TO_SPECIFIC`: pulmonary artery

#### MAY_CAUSE (FindingClass that may occur as a consequence of the diagnosis)

- **pleural effusion**
  - `SCOPED_TO_SPECIFIC`: pleural space

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## pulmonary granuloma

**SCOPED_TO_REGION:** lung

#### HAS_ETIOLOGY

- **infectious**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **solid pulmonary nodule**
  - `SCOPED_TO_REGION`: lung (inferred from pulmonary nodule)

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## pulmonary hamartoma

**SCOPED_TO_REGION:** lung

#### HAS_ETIOLOGY

- **congenital**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **solid pulmonary nodule**
  - `SCOPED_TO_REGION`: lung (inferred from pulmonary nodule)

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## reactive lymphadenopathy

**SCOPED_TO_CLASS:** lymph node

#### HAS_ETIOLOGY

- **inflammatory**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **mediastinal lymphadenopathy**
  - `SCOPED_TO_CLASS`: mediastinal lymph node

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## renal cell carcinoma

**SCOPED_TO_REGION:** kidney

#### HAS_ETIOLOGY

- **neoplastic**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **complex renal cyst**
  - `SCOPED_TO_REGION`: kidney (inferred from renal cyst)
- **renal mass**
  - `SCOPED_TO_REGION`: kidney

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**

---

## tension pneumothorax

**SCOPED_TO_SPECIFIC:** pleural space

#### HAS_ETIOLOGY

- **iatrogenic**
- **traumatic**

#### MAY_MANIFEST_AS (FindingClass that may represent a manifestation of the diagnosis)

- **atelectasis**
  - `SCOPED_TO_REGION`: lung
- **mediastinal shift**
  - `SCOPED_TO_SPECIFIC`: mediastinum
- **pneumothorax**
  - `SCOPED_TO_SPECIFIC`: pleural space

#### HAS_DATA_ELEMENT (attributes associated directly with it)

- **presence**
