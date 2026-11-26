# DLU Lab 2.0 — Instructor / Classroom Guide

## Classroom setup

1. Launch the Windows onefile release.
2. Confirm Morning/Night theme and the target display resolution.
3. Start from Learning Home or the Instructor workspace.
4. Use Reset Demo before a clean demonstration.

## Demonstration flow

Recommended teaching sequence:

1. Introduce the objective.
2. Open the relevant technical workspace.
3. Execute the real simulator action.
4. Explain the visible state transition.
5. Compare expected and actual behavior when answers are intentionally revealed.
6. Conclude with the telecom concept and evidence.

## Instructor mode

The Instructor workspace supports:

- scenario selection;
- reset;
- real scenario execution;
- answer visibility control;
- expected-vs-actual teaching;
- guided demonstration;
- projector-friendly presentation.

Answers are hidden until REVEAL ANSWERS is explicitly enabled. The hidden state must not expose PASS/FAIL.

## Projector mode

Projector mode reduces operational clutter and emphasizes:

- scenario title;
- objective;
- result summary.

Night mode is supported for classroom projection.

## Recommended scenarios

Use the six source-backed scenarios according to the lesson objective:

- Aleppo 8-Line Expansion
- CMRL Capacity Limit
- DLU / Card Maintenance
- Billing Block
- International Blacklist
- Command File Overnight Run

## Reset discipline

Before switching demonstrations:

- reset the current teaching state;
- verify the UI shows RESET/clean state;
- then load and run the next scenario.

Do not teach students to infer hidden hardware facts from the UI. Keep the dataset-backed boundaries visible.

## Classroom safety

The simulator is intentionally local and deterministic. It is suitable for demonstration and controlled practice. It should not be presented as a full physical-network or RF laboratory.
