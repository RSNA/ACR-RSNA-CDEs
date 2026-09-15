# -*- coding: utf-8 -*-
"""
SNOMED CT bindings.

None of these codes was written from memory. Every one comes from a supplied
list or from the colleague's worked JSONL files, with his display label kept as
`source_label` so a later release can detect an upstream relabelling.

These bindings coexist with other terminology bindings on the same CDE concept.
No terminology is designated primary or secondary by this module.
"""

# RID -> (code, source_label, match)
ANATOMY = {
    "RID56":    ("818983003", "Abdomen", "exactMatch"),
    "RID58":    ("10200004", "Liver structure", "exactMatch"),
    "RID86":    ("78961009", "Splenic structure", "exactMatch"),
    "RID88":    ("23451007", "Adrenal structure", "exactMatch"),
    "RID170":   ("15776009", "Pancreatic structure", "exactMatch"),
    "RID205":   ("64033007", "Kidney structure", "exactMatch"),
    "RID228":   ("25990002", "Renal pelvis structure", "exactMatch"),
    "RID585":   ("86117002", "Internal carotid artery structure", "exactMatch"),
    "RID1243":  ("51185008", "Thoracic structure", "exactMatch"),
    "RID1301":  ("39607008", "Lung structure", "exactMatch"),
    "RID1302":  ("3341006", "Right lung structure", "exactMatch"),
    "RID1303":  ("42400003", "Structure of upper lobe of right lung", "exactMatch"),
    "RID1310":  ("72481006", "Middle lobe of right lung structure", "exactMatch"),
    "RID1315":  ("266005", "Structure of lower lobe of right lung", "exactMatch"),
    "RID1326":  ("44029006", "Left lung structure", "exactMatch"),
    "RID1327":  ("44714003", "Structure of upper lobe of left lung", "exactMatch"),
    "RID1338":  ("41224006", "Structure of lower lobe of left lung", "exactMatch"),
    "RID1362":  ("3120008", "Pleural structure", "exactMatch"),
    "RID1363":  ("91381003", "Pleural cavity structure", "exactMatch"),
    "RID1370":  ("80338007", "Parietal pleura structure", "exactMatch"),
    "RID1371":  ("81623005", "Visceral pleura structure", "exactMatch"),
    "RID1384":  ("72410000", "Mediastinum structure", "exactMatch"),
    "RID6434":  ("12738006", "Brain structure", "exactMatch"),
    "RID7578":  ("69748006", "Thyroid gland structure", "exactMatch"),
    "RID7581":  ("29565003", "Structure of right lobe of thyroid gland", "exactMatch"),
    "RID13296": ("59441001", "Structure of lymph node", "exactMatch"),
    "RID28749": ("76752008", "Breast structure", "exactMatch"),
}

# class name -> (code, source_label, match)
FINDINGS = {
    "pulmonary nodule":            ("427359005", "Solitary nodule of lung", "narrowMatch"),
    "thyroid nodule":              ("237495005", "Thyroid nodule", "exactMatch"),
    "renal mass":                  ("309088003", "Kidney mass", "exactMatch"),
    "simple renal cyst":           ("77945009", "Simple renal cyst", "exactMatch"),
    "pleural effusion":            ("60046008", "Pleural effusion", "exactMatch"),
    "pneumothorax":                ("36118008", "Pneumothorax", "exactMatch"),
    "consolidation":               ("95436008", "Lung consolidation", "exactMatch"),
    "ground-glass opacity":        ("1217294009", "Ground glass opacity", "exactMatch"),
    "atelectasis":                 ("46621007", "Atelectasis", "exactMatch"),
    "encephalomalacia":            ("58762006", "Encephalomalacia", "exactMatch"),
    "mediastinal lymphadenopathy": ("52324001", "Mediastinal lymphadenopathy", "exactMatch"),
    "hydronephrosis":              ("43064006", "Hydronephrosis", "exactMatch"),
    # from the colleague's files
    "mediastinal shift":           ("19616004", "Mediastinal shift", "exactMatch"),
    "renal cortical scarring":     ("441872001", "Renal scarring", "closeMatch"),
    "renal enlargement":           ("300444006", "Large kidney", "exactMatch"),
}

DIAGNOSES = {
    "pulmonary granuloma":          ("101401000119103", "Pulmonary granuloma", "exactMatch"),
    "lung cancer":                  ("363358000", "Malignant neoplasm of lung", "exactMatch"),
    "empyema":                      ("58554001", "Empyema of pleura", "exactMatch"),
    "hemothorax":                   ("31892009", "Hemothorax", "exactMatch"),
    "heart failure":                ("84114007", "Heart failure", "exactMatch"),
    "pneumonia":                    ("233604007", "Pneumonia", "exactMatch"),
    "pulmonary edema":              ("19242006", "Pulmonary edema", "exactMatch"),
    "malignant neoplastic disease": ("363346000", "Malignant neoplastic disease", "exactMatch"),
    "pulmonary embolism":           ("59282003", "Pulmonary embolism", "exactMatch"),
    "acute pyelonephritis":         ("36689008", "Acute pyelonephritis", "exactMatch"),
    "renal cell carcinoma":         ("702391001", "Renal cell carcinoma", "exactMatch"),
    "hepatocellular carcinoma":     ("109841003", "Liver cell carcinoma", "exactMatch"),
    "adrenal adenoma":              ("255036008", "Adrenal adenoma", "exactMatch"),
    "metastatic disease":           ("128462008", "Metastatic malignant neoplasm", "exactMatch"),
    "cerebral infarction":          ("432504007", "Cerebral infarction", "exactMatch"),
    # from the colleague's files
    "chylothorax":                  ("83035003", "Chylothorax", "exactMatch"),
    "parapneumonic effusion":       ("81075000", "Pleural effusion associated with pulmonary infection", "exactMatch"),
    "chronic pyelonephritis":       ("63302006", "Chronic pyelonephritis", "exactMatch"),
    "nephrotic syndrome":           ("52254009", "Nephrotic syndrome", "exactMatch"),
}

# value id -> (code, source_label, match)
VALUES = {
    "V-000001": ("52101004", "Present", "exactMatch"),
    "V-000002": ("2667000", "Absent", "exactMatch"),
    "V-000003": ("82334004", "Indeterminate", "exactMatch"),
    "V-000004": ("261665006", "Unknown", "exactMatch"),
    "V-000020": ("82280004", "Smooth", "exactMatch"),
    "V-000023": ("49608001", "Irregular", "exactMatch"),
    "V-000151": ("255507004", "Small", "exactMatch"),
    "V-000191": ("255604002", "Mild", "exactMatch"),
    "V-000192": ("6736007", "Moderate", "exactMatch"),
    "V-000193": ("24484000", "Severe", "exactMatch"),
}

ETIOLOGY = {
    "ET-000001": ("441862004", "Infectious process", "exactMatch"),
    "ET-000008": ("308490002", "Degenerative process", "exactMatch"),
}

MODALITY = {
    "MD-000001": ("312251004", "Computed tomography imaging - action", "exactMatch"),
    "MD-000004": ("278110001", "Radiographic imaging - action", "broadMatch"),
}

