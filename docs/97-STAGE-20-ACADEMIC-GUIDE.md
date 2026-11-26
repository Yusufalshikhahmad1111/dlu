# DLU Lab 2.0 — Academic Learning Guide

## Purpose

DLU Lab 2.0 is a university communications laboratory, not a general-purpose telecom emulator. Use the UI to connect a visible operation with the source-backed EWSD training model.

## Recommended student sequence

### 1. Learning Home

Orient yourself before opening technical views.

Read the current context and the NEXT guidance before moving into a lab.

### 2. Hardware

Follow:

Exchange → DLU → Side/Controller → Shelf → Module → Port → Subscriber.

Use the inspector to identify the selected object, its state, EQN, role/family and capacity.

Never infer an undocumented physical placement. UNCONFIGURED is a valid academic state.

### 3. OMT / MML

Use a real command and read the complete result:

Intent → Command → Result → Affected object → Explanation.

Useful starting commands are documented in the user manual.

### 4. Call Path

Observe:

Origin → CPT → Resource → Switching → Destination.

Use the visual state to explain why a call connected, was blocked, or was released.

### 5. Command Files

Compose commands, schedule them with the virtual clock and inspect the execution lifecycle.

### 6. Communications

Work through:

Concept → Parameters → Experiment → Visualization → Measurement → Interpretation → Challenge.

The calculations are deterministic teaching models, not a full RF electrical simulator.

### 7. Scenarios

Complete the guided path:

Objective → Observe → Execute → Diagnose → Fix → Verify → Result.

Use the expected-vs-actual information to explain what happened rather than memorizing PASS/FAIL.

## Recovery and reset

When an experiment becomes confusing:

1. Read the current workspace context and NEXT hint.
2. Inspect the visible result or error state.
3. Use the feature's recovery guidance.
4. Use TOOLS → Reset Demo when a clean academic state is required.
5. Create a backup first when the current database state matters.

## What to explain after each lab

A successful student should be able to state:

- what object or subsystem was involved;
- what action was performed;
- what state changed;
- why the result occurred;
- what evidence in the UI proves the result.
