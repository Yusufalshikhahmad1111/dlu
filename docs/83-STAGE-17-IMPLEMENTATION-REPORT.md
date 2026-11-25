# Stage 17 — Accessibility & Usability Audit Implementation

**Status:** IMPLEMENTED

## Delivered

### Shared accessibility layer

Added `dlu_app/stage17_accessibility.py` with:

- contrast ratio calculation and Morning/Night regression reporting;
- accessible names and descriptions for primary controls;
- discoverability tooltips for technical actions;
- StrongFocus on interactive controls that previously had no keyboard focus;
- deterministic keyboard tab order for the main hardware workflow and Instructor controls;
- reusable visible-focus QSS;
- non-focusable hardware canvas with keyboard alternatives through PATH controls and technical tabs.

### Core UI hardening

Updated `dlu_app/ui.py`:

- minimum window size reduced from 1250×760 to 1180×680;
- added a clear Hardware empty state;
- named important controls for accessibility;
- exposed action controls as attributes for deterministic QA;
- reapplies accessibility state after theme changes.

### Application styling

Updated `dlu_app/app_style.py` with explicit focus styling for checkboxes, tabs, text/list/table views and generic item views.

### Instructor answer visibility

Stage 16 was hardened so `PASS` / `FAIL` stays hidden while answers are concealed. Revealing answers synchronizes the status label with the real scenario result. No scenario engine was changed.

### Automated QA

Added:

- `tests/test_stage17_accessibility.py`;
- `tools/stage17_accessibility_qa.py`;
- `.github/workflows/stage17-accessibility-qa.yml`.

The tests cover contrast, accessible names, focus, keyboard order, tooltips, empty state, target size, and Instructor answer visibility.

## State communication

The app already uses text states such as READY, ERROR, RESET, SYSTEM ACT, EXECUTED and explicit scenario status. Stage 17 adds accessibility metadata without replacing the existing state model.

There is no asynchronous/network loading step in the core desktop workflow, so a fake spinner was not introduced. Deterministic local operations communicate readiness, execution, errors and reset explicitly instead.

## Domain safety

- no telecom rule changes;
- no MML semantic changes;
- no CallEngine semantic changes;
- no database migration;
- no runtime dependency added.
