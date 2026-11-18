# 05 — Milestones

## Stage 0 — Foundation & Specification

**الحالة: مكتملة**

ثبتنا:
- Python + PySide6 + SQLite.
- المعمارية.
- قاعدة عدم اختراع العتاد.
- Hardware Reference Basis.
- Database specification.
- MML specification.
- UI wireframe.
- Academic tests.

## Stage 1 — Hardware Dataset + SQLite + First Runnable GUI

**الحالة: Prototype runnable implemented**

المخرجات:
- Python/PySide6 project skeleton.
- SQLite schema/migrations.
- hardware dataset.
- ALE1.
- DLU 10 / 50.
- shelves 0..7.
- module positions 0..15 حيث يدعمها المرجع.
- card types مع capacity صريحة.
- subscriber seed.
- CPT seed.
- event log.

## Stage 2 — Hardware Fidelity + MML Core

**الحالة: مكتملة — automated regression + prior Windows QA passed**

المخرجات:
- Hardware Dataset + source registry.
- DLU frame/shelf/module/port renderer.
- Physical + Logical modes.
- Source viewer.
- Card install/replace workflow.
- OMT ↔ hardware highlighting.
- Lexer/parser/normalizer/validator/dispatcher.
- cr/can/mod/disp/stat/test/conf/diag.

## Stage 3 — Call Engine + CPT + Call Path

**الحالة: مكتملة — Windows manual QA passed**

المخرجات:
- deterministic CPT exact/prefix/range resolver.
- LOCAL / NATIONAL / INTERNATIONAL / SERVICE classification.
- persistent call sessions and call legs.
- PDC voice resource capacity 120 with reservation/release.
- LOCAL, NATIONAL, INTERNATIONAL call paths.
- EVAL=NO blocking before resource reservation.
- CALL ENGINE · CPT · CALL PATH teaching tab.
- OMT TEST/STAT/DISP CALL integration.

Closeout:
docs/16-STAGE-03-CLOSEOUT.md

## Stage 3.5 — Next-Generation UX/UI + Hardware Visual Redesign

**الحالة: مكتملة — Windows visual QA/hardening passed**

المخرجات:
- Space telecommunications visual system.
- permanent OMT command dock.
- simplified navigation.
- DLU fleet rack-card visuals.
- DLU chassis / Shelf / Module / Port visuals.
- redesigned Logical signal map.
- redesigned Call Path visual treatment.
- shared theme and font safety hardening.

QA:
docs/19-STAGE-03_5-WINDOWS-QA.md

## Stage 4 — Command Files

**الحالة: مكتملة — Windows manual QA passed**

المخرجات:
- command-file parser.
- persistent lifecycle: Accepted / Started / Finished / Executed / Failed.
- fail-fast execution logging.
- HH:MM scheduling.
- deterministic virtual clock.
- due-file execution through MML.
- OMT EXECMDFILE integration.
- Command Files teaching workbench.
- automated Stage 4 tests.

QA:
docs/22-STAGE-04-WINDOWS-QA.md

Report:
docs/21-STAGE-04-IMPLEMENTATION-REPORT.md

## Stage 5 — Communications Labs

**الحالة: مكتملة — automated release verified**

المخرجات:
- OSI 7-layer teaching view.
- TCP vs UDP comparison.
- AM / FM / PM waveform lab.
- PAM / PWM / PPM / PCM pulse lab.
- ASK / FSK / PSK / QPSK / 16-QAM waveform lab.
- QPSK / 16-QAM constellation visualizer.
- BPSK / QPSK / 16-QAM theoretical + deterministic empirical BER basics.
- Communications Lab UI.
- pure Python domain core with no new runtime dependency.
- UI smoke coverage.
- synchronized package/build metadata.

Plan:
docs/23-STAGE-05-COMMUNICATIONS-LABS-PLAN.md

Report:
docs/24-STAGE-05-IMPLEMENTATION-REPORT.md

QA:
docs/25-STAGE-05-WINDOWS-QA.md

Closeout:
docs/26-STAGE-05-CLOSEOUT.md

## Stage 6 — Teaching Scenarios

**الحالة: مكتملة — automated Windows release gate passed**

المخرجات:
- formal deterministic Teaching Scenario model;
- Aleppo 8-line expansion;
- CMRL capacity limit;
- DLU/card maintenance;
- Billing block;
- International blacklist;
- Command File overnight run;
- unified commands/actions + affected EQN + expected/actual + PASS/FAIL workbench;
- automated scenario + UI smoke coverage.

Plan:
docs/27-STAGE-06-TEACHING-SCENARIOS-PLAN.md

Report:
docs/28-STAGE-06-IMPLEMENTATION-REPORT.md

QA:
docs/29-STAGE-06-WINDOWS-QA.md

Closeout:
docs/30-STAGE-06-CLOSEOUT.md


## Stage 7 — Packaging & Final Audit

- Windows executable.
- optional installer.
- reset/backup/restore.
- screenshots.
- user manual.
- final academic test report.

## قاعدة التنفيذ

Implement → Tests → Manual Demo → Fix → Report → Commit

ولا ننتقل للمرحلة التالية قبل إثبات السابقة.
