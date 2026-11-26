# Stage 20 — DLU Lab 2.0 Release Implementation Report

**Status:** IN PROGRESS

## Delivered so far

### Release identity

- dlu_app.__version__ is now 2.0.0.
- pyproject.toml package metadata is now 2.0.0.
- Release regression tests now require 2.0.0.

### Final release QA

Added:

- tests/test_stage20_release.py
- tools/stage20_release_qa.py
- .github/workflows/stage20-release.yml

The new release gate combines compatibility checks from Stages 17–19, full regression, target-resolution visual coverage, instructor/projector verification, and packaged-version verification.

### Documentation

Added:

- docs/94-DLU-LAB-2.0-ACADEMIC-GUIDE.md
- docs/95-DLU-LAB-2.0-INSTRUCTOR-GUIDE.md

The user manual is updated to the 2.0.0 release.

## Domain boundary

Stage 20 does not introduce new telecom semantics. The release consumes the already-verified simulator and its existing learning/instructor layers.
