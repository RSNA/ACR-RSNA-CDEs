<!-----



Conversion time: 2.261 seconds.


Using this Markdown file:

1. Paste this output into your source file.
2. See the notes and action items below regarding this conversion run.
3. Check the rendered output (headings, lists, code blocks, tables) for proper
   formatting and use a linkchecker before you publish this page.

Conversion notes:

* Docs to Markdown version 1.0β35
* Wed Feb 28 2024 11:03:08 GMT-0800 (PST)
* Source doc: RadElement Standardization Guidelines
* Tables are currently converted to HTML tables.
----->


**ACR-RSNA Common Data Element Standardization Guide**

**_<span style="text-decoration:underline;">Table of Contents</span>_**


[TOC]



```
INTRODUCTION
```


**Intended Audience for this Guide**

Primarily for editors and reviewers concerned with establishing and administering Common Data Elements (CDE) standards. Authors of CDE content may find the information useful, however in order to facilitate the timely development of new content, the responsibility of applying the standards outlined here will lie with the editor/reviewer vs. the author.

**Utility of Standardization**

A coherent set of standards for common data elements (CDE) is crucial to the central management of data. Name, content and format should be designed to maximize the information and relationship to the logical structure of the data. This guide provides a method for structuring the format and content which maximizes opportunities for analysis and sharing of data.


```
GENERAL CDE STANDARDS
```


**_<span style="text-decoration:underline;">Letter Case Usage</span>_**



* Set name – title case
* Element name – sentence case
* Values – lower case (same as RadLex terms)

Some exceptions occur to these guidelines. For the types of values below, use the letter case that is used in the reference material for those values



* Modifiers: M1, M2, M3, etc. 
* Cervical spine levels C1, C2, etc.
* Cervical lymph levels: 1, 1a, 1b, etc.
* Knosp grade (capitalize surnames)

**Discuss adding this to guide: (Added by anonymous user 8-4-22)**

**_<span style="text-decoration:underline;">Sets as Observations</span>_**

