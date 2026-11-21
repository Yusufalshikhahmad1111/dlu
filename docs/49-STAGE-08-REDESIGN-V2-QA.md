# Stage 8 Rework — Windows UX/UI QA

Status: **PASS**

## Automated Windows checks
- Python compile: PASS
- UI static audit: PASS
- Full tests: **80 passed**
- Stage 8 v2 functional and visual QA: PASS
- QA screenshots uploaded: PASS

## Functional checks
1. Started the application in Morning mode.
2. Used LAB navigation to open OMT/MML.
3. Entered `> help;`.
4. Clicked the actual RUN button.
5. Verified the real `MmlEngine` result rendered in the terminal.
6. Switched Morning → Night.
7. Captured Night mode.
8. Switched back to Morning.

## Visual checks
The Stage 8 visual policy covered:
- 1280×720
- 1366×768
- 1600×900
- 1920×1080

The v2 QA runner uploaded functional Morning/Night captures.

## Artifact
`DLU-Stage8-v2-QA`

Artifact ID: `14697744787`

SHA-256:
`87d03d98636639fafcec14d561d0a51644387f9ea274c326d25d1209ad6d169e`

## Manual boundary
This is automated Windows CI validation. No separate personal-device visual session is claimed.
