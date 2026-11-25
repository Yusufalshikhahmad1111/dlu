# Stage 18 — Performance & Architecture Cleanup Implementation Report

**Status:** COMPLETE

## Delivered

### Application shell

Added `dlu_app/app_shell.py` to centralize:

- ordered stage installation;
- construction of `DluSimulatorWindow`;
- target-screen sizing policy.

`main.py` now owns process startup, database restore handling, CLI flags, and event-loop lifecycle rather than the feature composition pipeline.

### Hardware feature boundary

Added `dlu_app/hardware_view.py` containing:

- hardware graphics primitives;
- hardware selection/reference/library dialogs;
- hardware workspace rendering and navigation mixin;
- theme synchronization for the extracted feature.

The existing hardware method names and behavior were preserved. `DluSimulatorWindow` continues to expose the same public hardware API through `HardwareWorkspaceMixin`.

### Monolith reduction

The primary `dlu_app/ui.py` module was reduced from approximately **2,836 lines / 105KB** to approximately **1,484 lines / 56KB** by extracting the hardware feature surface.

## Domain safety

No MML, CallEngine, TeachingScenario, database schema, or runtime dependency changes were introduced.

## Validation

Final evidence: Stage18 focused **5/5**, Stage16 compatibility **7/7**, Stage17 compatibility **5/5**, full regression **139/139**, compile/static audit **PASS**, Windows architecture/resolution QA **PASS**, and screenshot artifact upload **PASS**.
