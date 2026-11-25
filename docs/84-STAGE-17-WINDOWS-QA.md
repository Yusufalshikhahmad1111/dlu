# Stage 17 — Windows Accessibility & Resolution QA

**Status:** PASS — Windows QA evidence captured in Stage 17 workflow run #17

## Target resolutions

The Stage 17 runner validates:

- 1280×720;
- 1366×768;
- 1600×900;
- 1920×1080.

It also captures an Instructor/Classroom Night-mode view at 1366×768 and a projector-mode screenshot.

## Functional coverage

- primary controls expose accessible names;
- keyboard focus can move through the main hardware path;
- Instructor controls expose a deterministic keyboard path;
- tooltips exist for ambiguous actions;
- Hardware details exposes an explicit empty state;
- Morning/Night focus styling is reapplied;
- low-resolution minimum size is no longer blocked at 1250×760;
- Stage 16 answer visibility remains enforced.

## Manual Windows gate

The CI runner is the authoritative Windows gate. Completion is recorded only after the Stage 17 GitHub Actions workflow passes compilation, static audit, focused tests, Stage 16 compatibility tests, full regression, screenshot QA and artifact upload.


## Recorded evidence

- Stage 17 focused tests: **5 passed**.
- Stage 16 compatibility tests: **7 passed**.
- Full regression: **134 passed in 1207.75s**.
- Compile check: **PASS**.
- UI static audit: **PASS**.
- Windows accessibility and resolution QA: **PASS**.
- Screenshot artifact: `DLU-Stage17-Accessibility-Usability-QA`.
- Artifact ID: `15042320814`.
- Artifact SHA-256: `65ffcbf2993ad7d51d45f2ed12e97b0da1b226266b53f2fbadfcb645c927c5d6`.
- Target resolution coverage: 1280×720, 1366×768, 1600×900, 1920×1080.
- Instructor Night-mode and projector screenshots were also captured.
