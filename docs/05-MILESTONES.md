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
السيناريوهات الأكاديمية الأساسية تعمل بدون UI.

## Stage 3 — DLU Visualizer

المخرجات:
- DLU overview.
- Shelf view.
- Module/Card view.
- Port 0..N حسب card type.
- subscriber ↔ EQN view.
- LEDs/state indicators.
- click drill-down.

Definition of Done:
الطالب يرى العلاقة DLU → Shelf → Module → Port → DN بوضوح.

## Stage 4 — OMT + SYP

- terminal.
- raw/structured output.
- command history.
- macros.
- alarms.
- traffic indicators.

## Stage 5 — Hardware Operations

- mbl/act.
- DLUC behavior.
- diag guards.
- card replacement.
- maintenance workflow.

## Stage 6 — Call Engine + CPT

- local route.
- national route.
- international route.
- blocked route.
- channel usage.
- call path animation.

## Stage 7 — Command Files

- file parser.
- scheduling.
- virtual clock.
- Accepted/Started/Finished/Executed.
- failure reporting.

## Stage 8 — Communications Labs

- OSI.
- TCP/UDP.
- AM/FM/PM.
- PAM/PWM/PPM/PCM.
- ASK/FSK/PSK/QPSK/QAM.
- constellation/BER basics.

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
