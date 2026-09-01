---
type: Proposal
title: Conditional Relationships — Engineering Memo
description: An engineering comparison of two ways to express a relationship that applies only under a condition, a condition property on the edge or explicit subtype classes, with the recommendation and the reasoning that tips it. Copy of the memo circulated 26 August 2026.
tags: [next-gen-schema, conditionality, subtypes, inheritance, edges]
status: stable
generated: { by: "claude-code/claude-opus-5", at: 2026-08-31 }
verified: [{ by: "claude-code/claude-opus-5", at: 2026-08-31 }]
sources:
  - id: memo
    resource: raw_sources/conditional_relationships_memo.md
    title: The memo as circulated, attached to the final message in the August 2026 thread
    author: "human:external-reviewer"
    last_modified: 2026-08-26
sanitization: None needed. The memo contains no personal or identifying content. Reproduced verbatim below a horizontal rule.
---

# Conditional Relationships — Engineering Memo

**Provenance.** The body below the rule is verbatim, written by the external reviewer drafting the model and attached to the closing message of the [25 August 2026 exchange](review-exchange-2026-08-25-extract.md), in reply to the counter-proposal that conditionality be handled by defining subtype classes instead. It is reproduced **verbatim** below, since it is an argument someone else made and paraphrasing it would blunt it.

**Two corrections that belong outside the text.** The memo lists its second candidate set as "RDES118 - Ventricular Shunt Catheter". RDES118 is a different published set, *Ventriculoperitoneal Shunt Assessment*. The correct identifier for the set described is **RDES329**. Both sets were checked against the live API on 31 August 2026 and the findings, including a value-level conditional in RDES329 that this memo does not cover, are in the [exchange extract appendix](review-exchange-2026-08-25-extract.md).

**Status: undecided.** This memo argues one side of an open fork. The other side, subtype classes, is Tarik's, recorded in [exchange §2](review-exchange-2026-08-25-extract.md). Reading only this file will give a one-sided picture.

**Note on identifiers.** The memo uses the older `FC-` / `DE-` / `VS-` placeholder ids rather than the `RDE2_` namespace since settled ([00 Issue E](../docs/next-gen-schema/00-current-understanding.md)). The samples in [03 §6](../docs/next-gen-schema/03-draft-structures.md) have the same lag.

---

## Conditional relationships: condition on the edge, or subtype classes (pending decision)

Both options are valid to handle the same case. Thus far only worked out with a
part-solid nodule that has a solid component with its own descriptors; a solid 
or ground glass nodule does not. 
### TODO: Identify and work out at least two more examples with conditional relationships
POSSIBLE CANDIDATES: 
- RDES332 - Extracorporeal membrane oxygenation (ECMO) Cannula
- RDES118 - Ventricular Shunt Catheter
Need clinical input if they have a valid clinical case for conditional relationship.
`Engineering recommendation:` Prefer a condition on the edge when an existing 
element value controls the applicability of a relationship. Reserve subtyping 
for distinctions that represent independently meaningful class identity. 
This recommendation should be tested against additional conditional cases 
before being generalized. 
`Possible subtype test:` If the relationship in question were removed, would this 
distinction still warrant its own FindingClass?
* If yes, subtype may be appropriate.
* If no, and the distinction only determines whether another relationship 
  applies, a condition is better suited.
The comparison below is meant to be even-handed. The section after it sets out 
why from an engineering perspective the subtype option carries more unknowns 
and more downstream consequences, which is what tips the recommendation.
## Option 1. Condition on the edge
Works because the edge is where a relationship's applicability naturally lives.
The condition points at an element the source already carries and a value from
that element's set, so both endpoints of the check are in view.
```json
{
  "edge": "HAS_COMPONENT",
  "from": "FC-000123",
  "to": "FC-000125",
  "props": {
    "condition": { "element": "DE-000015", "operator": "in", "values": ["VS-000044.1"] }
  }
}
```
**Enforcement.** At authoring, check the element is referenced by the source and
the values exist in its set. Conditions can avoid duplication in the canonical 
source model. A compiler may still materialize multiple downstream shapes,
but those shapes are generated deterministically rather than independently
authored and maintained. At instance validation, reject a solid nodule 
carrying a component.
**Pros**
- One Pulmonary Nodule definition. Less to maintain, eliminates cross-subtype 
  synchronization drift.
- The condition is data, so tooling can hide fields, compile variants, and
  validate. Tool can hide complexity.
- The mechanism does not change if the pattern recurs, though only one case 
  is tested so far (see TODO above).
**Cons**
- A new mechanism, with its own validation surface = perceived added complexity.
- Automated logic checkers, the software that reads an ontology and derives what
  follows from it, ignore this kind of annotation. Only our own code acts on it, 
  which may be sufficient given the checks we need.
