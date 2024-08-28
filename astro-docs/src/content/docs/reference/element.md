---
title: Element Standards
---
Submitters are advised to review existing Elements on radelement.org, perhaps in Elements Sets analogous to the Set being proposed, to get a sense of typical naming, definition and value set patterns.

## Element ID
Element ID is automatically assigned by radelement. When authoring JSON the schema allows for TO_BE_DETERMINEDnnn as a validation pattern.

## Element Definition
Express the full semantics of the Element and provide a clear description of the specific intended use. A few words is typically inadequate; i.e., don’t just repeat the Element Name.

For Elements indicating the presence of a condition or disease, clearly state whether the value represents the current finding or is reiterating patient history.

For Elements that are measurements, define the method sufficiently to get consistent results. For example, clarify whether a diameter should be the greatest diameter in the imaging place, the AP dimension, short axis, long axis, etc. Most formats in which CDEs will be encoded (e.g. FHIR, DICOM SR), encode units for each measurement directly, usually using UCUM.  The element definition may note default units to be assumed by coding systems that do not encode them directly. 

Include references when the Element is based on established scientific literature, such as BI-RADS, TI-RADS, ASPECTS, SLICS, TLICS, NASCET, AoSpine, Fazekas Score and many others.

## Element Name
Keep names as short as possible. Since elements all exist within the context of their specific parent Element Set, it is only necessary for the name to distinguish elements from the other elements in the same Set. The full semantics are in the Element Definition. 

Avoid reiterating semantics already present in the Set Name. Avoid jargon and acronyms. The Name is not a prompt, and should not be in the form of a question.

Capitalize the first word of the name only ("Vascular territory", not "Vascular Territory").

It is acceptable (and desirable) for elements in different Sets to have the same name when they capture equivalent information. E.g. the Location element in the Pulmonary Nodule Set and the Location element in the Epidural Hematoma Set both capture the anatomical location of the pathology. Two such elements would still have different Element IDs, and definitions specific to the Set they are in.

Avoid unnecessary specificity in the Name.

PREFERRED
- Anatomic focus
    - hip
    - thigh
    - knee
    - lower leg
    - ankle

AVOID
- Anatomic focus of leg
    - hip
    - thigh
    - knee
    - lower leg
    - ankle


### Element Name - Terms
If appropriate, consider the following terms for Element Names. 

Acceptable Qualitative Representation Terms:
- Category
- Characterization
- Classification
- Description
- Evaluation
- Location
- Score
- Severity 
- Status
- Type

Acceptable Quantitative Representation Terms 
- Amount - Non-numeric categorical descriptor, e.g. few, many, etc.
- Average
- Count - Numeric value arrived at by counting.
- Degree
- Diameter
- Distance 
- Length
- Quantity - Non-numeric categorical descriptor, e.g. few, many, etc.
- Rate
- Size
- Volume
- Width

Avoid using:
- Measure - Use more specific terms (rate, size, length, etc.)
- Number - Use “count” instead.

## Element Name - Detection Elements
It is not necessary to include either “Presence of” or “Detection” in the element name to distinguish from other Elements that describe severity, type, etc. Values and definitions will provide context.

AVOID
- Brain swelling detection
- Presence of brain swelling

PREFER
- Brain swelling

## Combine Detection and Categorization Elements
Where there is a need for both detection and categorization fields within a set, combine these into a single Element and add value of “absent”. This is only appropriate for Elements that are single vs. multiple select to prevent documenting both “absent” and a category in error.

AVOID
- Herniation
    - present
    - absent
- Herniation Type
    - uncal
    - central
    - cingulate

PREFER
- Herniation
    - absent
    - uncal
    - central
    - cingulate

## Normalcy, Appropriateness, Correctness 
When characterizing “appropriateness” (e.g., of the position of an enteric tube), use an element with value of “appropriate” and multiple other values indicating inappropriate categories/abnormalities/incorrectness (e.g., “bronchus”, “gastreoesophageal junction”, etc.).

## Element Type
Elements have three types:
- Integer: a number used for observations that can be counted, such as a number of occurrences, or ordered
    - ASPECTS score ( 0 - 10) integer; default 10.
    - minimum and maximum can also be specified
- Float: a decimal number used for measurements (e.g. 0.3 cm)
    - Set to the appropriate level of precision through inclusion of a step value (e.g. 0.01)
    - minimum and maximum can be specified
    - Use units that allow for measurements to be represented with no more than one decimal place
        - e.g. with units set to cm minimum value must be at least 0.1 cm
        - AVOID 0.01 cm (use 0.1 mm)
- Value Set: a pick list from which one or more values can be selected

## Measurement Elements
- Appropriate Units - The Unified Code for Units of Measure (UCUM) should be used as a reference for appropriate units.
(Unit is currently a free text in the MARVAL authoring tool, however an update is pending that will limit users to UCUM units.)

## Volume
When describing cubic units are to be avoided. 
- AVOID = cm3, mm3
- PREFER = mL, mcL

## Single-Labeled vs. Multiple Separate Data Elements
Frequently, leisonal properties (e.g., severity of stenosis, degree of calcification) can be assessed at different locations (e.g. left main artery, circumflex artery, obtuse marginal artery). 

There are two approaches:
- Define multiple data elements for each property at each possible location (e.g., separate element for stenosis at the circumflex, calcification at the circumflex, stenosis at the obtuse marginal, calcification at the obtuse marginal, etc.).
- Define a single data element for encoding each possible lesion where the location of the lesion is a possible choice (e.g., an element for lesion location [circumflex, obtuse marginal], and single elements for severity of stenosis and calcification).

Which approach should be taken can be decided on a case by case basis, but in general, the first approach is favored.