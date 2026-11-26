# Final Academic Test Report — DLU Lab 2.0.0

## Release scope

This report closes the full DLU Lab roadmap from Stage 0 through Stage 20.

Stage 0–19 were already completed before the final release pass. Stage 20 re-verifies the integrated application, packaging and current documentation on the release tree.

## Verification matrix

| Stage | Scope | Result |
| --- | --- | --- |
| 0 | Architecture, source-backed hardware rule, SQLite foundation | PASS |
| 1 | Seeded hardware dataset, DLU fleet, source registry | PASS |
| 2 | Hardware fidelity, Physical/Logical views, MML core, maintenance | PASS |
| 3 | CPT resolution, call routing, PDC 120, blacklist, atomicity | PASS |
| 4 | Command files, lifecycle, scheduling, virtual clock | PASS |
| 5 | OSI/TCP-UDP, analog/pulse/digital/BER labs | PASS |
| 6 | Six formal teaching scenarios and PASS/FAIL workbench | PASS |
| 7 | Backup/restore, initial packaging and release smoke test | PASS |
| 8 | UX/UI redesign v2 | PASS |
| 9 | Student-centered navigation | PASS |
| 10 | Hardware UX 2.0 | PASS |
| 11 | OMT/MML UX 2.0 | PASS |
| 12 | Call/network visualization | PASS |
| 13 | Communications Lab 2.0 | PASS |
| 14 | Teaching Scenarios 2.0 | PASS |
| 15 | Academic Learning Layer | PASS |
| 16 | Instructor / Classroom Mode | PASS |
| 17 | Accessibility & Usability Audit | PASS |
| 18 | Performance & Architecture Cleanup | PASS |
| 19 | Final Academic UX Audit | PASS |
| 20 | Final DLU Lab 2.0 release gate | PASS — Windows release verified |

## Existing Stage 19 evidence carried into the final release

- Stage 19 focused audit: 4/4 PASS.
- Stage 17 accessibility compatibility: 5/5 PASS.
- Stage 18 architecture compatibility: 5/5 PASS.
- Stage 19 full regression: 143/143 PASS.
- Windows Academic UX QA: PASS.
- DLU CI: PASS.

## Stage 20 final release evidence

Workflow 45790237917 on release tree 21a2ca410b68abdcc78752066d2c75e0497dca80 verified:
- compile: PASS;
- UI static audit: PASS;
- Stage 20 focused: 4/4 PASS;
- Stage 19 compatibility: 4/4 PASS;
- Stage 17 accessibility compatibility: 5/5 PASS;
- Stage 18 architecture compatibility: 5/5 PASS;
- full regression: 148/148 PASS;
- final visual/accessibility QA: PASS;
- Windows onefile package: PASS;
- packaged version: DLU Lab 2.0.0;
- packaged smoke-test: PASS;
- screenshots: 14 PNGs;
- Windows package artifact ID: 15103962398;
- screenshot artifact ID: 15102814267.

Commit 147ea8e66416f7f45164c63d363a1eeb52c8d4d1 was a workflow-trigger-only change after the verified application/package tree; no application/runtime/package source changed.

## Hardware academic integrity

The release does not alter the course-backed physical dataset.

Authoritative seeded placements remain:

- DLU 50 / Shelf 0 / Module 15 → SLMA8.
- DLU 10 / Shelf 1 / Module 7 → CMRL.

Unknown physical placement remains UNCONFIGURED.

## Academic conclusion

The simulator is complete through Stage 20 and the DLU Lab 2.0.0 Windows release gate is green. The release preserves the source-backed hardware boundary and the existing MML, CallEngine, Communications, Command Files, Teaching Scenario and database semantics.
