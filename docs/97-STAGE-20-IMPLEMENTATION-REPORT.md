# Stage 20 — DLU Lab 2.0 Release Implementation Report

**Status:** COMPLETE

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


## Final verification

Stage 20 introduced no new telecom semantics. The final candidate was repaired only at the release-process/CI layer:
- packaged version verification now uses the existing deterministic `--write-version <file>` contract;
- Ubuntu CI installs the Qt runtime libraries required by UI imports;
- the Linux-only Stage 8 theme-toggle interaction is explicitly skipped because that Windows-targeted Qt style path can hang under Ubuntu; the interaction remains covered by the Windows regression matrix.

Final verification on merged main:
- merge commit: `fe0b21b33db7239c294d82b02b5e6dc6f35e88f5`;
- Stage 20 Run #83: PASS;
- Windows regression: 149/149 passed;
- packaged version: DLU Lab 2.0.0;
- Main CI Run #732: PASS, 148 passed / 1 skipped.
