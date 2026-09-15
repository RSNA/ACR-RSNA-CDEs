---
type: Analysis
title: The Anatomy Axis, Current State
description: Current anatomy substrate, known gaps, and tissue-type and structure-type scope families, with their connections to the location hierarchy still open as of 15 September 2026.
tags: [next-gen-schema, anatomy, radlex, anatomic-locations, summary]
status: draft
generated: { by: ["human:talkasab", "claude-code/claude-fable-5.1", "codex/gpt-6"], at: 2026-09-15 }
sources:
  - id: scope-discussion
    resource: /docs/plans/2026-09-14-structural-decision-agenda.md
    title: Owner's scope-specifier families and agenda corrections, 15 September 2026, S50–S51
  - id: record
    resource: /docs/next-gen-schema/10-decision-record-2026-09-02.md
    title: The decision record; S12, S20, S27, S33, S35, S37 are the anatomy decisions
    author: "human:talkasab"
  - id: gaps
    resource: /docs/next-gen-schema/04-anatomy-gaps.md
    title: The gap log and the running list of node requests
  - id: exchange-0908
    resource: /notes/review-exchange-2026-09-08-extract.md
    title: The 8 September exchange, §4 on RadLex anatomy
  - id: exchange-0913
    resource: /notes/review-exchange-2026-09-13-extract.md
    title: The 13 September exchange on the overlay
  - id: data
    resource: "https://raw.githubusercontent.com/openimagingdata/findingmodel/854d1f55d3ed039c455fe8eaa9a2a2983dcefc32/notebooks/data/anatomic_locations_noembed.json"
    title: The anatomic locations data, pinned to the commit of 2026-03-02
    author: "human:talkasab"
---

# The Anatomy Axis, Current State

**Status:** Draft summary, updated 15 September 2026. The owner's directions are marked with their decision-record numbers; data findings retain their original check dates. The new scope families are a direction to develop, not an adopted connection model. S49 keeps integration proposals provisional.

## 1. The substrate and what it is to RadLex

The anatomy the vocabulary points at is the **anatomic locations data** behind the owner's published `anatomic-locations` Python package: 2,926 locations, each keyed by its RadLex id, with containment, part-of, left, right, and unsided variants, a body region, SNOMED and other codes, synonyms, and some definitions. It is pointed to, pinned to its commit, not copied (S37).

Its relation to RadLex is settled by the owner on 13 September: it is **an overlay on RadLex**, not a replacement and not the sole source. RadLex concepts and predicates sit underneath; the file adds ids RadLex lacks, its own containment and part-of, and laterality. It is **the basis of the RadLex anatomy axis going forward**, because the RadLex anatomy track is editing it; aiming at the published RadLex release "is like you're editing a three-year old version of a document that others have been editing". The reviewer's anatomy implementation, after her refactor, points at RadLex directly with no reproduction of the ontology, and agreed to work within this file as the overlay.

Consequences already in the model:

- **A location's id is its RadLex id** (S12). The file's compound ids for sided variants that RadLex lacks (`RID1363_RID5825` for the right pleural space) are the exception the RadLex track will remove by minting real ids; our needed changes go into that track, not into a local scheme (S37).
- **Sided locations are subtypes of the unsided one**, and a class scoped to the unsided organ is satisfied by an Observation on a sided one (S20). Anatomy edges use `SUBTYPE_OF` for the is-a and, from the part-solid nodule example onward, `PART_OF` for containment (S27, S35); the reviewer's viewer uses `IS_A` and `PART_OF`, and the names are on the to-do list to settle.
- **Anatomic scope** (agreed term, S31) is where a kind of finding belongs: a place or a kind of structure. The check walks up the location's classification and containment; nothing propagates down (S3, S13 rejected). The same mechanism now serves **component-of scope** (S33).

## 2. What the file has and lacks

Checked against the pinned file on 13 and 14 September 2026.

