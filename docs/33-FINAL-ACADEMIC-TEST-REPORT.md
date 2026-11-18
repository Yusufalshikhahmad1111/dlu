# Final Academic Test Report — DLU Lab 1.0.0

Date: 2026-11-18

## Executive result

DLU Lab 1.0.0 passed the final automated Windows release gate. The complete suite executed on the Windows runner with **76 passed tests**.

## Final verification matrix

| Stage | Academic / Engineering scope | Final result |
| --- | --- | --- |
| 0 | Architecture, source-backed hardware rule, SQLite foundation | PASS |
| 1 | Seeded hardware dataset, DLU fleet, source registry | PASS |
| 2 | Hardware fidelity, Physical/Logical views, MML core, maintenance | PASS |
| 3 | CPT resolution, call routing, PDC 120, blacklist, atomicity | PASS |
| 4 | Command files, lifecycle, scheduling, virtual clock | PASS |
| 5 | OSI/TCP-UDP, analog/pulse/digital/BER labs | PASS |
| 6 | Six formal teaching scenarios and PASS/FAIL workbench | PASS |
| 7 | Backup/restore, packaging, screenshots, release smoke test | PASS |

## Automated release evidence

- Windows Python compilation: PASS.
- UI static audit: PASS.
- Full pytest suite: **76 passed**.
- Windows onefile deployment: PASS.
- Packaged executable smoke test: PASS.
- Windows executable artifact uploaded: PASS.
- Final UI screenshot artifact uploaded: PASS.

Release artifacts:
- `DLU-Lab-Windows` — Windows executable artifact, approximately 27.9 MB.
- `DLU-Lab-Screenshots` — five final UI PNG screenshots, approximately 309 KB total.

## Hardware academic integrity

The final package does not alter the course-backed physical dataset.

Authoritative seeded placements remain:
- DLU 50 / Shelf 0 / Module 15 → SLMA8.
- DLU 10 / Shelf 1 / Module 7 → CMRL.

Unknown physical placement remains UNCONFIGURED.

## Critical call-engine verification

Stage 3 regression confirms:
- deterministic exact/prefix/range CPT matching;
- LOCAL / NATIONAL / INTERNATIONAL routing;
- EVAL=NO blocking before PDC reservation;
- PDC capacity of 120;
- resource release;
- busy subscriber guard;
- atomic rollback after internal persistence failure;
- structured invalid-number errors.

## Command-file verification

Stage 4 regression confirms:
- source-line preservation;
- malformed-file rejection;
- nested EXECMDFILE rejection;
- Accepted → Started → Finished → Executed/Failed lifecycle;
- HH:MM validation;
- midnight rollover;
- no duplicate scheduled execution;
- scheduled_at cleanup.

## Stage 6 teaching verification

All six formal scenarios are covered:
- Aleppo 8-Line Expansion;
- CMRL Capacity Limit;
- DLU / Card Maintenance;
- Billing Block;
- International Blacklist;
- Command File Overnight Run.

## Stage 7 data-safety verification

Backup/restore coverage confirms:
- SQLite backup API is used instead of raw file copying for live backup;
- integrity check validates every backup;
- required schema tables are checked;
- restore is staged safely;
- automatic pre-restore safety backup is created;
- restore is applied only on a clean application restart.

## Manual boundary

The final release was validated on GitHub's Windows runner, including automated GUI construction and screenshot capture. A separate physical hands-on session on the developer's own Windows machine was not performed during this closeout, so no unsupported claim is made about a local monitor/driver-specific visual result.

## Academic conclusion

**The simulator is release-ready for the next packaging/distribution step and for course use as a local educational lab, subject to normal classroom machine verification.**