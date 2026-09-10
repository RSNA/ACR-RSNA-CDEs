# Ontology Visualizations

This directory contains visualizations and supporting files for exploring and illustrating the alpha ontology. It includes the Turtle export used as the source for the interactive ontology map, the script that generates that map, a hardcoded demonstration UI, and conceptual PNG illustrations of the knowledge graph structure.

## Directory Structure

```text
visualizations/
├── alpha-turtle.ttl
├── cde-knowledge-graph-hardcoded-view.html
├── conceptual-illustration-zoomed-findingclass.png
├── conceptual-illustration-zoomed-out.png
├── ontology_map.html
├── ontology_visualizer.py
└── README.md
```

## Files

### `alpha-turtle.ttl`

Turtle-format export of:

`alpha/standalone/radcde-standalone.ttl`

The file is exported from Protégé and serves as the ontology source used by the visualization script.

### `cde-knowledge-graph-hardcoded-view.html`

Hardcoded UI containing synthetic data for demonstration purposes.

This file is not generated from `alpha-turtle.ttl` and does not have an associated generation script. Use `ontology_map.html` to interact with the current alpha ontology.

### `conceptual-illustration-zoomed-findingclass.png`

Conceptual PNG illustration showing a zoomed-in view of the knowledge graph with a `FindingClass` as the central concept.

This is an explanatory illustration rather than a visualization generated from the Turtle ontology.

### `conceptual-illustration-zoomed-out.png`

Conceptual PNG illustration showing a zoomed-out view of the knowledge graph structure.

This is an explanatory illustration rather than a visualization generated from the Turtle ontology.

### `ontology_visualizer.py`

Python script that reads `alpha-turtle.ttl` and generates the interactive ontology visualization.

Running the script produces `ontology_map.html`.

### `ontology_map.html`

Interactive visualization of the alpha ontology network generated directly from `alpha-turtle.ttl`.

The map is intended as an exploratory view of the ontology rather than a separate representation of the model. It can be useful for understanding how FindingClasses, Diagnoses, DataElements, Values, Measurements, anatomy, assessment schemes, modalities, subspecialties, and other concepts connect across the network.

## Using the Interactive Ontology Map

Open `ontology_map.html` in a web browser.

### Search

Use the search box at the top of the page to search nodes by name or ID. Matching nodes appear in a dropdown as you type.

Selecting a result focuses the graph on that concept and its relevant semantic neighborhood.

The search results can also be navigated with the arrow keys and selected with Enter. Escape closes the search results.

### Selecting a Node

Click a node to focus on the relationships most relevant to that type of concept.

The focus is semantic rather than simply showing every node within a fixed number of graph hops. For example:

- Selecting a `FindingClass` shows its directly related findings, diagnoses, anatomy, assessments, modalities, subspecialties, DataElements, and Measurements. Values belonging to its DataElements are also included.
- Selecting a `Diagnosis` shows its directly associated findings, diagnoses, assessments, modalities, subspecialties, and directly attached DataElements and their values.
- Selecting a `DataElement` shows its permitted Values, the FindingClasses and Diagnoses that use it, and its direct anatomic scope when one is declared.
- Selecting a `Value` shows its DataElement, sibling values, and the FindingClasses and Diagnoses that use that DataElement.
- Selecting a `Measurement` shows its direct semantic relationships, including the FindingClasses or Diagnoses that use it and related Measurements.

FindingClass focus may also display reusable modeling patterns and peer FindingClasses that share those patterns. These are contextual authoring information rather than ontology nodes in the generated artifacts.

Double-clicking a node focuses the same semantic neighborhood and centers the selected node in the viewport.

Clicking empty space returns to the full graph.

### Highlight Node Type

The **Highlight node type** controls in the lower-right corner provide another way to explore the ontology.

Selecting a type emphasizes all nodes of that type, their incident relationships, and their immediately connected nodes. Connected nodes remain visible as context but are visually secondary.

This is useful for examining where a particular kind of concept, such as DataElements, Diagnoses, Measurements, or anatomy, participates across the network without expanding every neighboring relationship.

### Graph Controls

The toolbar provides several controls:

- **Reset Selection** clears the current search and selection and returns the visualization to the full graph.
- **Fit graph** fits the currently visible portion of the graph into the viewport. When a focus or type highlight is active, it fits that view rather than the entire hidden network.
- **Enable physics / Disable physics** toggles the force-directed graph simulation. Physics is disabled after the initial graph stabilization so the layout remains stable during exploration. Re-enable it if you want the network to reposition itself.
- **Reset focus** removes the current semantic focus or node-type highlight without otherwise changing the graph.

The graph itself can also be panned and zoomed normally.

## Regenerating the `ontology_map` Visualization

After exporting an updated `alpha-turtle.ttl`, run:

```bash
python3 ontology_visualizer.py
```

The script will regenerate `ontology_map.html` using the current Turtle file.

`ontology_map.html` should therefore be regenerated whenever the Turtle export changes so that the visualization remains synchronized with the current alpha.