- Author discretion about when a relationship is conditional rather than 
  always present. Misuse is possible and would need review to catch. Tooling
  can curb it, alternative authoring methods potentially goes unchecked.
- Previously deferred to the template layer, requires revisiting implications.
## Option 2. Subtype classes
Works because the distinction becomes part of the class identity, and each class
declares its own relationships.
```json
{ "node": "FindingClass", "id": "FC-000124", "name": "part-solid pulmonary nodule" }
{ "edge": "SUBTYPE_OF", "from": "FC-000124", "to": "FC-000123" }
{ "edge": "HAS_COMPONENT", "from": "FC-000124", "to": "FC-000125", "props": { "required": true } }
```
**Enforcement.** No runtime condition evaluation is needed because applicability 
is encoded structurally. Authoring validation is still needed to ensure subtype 
relationships and their declared edges are semantically consistent.
The relationship exists on one class and not the others, so validation is just 
the ordinary check that required edges are satisfied.
**Pros**
- No new mechanism, but requires adopting a broader modeling convention: when
  a distinction affects a finding's relationships, represent that distinction 
  as a subtype. `SUBTYPE_OF` already exists, although its semantics and 
  inheritance behavior are still somewhat loosely defined.
- Expressible in a description logic, so automated logic checking is possible. 
  Unclear if that buys anything at our scale, since the checks we need can be
  handled by code.
- No compile step needed to produce the vendor-facing form, since each class 
  is already its own distinct shape. Conditions can reach the same result, but    
  have to be resolved first.
- Perceived as less complex to author (stays closer to how radiologists think) 
  for the pulmonary nodule case, where only part-solid carries a solid
  component. Need to confirm generalizability.
**Cons**
- Subtypes inherit nothing as currently proposed, so each class independently 
  declares its finding-level structure. That works against the duplication 
  reference-by-default exists to prevent, unless inheritance is revisited.
- Author discretion about when a distinction warrants a subtype could lead 
  to inconsistent modeling of otherwise similar cases unless the boundary 
  between subtype and element is explicitly defined and enforceable.
- Multiplies. If subtype identity must encode combinations of independently 
  varying properties, the number of explicit classes can approach the 
  Cartesian product of those dimensions unless the model introduces additional 
  composition, multiple-inheritance, or logical-restriction machinery.
- Adding a value to the attenuation set means an additional FindingClass, 
  not an allowed value (perhaps not as realistic to add another attenuation 
  type for this specific case, but stated as a generalizability implication).
- "Part-solid pulmonary nodule" as a class competes with attenuation as an
  element. Either the element goes away for nodules (and forces splitting 
  classes for other nodules as well), or the same fact lives in two places
  (+ drift risk).
## The (still) loosely defined subtype mechanism carries weight
### Reference-by-default forces the elements to be shared. Nothing exists (yet) to make the subtypes consistent. 
Subtypes inherit nothing as currently recorded, so each subtype needs its own 
edges to every shared element. The elements themselves are still referenced 
once, so the shared definitions can stay identical since that is structurally
enforced. However, there's no structural guarantee that the three subtypes match 
each other in everything else: their own definitions, synonyms, mappings, which
nodes each references, and what properties sit on those edges. 
Pulmonary nodule happens to split in 3 attenuation types to be maintained (part-solid, 
solid, ground-glass); other findings that would require the mechanism may have  
more to maintain. A referenced node change propagates smoothly, but a change
in the finding properties themselves has to be done manually in all subtypes
(high drift risk).
That makes the inheritance position load-bearing. 
It also raises a question about incomplete reports. Under subtyping, does  
attenuation stop being an element and become part of the class name? Or is it
repeated in the title and the Data Element as a hardcoded option? If a report 
describes a nodule without characterizing it, is there a class to record it 
against?
Inheritance also means building out the mechanism that thus far had been ruled 
out. Embracing inheritance would address much of the duplication concern, but 
at the cost of a resolution mechanism larger than the condition property it 
replaces.
### Summary:
- Condition: one new mechanism, small, assuming it is restricted to pre-approved 
  grammar. If adopted, condition expressivity should initially be constrained 
  to direct membership/equality checks against a source element. 
- Subtyping without inheritance: no new mechanism, but duplication that nothing 
  prevents from drifting (back to author/review burden).
- Subtyping with inheritance: requires an additional resolution/inheritance 
  mechanism whose scope is likely broader than the narrowly constrained 
  condition mechanism, while retaining subtype multiplication concerns.
## Related concept
`MAY_HAVE_COMPONENT` is a separate relationship type rather than an alternative 
to either option above. It is better suited where a component is genuinely 
optional in all cases, with nothing gating it.
