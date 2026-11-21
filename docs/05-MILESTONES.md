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

**الحالة: مكتملة — Windows release gate passed**

المخرجات:
- Windows onefile executable via `pyside6-deploy`;
- automated executable smoke test;
- safe SQLite reset/backup/restore lifecycle;
- final UI screenshot artifact generation;
- user manual;
- final academic test report;
- final Windows QA and closeout.

Plan:
docs/31-STAGE-07-PACKAGING-PLAN.md

User manual:
docs/32-USER-MANUAL.md

Final academic report:
docs/33-FINAL-ACADEMIC-TEST-REPORT.md

Windows QA:
docs/34-STAGE-07-WINDOWS-QA.md

Closeout:
docs/35-STAGE-07-CLOSEOUT.md

---

# Post-Release Roadmap — Stage 8→20

**الحالة: Stage 8 مكتملة — Stage 9→20 مخططة**

الهدف: تحويل DLU Lab من simulator release-ready إلى **University Communications Digital Laboratory** مع الحفاظ على المنطق الأكاديمي وبيانات العتاد المصدرية.

## Stage 8 — UX/UI Reimagination

**الحالة: مكتملة — Rework v2 — 80/80 tests passed — Windows UX/functional QA passed**

The first blue/black visual direction was rejected and replaced by the accepted v2 direction:

- Morning: warm white + soft green;
- Night: charcoal-green + soft mint;
- shared component system and spacing;
- visible Morning/Night switch;
- stable LAB navigation;
- first-class OMT/MML workbench;
- real GUI command execution regression;
- Windows target-resolution QA.

Implementation:
docs/48-STAGE-08-REDESIGN-V2-IMPLEMENTATION.md

Windows UX QA:
docs/49-STAGE-08-REDESIGN-V2-QA.md

Closeout:
docs/50-STAGE-08-REDESIGN-V2-CLOSEOUT.md

## Stage 9 — Student-Centered Navigation

**الحالة: مخططة**

- Learning Home.
- Continue Learning.
- current context.
- progress.
- recent activity.
- quick actions.
- progressive disclosure.

## Stage 10 — Hardware UX 2.0

**الحالة: مخططة**

- Exchange → DLU → Side → Shelf → Module → Port → Subscriber hierarchy.
- context inspector.
- EQN/capacity/state presentation.
- hover/selection/maintenance visualization.

## Stage 11 — OMT/MML UX 2.0

**الحالة: مخططة**

- command editor.
- history.
- syntax feedback.
- command explanation.
- result + affected hardware pairing.
- no duplicate MML engine.

## Stage 12 — Call & Network Visualization

**الحالة: مخططة**

- readable call-flow visualization.
- resource reservation states.
- route explanation.
- blocked-call explanation.
- controlled signal-flow animation.

## Stage 13 — Communications Lab 2.0

**الحالة: مخططة**

- Concept → Parameters → Experiment → Visualization → Measurement → Explanation → Challenge.
- improved waveform/constellation readability.

## Stage 14 — Teaching Scenarios 2.0

**الحالة: مخططة**

- Objective → Observe → Execute → Diagnose → Fix → Verify → Result.
- progress.
- hints.
- mistake explanations.
- expected vs actual.

## Stage 15 — Academic Learning Layer

**الحالة: مخططة**

- Learn → Practice → Experiment → Challenge → Verify.
- coherent course progression over the existing modules.

## Stage 16 — Instructor / Classroom Mode

**الحالة: مخططة**

- reset.
- scenario loading.
- guided demonstration.
- answer visibility.
- expected vs actual.
- projector-friendly view.

## Stage 17 — Accessibility & Usability Audit

**الحالة: مخططة**

- contrast.
- focus.
- keyboard navigation.
- state communication.
- typography.
- empty/error/loading states.
- target resolution audit.

## Stage 18 — Performance & Architecture Cleanup

**الحالة: مخططة**

Target boundaries:
- app_shell.
- navigation.
- design_tokens.
- feature views.
- shared components.

The domain core remains independent.

## Stage 19 — Final Academic UX Audit

**الحالة: مخططة**

End-to-end student/instructor audit covering:
- Hardware.
- MML.
- Calls.
- Communications.
- Scenarios.

## Stage 20 — DLU Lab 2.0 Release

**الحالة: مخططة**

- full regression.
- visual/accessibility QA.
- Windows packaging.
- screenshots.
- updated manuals/guides.
- final closeout.

Master plan:
docs/36-POST-RELEASE-UX-UI-MASTER-PLAN.md

Research:
docs/37-UX-UI-RESEARCH-STUDY.md

Design System:
docs/38-DESIGN-SYSTEM-SPECIFICATION.md

UX Journeys:
docs/39-UX-JOURNEYS-AND-INFORMATION-ARCHITECTURE.md

Architecture Target:
docs/40-UX-UI-ARCHITECTURE-TARGET.md

Quality Gates:
docs/41-UX-UI-QUALITY-GATES.md

Stage 8 Prompt:
docs/42-STAGE-08-EXECUTION-PROMPT.md

Stage 9→20 Prompts:
docs/43-STAGE-09-20-EXECUTION-PROMPTS.md


## قاعدة التنفيذ

Implement → Tests → Manual Demo → Fix → Report → Commit

ولا ننتقل للمرحلة التالية قبل إثبات السابقة.
