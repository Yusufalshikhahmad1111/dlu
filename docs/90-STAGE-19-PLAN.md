# Stage 19 — Final Academic UX Audit

**Status:** IN PROGRESS

## Objective

Audit the complete academic product journey from student and instructor perspectives against the existing source-backed simulator workflow.

## Scope

- Learning Home → Hardware → OMT/MML → Command Files → Calls → Communications → Scenarios.
- Instructor / Classroom mode.
- Context continuity and next-step guidance.
- State communication and recovery messaging.
- Accessibility metadata already introduced in Stage 17.
- Preservation of real domain behavior.

## Stage 19 implementation

Add a small academic UX context layer that:

- standardizes the meaning of each major learning area;
- exposes `YOU ARE HERE` and `NEXT` guidance through the existing learning navigation bar;
- synchronizes the main breadcrumb with the selected academic workspace;
- adds tab tooltips, accessible names, and descriptions;
- preserves existing views and engines instead of wrapping or rewriting them.

## Acceptance

- the six student learning areas remain reachable through the existing navigation;
- each workspace communicates purpose and next action;
- real MML, call, communications, and scenario operations still work;
- instructor answers remain hidden until explicitly revealed;
- 1280×720, 1366×768, 1600×900, and 1920×1080 remain usable;
- full regression remains green;
- the stage has focused tests, Windows visual QA, report, and closeout evidence.

## Safety

No new domain logic, database migration, dependency, or simulator behavior is introduced.
