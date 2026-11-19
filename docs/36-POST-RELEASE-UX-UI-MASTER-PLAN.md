# DLU Lab — Post-Release UX/UI Master Plan

**Status:** Planning approved  
**Baseline:** DLU Lab 1.0.0 / Stage 0→7 complete  
**Planning date:** 2026-11-19

## 1. Product direction

DLU Lab should evolve from a technically capable Siemens EWSD simulator into a **University Communications Digital Laboratory**.

The next roadmap does **not** start by adding more simulator logic. It starts by improving how the existing academic capabilities are discovered, understood, practiced, and demonstrated.

The academic chain already implemented is:

Hardware → OMT/MML → Call Path → Command Files → Communications → Scenarios

The target experience is:

Learn → Explore → Execute → Observe → Explain → Practice → Verify

## 2. Non-negotiable principles

1. **Preserve academic truth.** No invented hardware capacity, placement, command behavior, or source data.
2. **Preserve domain logic.** UX/UI work must not duplicate the MML, database, call engine, communications, or scenario engines.
3. **Context before complexity.** Advanced controls appear when they become relevant.
4. **Visual hierarchy before decoration.** Color, spacing, typography, and state must communicate meaning.
5. **One design language.** Every tab and dialog must use the same tokens and interaction rules.
6. **Student-first, instructor-ready.** The default path optimizes learning; a later instructor mode optimizes demonstrations.
7. **Desktop-first, projector-safe.** Primary targets are Windows desktop resolutions from 1280×720 through 1920×1080.
8. **Keyboard and focus are first-class.** Mouse-only interaction is not acceptable for core workflows.
9. **Explain state transitions.** PASS, FAIL, BLOCKED, MBL, FAULT, ACTIVE, BUSY, and DIAGNOSTIC must be distinguishable without relying on color alone.
10. **Stage isolation.** Every stage is implemented, tested, visually verified, documented, then closed.

## 3. Roadmap

### Stage 8 — UX/UI Reimagination
Design system, new visual identity, application shell, navigation model, theme tokens, spacing, typography, states, and first-pass visual migration.

### Stage 9 — Student-Centered Navigation
Learning home, current context, progress, continuation, recent activity, quick actions, and task-oriented navigation.

### Stage 10 — Hardware UX 2.0
Visual hardware hierarchy, interactive DLU/shelf/module/port inspection, context inspector, status visualization, EQN and capacity presentation.

### Stage 11 — OMT/MML UX 2.0
Command editor, history, syntax states, explanations, affected hardware, command-result pairing, and safer command discovery.

### Stage 12 — Call & Network Visualization
Readable call-flow visualization, resource reservation states, route explanation, blocked-call explanation, and instructor-friendly demonstration mode.

### Stage 13 — Communications Lab 2.0
Concept → controls → visualization → measurements → explanation → mini challenge workflow for each experiment.

### Stage 14 — Teaching Scenarios 2.0
Convert PASS/FAIL scenarios into guided labs with objective, observation, execution, diagnosis, fix, verification, hints, and result interpretation.

### Stage 15 — Academic Learning Layer
Connect current modules into a coherent Learn → Practice → Experiment → Challenge → Verify progression.

### Stage 16 — Instructor / Classroom Mode
Projection-friendly presentation, scenario loading, reset, answer visibility, guided demonstration, and expected-vs-actual teaching controls.

### Stage 17 — Accessibility & Usability Audit
Contrast, focus, keyboard traversal, text sizing, state communication, empty/error/loading states, discoverability, and resolution QA.

### Stage 18 — Performance & Architecture Cleanup
Gradual decomposition of the large UI module into app shell, navigation, domain views, design system, and supporting adapters without duplicating domain logic.

### Stage 19 — Final Academic UX Audit
Evaluate the product end-to-end from student and instructor perspectives against the course workflow and source-backed simulator behavior.

### Stage 20 — DLU Lab 2.0 Release
Regression, visual QA, release packaging, updated manual, academic/instructor guides, screenshots, and final closeout.

## 4. Execution rule

Every stage follows exactly:

**Implement → Tests → Visual QA → Manual Demo → Fix → Report → Commit**

No stage is considered complete from code changes alone.

## 5. Definition of success

At the end of Stage 20:

- A student can understand where they are and what to do next without being taught the UI first.
- A student can connect a visible action to the underlying EWSD/MML concept.
- A student can diagnose why an operation passed, failed, or became blocked.
- An instructor can demonstrate a lab workflow on a projector without UI clutter becoming the lesson.
- The product has one coherent visual language across all major learning surfaces.
- Existing Stage 0→7 academic and release guarantees remain green.

## 6. Source baseline

The roadmap is grounded in:

- `docs/05-MILESTONES.md`
- `DLU_AUDIT_REPORT.md`
- `docs/32-USER-MANUAL.md`
- `dlu_app/ui.py`
- `dlu_app/theme.py`
- `docs/19-STAGE-03_5-WINDOWS-QA.md`

No domain behavior is redefined by this planning document.
