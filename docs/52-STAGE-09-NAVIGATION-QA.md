# Stage 9 — Student-Centered Navigation QA

Status: **Awaiting Windows CI evidence**

## Required gates

### Functional

- Application opens on Learning Home after Stage 9 is applied.
- HOME is visibly active.
- Continue Learning is enabled.
- Six Quick Start actions exist.
- Opening a learning area restores the technical workspace.
- Active navigation follows the selected area.
- Returning HOME collapses the technical workspace again.
- Direct feature-tab selection synchronizes student context.
- Session progress and recent activity update.
- Morning/Night theme switching remains functional.

### Keyboard

- Navigation controls are focusable.
- Tab traversal can leave HOME.
- Space activates a focused learning action.

### Visual

Screenshots are generated at:

- 1280×720
- 1366×768
- 1600×900
- 1920×1080

Additional visual checks:

- OMT/MML workspace screenshot at 1600×900.
- Night Home screenshot at 1600×900.
- No horizontal clipping on the Home scroll surface.

### Regression

The existing full test suite remains the release gate.

### Packaging

Stage 9 changes startup/navigation modules, so the Windows workflow must continue to compile every Python module. A packaged release will be regenerated at the next release-oriented checkpoint.

