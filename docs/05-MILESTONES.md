# 05 — Milestones

## Stage 0 — Foundation & Specification

**الحالة: مكتملة في هذه الخطوة**

المخرجات:
- tech decision.
- architecture.
- database specification.
- MML specification.
- UI wireframe.
- academic tests.

Definition of Done:
- لا يوجد قرار معماري أساسي غامض.
- يمكن بدء البرمجة دون تغيير نموذج البيانات كل يوم.

## Stage 1 — SQLite + Seed Dataset

المخرجات:
- Tauri + React project.
- SQLite connection.
- migrations/schema.
- repositories.
- ALE1.
- DLU 10 / 50.
- shelves/slots/cards.
- CPT seed.
- event log.

Tests:
- EQN uniqueness.
- card capacity.
- seed integrity.
- transaction rollback.

## Stage 2 — MML Core

المخرجات:
- Lexer.
- Parser.
- Normalizer.
- Validator.
- Dispatcher.
- cr/can/mod/disp/stat/test/conf/diag.

Definition of Done:
- السيناريوهات الأساسية الأربعة تعمل عبر tests بدون UI.

## Stage 3 — DLU Visualizer

المخرجات:
- DLU overview.
- Side 0/1.
- Shelf 0–7.
- Slot 0–15.
- card rendering.
- port LEDs.
- click drill-down.

Definition of Done:
- أي تغيير في DB يظهر في الواجهة دون refresh كامل.

## Stage 4 — OMT + SYP

المخرجات:
- terminal.
- raw/structured output.
- command history.
- macros.
- alarms.
- traffic counter.

## Stage 5 — Hardware Operations

المخرجات:
- mbl/act.
- DLUC failover.
- diag guards.
- card replacement.
- maintenance workflow.

## Stage 6 — Call Engine + CPT

المخرجات:
- local route.
- national route.
- international route.
- blocked route.
- 120-channel traffic indicator.
- call animation.

## Stage 7 — Command Files

المخرجات:
- file parser.
- scheduling.
- virtual clock.
- Accepted/Started/Finished/Executed.
- failure reporting.

## Stage 8 — Communications Labs

المخرجات:
- OSI encapsulation.
- TCP three-way handshake.
- UDP comparison.
- AM/FM/PM.
- PAM/PWM/PPM/PCM.
- ASK/FSK/PSK/QPSK/QAM.
- constellation/BER basics.

## Stage 9 — Scenarios & Teaching UX

Macros جاهزة:
1. Aleppo 8-line expansion.
2. CMRL six-port limit.
3. DLU/card maintenance.
4. Billing block.
5. International blacklist.
6. Command file overnight run.

كل macro:
- preview commands.
- execute.
- show affected objects.
- show result summary.

## Stage 10 — Packaging & Final Audit

المخرجات:
- Windows installer.
- portable/demo build if useful.
- seed reset.
- backup/import.
- screenshots.
- user manual.
- final test report.

## قاعدة التنفيذ

كل Stage لها:
Implement → Tests → Manual Demo → Fix → Report → Commit

ولا نبدأ Stage التالي قبل أن يكون الحالي قابلًا للعرض.
