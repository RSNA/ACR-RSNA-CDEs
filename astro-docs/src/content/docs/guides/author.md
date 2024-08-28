---
title: Author Guide and Global CDE Conventions
---

## Intended Audience for this Guide

Primarily for editors and reviewers concerned with establishing and administering Common Data Elements (CDE) standards. Authors of CDE content may find the information useful, however in order to facilitate the timely development of new content, the responsibility of applying the standards outlined here will lie with the editor/reviewer vs. the author.

## Utility of Standardization

A coherent set of standards for common data elements (CDE) is crucial to the central management of data. Name, content and format should be designed to maximize the information and relationship to the logical structure of the data. This guide provides a method for structuring the format and content which maximizes opportunities for analysis and sharing of data.

## CDE Scope and Conventions

### Capitalization
- Set name – title case
- Element name – sentence case
- Values – lower case (same as RadLex terms)

Some case exceptions are shown below, and follow common convention from the medical literature.

- Modifiers: M1, M2, M3, etc. 
- Cervical spine levels C1, C2, etc.
- Knosp grade (capitalize surnames)

## Literature Search

Standardized observation elements and standardized values are not a new concept. The CDE initiative introduces a method for managing the data structures and ID codes, but from a clinical perspective the literature is replete with examples of content appropriate for CDEs.

Before formulating a CDE Element Set, explore the peer-reviewed literature. If there is an existing imaging classification system for a specific observation, this should be considered first before attempting to create one from scratch. A codified and validated grading system is preferred over a new and unvalidated scheme. There are many validated imaging features in the literature that have been assessed for agreement (kappa or ICC). Studies which have validated the classification scheme through interobserver analysis for a specific clinical use case are particularly valuable and should be given high priority when composing a CDE Element Set submission. 

The order of priority for existing CDE schemes include: 

1. unique classification systems with successful validation analysis, 
2. classification systems developed through expert consensus panels, 
3. other classification in use in the peer review literature and 
4. individual methods. 

In most instances provenance for a CDE element or CDE set should be citable and point to an original reference in the literature.

## Scope

Begin by deciding on an appropriate scope of Elements to be included in an Element Set. Review existing Sets on radelement.org to get a sense of typical scope patterns and to confirm the proposed set is not already adequately covered.  If an existing set covers most of your intended content, consider suggesting modifications rather than a new Element Set.  

A Set should include Elements for all the essential discrete detailed observations or properties to be recorded by a reading radiologist for a particular general finding or clinical scenario. 

CDE set scope avoids data that is mostly not obtained from images but rather from EHR.

For example:

- a Set for a pulmonary nodule would include Elements for size, location, and solidity 
- a Set for pancreatitis would include Elements for the presence of necrosis, presence of peripancreatic collections, size of peripancreatic collections, and patency of the adjacent vessels 
- a Set for acute stroke could include Elements for vascular territory, presence of hemorrhage, midline shift, and an ASPECTS score

For a simple radiology procedure, the scope may be congruent with all the observations typically reported for the entire procedure.
For more complex interpretations, image interpretation and diagnosis may involve forking paths of conditional ("If/then") logic where each finding leads to a new set of observations, such as in a flowchart. In such cases, the scope of a Set will typically correspond to one "branch" of that graph.

Note: While creation of a CDE Set addresses content, it does not define the conditional logic (see ACRCAR/DS).

Consider reviewing and having at hand a reference such as a best-practice guide, a reporting template, or an exemplary report as a basis for determining what Elements will be included in the Set. You may need to begin by identifying the discrete pieces of data implied in the narrative text of such resources.

CDEs should not include data elements that are contained elsewhere in the patient record, such as patient demographics (age, sex) and general medical history, even though this information may be included in a radiology report.

### EHR, RIS, and PACS Data

Avoid including Elements for information already captured and available within the patient’s EHR or the radiology information system. CDEs are intended to be used within such systems, so documenting these items in CDEs is duplicative and CDE’s try to avoid modelling information outside our domain. CDEs should only contain features derived from images

**Specifically Avoid:**

- Patient demographics: Age, sex, MRN, etc.
- Patient history: complaints, comorbidities, family or surgical history, vital signs, lab values, prior diagnosis
- Exam description: procedure, modality, scanner info, position, views, etc. CDEs correspond with a set of images, and those images already have a standardized way for representing what was performed. DICOM has spent a lot of time thinking about how to model this including more granular procedure steps.

## Age and Sex at Birth
Most CDEs will be applicable to patients of any age, however where a CDE is age specific, such as pediatrics, neonatal, etc., use the minimum and maximum age parameters  to specify this. In addition, some sets/elements may be specific to one or more assigned sex at birth values; these can also be specified. 

If no values are given for these applicability elements, the set/element is presumed to apply to all patients. Therefore, it is advantageous to narrow the applicability where that pertains.