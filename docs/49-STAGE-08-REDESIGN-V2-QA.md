# Stage 8 Rework — Windows UX/UI QA

Status: Pending final CI execution.

## Required checks

### Functional
- `python -m py_compile`
- UI static audit
- complete pytest suite
- OMT/MML GUI command test
- Morning/Night toggle test

### Visual
Capture at:

- 1280×720
- 1366×768
- 1600×900
- 1920×1080

Inspect:

- no clipping;
- no overlap;
- readable green-on-white contrast in Morning;
- readable mint-on-charcoal contrast in Night;
- navigation remains understandable;
- OMT input and Run button remain obvious;
- command results remain legible.

### Packaging
- Windows onefile build
- EXE smoke test
- screenshot artifact upload

## Manual boundary

Automated Windows CI is the authoritative repeatable gate. A separate personal-device visual session is not claimed unless performed.