| Has | Lacks |
|---|---|
| RadLex ids on 1,910 nodes; compound sided ids on 1,016 | **any is-a relation** |
| containment for every node; part-of on 1,123 | **structure-type nodes** (artery, muscle, tendon, and so on), so "applies to tendons" cannot be stated |
| left, right, unsided links on about 1,600 | lung parenchyma; perirenal space (RID434) and its sided forms, which the pyelonephritis example uses from RadLex directly |
| pleural space, sided | pericardial space, subarachnoid space |
| SNOMED CT on 1,782; FMA, MeSH, UMLS on many | codes on 608 nodes |
| region as one of nine values | the package's structure-type, body-system, and location-type fields exist but are empty in this data |

The missing is-a and structure types are **the major shortcoming** for this work and the first thing to resolve (S37).

## 3. What RadLex can supply now

RadLex 4.3 has an is-a chain for every one of the 1,910 plain-id locations, up to "anatomical entity". Walking it gives a first structure-type layer without inventing anything: 352 locations under muscle organ, 221 under artery, 137 under vein, 115 under tendon, 101 under bone organ, 28 each under joint and nerve, 26 under lymph node; ligament organ, cartilage organ, and anatomical space exist as concepts too. Sided variants take their unsided location's types. RadLex's own release note warns that some of its is-a categorizations were converted from part-of and may be wrong, so the derived layer needs a clinical skim, and the FMA-style chain (lung is a "lobular organ") is not the clinical layer; the short list above is. This is to-do item 11: an overlay file, derived and pinned, handed to the anatomic-locations track.

## 4. Decisions with the reviewer, in date order

- **25 August:** anatomic scope resolves by walking the hierarchy; scope may be stated on data elements too (not yet applied).
- **8 September:** no local "safety layer" project around RadLex; build on the anatomic-locations effort; historical provenance not needed. The reviewer's gap-filling concern is legitimate for genuine gaps.
- **13 September:** the file is the overlay and the basis of the axis; work at its current state, not the published release; keep a list of specific node requests and feed them upstream regardless; a working session on planned changes is owed.

## 5. Anatomy scope specifiers: two families (S50)

The owner identifies two initial families to flesh out:

| Family | Starting examples |
|---|---|
| Tissue types | Pulmonary parenchyma, hepatic parenchyma, subcutaneous fat |
| Structure types | Solid organs; vessels, with arteries and veins as subtypes; muscles; tendons; ligaments |

**Open structural work:** connect these families to the anatomic location hierarchy. The family distinction does not itself choose separate node types, require disjoint categories, or settle a relationship vocabulary. It extends the structure-type work above to include tissue-type scope explicitly.

**Exploratory ideas from the assistant, not adopted:** compare tissue concepts represented as anatomical nodes with tissue scope specifiers linked to locations. Explore is-a for structure classification and separate part-of/location links for tissue setting, keeping an organ distinct from its parenchyma. A named artery, hepatic parenchyma, and subcutaneous fat in a region could be comparison cases; exact connections still need discussion.

This does not reopen the Observation model: the Observation specifies a sided anatomic location (S20, reaffirmed in S51). Missing taxonomy links belong in the gap work, not in a new abstract question about incomplete reports.

## 6. Open items

- Develop the tissue-type and structure-type scope families and agree their connections to the location hierarchy (S50); assess coverage before turning every candidate into a missing-node request.

- The working session with the reviewer on planned changes to RadLex anatomic locations, and the review of her merged refactor when it lands.
- To-do 5: the names of the anatomy relations (`SUBTYPE_OF` or `IS_A`; `PART_OF`).
- To-do 11: the derived structure-type overlay.
- The running **node request list** in the gap log: lung parenchyma; perirenal space and its sided forms; pericardial space; subarachnoid space; real ids for the compound sided variants.
- Which of the file's hierarchies a given check walks (containment, part-of, or both) must be stated each time; for the lobe-of-lung case they agree.
