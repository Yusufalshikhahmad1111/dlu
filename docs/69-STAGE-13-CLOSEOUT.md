# Stage 13 — Communications Lab 2.0 Closeout

**Status:** COMPLETE — merged to main after CI / Windows gate

## Acceptance target

A student can choose an existing communications experiment, change a parameter, observe the visual change, read a measurement, understand the explanation, and answer a small challenge without needing a separate explanation of the UI.

## Delivered

- Concept → Parameters → Experiment → Visualization → Measurement → Explanation → Challenge workflow;
- improved waveform readability;
- improved constellation readability;
- measurement cards;
- plain-language result explanations;
- deterministic mini challenges;
- Live Update;
- Morning/Night synchronization;
- preserved deterministic communications domain core.

## Evidence

- Stage 13 focused tests: **6/6 passed**.
- Compile check: **passed**.
- UI static audit: **passed**.
- Full pytest regression in the Stage 13 Windows QA workflow: **passed**.
- Functional visual QA: **passed**.
- Screenshot artifact: **5 PNGs successfully uploaded**.
- Main DLU CI: **passed** on the final Stage 13 code commit.
- Final merge commit: \`7a75926824f7abe6a15d35f9ec374ccff658fb87\`.

### Fixes made during verification

1. Corrected a BER plot generator-expression syntax error caught by the Windows compile gate.
2. Preserved domain truth for BPSK by avoiding an unsupported \`constellation_points("BPSK")\` call and showing an explanatory fallback instead.
3. Populated the initial Stage 13 experiment automatically and preserved the existing Communications tab position during installation.

### Scope guard

No communications calculation formulas, SQLite schema, CallEngine, MML engine, hardware database, or scenario engine were changed.

## Next

Stage 14 — Teaching Scenarios 2.0.
