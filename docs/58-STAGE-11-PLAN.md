# Stage 11 — OMT/MML UX 2.0 Plan

## Goal
Improve the teaching experience around the existing MML workbench while preserving real MML execution.

## Required outcomes
- command editor remains fast for experienced users;
- visible command history with reuse/copy;
- live syntax-shape feedback without executing commands;
- plain-language explanation of the current command;
- clear execution result and linked hardware target;
- existing MML engine remains the single source of truth.

## Constraints
- no second MML parser/engine;
- no database migration;
- no new telecom facts;
- no changes to command semantics;
- keep the existing Quick Run and Up/Down history behavior.

## Validation
Implement → automated tests → Windows functional/visual QA → documentation → closeout.

## Non-destructive UX rule
- clearing the teaching/history view must never delete the real editor history used by ↑/↓ navigation;
- result summaries must not imply a single hardware target when the MML result contains multiple distinct targets.
