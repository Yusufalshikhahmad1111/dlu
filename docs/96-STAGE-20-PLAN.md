# Stage 20 — DLU Lab 2.0 Release Plan

**Status:** COMPLETE

## Objective

Turn the completed Stage 0→19 product into the final DLU Lab 2.0.0 release candidate and verify that implementation, documentation, packaging, and roadmap state are synchronized.

## Required gates

1. Full regression.
2. Stage 17 accessibility compatibility.
3. Stage 18 architecture compatibility.
4. Stage 19 academic workflow compatibility.
5. Target-resolution visual QA at 1280×720, 1366×768, 1600×900, and 1920×1080.
6. Morning/Night and instructor/projector evidence.
7. Windows onefile packaging.
8. Packaged executable --smoke-test.
9. Packaged executable --version reports DLU Lab 2.0.0.
10. Updated user manual, academic guide, and instructor guide.
11. Stage 20 evidence and final closeout.
12. Stage 0→20 roadmap synchronization.

## Release identity

- Application: DLU Lab
- Release: 2.0.0
- Platform: Windows 11
- Python: 3.12
- GUI: PySide6
- Packaging: pyside6-deploy onefile

## Safety

No new telecom domain rules, database migrations, alternate MML parser, alternate call engine, or communications/scenario semantics are introduced by Stage 20.


## Final evidence

- Final merged main commit: `fe0b21b33db7239c294d82b02b5e6dc6f35e88f5`.
- Post-merge Stage 20 workflow Run #83: PASS.
- Stage 20 focused 5/5; Stage 17 5/5; Stage 18 5/5; Stage 19 4/4.
- Windows regression: 149/149 passed.
- Windows visual QA, onefile packaging, packaged smoke-test and packaged version verification: PASS.
- Main DLU CI Run #732: PASS (148 passed, 1 intentional Linux platform skip).
