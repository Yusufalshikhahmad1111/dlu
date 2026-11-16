# 13 — Stage 2 Final QA Checklist

## Code-level checks

- Windows Python 3.12 compile workflow present.
- pytest workflow present.
- Source-backed hardware registry present.
- DLU 10..250 seed present.
- Shelf 0..7 and Module 0..15 constraints enforced.
- Compact MML aliases normalized.
- QGraphics callback lifecycle hardened.
- Physical and Logical renderers implemented.
- Hardware Library and Reference Viewer implemented.
- Maintenance event timeline implemented.
- Card Drag & Drop installation implemented.
- Large-card rendering path exists for SLMA16/64.

## Manual Windows 11 audit

Run:

    git pull
    run.bat

Then verify:

1. Hardware home shows DLU 10..250.
2. Open DLU 50.
3. Physical mode renders 8 shelves.
4. Shelf 0 renders Modules 0..15.
5. Module 15 opens SLMA8.
6. Port 0..7 render and can be selected.
7. Logical mode opens without exceptions.
8. Hardware Library opens as a modeless window.
9. Drag SLMA8 from Hardware Library onto an UNCONFIGURED Module.
10. Existing configured Module rejects a drop with a clear reason.
11. FAULT marks the module MBL and raises MAJOR.
12. DIAG confirms the fault.
13. REMOVE clears the physical card.
14. INSTALL requires a verified registry card.
15. ACTIVATE restores service.
16. Maintenance Timeline contains all steps.
17. OMT `DISP/STAT/TEST` focuses the hardware.
18. `COPY MML` produces a valid command.
19. CMRL ports 0..5 work and port 6 is rejected.
20. 8-Line scenario asks for DLU/Shelf/Module rather than hard-coding a location.

## Release gate

Stage 2 is release-ready only after:

- latest CI on the current head is green, and
- the above Windows manual audit is completed once.
