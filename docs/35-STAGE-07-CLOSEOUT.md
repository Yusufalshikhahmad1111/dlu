# Stage 7 — Packaging & Final Audit Closeout

Date: 2026-11-18

## Status

**Stage 7 is complete and release-ready.**

## Delivered

- Release version 1.0.0.
- Windows onefile executable build through Qt for Python `pyside6-deploy`.
- Reproducible Windows build script: `tools/build_windows.ps1`.
- CI release workflow: `.github/workflows/stage7-release.yml`.
- Executable smoke test through `--smoke-test`.
- Safe SQLite backup/restore service.
- Restore-on-restart flow with automatic pre-restore backup.
- Confirmed demo reset operation.
- Final screenshot automation.
- User manual.
- Final academic test report.
- Stage 7 Windows QA checklist.

## Final Windows release evidence

Final release workflow run: **#14**.

Final release gate:
- Windows build: PASS.
- Executable smoke test: PASS.
- `DLU-Lab-Windows` artifact uploaded successfully.
- `DLU-Lab-Screenshots` artifact uploaded successfully.

Final regression workflow on the release branch:
- compile: PASS;
- UI static audit: PASS;
- **76 tests passed**.

## Build engineering lessons closed during Stage 7

Three real release issues were discovered and fixed:

1. `QDesktopServices` was imported from the wrong Qt module; Windows CI caught it before release.
2. The screenshot runner passed `Path` objects to `QPixmap.save`; Windows PySide6 requires a string filename. Cleanup was also hardened so the SQLite file is closed even on screenshot failure.
3. `pyside6-deploy` required an explicit automated download approval for Dependency Walker, and its output directory needed to exist after deployment initialization. Both were handled in the reproducible build gate.

Qt's current documentation confirms `pyside6-deploy` is the Qt for Python desktop deployment tool and supports Windows `.exe` output with explicit `onefile`/`standalone` modes. citeturn322529search0
Nuitka's current documentation/API exposes `--assume-yes-for-downloads`, and its Windows standalone flow uses Dependency Walker for DLL dependency discovery. citeturn415968search0turn415968search20

## Release artifacts

- `DLU-Lab-Windows` artifact: approximately 27.9 MB.
- `DLU-Lab-Screenshots` artifact: approximately 309 KB, containing five PNG captures.

## Manual boundary

The final automated release gate executes on Windows and includes GUI construction, screenshot generation and packaged executable smoke testing. A separate hands-on local Windows session by the developer was not performed during this closeout.

## Final roadmap

Stage 0 → Stage 7 are complete.

Any future work is now post-release enhancement, not an unfinished milestone.