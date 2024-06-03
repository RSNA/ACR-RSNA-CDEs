# Element Guidance
Submitters are advised to review existing Elements on radelement.org, perhaps in Elements Sets analogous to the Set being proposed, to get a sense of typical naming, definition and value set patterns.

## Element ID
Leave Element ID codes blank at the time of submission. They are assigned as part of the publication process.

## Element Definition
Express the full semantics of the Element and provide a clear description of the specific intended use. A few words is typically inadequate; i.e., don’t just repeat the Element Name.

For Elements indicating the presence of a condition or disease, clearly state whether the value represents the current finding or is reiterating patient history.

For Elements that are measurements, define the method sufficiently to get consistent results. For example, clarify whether a diameter should be the greatest diameter in the imaging place, the AP dimension, short axis, long axis, etc. Most formats in which CDEs will be encoded (e.g. FHIR, DICOM SR), encode units for each measurement directly, usually using UCUM.  The element definition may note default units to be assumed by coding systems that do not encode them directly. 

Include references when the Element is based on established scientific literature, such as BI-RADS, TI-RADS, ASPECTS, SLICS, TLICS, NASCET, AoSpine, Fazekas Score and many others.

## Element Name
Think of the Element Name as a data item label within the Set.  

Keep names as short as possible. Since elements all exist within the context of their specific parent Element Set, it is only necessary for the name to distinguish elements from the other elements in the same Set. The full semantics are in the Element Definition. 

Avoid reiterating semantics already present in the Set Name. Avoid jargon and acronyms. The Name is not a prompt, and should not be in the form of a question.

Capitalize the first word of the name only ("Vascular territory", not "Vascular Territory").

It is acceptable (and desirable) for elements in different Sets to have the same name when they capture equivalent  information. E.g. the Location element in the Pulmonary Nodule Set and the Location element in the Epidural Hematoma Set both capture the anatomical location of the pathology. Two such elements would still have different Element IDs, and definitions specific to the Set they are in.

## Element Name - Terms
If appropriate, consider the following terms for Element Names. 

Qualitative Representation Terms:
  - **>**:  hyphen
- **>**: Category
- **>**: Characterization
- **>**: Classification
- **>**: Description
- **>**: Evaluation
- **>**: Location
- **>**: Score
- **>**: Severity 
- **>**: Status
- **>**: Type

Quantitative Representation Terms 
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

## Avoid using the following terms. 
Measure - Use more specific terms (rate, size, length, etc.)
Number - Use “count” instead.


## Element Name - Detection Elements
It is not necessary to include either “Presence of” or “Detection” in the element name to distinguish from other Elements that describe severity, type, etc. Values and definitions will provide context.

AVOID
PREFER
Brain swelling detection
or
Presence of brain swelling
Brain swelling

## Combine Detection and Categorization Elements
Where there is a need for both detection and categorization fields within a set, combine these into a single Element and add value of “absent”. This is only appropriate for Elements that are single vs. multiple select to prevent documenting both “absent” and a category in error.

AVOID
Separate Elements
PREFER
Combined Elements
Element Name
Values
Element Name
Values
Herniation detection
present
absent
Herniation
absent
uncal
central
Cingulate
indeterminate
Herniation type
uncal
central
cingulate


## Normalcy/Appropriateness/Correctness 
Analogous to the case above of detection/categorization, when characterizing “appropriateness” (e.g., of the position of an enteric tube), one can define a single element with value of “appropriate” and multiple other values indicating inappropriate categories/abnormalities/incorrectness (e.g., “bronchus”, “gastreoesophageal junction”, etc.).


AVOID
Element Name Specifies Usage
PREFER
Brief Element Name 
Element Name
Values
Definition
Element Name
Values
Definition
Anatomic focus of leg
hip
thigh
knee
leg
ankle
Anatomic focus of leg.
Anatomic focus
hip
thigh
knee
leg
ankle
Anatomic focus of leg.


## Element Type
CDEs have four data types:
Integer: a number used for observations that can be counted, such as a number of occurrences, or ordered
Numeric: a floating point number used for measurements 
Value Set: a pick list from which one or more values can be selected

This may be a fixed response (present or absent), categorical with a fixed set of responses or a measurement with a defined upper or lower limits and potentially a default value.
e.g.. hemorrhage: present/absent
Hemorrhage type: epidural, subdural, subarachnoid, intraparenchymal, intraventricular.
ASPECTS score ( 0 - 10) integer; default 10.

## Element Minimum Cardinality
Indicate the number of values required for the containing Element Set to be valid.
A value of 0 indicates the Element is optional. A value of 1 or more indicates the Element is required, i.e. that 0 values is invalid.
Be judicious. Required means that if all other elements are present but this one is absent, then the Element Set must be rejected. 

## Element Maximum Cardinality
Indicate the number of values beyond which the containing Element Set is invalid. Most often, this is 1.

## Measurement Elements
- Appropriate Units - The Unified Code for Units of Measure (UCUM) should be used as a reference for appropriate units.
(Unit is currently a free text in the MARVAL authoring tool, however an update is pending that will limit users to UCUM units.)

Numeric = the decimal point can be set to the appropriate level of precision (eg, "step level: .1") and range of allowable values, and a unit of measure specified

## Minimum Allowable Entry for Numeric Element  
Maximum limits for numeric entries will vary, however minimum allowable entry for numeric fields should be set as follows:
Unit with minimum allowable entry
- cm  = 0.1 cm
- mm = 1 mm

## Volume
When describing volume the following are to be avoided.
Volume Units
-AVOID = cm3, mm3
-PREFER = mL, mcL

## Single-Labeled vs. Multiple Separate Data Elements
Example, in coronary artery imaging, several properties of a lesion (e.g., severity of stenosis, degree of calcification) can be assessed at different locations (left main artery, circumflex artery, obtuse marginal artery) in the coronary anatomy. There are two approaches:
- Define multiple data elements for each property at each possible location (e.g., separate element for stenosis at the circumflex, calcification at the circumflex, stenosis at the obtuse marginal, calcification at the obtuse marginal, etc.).
- Define a single data element for encoding each possible lesion where the location of the lesion is a possible choice (e.g., an element for lesion location [circumflex, obtuse marginal], and single elements for severity of stenosis and calcification).
Which approach should be taken can be decided on a case by case basis, but in general, the first approach is favored.


