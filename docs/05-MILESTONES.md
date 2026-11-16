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

المنفذ حاليًا: قاعدة البيانات + نواة MML الأساسية + أول واجهة DLU/OMT قابلة للتشغيل.

اختبارات:
- EQN uniqueness.
- shelf/module range.
- card capacity.
- port range.
- DN uniqueness.
- seed integrity.
- transaction rollback.

**ممنوع في هذه المرحلة:** رسم DLU النهائي قبل إثبات صحة dataset.

## Stage 2 — Hardware Fidelity + MML Core

**الحالة: Code-complete — final Windows manual audit is the release gate**

المخرجات:
- Hardware Dataset + source registry.
- DLU frame/shelf/module/port renderer.
- Physical + Logical modes.
- Source viewer.
- Card install/replace workflow.
- OMT ↔ hardware highlighting.
- Lexer.
- Parser.
- Normalizer.
- Validator.
- Dispatcher.
- cr/can/mod/disp/stat/test/conf/diag.

Definition of Done:
Hardware hierarchy + source-backed cards + Physical/Logical modes + maintenance replacement + OMT hardware linking are implemented.

## Stage 3 — Call Engine + CPT + Call Path

**الحالة: مكتملة — Windows manual QA passed**

المخرجات:
- deterministic CPT exact/prefix/range resolver.
- number analysis.
- LOCAL / NATIONAL / INTERNATIONAL / SERVICE call classification.
- persistent call sessions and call legs.
- PDC voice resource capacity 120 with reservation/release.
- LOCAL path: DLU → SN → DLU.
- NATIONAL path: DLU → LTG → SN → LTG → logical remote DLU/LAC.
- INTERNATIONAL path: DLU → LTG → SN → International Gateway.
- EVAL=NO blocking before resource reservation.
- CALL ENGINE · CPT · CALL PATH teaching tab.
- OMT TEST/STAT/DISP CALL integration.
- Stage 3 automated tests.
- Final Windows manual runtime verification.

Definition of Done:
Call decisions, resource state, subscriber busy state, DB session state, and visual Call Path agree.

Closeout:
docs/16-STAGE-03-CLOSEOUT.md

## Stage 3.5 — Next-Generation UX/UI + Hardware Visual Redesign

**الحالة: Implemented — Windows visual QA is the release gate**

المخرجات:
- Space telecommunications visual system.
- permanent OMT command dock.
- simplified navigation and secondary Tools menu.
- redesigned teaching action hierarchy.
- DLU fleet rack-card visuals.
- DLU chassis / Shelf equipment bay / Module faceplate / Port connector visuals.
- redesigned Logical signal map.
- redesigned Call Path visual treatment.
- no intentional change to Stage 1–3 domain behavior.

Definition of Done:
Visual hierarchy, readability, hardware representation, MML visibility, and classroom usability are improved without breaking existing functionality.

QA checklist:
docs/19-STAGE-03_5-WINDOWS-QA.md

Implementation report:
docs/18-STAGE-03_5-UX-UI-IMPLEMENTATION.md

## Stage 4 — Command Files

**الحالة: Implemented — Windows manual QA is the release gate**

المخرجات:
- command-file parser.
- persistent command file records.
- Accepted / Started / Finished / Executed / Failed lifecycle.
- fail-fast execution logging.
- HH:MM scheduling.
- deterministic virtual clock.
- due-file execution through MML.
- OMT EXECMDFILE integration.
- Command Files teaching workbench.
- automated Stage 4 tests.

Definition of Done:
Command files use the existing MML engine, persist their lifecycle/log, execute deterministically, and scheduled files run when the virtual clock reaches their target time.

QA:
docs/22-STAGE-04-WINDOWS-QA.md

Report:
docs/21-STAGE-04-IMPLEMENTATION-REPORT.md

## Stage 5 — Communications Labs

- OSI.
- TCP/UDP.
- AM/FM/PM.
- PAM/PWM/PPM/PCM.
- ASK/FSK/PSK/QPSK/QAM.
- constellation/BER basics.

## Stage 6 — Teaching Scenarios

- Aleppo 8-line expansion.
- CMRL capacity limit.
- DLU/card maintenance.
- Billing block.
- International blacklist.
- Command file overnight run.

كل Scenario يعرض:
- commands.
- affected EQN.
- expected result.
- actual result.
- PASS/FAIL.

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
