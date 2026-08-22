---
type: Reference
title: Source Review of Nodule Content
description: Findings from checking the pulmonary-nodule and thyroid-nodule example content against Radiopaedia, Radiology Assistant, and Wikipedia on 2026-08-20, including foundational content those pages suggest the vocabulary should capture.
tags: [source-review, pulmonary-nodule, thyroid-nodule, tirads, lung-rads, fleischner]
status: stable
generated: { by: ["claude-code/claude-sonnet-5", "claude-code/claude-fable-5"], at: 2026-08-20 }
sources:
  - id: rp-pn
    resource: "https://radiopaedia.org/articles/pulmonary-nodule-1"
    title: Radiopaedia, Pulmonary nodule
    last_modified: 2026-08-20
  - id: rp-spn
    resource: "https://radiopaedia.org/articles/solitary-pulmonary-nodule-1"
    title: Radiopaedia, Solitary pulmonary nodule
  - id: rp-lungrads
    resource: "https://radiopaedia.org/articles/lung-imaging-reporting-and-data-system-lung-rads"
    title: Radiopaedia, Lung-RADS
  - id: rp-itn
    resource: "https://radiopaedia.org/articles/incidental-thyroid-nodule-1"
    title: Radiopaedia, Incidental thyroid nodule
  - id: rp-tirads
    resource: "https://radiopaedia.org/articles/acr-thyroid-imaging-reporting-and-data-system-acr-ti-rads"
    title: Radiopaedia, ACR TI-RADS
  - id: ra-fleischner
    resource: "https://radiologyassistant.nl/chest/plumonary-nodules/fleischner-2017-guideline"
    title: Radiology Assistant, Fleischner 2017 guideline
  - id: ra-tirads
    resource: "https://radiologyassistant.nl/head-neck/ti-rads/ti-rads"
    title: Radiology Assistant, TI-RADS
  - id: wp-ln
    resource: "https://en.wikipedia.org/wiki/Lung_nodule"
    title: Wikipedia, Lung nodule
  - id: wp-tn
    resource: "https://en.wikipedia.org/wiki/Thyroid_nodule"
    title: Wikipedia, Thyroid nodule
---

# Source Review of Nodule Content

Checked 2026-08-20. The corrections were applied to the examples in [03](../docs/next-gen-schema/03-draft-structures.md); this note keeps the full findings so nothing from the review is lost.

## 1. Corrections applied

| Claim in draft | Verdict | Corrected to |
|---|---|---|
| pulmonary nodule "approximately spherical" | imprecise | "rounded or oval" (every source) |
| "up to 30 mm" | incomplete | less than 30 mm; below ~6 mm is a micronodule; above is a mass |
| characterized by presence, size, margin | materially incomplete | **attenuation (solid / part-solid / ground-glass)** added: the primary branch point of Fleischner and Lung-RADS |
| size "(3D)" | imprecise | Fleischner standard is the mean of long and short axis on one plane; Lung-RADS uses mean diameter with volume as an alternative |
| assessed by Lung-RADS | incomplete | Lung-RADS is for the low-dose screening population; Fleischner covers incidental nodules. Both now linked |
| etiologies: neoplastic, inflammatory | incomplete | congenital and miscellaneous (infarct, intrapulmonary node, hematoma, amyloid) added |
| "peaks middle-aged / elderly" | unverified | removed |
| thyroid: presence, size, composition, echogenicity | materially incomplete | the five ACR TI-RADS axes: composition, echogenicity, **shape, margin, echogenic foci** |
| thyroid etiology "neoplastic: potential" only | misleading | most nodules are hyperplastic/colloid; the OIFM etiology list has no such value |
| thyroid "seen on US" only | incomplete | detected incidentally on CT, MR, PET with distinct triage rules; characterized on US |

## 2. Foundational content the pages suggest, not yet in the vocabulary

**Pulmonary nodule**

- **Calcification pattern**: benign (diffuse, central, laminated, popcorn) versus suspicious (eccentric, stippled). **Fat attenuation** (about -40 to -120 HU) as a hamartoma discriminator.
- **Cavitation**: presence, and wall thickness (thin suggests benign, thick malignant).
- **Significant interval growth** as a measurable event: Lung-RADS uses 1.5 mm or more; TI-RADS and ATA use 20% or more in at least two dimensions with a 2 mm minimum, or 50% or more by volume. A candidate for one shared, parameterized definition.
- **Distribution / multiplicity**: miliary, centrilobular, perilymphatic, random, perifissural. Perifissural nodules under 10 mm with benign morphology get a no-follow-up carve-out in Lung-RADS.
- **Lung-RADS categories** 0 / 1 / 2 / 3 / 4A / 4B / 4X, with their size, attenuation, and growth thresholds: a ready-made value set for the assessment class.

**Thyroid nodule**

- **Shape** (taller-than-wide): the single highest-weighted yes/no feature in ACR TI-RADS.
- **Margin**: smooth, ill-defined, lobulated/irregular, extrathyroidal extension. **Trap**: ill-defined scores 0 (benign) while lobulated/irregular scores 2. Value definitions must keep these unconfusable.
- **Echogenic foci**: none or large comet-tail, macrocalcification, peripheral/rim, punctate. Values co-occur and **score additively** (punctate plus rim is 3 + 2), so this element is multi-select with per-value weights, not single-select. Punctate foci may be microcalcification or inspissated colloid, indistinguishable at this granularity.
- **Vascularity**: used in older pattern systems and still cited on Wikipedia, but dropped from current ACR TI-RADS scoring; a legacy or optional attribute.
- **TI-RADS category to management thresholds**: TR3 FNA at 2.5 cm or more, follow at 1.5 cm; TR4 FNA at 1.5 cm, follow at 1.0 cm; TR5 FNA at 1.0 cm, follow at 0.5 cm; nodules under 5 mm need no follow-up regardless. Needed if management implications are ever encoded.
- **Age-stratified incidental thresholds** from the ACR incidental-thyroid white paper: under 35 years, 1 cm or more triggers work-up; 35 and over, 1.5 cm. A different rule set from TI-RADS, applying to nodules found on CT, MR, or PET.
- **Multiple-nodule rule**: score by TI-RADS category, not by size; at most four nodules scored, at most two biopsied. Implies a "which nodule is the assessment subject" concept when multiplicity is present.
- **Sibling systems**: K-TIRADS, EU-TIRADS, ATA guidelines, BTA U-classification, SRU; relevant if cross-system mapping is wanted.
- **Bethesda System** (six categories) as the downstream cytology vocabulary for any biopsy-result branch.
- **TI-RADS applicability exceptions**: pediatric patients, FDG-PET-avid nodules, suspicious lymphadenopathy, known genetic risk (e.g. MEN2) are carved out of standard scoring, each with elevated prior risk. Useful as an "assessment system not applicable" flag.

## 3. Reuse caveat

Radiopaedia's terms of use, shown on every page fetched, prohibit scraping, bulk download, and use for commercial AI/ML training without a license. This note contains our own summaries and links only.

## 4. Verification tooling that worked from this environment

- **RadLex**: grep the 4.3 OWL from [RSNA/RadLex](https://github.com/RSNA/RadLex) directly; `rdfs:label` gives the term for any RID.
- **SNOMED CT**: the EBI OLS4 API, `https://www.ebi.ac.uk/ols4/api/ontologies/snomed/terms?iri=http://snomed.info/id/{code}`, returns the label. BioPortal pages and the Snowstorm API were blocked.
- **LOINC answer codes**: loinc.org answer-list pages (e.g. LL2987-7) list the SNOMED-mapped LA codes.
