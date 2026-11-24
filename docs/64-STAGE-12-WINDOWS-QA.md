# Stage 12 — Windows QA

## Automated gate

Required:

- \`compileall\`;
- UI static audit;
- full pytest suite;
- focused Stage 12 tests;
- functional screenshot runner.

## Functional cases

### LOCAL
Expected: CONNECTED, DLU → SN → DLU, PDC-VOICE NOT REQUIRED.

### NATIONAL
Expected: CONNECTED, LTG → SN → LTG, PDC-VOICE RESERVED, one short signal animation.

### BLACK LIST
Expected: BLOCKED, CPT / BLOCKED endpoint, explanation that EVAL=NO blocks before voice reservation.

### PDC full
Expected: BLOCKED, PDC-VOICE FULL, explanation that capacity blocked the call before CONNECTED.

### RELEASE
Expected: RELEASED, current PDC usage shown, and a clear explanation of whether a PDC resource was actually held.

## Visual targets

The Stage 12 runner captures 1600×900 morning and night examples and a blocked-call example.

The existing release QA matrix for earlier stages continues to cover 1280×720 through 1920×1080.

## Non-regression

The full suite remains the required gate for Hardware, OMT/MML, Calls, Communications, and Scenarios.
