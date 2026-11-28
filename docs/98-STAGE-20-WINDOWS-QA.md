# Stage 20 — Windows Release QA

**Status:** PASS — FINAL WORKFLOW VERIFIED

## Gates

- [x] Compile.
- [x] UI static audit.
- [x] Stage 20 focused release checks.
- [x] Stage 17 accessibility compatibility.
- [x] Stage 18 architecture compatibility.
- [x] Stage 19 academic compatibility.
- [x] Full regression.
- [x] Windows Stage 20 visual QA.
- [x] Windows onefile packaging.
- [x] Packaged executable smoke test.
- [x] Packaged executable reports DLU Lab 2.0.0.
- [x] Release artifacts uploaded.

## Visual matrix

- 1280×720 Morning
- 1366×768 Morning
- 1600×900 Morning
- 1920×1080 Morning
- 1366×768 Night
- Call result
- Communications result
- Scenario PASS/FAIL
- Instructor answers hidden
- Instructor projector/revealed
- Reset clean state

## Artifacts

Expected:

- DLU-Lab-2.0.0-Windows
- DLU-Lab-2.0.0-Screenshots
- DLU-Lab-2.0.0-Build-Screenshots

The final closeout will record the actual GitHub Actions run IDs, artifact IDs/digests, regression count, and final merge commit.


## Final evidence

- Post-merge workflow: Run #83.
- Verified main commit: `fe0b21b33db7239c294d82b02b5e6dc6f35e88f5`.
- Windows regression shards: 149/149 passed.
- Visual QA: PASS.
- Onefile package: PASS.
- Packaged smoke-test: PASS.
- Packaged version: `DLU Lab 2.0.0`.

Final artifacts:
- `DLU-Lab-2.0.0-Windows` — artifact 15262455683 — sha256 `27374d314c5a6d82520c0dc147ef83c938cc4c511ca9b53321759ec467e68408`.
- `DLU-Lab-2.0.0-Screenshots` — artifact 15262455686 — sha256 `f94c7683f73cd7154e56613d2a316838ac3e3f85db58dc31f3588b4e6f9cf58c`.
- `DLU-Lab-2.0.0-Build-Screenshots` — artifact 15262580481 — sha256 `162bca3a01f94c37926170ca417966fa42345c3b44ea610aea772ccff40d5f3c`.
