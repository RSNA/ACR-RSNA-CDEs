# DataElement Concepts

DataElements extracted from `alpha-turtle.ttl`. DataElements are attributes that describe a FindingClass or Diagnosis. Each section shows the allowed values defined by the ontology and where the DataElement is used. Scope is shown if a DataElement itself is explicitly scoped in the ontology.

## acuity

#### VALUES

- **acute**
- **chronic**
- **healed**
- **healing**
- **indeterminate age**
- **subacute**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - rib fracture |

---

## amount

#### VALUES

- **large**
- **moderate**
- **small**
- **trace**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - intracranial hemorrhage<br/>- pleural effusion |

---

## atelectasis mechanism

**SCOPED_TO_REGION:** lung

#### VALUES

- **adhesive**
- **cicatricial**
- **compressive**
- **obstructive**
- **passive**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - atelectasis |

---

## atelectasis morphology

**SCOPED_TO_REGION:** lung

#### VALUES

- **linear**
- **lobar**
- **rounded**
- **segmental**
- **subsegmental**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - atelectasis |

---

## attenuation

**SCOPED_TO_REGION:** lung

#### VALUES

- **non-solid**
- **part-solid**
- **solid**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - pulmonary nodule<br/>- solid component of part-solid pulmonary nodule |

---

## calcification

#### VALUES

- **central**
- **coarse**
- **none**
- **peripheral / rim**
- **popcorn**
- **punctate**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - adrenal nodule<br/>- complex renal cyst<br/>- hepatic mass<br/>- pulmonary mass<br/>- pulmonary nodule<br/>- renal lesion<br/>- renal mass |

---

## collection shape

#### VALUES

- **biconvex**
- **conforming**
- **crescentic**
- **rounded**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - intracranial hemorrhage |

---

## comminution

#### VALUES

- **comminuted**
- **simple**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - rib fracture |

---

## composition

#### VALUES

- **cystic**
- **mixed cystic and solid**
- **predominantly cystic**
- **solid**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - renal cyst |

---

## degree of narrowing

#### VALUES

- **mild**
- **moderate**
- **near-occlusion**
- **occluded**
- **severe**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - internal carotid artery stenosis |

---

## device integrity

#### VALUES

- **disconnected**
- **fractured**
- **intact**
- **kinked**
- **migrated**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - ventricular shunt catheter |

---

## direction

#### VALUES

- **anterior**
- **inferior**
- **leftward**
- **posterior**
- **rightward**
- **superior**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - mediastinal shift<br/>- midline shift |

---

## distribution

#### VALUES

- **centrilobular**
- **clustered**
- **miliary**
- **perilymphatic**
- **random**
- **scattered**
- **solitary**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - consolidation<br/>- ground-glass opacity<br/>- pulmonary mass<br/>- pulmonary nodule |

---

## ECA stenosis significance

**SCOPED_TO_REGION:** external carotid artery

#### VALUES

- **non-significant**
- **significant**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - external carotid artery stenosis |

---

## echogenic foci

**SCOPED_TO_REGION:** thyroid gland

#### VALUES

- **large comet-tail artifact**
- **macrocalcifications**
- **none**
- **peripheral rim calcifications**
- **punctate echogenic foci**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - thyroid nodule |

---

## echogenicity

#### VALUES

- **anechoic**
- **hyperechoic**
- **hypoechoic**
- **isoechoic**
- **very hypoechoic**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - thyroid nodule |

---

## enhancement pattern

#### VALUES

- **arterial hyperenhancement with washout**
- **heterogeneous**
- **homogeneous**
- **none**
- **peripheral nodular discontinuous**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - hepatic mass<br/>- mural nodule<br/>- renal mass |

---

## extent

#### VALUES

- **diffuse**
- **focal**
- **lobar**
- **multifocal**
- **segmental**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - atelectasis<br/>- consolidation<br/>- ground-glass opacity |

---

## FDG avidity

#### VALUES

- **intense**
- **mild**
- **moderate**
- **none**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - mediastinal lymphadenopathy<br/>- pulmonary nodule |

---

## flow character

#### VALUES

- **laminar**
- **turbulent**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - external carotid artery stenosis |

---

## fracture displacement

#### VALUES

- **displaced**
- **minimally displaced**
- **non-displaced**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - rib fracture |

---

## hemorrhage age

**SCOPED_TO_REGION:** head

#### VALUES

- **acute**
- **chronic**
- **early subacute**
- **hyperacute**
- **indeterminate age**
- **late subacute**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - intracranial hemorrhage |

---

## internal complexity

#### VALUES

- **dependent debris**
- **fluid-fluid level**
- **gas**
- **loculation**
- **septations**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - pleural effusion |

---

## interval change

#### VALUES

- **decreased**
- **increased**
- **new**
- **no prior available**
- **unchanged**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - acute infarct<br/>- adrenal nodule<br/>- atelectasis<br/>- cerebral atrophy<br/>- complex renal cyst<br/>- consolidation<br/>- encephalomalacia<br/>- epidural hematoma<br/>- external carotid artery stenosis<br/>- ground-glass opacity<br/>- hepatic mass<br/>- hydronephrosis<br/>- internal carotid artery stenosis<br/>- intracranial hemorrhage<br/>- intraparenchymal hemorrhage<br/>- intraventricular hemorrhage<br/>- mediastinal lymphadenopathy<br/>- mediastinal shift<br/>- midline shift<br/>- mural nodule<br/>- non-solid pulmonary nodule<br/>- part-solid pulmonary nodule<br/>- perinephric fat stranding<br/>- pleural effusion<br/>- pneumothorax<br/>- pulmonary artery filling defect<br/>- pulmonary mass<br/>- pulmonary nodule<br/>- renal cortical scarring<br/>- renal cyst<br/>- renal enlargement<br/>- renal lesion<br/>- renal mass<br/>- rib fracture<br/>- simple renal cyst<br/>- solid pulmonary nodule<br/>- striated nephrogram<br/>- subarachnoid hemorrhage<br/>- subdural hematoma<br/>- tendon lesion<br/>- thyroid nodule<br/>- ventricular shunt catheter<br/>- white matter hyperintensity |

