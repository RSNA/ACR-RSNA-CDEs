# Native RadLex anatomy shape

Generated on 2026-09-14 from configured RadLex 4.3. Do not hand-edit.

This document describes the imported RadLex side of the model. These are native RadLex classes and predicates, not CDE-defined relationships. Predicate identity is preserved exactly. `rdfs:subPropertyOf` and `owl:inverseOf` are ontology metadata and do not, by themselves, authorize an application to substitute predicates or recursively traverse them.

## Anatomy branch

- Native RadLex classes: **46,898**
- RID3 anatomical-entity branch: **38,178**
- Native object properties declared by RadLex: **52**
- Native semantic relationships in the full index: **83,161**
- Distinct native predicates used between RID3 anatomy concepts: **46**

## Native object properties

| Property | Anatomy assertions | subPropertyOf | inverseOf | Domain | Range | OWL characteristics |
|---|---:|---|---|---|---|---|
| `http://www.radlex.org/RID/Anatomical_Site` | 0 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Anterior_to` | 2 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Attaches_to` | 139 | — | `http://www.radlex.org/RID/Receives_attachment_from` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Blood_Supply_of` | 26 | — | `http://www.radlex.org/RID/Has_Blood_Supply` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Bounded_by` | 105 | — | `http://www.radlex.org/RID/Bounds` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Bounds` | 103 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Branch_Of` | 3827 | `http://www.radlex.org/RID/Continuous_With` | `http://www.radlex.org/RID/Has_Branch` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Branch_Part_of` | 0 | `http://www.radlex.org/RID/Regional_Part_Of` | `http://www.radlex.org/RID/Has_Branch_Part` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Constitutional_Part_Of` | 5258 | `http://www.radlex.org/RID/Part_Of` | `http://www.radlex.org/RID/Has_Constitutional_Part` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Contained_In` | 258 | — | `http://www.radlex.org/RID/Contains` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Contains` | 246 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Continuous_With` | 2278 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Distal_to` | 885 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Drains_Into` | 74 | `http://www.radlex.org/RID/Sends_Output_To` | `http://www.radlex.org/RID/Receives_Drainage_From` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/External_to` | 1 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Has_Blood_Supply` | 26 | — | — | — | `http://www.radlex.org/RID/RID478` | — |
| `http://www.radlex.org/RID/Has_Branch` | 3996 | `http://www.radlex.org/RID/Continuous_With` | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Has_Branch_Part` | 0 | `http://www.radlex.org/RID/Has_Regional_Part` | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Has_Constitutional_Part` | 5378 | `http://www.radlex.org/RID/Has_Part` | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Has_Entrapment_Site` | 2 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Has_Innervation_Source` | 520 | — | `http://www.radlex.org/RID/Innervates` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Has_insertion` | 100 | — | `http://www.radlex.org/RID/Insertion_of` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Has_Member` | 728 | — | `http://www.radlex.org/RID/Member_Of` | — | — | — |
| `http://www.radlex.org/RID/Has_origin` | 92 | — | `http://www.radlex.org/RID/Origin_of` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Has_Part` | 9540 | — | `http://www.radlex.org/RID/Part_Of` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Has_Regional_Part` | 15615 | `http://www.radlex.org/RID/Has_Part` | `http://www.radlex.org/RID/Regional_Part_Of` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Inferior_to` | 3 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Innervates` | 477 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Insertion_of` | 83 | — | — | — | `http://www.radlex.org/RID/RID13389` | — |
| `http://www.radlex.org/RID/Lymphatic_Drainage` | 65 | — | `http://www.radlex.org/RID/Lymphatic_Drainage_Of` | — | `http://www.radlex.org/RID/RID13389` | — |
| `http://www.radlex.org/RID/Lymphatic_Drainage_Of` | 65 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/May_Be_Caused_By` | 0 | — | `http://www.radlex.org/RID/May_Cause` | — | — | — |
| `http://www.radlex.org/RID/May_Cause` | 0 | — | — | — | — | — |
| `http://www.radlex.org/RID/Member_Of` | 741 | — | — | `http://www.radlex.org/RID/RID0` | `http://www.radlex.org/RID/RID1` | — |
| `http://www.radlex.org/RID/Origin_of` | 108 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Part_Of` | 9521 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Posterior_to` | 9 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Projects_From` | 109 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Projects_To` | 112 | — | `http://www.radlex.org/RID/Receives_Projection_From` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Proximal_to` | 885 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Receives_attachment_from` | 137 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Receives_Drainage_From` | 74 | `http://www.radlex.org/RID/Receives_Input_From` | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Receives_Input_From` | 811 | — | `http://www.radlex.org/RID/Sends_Output_To` | — | `http://www.radlex.org/RID/RID1` | — |
| `http://www.radlex.org/RID/Receives_Projection_From` | 108 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Regional_Part_Of` | 15301 | `http://www.radlex.org/RID/Part_Of` | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Related_modality` | 0 | — | — | `http://www.radlex.org/RID/RID5` | — | — |
| `http://www.radlex.org/RID/Segment_Of` | 67 | `http://www.radlex.org/RID/Part_Of` | — | — | `http://www.radlex.org/RID/RID3` | functional |
| `http://www.radlex.org/RID/Sends_Output_To` | 811 | — | — | — | `http://www.radlex.org/RID/RID1` | — |
| `http://www.radlex.org/RID/Superior_to` | 3 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Surrounded_by` | 11 | — | `http://www.radlex.org/RID/Surrounds` | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Surrounds` | 11 | — | — | — | `http://www.radlex.org/RID/RID3` | — |
| `http://www.radlex.org/RID/Tributary_Of` | 3 | `http://www.radlex.org/RID/Continuous_With` | — | — | `http://www.radlex.org/RID/RID3` | functional |

## Canonical-graph representation

The canonical CDE definition graph materializes only native RID anatomy concepts explicitly referenced by CDE definitions. Full native taxonomy edges, object-property assertions, and object-property declarations remain in `scripts/anatomy.json` and the untouched RadLex source. Consumers that need RadLex context join against that index rather than relying on a copied RadLex subgraph.

No CDE `PART_OF`, `ANATOMY_RELATION`, `Contained_In` proxy, or other flattened anatomy predicate is created.
