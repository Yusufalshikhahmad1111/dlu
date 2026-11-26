# Stage 20 — DLU Lab 2.0 Release Implementation Report

**Status:** COMPLETE

## Release synchronization

- Runtime version moved to 2.0.0.
- pyproject.toml version moved to 2.0.0.
- PySide project file inventory synchronized with the current application modules.
- Windows release build now refuses non-2.0.0 builds.
- Final release QA uses dlu_app.app_shell.build_window, so the same staged application composition used by the real app is audited.

## Final QA runner

Added tools/stage20_release_qa.py.

It verifies:

- release version;
- workspace accessibility metadata;
- Learning Home;
- Hardware;
- OMT/MML;
- Call Path;
- Command Files;
- Communications;
- Scenarios with a real PASS;
- Instructor hidden-answer behavior;
- Instructor reveal behavior;
- Night projector path;
- all four target resolutions.

## Release workflow

Added .github/workflows/stage20-release.yml.

The final Windows gate runs compile, static audit, Stage 20 focused checks, Stage 19/18/17 compatibility, the complete pytest suite, final visual/accessibility QA, Windows onefile packaging and executable smoke tests.

## Documentation

Stage 20 adds:

- final academic guide;
- instructor guide;
- 2.0.0 user-manual synchronization;
- final academic release report;
- release closeout evidence.

All claims remain subject to the final Windows workflow evidence recorded in the Stage 20 QA and closeout documents.


## Final verified evidence

Workflow 45790237917 completed the integrated Windows release gate:
- 148/148 full regression;
- 4/4 Stage 20 focused;
- 4/4 Stage 19 compatibility;
- 5/5 Stage 17 compatibility;
- 5/5 Stage 18 architecture compatibility;
- compile and UI static audit PASS;
- final visual/accessibility QA PASS;
- Windows onefile build PASS;
- packaged version output: DLU Lab 2.0.0;
- packaged smoke-test PASS;
- Windows package artifact ID 15103962398;
- screenshot artifact ID 15102814267.

The verified application/package tree is 21a2ca410b68abdcc78752066d2c75e0497dca80. Later branch commit 147ea8e66416f7f45164c63d363a1eeb52c8d4d1 changes only the release-workflow trigger configuration and does not alter application/runtime/package source.
