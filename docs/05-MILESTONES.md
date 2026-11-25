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

**الحالة: Stage 13 مكتملة — Stage 14 قيد التنفيذ — Stage 15→20 مخططة**

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

**الحالة: مكتملة — 85/85 tests passed — Windows Stage 9 functional/visual QA passed — Windows release smoke-test passed**

المخرجات:
- Learning Home entry surface.
- Continue Learning with session-aware recommendation.
- live current-context ribbon.
- session progress across six learning areas.
- recent activity.
- live hardware/resource status.
- six Quick Start actions.
- progressive disclosure between Home and technical workspaces.
- preserved Stage 8 tab ordering and Morning/Night theme behavior.
- Stage 9 navigation regression coverage and target-resolution screenshots.

QA:
docs/52-STAGE-09-NAVIGATION-QA.md

Closeout:
docs/53-STAGE-09-CLOSEOUT.md

## Stage 10 — Hardware UX 2.0

**الحالة: مكتملة — 90/90 tests passed — Windows Hardware UX QA passed — main CI + Windows release smoke-test passed**

المخرجات:
- persistent Hardware Inspector beside the hardware canvas;
- Exchange → DLU → Side/Controller → Shelf → Module → Port → Subscriber context;
- hover inspection without opening dialogs;
- selection and hover highlighting;
- explicit state, EQN, capacity, role/family and subscriber context;
- maintenance/fault state presentation;
- theme synchronization with Morning/Night;
- presentation-only hit targets without database or renderer-domain changes;
- no database migration and no duplicate MML/domain logic.

Plan:
docs/54-STAGE-10-HARDWARE-UX-2.0-PLAN.md

Implementation:
docs/55-STAGE-10-IMPLEMENTATION-REPORT.md

Windows QA:
docs/56-STAGE-10-WINDOWS-QA.md

Closeout:
docs/57-STAGE-10-CLOSEOUT.md

## Stage 11 — OMT/MML UX 2.0

**الحالة: مكتملة — full pytest + Windows OMT/MML QA passed**

المخرجات:
- command editor with live syntax-shape feedback;
- visible history with USE/COPY/CLEAR;
- command explanation and target hint;
- execution result + linked DLU/module/EQN pairing;
- preserved Quick Run and Up/Down workflow;
- Morning/Night synchronization;
- presentation-only layer with the existing MML engine as the sole executor.

Plan:
docs/58-STAGE-11-PLAN.md

Implementation:
docs/59-STAGE-11-IMPLEMENTATION-REPORT.md

Windows QA:
docs/60-STAGE-11-WINDOWS-QA.md

Closeout:
docs/61-STAGE-11-CLOSEOUT.md

## Stage 12 — Call & Network Visualization

**الحالة: مكتملة — 7/7 Stage 12 tests passed — full regression passed — Windows visual QA passed — merged to main**

المخرجات:
- readable call-flow visualization.
- REQUEST / ROUTING / RESOURCE / CONNECTED / BLOCKED / RELEASED states.
- resource reservation/release presentation.
- route and CPT explanation.
- EVAL=NO blocked-call explanation.
- PDC-full blocking explanation.
- controlled deterministic signal-flow animation.
- Morning/Night synchronization.
- preserved CallEngine/MML semantics with no database migration or runtime dependency.

Closeout:
docs/65-STAGE-12-CLOSEOUT.md

## Stage 13 — Communications Lab 2.0

**الحالة: COMPLETE — merged to main after CI / Windows QA**

- Concept → Parameters → Experiment → Visualization → Measurement → Explanation → Challenge.
- improved waveform/constellation readability.
- Live Update, measurement cards, deterministic mini challenges, Morning/Night sync.
- Stage 13 focused tests 6/6 passed; full regression and Windows visual QA passed.
- Final merge: `7a75926824f7abe6a15d35f9ec374ccff658fb87`.

Next planned stage: **Stage 14 — Teaching Scenarios 2.0**.

Plan: docs/66-STAGE-13-PLAN.md
Implementation: docs/67-STAGE-13-IMPLEMENTATION-REPORT.md
Windows QA: docs/68-STAGE-13-WINDOWS-QA.md
Closeout: docs/69-STAGE-13-CLOSEOUT.md

## Stage 14 — Teaching Scenarios 2.0

**الحالة: قيد التنفيذ — guided teaching studio implemented; final CI/Windows gate pending**

- Objective → Observe → Execute → Diagnose → Fix → Verify → Result.
- progress and explicit current phase.
- hints.
- mistake explanations.
- expected vs actual.
- clear PASS/FAIL.
- scenario-specific recovery guidance.

Plan:
docs/70-STAGE-14-PLAN.md

Implementation:
docs/71-STAGE-14-IMPLEMENTATION-REPORT.md

Windows QA:
docs/72-STAGE-14-WINDOWS-QA.md

Closeout:
docs/73-STAGE-14-CLOSEOUT.md

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