In the standard FHIR model of an Diagnostic Report (as [documented by the FHIR Specification](https://www.hl7.org/fhir/diagnosticreport.html)), the actual results are included as Observation objects in the result element.

**Discuss adding this to guide (this standard is used for journals):**

**_<span style="text-decoration:underline;">Medical Eponyms</span>_**

Per AMA standards, eliminate possessive forms of medical eponyms (medical terms named after people). Ex "Crohn's disease" should be "Crohn disease". This will reduce a possible source of confusion as the non-possessive form is more efficient and simpler.

**_<span style="text-decoration:underline;">Acronyms, Abbreviations and Initialisms</span>_**

Commonly used acronyms, abbreviations and initialisms are allowed within item names, but should be spelled-out within the corresponding description field to avoid confusion for terms such as coronary artery disease vs. computer assisted diagnosis. Exceptions to this rule are the less common and not well known items which need to be spelled out within the name of the item itself. It is not necessary to spell out a standard unit of measurement. Ex. MRI, cm, etc. Be careful not to coin new abbreviations for terms that already have a standard. Ex. hepatocellular carcinoma is commonly abbreviated as “HCC” in the literature, so you wouldn’t want to use “HC” for the same term.

Spell out acronyms and abbreviations in the following fields:



* **Sets** - Description
* **Data Elements**- Description
* **Values** - Definition

**_<span style="text-decoration:underline;">Special Characters</span>_**

**Discuss adding this to guide: % symbol and whether allowed or not**


<table>
  <tr>
   <td>
    <strong>Avoid</strong>
   </td>
   <td>
    <strong>Acceptable</strong>
   </td>
  </tr>
  <tr>
   <td>
    /
   </td>
   <td>
    “and” or “or”
   </td>
  </tr>
  <tr>
   <td>
    #
   </td>
   <td>
    “number”
   </td>
  </tr>
  <tr>
   <td colspan="2" >
    <strong>Allowed Characters</strong>
   </td>
  </tr>
  <tr>
   <td>
    -
   </td>
   <td>
    hyphen
   </td>
  </tr>
  <tr>
   <td colspan="2" >
    <strong>Allowed Characters - Within Values Only</strong>
   </td>
  </tr>
  <tr>
   <td>
    ><strong><em><span style="text-decoration:underline;"> </span></em></strong>
   </td>
   <td>
    greater than
   </td>
  </tr>
  <tr>
   <td>
    &lt;<strong><em><span style="text-decoration:underline;"> </span></em></strong>
   </td>
   <td>
    less than
   </td>
  </tr>
  <tr>
   <td>
    ≥
   </td>
   <td>
    greater than or equal to
   </td>
  </tr>
  <tr>
   <td>
    ≤
   </td>
   <td>
    less than or equal to
   </td>
  </tr>
  <tr>
   <td>
    =
   </td>
   <td>
    equal
   </td>
  </tr>
</table>


**_<span style="text-decoration:underline;">Quality Rating for CDEs</span>_**

**Discuss adding this to guide - From Adam Flanders email (1-16-22)**

**Personal or local practice (Lowest quality)** – based upon the comfort level of individual Radiologists.  In conversation with another radiologist these are usually prefaced with the statement: “I (we) like to call this a [fill in the blank]”.

**Consensus Based (Low quality)**– Criteria for a specific observation/finding determined by a panel of experts or proposed in a peer-reviewed publication.  No validation performed to determine reproducibility of observation  through independent testing.  No ties to outcomes or treatment paradigms are present.

**Consensus with Validation (Good Quality)** – Same as above but the authors have taken the next step and performed an independent multi-observer reproducibility study to determine that the proposed schema has been modified to minimize ambiguity and has reached a specific level of agreement (through kappa or ICC).

**Consensus, Validation with Outcomes or Treatment Guidance Value (Best Quality)**– Same as above but a direct correlation between the observation score/grade has direct implications to prognosis or has value in directing treatment.  Example:  the ASPECTS score for stroke has been linked to outcomes and is an established threshold for specific treatments.


```
ELEMENT STANDARDS
```


**_<span style="text-decoration:underline;">Element Name - Brevity</span>_**

**Brevity** - Names are as short as possible. The definition and values will provide guidance for the usage of the Element.

**Context-Freedom** - Each Element is considered discretely from all others and can exist in one or more Sets. 

It is acceptable to have two Elements with identical names. The Element ID, definition, values, units, etc. will distinguish them from one another.

**Note:** Systems using CDEs are free to use different Element names within their system as long as the usage and RDE ID stay intact.


<table>
  <tr>
   <td colspan="3" ><strong>AVOID</strong>
<p>
<strong>Element Name Specifies Usage</strong>
   </td>
   <td colspan="3" ><strong>PREFERRED</strong>
<p>
<strong>Brief Element Name </strong>
   </td>
  </tr>
  <tr>
   <td><strong>Element Name</strong>
   </td>
   <td><strong>Values</strong>
   </td>
   <td><strong>Definition</strong>
   </td>
   <td><strong>Element Name</strong>
   </td>
   <td><strong>Values</strong>
   </td>
   <td><strong>Definition</strong>
   </td>
  </tr>
  <tr>
   <td>Anatomic focus <strong>of leg</strong>
   </td>
   <td>hip
<p>
thigh
<p>
knee
<p>
leg
<p>
ankle
   </td>
   <td>Anatomic focus of leg.
   </td>
   <td>Anatomic focus
   </td>
   <td>hip
<p>
thigh
<p>
knee
<p>
leg
<p>
ankle
   </td>
   <td>Anatomic focus of leg.
   </td>
  </tr>
</table>


**_<span style="text-decoration:underline;">Element Name - Detection Elements</span>_**

It is not necessary to include either “Presence of” or “Detection” in the element name to distinguish from other Elements that describe severity, type, etc. Values and definitions will provide context.


<table>
  <tr>
   <td><strong>AVOID</strong>
<p>
<strong>Element Name</strong>
   </td>
   <td><strong>PREFERRED</strong>
<p>
<strong>Element Name</strong>
   </td>
  </tr>
  <tr>
   <td>Brain swelling detection
<p>
or
<p>
Presence of brain swelling
   </td>
   <td>Brain swelling
   </td>
  </tr>
</table>


**Need further discussion - do we need to revise the below item**

**_<span style="text-decoration:underline;">Combine Detection and Categorization Elements</span>_**

Where there is a need for both detection and categorization fields within a set, combine these into a single Element and add value of “absent”. This is only appropriate for Elements that are single vs. multiple select to prevent documenting both “absent” and a category in error.


<table>
  <tr>
   <td colspan="2" ><strong>AVOID</strong>
<p>
<strong>Separate Elements</strong>
   </td>
   <td colspan="2" ><strong>PREFERRED</strong>
<p>
<strong>Combined Elements</strong>
   </td>
  </tr>
  <tr>
   <td><strong>Element Name</strong>
   </td>
   <td><strong>Values</strong>
   </td>
   <td><strong>Element Name</strong>
   </td>
   <td><strong>Values</strong>
   </td>
  </tr>
  <tr>
   <td>Herniation detection
   </td>
   <td>present
<p>
absent
   </td>
   <td rowspan="2" >Herniation
   </td>
   <td rowspan="2" >uncal
<p>
central
<p>
cingulate
<p>
absent
   </td>
  </tr>
  <tr>
   <td>Herniation type
   </td>
   <td>uncal
<p>
central
<p>
cingulate
   </td>
  </tr>
</table>


**_<span style="text-decoration:underline;">Normalcy/Appropriateness/Correctness </span>_**

Analogous to the case above of detection/categorization, when characterizing “appropriateness” (e.g., of the position of an enteric tube), one can define a single element with value of “appropriate” and multiple other values indicating inappropriate categories/abnormalities/incorrectness (e.g., “bronchus”, “gastreoesophageal junction”, etc.).

**_<span style="text-decoration:underline;">Representation Terms</span>_**

**Qualitative Representation Terms** 



* Category
* Characterization
* Classification
* Description
* Evaluation
* Location
* Score
* Severity 
* Status
* Type

**Quantitative Representation Terms**



* Amount or Quantity - Non-numeric categorical descriptor, e.g. few, many, etc.
* Average
* Count - Numeric value arrived at by counting.
* Degree
* Diameter
* Distance 
* Length
* Measure - **Avoid using**. Use more specific terms (rate, size, length, etc.)
* Number - **Avoid using.** Recommend using “count”.
* Rate
* Size
* Volume
* Width

**_<span style="text-decoration:underline;">Element Definitions</span>_**

Each Element must contain a definition. Avoid repeating the name of the Element as the definition and provide a descriptive definition providing clear guidance for the specific intended use of that Element.

**_<span style="text-decoration:underline;">Avoid Elements Documented within EHR or RIS</span>_**

Avoid Elements that address information already captured within the patient’s EHR or the radiology information system. Documenting these items is duplicative. The goal is to use CDEs within radiology reporting templates that live within systems that have already documented these items. CDEs should only contain elements that capture image derived features

**AVOID THESE ITEMS:**



* **Patient demographics**- Age, sex, MRN, etc. should not be included.
* **Patient health - history or current** - Comorbidities, previous history of disease/surgery, pulse rate, etc. should not be included. They describe the patient, but aren’t derived from an imaging exam. They may be considered helpful, but we want to avoid trying to model things that are outside our domain. It’s a matter of weighing the cost and benefit of storing this type of information in CDEs.
* **Exam description**  - Procedure, modality, scanner info, position, views, etc. should not be included. CDEs correspond with a set of images, and those images already have a standardized way for representing what was performed. DICOM has spent a lot of time thinking about how to model this including more granular procedure steps.

**_<span style="text-decoration:underline;">Condition/Disease Elements</span>_**

Elements indicating the presence of a condition or disease must contain a definition that clearly states whether condition/disease is inferred from image or is reiterating patient history information.

**_<span style="text-decoration:underline;">Measurement Elements</span>_**

**Definitions**- Measurement Elements must contain a definition that specifies the use of the Element. Definitions need to provide whether it describes greatest diameter, AP dimension, short axis, long axis, etc.

**Appropriate Units**—Unit is currently a free text in the MARVAL authoring tool. The Unified Code for Units of Measure (UCUM) should be used as a reference for appropriate units.

(Update to MARVAL is pending that will limit users to UCUM units.)

**Minimum Allowable Entry for Numeric Element **- Maximum limits for numeric entries will vary, however minimum allowable entry for numeric fields should be set as follows:


<table>
  <tr>
   <td><strong>Unit</strong>
   </td>
   <td><strong>Minimum </strong>
<p>
<strong>Allowable Entry</strong>
   </td>
  </tr>
  <tr>
   <td>cm
   </td>
   <td>0.1 cm
   </td>
  </tr>
  <tr>
   <td>mm
   </td>
   <td>1 mm
   </td>
  </tr>
</table>


**Volume** - When describing volume the following are to be avoided.


<table>
  <tr>
   <td colspan="2" ><strong>Volume Units</strong>
   </td>
  </tr>
  <tr>
   <td><strong>AVOID</strong>
   </td>
   <td><strong>Acceptable</strong>
   </td>
  </tr>
  <tr>
   <td>cm<sup>3</sup>
   </td>
   <td>mL
   </td>
  </tr>
  <tr>
   <td>mm<sup>3</sup>
   </td>
   <td>mcL
   </td>
  </tr>
</table>


**_<span style="text-decoration:underline;">Single-Labeled vs. Multiple Separate Data Elements</span>_**

Example, in coronary artery imaging, several properties of a lesion (e.g., severity of stenosis, degree of calcification) can be assessed at different locations (left main artery, circumflex artery, obtuse marginal artery) in the coronary anatomy. There are two approaches:



* **Define multiple data elements for each property at each possible location** (e.g., separate element for stenosis at the circumflex, calcification at the circumflex, stenosis at the obtuse marginal, calcification at the obtuse marginal, etc.).
* **Define a single data element for encoding each possible lesion where the location of the lesion is a possible choice** (e.g., an element for lesion location [circumflex, obtuse marginal], and single elements for severity of stenosis and calcification).

Which approach should be taken can be decided on a case by case basis, but in general, the first approach is favored.


```
SET STANDARDS
```


**_<span style="text-decoration:underline;">Set Name Format</span>_**

Use below format when naming Sets:

(Modality) (Body region) (Region of interest) (Finding or reason for study/observation)

Example: CT Chest Rib Fracture Identification - Emergency Setting

Sets that are modality specific should specify the modality using the corresponding RadLex code. Where a Set is applicable to multiple modalities, it is not necessary to include a code.


<table>
  <tr>
   <td><strong>Code</strong>
   </td>
   <td><strong>Modality</strong>
   </td>
  </tr>
  <tr>
   <td><strong>CT</strong>
   </td>
   <td>Computed Tomography
   </td>
  </tr>
  <tr>
   <td><strong>FL</strong>
   </td>
   <td>Fluoroscopy
   </td>
  </tr>
  <tr>
   <td><strong>MR</strong>
   </td>
   <td>Magnetic Resonance Imaging
   </td>
  </tr>
  <tr>
   <td><strong>NM</strong>
   </td>
   <td>Nuclear Medicine
   </td>
  </tr>
  <tr>
   <td><strong>PET</strong>
   </td>
   <td>Positron Emission Tomography
   </td>
  </tr>
  <tr>
   <td><strong>US</strong>
   </td>
   <td>Ultrasound
   </td>
  </tr>
  <tr>
   <td><strong>XR</strong>
   </td>
   <td>Projection Radiography
   </td>
  </tr>
</table>


**_<span style="text-decoration:underline;">Specialty Specific Sets </span>_**

Sets and Elements specific to a specialty will be assigned a specialty code within MARVAL.


<table>
  <tr>
   <td><strong>Specialty</strong>
<p>
<strong>Code</strong>
   </td>
   <td><strong>Specialty</strong>
   </td>
  </tr>
  <tr>
   <td><strong>AB</strong>
   </td>
   <td>Abdominal Radiology
   </td>
  </tr>
  <tr>
   <td><strong>BR</strong>
   </td>
   <td>Breast Imaging
   </td>
  </tr>
  <tr>
   <td><strong>CA</strong>
   </td>
   <td>Cardiac Radiology
   </td>
  </tr>
  <tr>
   <td><strong>CH</strong>
   </td>
   <td>Chest Radiology
   </td>
  </tr>
  <tr>
   <td><strong>ER</strong>
   </td>
   <td>Emergency Radiology
   </td>
  </tr>
  <tr>
   <td><strong>GI</strong>
   </td>
   <td>Gastrointestinal Radiology
   </td>
  </tr>
  <tr>
   <td><strong>GU</strong>
   </td>
   <td>Genitourinary Radiology
   </td>
  </tr>
  <tr>
   <td><strong>HN</strong>
   </td>
   <td>Head and Neck
   </td>
  </tr>
  <tr>
   <td><strong>IR</strong>
   </td>
   <td>Interventional Radiology
   </td>
  </tr>
  <tr>
   <td><strong>MI</strong>
   </td>
   <td>Molecular Imaging
   </td>
  </tr>
  <tr>
   <td><strong>MK</strong>
   </td>
   <td>Musculoskeletal Radiology
   </td>
  </tr>
  <tr>
   <td><strong>NR</strong>
   </td>
   <td>Neuroradiology
   </td>
  </tr>
  <tr>
   <td><strong>OB</strong>
   </td>
   <td>OB/GYN Radiology
   </td>
  </tr>
  <tr>
   <td><strong>OI</strong>
   </td>
   <td>Oncologic Imaging
   </td>
  </tr>
  <tr>
   <td><strong>OT</strong>
   </td>
   <td>Other
   </td>
  </tr>
  <tr>
   <td><strong>PD</strong>
   </td>
   <td>Pediatric Radiology
   </td>
  </tr>
  <tr>
   <td><strong>QI</strong>
   </td>
   <td>Quality Improvement
   </td>
  </tr>
  <tr>
   <td><strong>RS</strong>
   </td>
   <td>Research
   </td>
  </tr>
  <tr>
   <td><strong>VI</strong>
   </td>
   <td>Vascular Imaging
   </td>
  </tr>
</table>


**_<span style="text-decoration:underline;">Age and Assigned Sex at Birth Applicability</span>_**

Most CDEs will be applicable to patients of any age, however where a CDE is age specific, such as pediatrics, neonatal, etc., use the minimum and maximum age parameters  to specify this. In addition, some sets/elements may be specific to one or more assigned sex at birth values; these can also be specified. 

If no values are given for these applicability elements, the set/element is presumed to apply to all patients. Therefore, it is advantageous to narrow the applicability where that pertains.


```
VALUE STANDARDS
```


**_<span style="text-decoration:underline;">Value Name - Single Terms</span>_**

Values should be single terms vs. pre-coordinated terms where possible. Values should use terms defined in Radlex whenever possible. Always list “absent” as the first value within the list.


<table>
  <tr>
   <td><strong>AVOID</strong>
<p>
<strong>Pre-Coordinated</strong>
   </td>
   <td><strong>PREFERRED</strong>
<p>
<strong>Single Terms</strong>
   </td>
  </tr>
  <tr>
   <td>cardiac amyloid absent
<p>
cardiac amyloid present
<p>
uterine position indeterminate
   </td>
   <td>absent
<p>
present 
<p>
indeterminate
   </td>
  </tr>
</table>


**_<span style="text-decoration:underline;">Standardized Values for Detection</span>_**

Detection type elements should use the below standardized values where possible and avoid options of, “undetermined”, “equivocal”, etc. 

**Discuss adding this to the guide: **

**Avoid yes/no and use absent/present instead? **

**Standardize the order values are displayed in to be “absent” first then “present”?**

**Avoid NA (not applicable)? **

**Avoid “None” and use absent instead?**



* absent
* present
* indeterminate - cannot conclusively establish or define
* unknown - not known 

**_<span style="text-decoration:underline;">Values and Labels</span>_**

Values are intended for data transmission and storage, but should be human interpretable. Ideally, they will contain no spaces or special characters other than the underscore (“_”). Labels are intended for human interpretation, and can contain any characters, space, and may involve longer phrases (or even brief explanations). Labels should start with capital letters. 

**_<span style="text-decoration:underline;">Standardized Values for Laterality</span>_**

The below values are recommended for use within laterality type elements. It is recommended to make the element type multi select. In general, for elements that require a “bilateral” option it is recommended to use a multi select field that contains both “right” and “left” values, although there may be instances where “bilateral” may be more appropriate.



* left
* right
* midline
* central
* indeterminate

**_<span style="text-decoration:underline;">Value of "Other”</span>_**

Use of the value “other” should be avoided and should only be used where truly appropriate.

**_<span style="text-decoration:underline;">Numeric/Alpha Characters Associated to Values</span>_**

Numbers or alpha characters will not be associated with values. If required, this will be addressed within the reporting system utilizing the element.


<table>
  <tr>
   <td><strong>Values with Numbers/</strong>
<p>
<strong>Alpha Characters</strong>
<p>
<strong>(Avoid)</strong>
   </td>
   <td><strong>Values without Numbers/</strong>
<p>
<strong>Apha Characters</strong>
<p>
<strong>(Acceptable)</strong>
   </td>
  </tr>
  <tr>
   <td>1 - present
<p>
3 - absent
<p>
2 - indeterminate
   </td>
   <td>present
<p>
absent
<p>
indeterminate
   </td>
  </tr>
  <tr>
   <td>R - right
<p>
L - left
   </td>
   <td>right
<p>
left
   </td>
  </tr>
</table>

