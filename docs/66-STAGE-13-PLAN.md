# Stage 13 — Communications Lab 2.0 Plan

**Status:** COMPLETE — implementation and QA gates passed

## Goal

Transform the existing Communications Labs from a tool-oriented panel into a guided teaching studio:

**Concept → Parameters → Experiment → Visualization → Measurement → Explanation → Challenge**

## Scope

The stage covers the existing five deterministic experiments:

1. OSI / TCP / UDP
2. AM / FM / PM
3. PAM / PWM / PPM / PCM
4. ASK / FSK / PSK / QPSK / 16-QAM
5. Constellation / BER

## Required outcomes

- clear Concept and engineering context before controls;
- explicit parameter section;
- one-click Experiment action plus optional Live Update;
- improved normalized waveform readability;
- improved I/Q constellation readability with explicit axes and point count;
- measurement cards that expose the selected parameters and observed results;
- plain-language explanation tied to the current result;
- deterministic mini challenge for each experiment;
- Morning/Night synchronization;
- responsive vertical layout for the existing right-side lab workspace.

## Architecture constraints

- dlu_app/communications_lab.py remains the sole calculation source.
- No changes to CallEngine, MML, hardware database, scenario engine, or SQLite schema.
- No new runtime dependency.
- Stage 13 is presentation/teaching only.
- The legacy Communications Lab widget remains available as an implementation fallback during the stage branch but is replaced in the main feature tab by the Stage 13 widget.

## Quality gates

- compile check;
- focused Stage 13 tests;
- full pytest regression;
- UI static audit;
- Windows functional/visual QA at the project target desktop size;
- screenshot artifacts for all five lab families;
- documentation synchronized before merge.

## Execution rule

Implement → Tests → Visual QA → Manual Demo → Fix → Report → Commit.
