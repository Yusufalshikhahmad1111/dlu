# Stage 7 — Packaging & Final Audit Plan

## Objective

Turn the educational simulator into a reproducible Windows release with safe local-data operations, a final academic verification record, and a repeatable visual/package gate.

## Release architecture

- Runtime: Python 3.12 + PySide6 6.12-compatible range.
- Database: SQLite under `%USERPROFILE%\\AppData\\Local\\DLULab`.
- Packaging: Qt for Python `pyside6-deploy` using the official Nuitka-backed deployment path.
- Release mode: Windows onefile `.exe`.
- Bundled academic data: `data/hardware_seed.json` and `data/references.json`.

Qt's current deployment documentation states that `pyside6-deploy` is the supported deployment tool, produces `.exe` on Windows, and supports `onefile` and `standalone` modes; the default packaging mode changed to standalone in PySide6 6.12, so this project pins onefile explicitly. citeturn322529search0

## Deliverables

1. Reproducible Windows onefile build script.
2. Windows CI release gate with executable smoke test.
3. Automated UI screenshots uploaded as build artifacts.
4. SQLite backup service with integrity validation.
5. Restore-on-restart workflow with automatic pre-restore safety backup.
6. Explicit demo reset confirmation.
7. Release version 1.0.0.
8. User manual.
9. Final academic test report.
10. Stage 7 Windows QA and closeout.

## Acceptance gate

- Python compile: PASS.
- UI static audit: PASS.
- Full pytest regression: PASS.
- Windows onefile executable produced: PASS.
- Packaged executable `--smoke-test`: PASS.
- Final screenshots generated: PASS.
- Backup/restore integrity tests: PASS.
- Stage 1–6 behavior preserved.

## Non-negotiable rule

No course hardware capacities, placements or telecom semantics are invented during packaging or final audit.