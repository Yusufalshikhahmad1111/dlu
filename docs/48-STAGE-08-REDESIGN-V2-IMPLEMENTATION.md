# Stage 8 Rework — UX/UI Reimagination v2 Implementation

Status: Implemented on branch `stage-08-ui-redesign-v2`; final CI/visual gates pending.

## Changed

### Visual system
- Replaced the blue/black identity with green-family tokens.
- Added Morning and Night token sets.
- Added compatibility aliases for existing feature widgets.
- Centralized application palette/style generation.

### Theme UX
- Morning is the default.
- Visible `☾ NIGHT MODE` / `☀ DAY MODE` switch.
- Theme change updates the shell and feature widgets in place.
- Legacy theme submenu is removed from the visible Tools UX.

### Navigation shell
- Preserved the Stage 8 lab navigation concept.
- Made tab matching tolerant of old/new labels so navigation cannot silently miss a target.

### OMT / MML
- Promoted OMT to a first-class command workbench.
- Added QUICK RUN examples.
- Added explicit command status feedback.
- Renamed SEND to RUN.
- Added safe exception reporting around command execution.
- Kept execution delegated to the existing `MmlEngine`.

### Regression protection
Added a GUI-level test that:
- switches to OMT/MML;
- executes `> help;` through the actual Run button;
- checks the rendered result;
- toggles Morning ↔ Night.

## Preserved

- Database schema and seed data.
- Hardware hierarchy and source rules.
- MML parser/engine.
- Call engine.
- Communications calculations.
- Teaching scenarios.
- Backup/restore.
