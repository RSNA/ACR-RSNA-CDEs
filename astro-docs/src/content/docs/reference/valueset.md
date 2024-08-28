---
title: Value Set Standards
---

## Name and Value
Name is a human readable answer to the question being asked by the element. Names may be a phrase, or brief explanations. Names are lower-case, and use only [approved symbols](#character-and-symbol-usage). (note: MARVAL 'display name' maps to name in JSON & radelement.org)

A Value's value is intended to be easily machine readable, but should be human interpretable. Values will contain no spaces or special characters other than the underscore (“_”).

## Value Set Minimum Cardinality
Indicate the minimum number of values that may be reported to be valid. 
- A value of 0 indicates the Element is optional. 
- A value of 1 or more indicates the Element is required. 

Be judicious, required means that if all other elements are present but this one is absent the entire set may be rejected by the recieving system.

## Value Set Maximum Cardinality
Indicate the number of values beyond which the containing Element Set is invalid. Most often, this is 1.

## Value Set Values
Use terms defined in Radlex whenever possible.
Do not embed/pre-coordinate the name of the Element in the values for the Element.  
- Avoid Pre-Coordinated
  - no T1 hyperintensity
  - cardiac amyloid present
  - uterine position indeterminate
- Prefer Single Terms
  - absent
  - present 
  - indeterminate

## Values for Detection
Detection elements should use standardized choices: 
- absent
- present
- indeterminate - cannot conclusively establish or define [assessment performed but was not conclusive]
- unknown - not known [assessment not performed]


## Values for Laterality
The below values are recommended for use within laterality type elements. It is recommended to make the element type multi select (max cardinality greater than 1). 

In general, for elements that require a “bilateral” option it is recommended to use a multi select that contains both “right” and “left” values, although there may be instances where “bilateral” may be more appropriate.

- left
- right
- bilateral
- midline
- indeterminate

## Value of "Other”
Use of the value “other” should be avoided and should only be used where truly appropriate.

## Numeric/Alpha Characters as Value Name
Numbers or alpha characters will not be associated with values. If required, this will be addressed within the reporting system utilizing the element.

AVOID Values with Numbers/ Alpha Characters
- 1 - absent
- 3 - present
- 2 - indeterminate
- L - left
- R - right
- M - midline

PREFER Values without Numbers/ Apha Characters
- absent
- present
- indeterminate
- left
- right
- midline

An allowed exception to this rule is where a standardized lexicon (e.g. BI-RADS or LI-RADS uses an alphanumeric scoring system)

## Character and Symbol Usage
| Avoid | Acceptable |
| ------ | ----------- |
| /      | and, or |
| #      | number |
| I, V, VI | 1, 5, 6 |

### Allowed within Value Names
| Symbol | Meaning |
| ------ | ------- |
| - | hyphen for separation |
| =      | equals |
| >, >=, ≥ | greater than, greater than or equal to |
| <, <=, ≤ | less than, less than or equal to |

## Exemplar Images
Some values may benefit from exemplar images that illustrate, for example, what constitutes mild, moderate, or severe. Such images can be uploaded to MARVAL and associated with the corresponding Value (or Element or Set).

## Value Codes
Each value in a value set is issued an identifer based on the parent element ID by radelement. For example: the first answer choice for RDE35 would be RDE35.0. As this is done by radelement, if authoring in JSON, the validation allows TO_BE_DETERMINEDnnn.