# Stage 16 — Instructor / Classroom Mode Closeout

**Status:** COMPLETE — merged to main after CI / Windows QA

## Delivered

Instructor can:

- reset the teaching environment;
- load any of the six existing Teaching Scenarios;
- control answer visibility;
- compare expected vs actual;
- demonstrate a real scenario progressively;
- switch to a projector-friendly layout.

## Verification

- Stage 16 focused tests: **7/7 passed**;
- compile check: PASS;
- UI static audit: PASS;
- full regression: **129 passed**;
- Windows functional visual QA: PASS;
- five screenshots uploaded as `DLU-Stage16-Instructor-Classroom-QA`;
- DLU CI and Stage 16 QA gates passed before merge.

## Scope safety

- no MML semantic changes;
- no CallEngine semantic changes;
- no TeachingScenarioRunner semantic changes;
- no database migration;
- no new runtime dependency;
- no duplicate Telecom or scenario rules;
- existing domain engines remain the source of truth.

## Implementation

- `dlu_app/stage16_ui.py`
- `tests/test_stage16_instructor_classroom.py`
- `tools/stage16_instructor_qa.py`
- `.github/workflows/stage16-instructor-qa.yml`

## Final merge

Merge commit will be recorded here after PR #17 is merged.

Next planned stage: **Stage 17 — Accessibility & Usability Audit**.
