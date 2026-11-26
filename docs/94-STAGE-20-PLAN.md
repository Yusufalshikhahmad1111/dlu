# Stage 20 — DLU Lab 2.0 Release Plan

**Status:** COMPLETE

## Objective

Close the DLU Lab roadmap by converting the completed Stage 19 product into a fully synchronized 2.0.0 Windows release.

## Required gates

1. Full automated regression.
2. Compile and UI static audit.
3. Accessibility compatibility.
4. Full target-resolution visual QA:
   - 1280×720
   - 1366×768
   - 1600×900
   - 1920×1080
5. Student workflow smoke coverage across Hardware, OMT/MML, Command Files, Calls, Communications and Scenarios.
6. Instructor hidden-answer and projector-path verification.
7. Windows onefile packaging.
8. Packaged version and smoke-test checks.
9. Screenshot artifact.
10. User manual, academic guide and instructor guide synchronized to 2.0.0.
11. Stage 0→20 milestone consistency.
12. Final closeout with all evidence.

## Release rules

- The version is 2.0.0.
- The existing MML, CallEngine, Communications, Teaching Scenario and database behavior remain authoritative.
- No new telecom facts, hardware capacities or placements are introduced.
- The packaged build must come from the same code tree that passed the automated gates.
- A historical stage document may retain its point-in-time version/count; current release documentation must use 2.0.0.

## Execution

Implement → Tests → Visual QA → Packaging → Documentation → Closeout.


## Final evidence

Workflow 45790237917 completed successfully on Windows:
- 148/148 full regression;
- 4/4 Stage 20 focused;
- 4/4 Stage 19 compatibility;
- 5/5 Stage 17 accessibility compatibility;
- 5/5 Stage 18 architecture compatibility;
- compile and UI static audit PASS;
- final visual/accessibility QA PASS at 1280x720, 1366x768, 1600x900 and 1920x1080;
- Windows onefile package PASS;
- packaged version check returned DLU Lab 2.0.0;
- packaged smoke-test PASS;
- 14 screenshots uploaded.

The verified release tree for that gate was 21a2ca410b68abdcc78752066d2c75e0497dca80. The later branch commit 147ea8e66416f7f45164c63d363a1eeb52c8d4d1 changes only the workflow trigger configuration; no application/runtime/package source changed.
