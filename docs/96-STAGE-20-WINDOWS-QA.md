# Stage 20 — Windows Release QA

**Status:** PASS

## Required evidence

| Gate | Result |
| --- | --- |
| Release version 2.0.0 | **PASS** |
| Compile | **PASS** |
| UI static audit | **PASS** |
| Stage 20 focused | **4/4 PASS** |
| Stage 19 compatibility | **4/4 PASS** |
| Stage 17 accessibility compatibility | **5/5 PASS** |
| Stage 18 architecture compatibility | **5/5 PASS** |
| Full regression | **148/148 PASS** |
| Final visual/accessibility QA | **PASS** |
| Windows onefile package | **PASS** |
| Packaged version check | **PASS — DLU Lab 2.0.0** |
| Packaged smoke-test | **PASS** |
| Screenshot artifact | **PASS — 14 PNGs** |

## Target resolutions

The final runner exercises:

- 1280×720
- 1366×768
- 1600×900
- 1920×1080

## Final application surfaces

- Learning Home
- Hardware
- OMT/MML
- Call Path
- Command Files
- Communications
- Scenarios
- Instructor hidden-answer path
- Instructor revealed/projector Night path

## Evidence policy

This file is finalized only after the Stage 20 Windows workflow completes successfully. No package, test count or artifact ID is considered proven before that run.


## Final evidence

- Workflow: 45790237917
- Verified release tree: 21a2ca410b68abdcc78752066d2c75e0497dca80
- Windows package artifact: DLU-Lab-2.0.0-Windows
  - Artifact ID: 15103962398
  - Size: 28,288,215 bytes
  - SHA-256: 1af1b3f171843e25626c72416d5218088f94f31a92f372362867a4cdf05e11be
- Screenshot artifact: DLU-Lab-2.0.0-Screenshots
  - Artifact ID: 15102814267
  - 14 PNGs
  - Size: 605,635 bytes
  - SHA-256: 93a04f77007ca6c888461b4bbeb118ecdc2735880eef9d3b115f7aed497fa95e
- Target resolutions: 1280x720, 1366x768, 1600x900, 1920x1080
- Final QA covered the full student surface plus Instructor hidden-answer/reveal/projector Night path.

The only commit after the verified application/package tree is 147ea8e66416f7f45164c63d363a1eeb52c8d4d1, which changes the Stage 20 workflow trigger configuration only.
