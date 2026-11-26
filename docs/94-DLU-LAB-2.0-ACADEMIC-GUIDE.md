# DLU Lab 2.0.0 — Academic Guide

## Purpose

DLU Lab 2.0.0 is the completed university communications digital laboratory built on the source-backed EWSD/DLU simulator.

The academic path is:

**Learn → Explore → Execute → Observe → Explain → Practice → Verify**

The application keeps the simulator engines authoritative. UI layers do not create alternate MML, call, communications, or scenario rules.

## Recommended student journey

### 1. Learning Home

Start at LAB / Learning Home.

Read the current context and the YOU ARE HERE / NEXT guidance, then choose the first relevant technical area.

### 2. Hardware

Use Hardware to inspect:

Exchange → DLU → Side/Controller → Shelf → Module → Port → Subscriber

Check the selected object's state, EQN, capacity, and role before moving to OMT/MML.

### 3. OMT / MML

Use real commands to connect intent to system state.

Good first commands:

    > stat dlu: dlu=50;
    > disp dlumod: dlu=50, shelf=0, module=15;
    > disp dlupport: eqn=50-0-15-0;

The result should explain the affected hardware/context.

### 4. Call Path

Run a local teaching call and inspect:

Origin → route classification → resource → path → destination → release/block

Explain why the call connected or was blocked.

### 5. Communications

Choose one experiment, change a parameter, run it, inspect the waveform/constellation or measurement, and state what changed and why.

### 6. Scenarios

Choose a formal teaching scenario and work through:

Objective → Observe → Execute → Diagnose → Fix → Verify → Result

Use Reset Demo before repeating a stateful scenario.

### 7. Verify

Use the academic learning layer to confirm that the workflow produced real simulator evidence rather than a presentation-only result.

## Academic integrity

The dataset remains source-backed. Unknown physical placement is not guessed. Existing MML, call engine, communications formulas, teaching scenario rules, and SQLite schema remain authoritative.

## Student success standard

A student should be able to answer:

- What am I looking at?
- What action am I taking?
- What changed?
- Why did it change?
- What evidence proves the result?

## Release identity

**DLU Lab 2.0.0**

Stage 20 is the final release stage of the current roadmap; further work is post-release enhancement rather than an unfinished milestone.