---

## laterality

#### VALUES

- **bilateral**
- **left**
- **midline**
- **right**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - acute infarct<br/>- adrenal nodule<br/>- atelectasis<br/>- consolidation<br/>- encephalomalacia<br/>- external carotid artery stenosis<br/>- ground-glass opacity<br/>- hydronephrosis<br/>- internal carotid artery stenosis<br/>- perinephric fat stranding<br/>- pleural effusion<br/>- pneumothorax<br/>- pulmonary artery filling defect<br/>- pulmonary mass<br/>- pulmonary nodule<br/>- renal cortical scarring<br/>- renal cyst<br/>- renal enlargement<br/>- renal lesion<br/>- renal mass<br/>- rib fracture<br/>- striated nephrogram<br/>- thyroid nodule<br/>- ventricular shunt catheter |

---

## nodal architecture

#### VALUES

- **central necrosis**
- **cortical thickening**
- **effaced fatty hilum**
- **preserved fatty hilum**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - mediastinal lymphadenopathy |

---

## nodal shape

#### VALUES

- **elongated**
- **rounded**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - mediastinal lymphadenopathy |

---

## occlusiveness

#### VALUES

- **non-occlusive**
- **occlusive**
- **partially occlusive**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - pulmonary artery filling defect |

---

## pneumothorax size

**SCOPED_TO_REGION:** pleural space

#### VALUES

- **large**
- **moderate**
- **small**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - pneumothorax |

---

## presence

#### VALUES

- **absent**
- **indeterminate**
- **present**
- **unknown**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
| - acute pyelonephritis<br/>- adrenal adenoma<br/>- cerebral infarction<br/>- chronic pyelonephritis<br/>- chronic small vessel disease<br/>- chylothorax<br/>- empyema<br/>- heart failure<br/>- hemothorax<br/>- hepatocellular carcinoma<br/>- intrapulmonary lymph node<br/>- lung cancer<br/>- malignant neoplastic disease<br/>- malignant pleural effusion<br/>- metastatic disease<br/>- nephrotic syndrome<br/>- parapneumonic effusion<br/>- pneumonia<br/>- pulmonary edema<br/>- pulmonary embolism<br/>- pulmonary granuloma<br/>- pulmonary hamartoma<br/>- reactive lymphadenopathy<br/>- renal cell carcinoma<br/>- tension pneumothorax | - acute infarct<br/>- adrenal nodule<br/>- atelectasis<br/>- azygos fissure<br/>- cerebral atrophy<br/>- complex renal cyst<br/>- consolidation<br/>- encephalomalacia<br/>- epidural hematoma<br/>- external carotid artery stenosis<br/>- ground-glass opacity<br/>- hepatic mass<br/>- hydronephrosis<br/>- internal carotid artery stenosis<br/>- intracranial hemorrhage<br/>- intraparenchymal hemorrhage<br/>- intraventricular hemorrhage<br/>- mediastinal lymphadenopathy<br/>- mediastinal shift<br/>- midline shift<br/>- mural nodule<br/>- non-solid pulmonary nodule<br/>- part-solid pulmonary nodule<br/>- perinephric fat stranding<br/>- pleural effusion<br/>- pneumothorax<br/>- pulmonary artery filling defect<br/>- pulmonary mass<br/>- pulmonary nodule<br/>- renal cortical scarring<br/>- renal cyst<br/>- renal enlargement<br/>- renal lesion<br/>- renal mass<br/>- rib fracture<br/>- simple renal cyst<br/>- solid component of part-solid pulmonary nodule<br/>- solid pulmonary nodule<br/>- striated nephrogram<br/>- subarachnoid hemorrhage<br/>- subdural hematoma<br/>- tendon lesion<br/>- thyroid nodule<br/>- ventricular shunt catheter<br/>- white matter hyperintensity |

---

## pulmonary margin

**SCOPED_TO_REGION:** lung

#### VALUES

- **irregular**
- **lobulated**
- **smooth**
- **spiculated**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - pulmonary mass<br/>- pulmonary nodule |

---

## severity

#### VALUES

- **mild**
- **minimal**
- **moderate**
- **severe**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
| - acute pyelonephritis<br/>- chronic small vessel disease<br/>- pulmonary edema | - cerebral atrophy<br/>- hydronephrosis |

---

## thyroid composition

**SCOPED_TO_REGION:** thyroid gland

#### VALUES

- **cystic or almost completely cystic**
- **mixed cystic and solid**
- **solid or almost completely solid**
- **spongiform**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - thyroid nodule |

---

## thyroid margin

**SCOPED_TO_REGION:** thyroid gland

#### VALUES

- **extra-thyroidal extension**
- **ill-defined**
- **irregular**
- **lobulated**
- **smooth**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - thyroid nodule |

---

## tip position status

#### VALUES

- **appropriate**
- **malpositioned**
- **suboptimal**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - ventricular shunt catheter |

---

## vascular territory

**SCOPED_TO_REGION:** brain

#### VALUES

- **anterior cerebral artery**
- **middle cerebral artery**
- **non-territorial**
- **posterior cerebral artery**
- **posterior circulation**
- **watershed**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - acute infarct |

---

## wall character

#### VALUES

- **enhancing**
- **imperceptible**
- **thickened**
- **thin**

#### USED_BY

| Diagnosis | FindingClass |
| --- | --- |
|  | - renal cyst |
