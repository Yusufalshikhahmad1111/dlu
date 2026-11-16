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

**الحالة: Implemented — final Windows manual audit is the release gate**

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
- Stage 3 automated tests and Windows QA checklist.

Definition of Done:
Call decisions, resource state, subscriber busy state, DB session state, and visual Call Path agree.

## Stage 4 — Command Files

- file parser.
- scheduling.
- virtual clock.
- Accepted/Started/Finished/Executed.
- failure reporting.

## Stage 5 — Communications Labs

- OSI.
- TCP/UDP.
- AM/FM/PM.
- PAM/PWM/PPM/PCM.
- ASK/FSK/PSK/QPSK/QAM.
- constellation/BER basics.

## Stage 6 — Teaching Scenarios

1. Aleppo 8-line expansion.
2. CMRL capacity limit.
3. DLU/card maintenance.
4. Billing block.
5. International blacklist.
6. Command file overnight run.

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

## Stage 9 — Teaching Scenarios

1. Aleppo 8-line expansion.
2. CMRL capacity limit.
3. DLU/card maintenance.
4. Billing block.
5. International blacklist.
6. Command file overnight run.

كل Scenario يعرض:
- commands.
- affected EQN.
- expected result.
- actual result.
- PASS/FAIL.

## Stage 10 — Packaging & Final Audit

- Windows executable.
- optional installer.
- reset/backup/restore.
- screenshots.
- user manual.
- final academic test report.

## قاعدة التنفيذ

Implement → Tests → Manual Demo → Fix → Report → Commit

ولا ننتقل للمرحلة التالية قبل إثبات السابقة.
