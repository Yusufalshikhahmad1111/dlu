# Stage 8 — UX/UI Reimagination — Master Execution Prompt

Use this prompt when executing Stage 8.

---

## ROLE

Act as a senior desktop UX/UI architect, educational-product designer, and PySide6/Qt Widgets engineer.

You are working on:

**DLU Lab — Siemens EWSD Educational Simulator**

The current repository is already complete through Stage 7 and is release-ready.

## NON-NEGOTIABLE CONSTRAINTS

1. Do not destroy existing functionality.
2. Do not rewrite the domain core.
3. Do not invent EWSD hardware data.
4. Do not change MML semantics.
5. Do not change call-engine semantics.
6. Do not change communications calculations.
7. Do not change teaching-scenario expected results.
8. Keep the existing Windows packaging path working.
9. Prefer reusable design tokens/components over scattered style code.
10. Follow the repository rule:
   Implement → Tests → Visual QA → Manual Demo → Fix → Report → Commit

## PRIMARY GOAL

Perform a genuine visual/UX transformation.

The application should move from:

**brown/ivory technical simulator**

to:

**modern telecom control room + university laboratory**

with:

- deep navy;
- graphite surfaces;
- cyan primary;
- emerald success;
- amber warning;
- red danger;
- clean neutral text;
- stronger visual hierarchy;
- reduced clutter;
- clearer context.

## STAGE SCOPE

### A. Design tokens

Create a centralized token layer for:

- colors;
- typography;
- spacing;
- radii;
- border weights;
- control heights;
- semantic states.

Use the proposed palette in `docs/38-DESIGN-SYSTEM-SPECIFICATION.md`.

Do not hard-code arbitrary new colors in individual widgets.

### B. Production styling strategy

Do not solve the redesign by adding an ever-growing runtime QSS string.

Use a centralized Qt styling strategy appropriate for production.

QSS may be used for local adjustments where justified.

Reference:
https://doc.qt.io/qt-6.12/qtwidgets-styling-approaches.html

### C. Main application shell

Redesign:

- header;
- primary navigation;
- status area;
- breadcrumb/context;
- content workspace;
- secondary/context panel.

The shell must make it obvious:

- where the user is;
- what is selected;
- what can be done next.

### D. Component primitives

Establish reusable primitives for:

- buttons;
- status chips;
- cards;
- tabs;
- inspector rows;
- section headers;
- banners;
- tables;
- tooltips;
- command input.

### E. State system

Create consistent visual states for:

ACTIVE
IDLE
MBL
BUSY
FAULT
TEST
BLOCKED
PASS
FAIL

Color is never the only state signal.

### F. Preserve hardware visual semantics

Do not remove:

- DLU;
- shelf;
- module;
- port;
- EQN;
- capacity;
- source verification;
- maintenance state.

Only redesign their presentation.

### G. Theme migration

The old Brown + Ivory / Brown + Silver theme switch is replaced by the new design direction.

Do not leave old theme-specific colors scattered through feature views.

## IMPLEMENTATION DISCIPLINE

Before changing code:

1. inspect current style/theme usage;
2. identify hard-coded visual constants;
3. identify shared widgets;
4. identify top-level layout dependencies;
5. make a small migration plan inside the implementation report.

Then implement in small safe changes.

## TESTS

Add/update tests where the design system can be tested deterministically.

At minimum verify:

- theme/token values exist;
- semantic states map correctly;
- app starts;
- main shell builds;
- existing tests remain green.

## VISUAL QA

Generate screenshots for:

1. main laboratory shell;
2. hardware home;
3. DLU/shelf/module view;
4. OMT;
5. call path;
6. communications;
7. scenarios.

Check at:

1280×720
1366×768
1600×900
1920×1080

## ACCEPTANCE

Stage 8 is complete only when:

- the visual language is clearly different from the old brown/ivory design;
- all major surfaces share one design system;
- no major clipping/overlap exists;
- keyboard focus is visible;
- status is understandable without color alone;
- existing academic behavior is preserved;
- test suite is green;
- visual QA is documented;
- implementation report and closeout are added.

## DO NOT

- add AI;
- add multiplayer;
- add unrelated academic features;
- replace source-backed data;
- rewrite the database;
- rewrite MML;
- rewrite CallEngine;
- rewrite communications mathematics.

Focus on UX/UI only, with the smallest architecture changes required to make the design system maintainable.
