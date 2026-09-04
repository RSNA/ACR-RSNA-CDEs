---
type: Reference
title: Profile of the Hood Finding Taxonomies
description: What the six per-modality finding taxonomies by Michael Hood contain and how they are shaped, measured on 2026-09-01 from the 2026-08-15 export - row counts, typing, hierarchy depth, the recurring name patterns, and the structural facts the vocabulary work draws on.
tags: [source-review, taxonomy, findingmodels, hood, test-material]
status: stable
generated: { by: "claude-code/claude-fable-5.1", at: 2026-09-01 }
sources:
  - id: lists
    resource: "https://github.com/openimagingdata/findingmodels/tree/main/lists"
    title: Hood finding taxonomies, lists/ directory of the openimagingdata findingmodels repository, exported 2026-08-15 (local checkout at ../findingmodels/lists)
    author: "human:hoodcm"
    last_modified: 2026-08-15
---

# Profile of the Hood Finding Taxonomies

Six CSV files, one hierarchy per exam context, developed by Michael Hood and exported 2026-08-15[^lists]. They are used in this bundle as test material for the finding vocabulary: worked examples draw on them ([08](../docs/next-gen-schema/08-worked-examples.md)), and several structural decisions were tested against them ([10](../docs/next-gen-schema/10-decision-record-2026-09-02.md), S5 to S8). They are not a source of truth; they are one experienced radiologist's working taxonomies, and their shape is what is informative.

## Shape

Columns: `name, category, parent, synonyms, finding_type, finding_cluster, oifm_id`. Rows are keyed by `name`, unique within a file, so there is no separate id column. `parent` names the parent row; blank means top level. `category` is an independent anatomic grouping, not part of the hierarchy. `finding_type` separates an observation from a diagnosis. `oifm_id` is filled where a row matched an existing OIFM model by exact name; nothing was minted.

| File | Rows | observation | diagnosis | untyped | categories | top-level | max depth |
|---|---:|---:|---:|---:|---:|---:|---:|
| `xr_chest_findings.csv` | 403 | 322 | 30 | 51 | 11 | 23 | 4 |
| `xr_msk_findings.csv` | 259 | 194 | 37 | 28 | 6 | 16 | 4 |
| `ct_head_findings.csv` | 520 | 261 | 222 | 37 | 15 | 34 | 5 |
| `ct_chest_abdomen_pelvis_findings.csv` | 2064 | 1371 | 448 | 245 | 34 | 68 | 6 |
| `mg_breast_findings.csv` | 198 | 44 | 133 | 21 | 25 | 25 | 3 |
| `mri_spine_findings.csv` | 345 | 251 | 62 | 32 | 12 | 19 | 3 |

Every `parent` reference resolves in every file. `finding_cluster` is used in one file only (`device`, 103 rows of the chest radiograph list).

## Structural facts the vocabulary work relies on

- **Untyped rows are parents.** Of the 414 rows with no `finding_type`, all but three are parents of other rows. They are the structural nodes of each hierarchy, and their names are almost all a location crossed with a small closed set of words: `abnormality` (87), `lesion` (33), `change` (33, as in `postsurgical_change`), `variant` (33), `neoplasm` (24). This is the observation behind the pattern-not-node decision (10 S6) and the narrow Grouping node type (10 S8).
- **Parents mix observations and diagnoses.** In the CT chest, abdomen, and pelvis list, 73 parents have both observation and diagnosis children; the head list has 15, the spine list 10, the chest radiograph list 10, the musculoskeletal list 7. `lung_abnormality`, `pulmonary_lesion`, `airway_abnormality`, and `renal_abnormality` are typical. A hierarchy node above both kinds cannot be either kind, which is the case for a third node type.
- **No diagnosis is ever placed under an observation**, in any of the six files. Where a diagnosis is a kind of a finding, the lists make them siblings instead: hemothorax, chylothorax, and empyema sit beside `pleural_effusion` under the untyped `pleural_abnormality`, and `renal_abscess` sits under the untyped `renal_lesion`. Under the unrestricted taxonomy of 10 S1 these move down one level. Worth raising with the author.
- **The naming triad.** Almost every region carries three untyped roots: `<region>_abnormality`, `<region>_anatomic_variant`, `<region>_postsurgical_change`, with `hardware` and `technique` in the lists where devices matter. Variant and post-operative are already an entity type and an etiology in this vocabulary; "abnormality" is the grouping node.
- **Lesion nodes are half typed.** Of 52 names ending in `_lesion` in the CT list, 19 carry a type and 33 do not. `renal_lesion` is untyped with children `solid_renal_lesion` and `hypoattenuating_renal_lesion` (observations) beside `renal_abscess` and `renal_pseudoaneurysm` (diagnoses). That is the "positively reportable but vague" class of 10 S8, an ordinary FindingClass, not a grouping node.
- **Duplicate OIFM ids.** Eight rows across the chest radiograph and head lists share an OIFM id with another row, for example `tortuosity_of_aorta` and `unfolding_of_aorta`, or `soft_tissue_swelling` and `soft_tissue_edema`. Each is a synonym-or-subtype decision the vocabulary will have to make explicit.
- **The breast list is mostly pathology.** 133 of 198 rows are diagnoses, many histologic (`solid_papillary_carcinoma_in_situ` under `papillary_carcinoma` under `papillary_neoplasm`), with a `radpath_correlation` branch. It tests whether the model handles histologic diagnoses, which none of the other lists do.
- **Deepest chains** reach six levels in the CT list (`krukenberg_tumor` under `ovarian_metastasis` under `ovarian_neoplasm` under `ovarian_lesion` under `ovarian_abnormality` under `female_reproductive_abnormality`) and five in the head list (`medialization_of_uncus` up through `herniation` and `mass_effect` to `brain_parenchymal_abnormality`).

## Name suffix census, all six files

Counted on the last underscore-separated word of every `name`. Of 3,789 rows, 2,970 end in a word not in this list.

| Suffix | Rows | Suffix | Rows |
|---|---:|---|---:|
| abnormality | 158 | collection | 42 |
| lesion | 93 | enlargement | 28 |
| fracture | 76 | nodule | 24 |
| cyst | 65 | dilation | 23 |
| calcification | 65 | disease | 23 |
| change | 58 | mass | 17 |
| variant | 50 | opacity | 15 |
| thickening | 46 | stenosis | 12 |

A morphology axis derived from this census was proposed and rejected on 2026-09-02 (10, rejected list): the suffixes describe how names are formed, not categories radiologists reason about. The census is kept because it is the fastest way to see how a list is shaped.

## Rows the worked examples used

- Pyelonephritis: `renal_abnormality` (untyped) with `striated_nephrogram`, `perinephric_fat_stranding` (as `perinephric_stranding` synonym), `renal_enlargement`, `renal_cortical_scarring`, `hydronephrosis`, `delayed_nephrogram`; `pyelonephritis` (diagnosis) with `emphysematous_pyelonephritis` and `xanthogranulomatous_pyelonephritis` beneath; `renal_abscess` under `renal_lesion`.
- Pleural effusion: `pleural_abnormality` (untyped) with `pleural_effusion` (observation; synonyms hydrothorax, pleural fluid), `hemothorax`, `chylothorax`, `empyema` (diagnoses, as siblings), `pleural_thickening`, `pleural_lesion`, `pleurodesis` under `pleural_postsurgical_change`.

[^lists]: Local checkout at `../findingmodels/lists`; the README there records the export date and the OIFM id fill counts.
