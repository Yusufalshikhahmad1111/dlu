# Stage 16 — Instructor / Classroom Mode Plan

**Status:** IMPLEMENTATION

## Goal

Add a separate instructor-facing classroom workspace without changing the student workflow or duplicating simulator semantics.

## Required capabilities

- reset;
- scenario loading;
- answer visibility controls;
- expected vs actual;
- guided demonstration;
- projector-friendly layout.

## Design

Stage 16 adds an **Instructor** tab beside the existing student-facing learning and technical tabs.

The instructor view is presentation-only and reuses:
- `TeachingScenarioRunner`;
- existing ScenarioDefinition / ScenarioResult / ScenarioStepResult;
- existing `DluSimulatorWindow.reset_demo()`;
- existing Morning/Night design tokens.

No new telecom rules, scenario expectations, database tables, or runtime dependencies are introduced.

## Acceptance

1. Instructor can load any of the six existing teaching scenarios.
2. Instructor can reset the teaching demo from the instructor workspace.
3. Expected/actual answers remain hidden until explicitly revealed.
4. A real scenario execution can be demonstrated one step at a time using the existing result.
5. Projector mode removes operational clutter and enlarges the teaching summary.
6. Student Learning Home and existing technical tabs remain functionally unchanged.
7. Morning/Night styling remains available.
8. Focused tests, full regression, static audit and Windows visual QA pass.

## Execution

Implement → focused tests → full regression → Windows visual QA → fix → report → merge.
