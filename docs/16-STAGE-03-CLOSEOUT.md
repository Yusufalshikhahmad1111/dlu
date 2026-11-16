# Stage 3 — Final Closeout

## Status

Stage 3 — Call Engine + CPT + Call Path: COMPLETED.

## Delivered

### CPT and Number Analysis
- Deterministic exact, prefix, and numeric-range CPT matching.
- Longest/specific match selection.
- LOCAL / NATIONAL / INTERNATIONAL / SERVICE / UNKNOWN analysis.
- CPT EVAL=NO blocking before resource reservation.
- Course-backed BLACK LIST handling for 00972.

### Call Engine
- Persistent call sessions.
- Persistent call legs.
- CONNECTED / FAILED / RELEASED states.
- Atomic PDC resource reservation and release.
- 120-channel PDC voice resource accounting.
- Busy/blocked subscriber guards.
- Release returns reserved resources and subscriber ports to idle.

### Call Paths
- LOCAL: DLU → SN → DLU.
- NATIONAL: DLU → LTG → SN → LTG → logical remote DLU/LAC.
- INTERNATIONAL: DLU → LTG → SN → International Gateway.
- SERVICE: DLU → SN → Service.

Where a remote physical DLU/card placement is not source-backed by the repository, the path uses an explicitly logical DLU-LACxxx node rather than inventing hardware placement.

### OMT
Read-only call inspection and analysis:
- TEST CALL
- STAT CALL
- DISP CALL

These expose the same domain state used by the Call Path UI.

### UI
- CALL ENGINE · CPT · CALL PATH tab.
- PREPARE DEMO.
- LOCAL.
- NATIONAL.
- INTERNATIONAL.
- BLACK LIST.
- RELEASE.
- Live PDC usage.
- Visual Call Path.

## Automated QA

Stage 3 tests cover:
- local connect and release.
- national routing and PDC reservation.
- international routing and PDC reservation.
- blacklist blocking without resource reservation.
- busy caller guard.
- deterministic CPT matching.
- PDC exhaustion.
- OMT call analysis/status integration.

Existing Stage 1 and Stage 2 tests remain in the same CI regression suite.

## Windows Manual QA

Verified by the project manual runtime audit:
- Call Path tab opens.
- PREPARE DEMO works.
- LOCAL displays DLU 50 → SN → DLU 50.
- Caller/called ports become BUSY.
- RELEASE returns ports to IDLE.
- PDC returns to 0/120.
- NATIONAL displays DLU 50 → LTG → SN → LTG → DLU-LAC052.
- NATIONAL consumes 1/120.
- RELEASE restores PDC.
- INTERNATIONAL displays International Gateway and uses 1/120.
- RELEASE restores PDC.
- BLACK LIST shows EVAL=NO / BLACK LIST.
- BLACK LIST leaves PDC at 0/120.

## Release Gate

Stage 3 is closed.

Next planned phase: Stage 4 — Command Files.
