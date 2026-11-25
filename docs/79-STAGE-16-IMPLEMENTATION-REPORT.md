# Stage 16 — Instructor / Classroom Mode Implementation

**Status:** IMPLEMENTATION

## Delivered

### Instructor workspace
Added `dlu_app/stage16_ui.py` and mounted a new **Instructor** tab from `main.py`.

### Scenario loading
The instructor can select all six source-backed Teaching Scenarios from the existing `TeachingScenarioRunner.catalog()`.

### Reset
The instructor reset control delegates to the existing window-level reset lifecycle. No reset logic was duplicated.

### Answer visibility
Expected and actual result content is hidden by default. The instructor explicitly enables **REVEAL ANSWERS** before showing academic answers.

### Guided demonstration
A real `TeachingScenarioRunner.run()` result is revealed one verified step at a time. The UI does not execute individual fake steps or reproduce scenario rules.

### Projector mode
Projector mode hides operational controls and the detailed step table, replacing them with a large scenario title, objective, and result summary.

### Theme
The widget uses the existing Stage 8 design tokens and supports Morning/Night.

## Domain safety

- no CallEngine changes;
- no MML changes;
- no TeachingScenarioRunner changes;
- no SQLite migration;
- no new runtime dependency;
- no parallel teaching rules.

## Known integration rule

Student mode continues using the existing Learning Home and technical workspaces. Instructor mode is additive.
