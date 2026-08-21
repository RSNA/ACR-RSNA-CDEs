---
type: Analysis
title: "RadLex Baseline: Synonyms and External References"
description: What RadLex 4.3 actually does for synonyms and external ontology references, verified directly against the published OWL — the baseline our vocabulary must interoperate with and improve on.
tags: [next-gen-schema, radlex, synonyms, mappings]
status: stable
generated: { by: ["human:talkasab", "claude-code/claude-fable-5"], at: 2026-08-20 }
sources:
  - id: radlex-owl
    resource: "https://github.com/RSNA/RadLex"
    title: RadLex.owl, 4.3 release (51.6 MB) — analyzed directly 2026-08-20
    author: team:radlex-committee
    last_modified: 2025-12-01
---

# RadLex Baseline: Synonyms and External References

**Verified directly against `RadLex.owl` from [RSNA/RadLex](https://github.com/RSNA/RadLex) (4.3, the authoritative source per [00 §2.4](./00-current-understanding.md)), 2026-08-20.** All counts are from the file, not from documentation.

## 1. Synonyms: custom properties, but with a type hierarchy

RadLex uses no SKOS and no oboInOwl synonym properties (zero occurrences of `skos:altLabel`, `hasExactSynonym`, `hasRelatedSynonym`). Instead, one custom annotation property with **subproperties as synonym types**:

| Property | ⊑ | Uses |
|---|---|---|
| `RID:Synonym` | — | 24,013 |
| `RID:Acronym` | Synonym | 139 |
| `RID:Unsanctioned_Term` | Synonym | 93 |
| `RID:Misspelling_of_term` | Synonym | 36 |
| `RID:UMLS_Term` | (separate) | 1,323 |

Two further facts:

- **Synonyms are language-tagged**: `xml:lang` en ×17,402 · la ×4,117 · de ×2,244, and `rdfs:label` is multilingual too (`lung` / `Lunge`). An internationalization baseline already exists in RadLex.
- Synonyms are **plain strings** — no per-synonym provenance, status, or source. The typing lives entirely in the property hierarchy.

**Reading for our design:** RadLex already validates the *typed synonyms* decision ([00 §8 Decided](./00-current-understanding.md)) — typing via property subsumption is its mechanism. What it cannot do, and we need, is synonym-level metadata (who added it, sanctioned status as data rather than as a distinct property, per-term source). That is exactly the SKOS-XL upgrade path noted in [03 §2.1](./03-draft-structures.md): labels become lightweight nodes when they carry their own metadata — and a `⊑ skos:altLabel` hierarchy would keep us structurally congruent with RadLex's own pattern.

## 2. External references: one untyped string property

All cross-ontology references go through a single annotation property, `RID:ExternalRefID`, whose values are prefix-coded strings (`FMA:7195`, `UMLS:C0024109`) — not IRIs, no match strength, no mapping type. 36,500 uses:

| System | Count |
|---|---|
| FMA | 33,404 |
| UMLS | 1,376 |
| Talairach | 1,098 |
| Freesurfer | 385 |
| AAL / JHU / CMA | 118 / 65 / 48 |
| **SNOMED** | **6** — and all six are `SNOMED_RT:` codes from the *retired pre-CT* SNOMED |

Separately: `RID:Source` (3,116) carries free-text provenance ("Playbook", "LOINC", "LI-RADS 2020", "Fleischner Society"), and lifecycle is `RID:Replaced_by` (442) plus `Preferred_Name_for_Obsolete`.

**Two consequences:**

1. **The SNOMED assumption fails verification — except where AnatomicLocations.org supplies it.** The [SIIM minutes](../../notes/siim-meeting-extract.md) record that "mappings to SNOMED and other standards will be maintained at the RadLex level." The shipped OWL contains effectively no SNOMED CT mapping — six retired SNOMED-RT codes against 33,404 FMA references. For **anatomy**, the gap is already closed upstream-of-upstream: AnatomicLocations.org carries **4,185 external code entries on 2,282 of its 2,890 nodes — modern SNOMED CT on 1,732 nodes (60%), FMA 1,643, UMLS 578, MeSH 232** (verified against `body_parts.json` 1.0.0-rc.1, 2026-08-20; e.g. lung → SNOMED CT 39607008). This is a principal value-add of that project, and as it becomes a RadLex collection ([00 §2.6](./00-current-understanding.md)) those mappings flow into RadLex with it. For **findings**, no such source exists: our vocabulary carries its own mappings (`skos:exactMatch`/`closeMatch`, per [03 §2.1](./03-draft-structures.md)).
2. **Untyped string references are the local version of the ungrounded-string problem.** `ExternalRefID` cannot say whether a reference is an exact match, a broader concept, or a see-also — the distinction [00 Issue J](./00-current-understanding.md) needs. SKOS mapping properties are the standard fix and coexist cleanly: RadLex's strings are recoverable into `skos:*Match` triples mechanically.

## 3. Annotation density is uneven across branches

Spot check: `lung` (RID1301) carries a definition, FMA and UMLS references, synonyms, and Playbook source. **`pulmonary nodule` (RID50149) carries no definition and no external references** — just a label, one synonym ("lung nodule"), a created date (2016), and "Cancer Care Ontario" as source. The anatomy branch is richly annotated; the imaging-observation branch is sparse. Consistent with treating RadLex imaging-observation terms as reference points rather than as a foundation ([00 §2.4](./00-current-understanding.md)).

## 4. Summary for the schema

| RadLex baseline | Our requirement | Gap |
|---|---|---|
| `Synonym` + typed subproperties, language-tagged strings | typed synonyms with per-term metadata | promote to SKOS-XL-style label nodes; keep a `⊑ altLabel` hierarchy for congruence |
| `ExternalRefID` untyped strings | typed mappings with match strength | `skos:exactMatch` / `closeMatch` / `broadMatch`; IRIs not strings |
| SNOMED via RadLex | assumed by committee | **not present in the OWL** — must be carried by our vocabulary or resolved upstream |
| multilingual labels (en/la/de) | not yet discussed for CDEs | baseline exists; decide deliberately |
