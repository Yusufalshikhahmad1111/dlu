# DLU Lab 2.0.0 — Instructor / Classroom Guide

## Purpose

The Instructor workspace is designed for projector-safe classroom demonstrations while preserving the same verified simulator behavior used by students.

## Classroom flow

### 1. Prepare

Open the Instructor workspace and choose one of the six formal scenarios:

1. Aleppo 8-Line Expansion
2. CMRL Capacity Limit
3. DLU / Card Maintenance
4. Billing Block
5. International Blacklist
6. Command File Overnight Run

### 2. Reset

Use Reset Demo before a repeat demonstration when a previous run may have changed shared training state.

### 3. Demonstrate

Run the selected scenario while answers are hidden.

The hidden state intentionally does not expose:

- expected result;
- actual result comparison;
- PASS/FAIL conclusion.

This lets the instructor ask students to predict the outcome.

### 4. Reveal

Use REVEAL ANSWERS after discussion.

Then use the guided demonstration controls to reveal the real verified scenario result step by step.

### 5. Project

Enable projector mode for a cleaner classroom surface. Morning and Night themes remain available.

## Teaching prompts

Ask students to explain:

- which object or subsystem changed;
- which command/action caused the change;
- what the expected result was;
- what actually happened;
- what evidence supports PASS or explains FAIL;
- how the state relates to the underlying EWSD concept.

## Recovery

When a demonstration becomes inconsistent:

1. Reset Demo.
2. Reload the scenario.
3. Repeat the real scenario runner.
4. Use the resulting state as the authoritative evidence.

Do not manually simulate PASS/FAIL in the instructor narrative.

## Release identity

**DLU Lab 2.0.0**

The instructor mode is presentation-only around the existing scenario engine; it does not duplicate telecom rules.
