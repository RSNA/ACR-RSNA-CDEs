# Value Set Guidance

## Values and Labels
Values are intended for data transmission and storage, but should be human interpretable. Ideally, they will contain no spaces or special characters other than the underscore (“_”). Labels are intended for human interpretation, and can contain any characters, space, and may involve longer phrases (or even brief explanations). Labels should start with capital letters. 

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

## Value Set Codes
Defines the identify of a value codes for element 

## Values for Detection
Detection type elements should use the below standardized values where possible and avoid options of, “undetermined”, “equivocal”, etc.   
Always list “absent” as the first value within the list. [Convention? If rule, why?]
- Standardized order is absent, then present.  
- Avoid “yes”, “no” and “none” instead use absent and present.
- Avoid NA (not applicable), what is the assessment not performable for the case?
- Suggested:
    - absent
    - present
    - indeterminate - cannot conclusively establish or define [assessment performed but was not conclusive]
    - unknown - not known [assessment not performed?]

## Values for Laterality
The below values are recommended for use within laterality type elements. It is recommended to make the element type multi select (max cardinality greater than 1). 
In general, for elements that require a “bilateral” option it is recommended to use a multi select field that contains both “right” and “left” values, although there may be instances where “bilateral” may be more appropriate.
- left
- right
- bilateral
- midline
- indeterminate

## Value of "Other”
Use of the value “other” should be avoided and should only be used where truly appropriate.

## Numeric/Alpha Characters Associated to Values
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

# Exemplar Images
Some values may benefit from exemplar images that illustrate, for example, what constitutes mild, moderate, or severe. Such images can be uploaded to MARVAL and associated with the corresponding Value (or Element or Set).
