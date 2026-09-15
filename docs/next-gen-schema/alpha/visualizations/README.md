# Ontology visualizations

This directory contains the interactive graph visualizer, a hardcoded demonstration UI, and conceptual illustrations of the knowledge-graph structure.

## Files

- `ontology_visualizer.py` reads `../graph/definition-graph.json` for CDE-authored semantics, `../scripts/anatomy.json` for native RadLex display context and inverse-property metadata, and `../radcde-alpha.ttl` for formal CDE inverse declarations and generated AssessmentCategory classes, then generates `ontology_map.html`.
- `cde-knowledge-graph-hardcoded-view.html` is a synthetic demonstration UI and is not generated from the canonical graph.
- `conceptual-illustration-zoomed-findingclass.png` is a conceptual FindingClass-centered illustration.
- `conceptual-illustration-zoomed-out.png` is a conceptual overview illustration.

## Interactive map

The visualizer consumes generated model artifacts rather than maintaining relationship or category vocabularies of its own. The canonical CDE definition graph supplies authored graph content, the generated RadLex anatomy index supplies native anatomy context and `inverseOf` metadata, and the generated CDE OWL supplies formal CDE `owl:inverseOf` declarations and AssessmentCategory class identities.

Anatomy nodes retain native RID identity. Native RadLex anatomy edges retain their exact predicate IRI and are marked as RadLex relationships. CDE-defined edges are marked separately. Anatomic refinement rules are CDE nodes whose tooltips expose their scope, exact target RIDs, taxonomy target set, permitted native RadLex predicates, and traversal specification independently.

The canonical graph contains only anatomy RIDs explicitly referenced by CDE definitions. For display, the visualizer joins those references to the RadLex index and adds native taxonomy ancestry plus a limited native relationship neighborhood. Projection affects display only; it does not alter predicate identity or graph semantics.

### Interaction

Use the search box to search nodes by name or ID. Selecting a result focuses its semantic neighborhood. Double-clicking a node applies the same focus and centers it at the configured 0.32 scale. Clicking empty space returns to the full projected graph.

The **Highlight node type** controls emphasize nodes of one type and their immediate context. The toolbar provides **Reset Selection**, **Fit graph**, **Enable/Disable physics**, and **Reset focus** controls.

Node tooltips show the node name, type, and definition. AssessmentScheme focus expands its category breakdown from generated model data; category names, ranks, bindings, and class identities are not hardcoded in the visualizer. Anatomic refinement rules additionally show each authored control separately. Native RadLex edge tooltips show the RadLex vocabulary, predicate label, and full predicate IRI.

When both directions of a formally declared inverse relationship are present, node focus keeps the edge whose direction leaves the selected node and suppresses only the matching reciprocal inverse. RadLex pairs are discovered from `anatomy.json`; CDE pairs are discovered from `owl:inverseOf` in `radcde-alpha.ttl`. Missing inverses are never guessed or synthesized.

## Regeneration

From this directory, run:

```bash
python3 ontology_visualizer.py
```

The script writes `ontology_map.html` beside itself. The generated HTML is a build artifact and need not be committed.
