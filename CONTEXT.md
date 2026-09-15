# CDE vocabulary

Working vocabulary for the next-generation discussion. These definitions express our current ideas for the reviewer's foundation, not a jointly settled integration model.

## Language

**DataElement**:
A categorical descriptor whose permissible values may be ordered or unordered. Semantic ordering is explicit and is distinct from display order.

**Categorization**:
A distinction expressed either by a categorizing DataElement or by a taxonomy of named classes, not both for the same distinction in the same model. Choosing the taxonomy does not exclude other descriptors unrelated to that categorization.

**Measurement**:
A quantitative descriptor, distinct from a DataElement. Its measurement method is optional and is unspecified by default.

**Element binding**:
A relationship connecting a definition to a DataElement it uses. A FindingClass's binding may restrict that use to a subset of the element's permissible values without changing the shared element or its other bindings.

**Selection cardinality**:
The permitted number of values selected for a DataElement in a use, such as single or multiple selection. This is distinct from value ordering, counts of finding components, and whether a report mentions the element.

**Modality applicability**:
The imaging modalities on which a finding can be seen, a descriptor can be evaluated, or a descriptor applies in a particular finding's binding. A descriptor's intrinsic modality limit is distinct from its binding-specific applicability and is not an overridable default.

**Unspecified modality applicability**:
No modality applicability information has been recorded. Omission alone means neither applicability to every modality nor exclusion from every modality.

**AssessmentScheme**:
A distinct definition of an assessment system whose descriptive dimensions are ordinary DataElements linked to the scheme, analogous to a FindingClass with its descriptors. The scheme is distinct from any one dimension or that dimension's permissible values.

**AnatomicLocation**:
An anatomical reference identified by its RadLex identity, with temporary sided-variant exceptions governed by the anatomy track. It can bind directly to DataElements and Measurements describing that anatomy without requiring a FindingClass.

**Component-of scope**:
The finding classes a component class belongs inside, stated on the component class; satisfied by those classes or any of their subtypes, checked by walking up the container's classification. A class with a component-of scope is never reported on its own. Owner's term, 13 September 2026 (S33).

**Lesion family**:
A group of related lesion types, usually specific to a location. Component classes are lesion-family specific (S34).

**Standard clinical metadata**:
The seven facts on a class: modality, body region, subspecialty, sex, age, time course, and etiology. Owner's term, 10 September 2026 (S31); "context" is not used for these.

**Anatomic scope**:
The eligible anatomical places, tissue types, or structure types for a definition. A plain list matches any one target by default; explicit combinations can require multiple conditions to hold together.

**Anatomy scope specifier**:
A concept used to identify eligible anatomy, including the tissue-type and structure-type families. How those families connect to the anatomic location hierarchy remains open.

**Tissue-type scope**:
An anatomy scope family exemplified by pulmonary parenchyma, hepatic parenchyma, and subcutaneous fat. The family does not by itself prescribe a separate graph node type.

**Structure-type scope**:
An anatomy scope family exemplified by solid organs, vessels and their artery/vein subtypes, muscles, tendons, and ligaments. The family does not by itself prescribe a separate graph node type.
