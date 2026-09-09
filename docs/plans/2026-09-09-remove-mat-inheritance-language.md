# Remove Inheritance Semantics from Mats

Status: Implementation complete; deployment pending an owner-approved commit

## Goal

Ensure mats show context explicitly asserted for the displayed node without claiming or implying that `IS_A`/`SUBTYPE_OF` propagates attributes or context.

## Plan

1. Capture the current incorrect acute-pyelonephritis rendering with a deterministic regression check for the phrase `inherited from`.
2. Trace the renderer and graph inputs to distinguish directly asserted context from any fallback traversal across `IS_A`/`SUBTYPE_OF`.
3. Change the rendering/model behavior so acute pyelonephritis still shows its applicable modalities and other context, but no property is obtained or labelled through inheritance.
4. Add regression coverage for both requirements: no inheritance language or propagation, and preservation of directly asserted acute-pyelonephritis context.
5. Update the relevant semantic/display documentation to state that `IS_A`/`SUBTYPE_OF` is classificatory only and does not imply OOP-style inheritance. Update this plan as work proceeds and review the active project log plus other reference documentation for final-state accuracy.
6. Run the focused regression checks and the full bundle validation, rebuild the rendered site, and inspect the affected pages.
7. Stop for explicit commit permission. Once committed, build from that commit, run the publication denylist sweep, upload only the committed generated site to `t3://oidm-public/cde-schema/next-gen-schema/`, and verify the public acute-pyelonephritis page and representative assets.

## Results

- Replaced the renderer's `SUBTYPE_OF` fallback with direct-only scope and context lookup, including tree-page detail data and hover cards.
- Added explicit acute-pyelonephritis edges for kidney scope, modality (including ultrasound), region, subspecialty, sex, age, and etiology; its existing time-course edges remain direct. The other pyelonephritis and pleural-effusion subtypes now also carry direct scope and shared context edges so removing propagation does not silently empty their established displays.
- Removed the older location-dossier inheritance display and updated the current model, display specification, decision record, historical build decision, graph reference, tool reference, and change log to state that `SUBTYPE_OF` never propagates outgoing edges.
- Added focused regression coverage and connected it to the bundle checker. The focused tests pass, the bundle reports `44 documents · 11 diagrams · 0 errors · 0 warnings`, and the rebuilt acute mat visibly retains `ultrasound RID10326` without the false label.
- Updated the affected OKF concept-document headers with the current generator and date, adjusted the expanded decision record's title and index entry, regenerated the affected committed diagrams, and visually inspected the acute-pyelonephritis mat.
- Staged this correction separately from the part-solid-nodule work, collaborator-review documentation, handoff edits, and unrelated validation cleanup; the mixed decision-record and log files were split at hunk level.
- No commit, upload, or deployed-object change has been made. Publication remains gated on explicit commit permission and a committed-tree denylist preflight.
