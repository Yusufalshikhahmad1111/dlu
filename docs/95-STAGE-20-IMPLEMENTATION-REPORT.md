# Stage 20 — DLU Lab 2.0 Release Implementation Report

**Status:** IN PROGRESS

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
