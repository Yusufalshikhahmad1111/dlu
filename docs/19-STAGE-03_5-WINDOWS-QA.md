# Stage 3.5 — Windows Visual QA Checklist

## OMT
- Open OMT.
- Confirm the terminal occupies the main output area.
- Confirm the MML command dock is permanently visible at the bottom.
- Type a command and verify SEND and Enter both work.

## Hardware Fleet
- Return to Hardware home.
- Confirm all 25 DLU entries remain visible/clickable.
- Confirm the entries look like rack cards rather than plain rectangles.

## Physical DLU
- Open DLU 50.
- Confirm the chassis, rails, controllers, DIUD/PDC indicators, and 8 shelves are visible.
- Click Shelf 0.

## Shelf
- Confirm Shelf 0 is displayed as an equipment bay.
- Confirm Module 15 is visually distinct as an SLMA8 card faceplate.
- Double-click Module 15.

## Module
- Confirm the faceplate contains card identity, state, capacity, EQN base, source, and connector-style ports.
- Click Port 0.
- Confirm the Details panel still updates.
- Right-click a port and confirm Inspect Port / Copy MML.

## Stage 2 preservation
- Run 8-Line.
- Run CMRL.
- Verify Maintenance and Inspect still work.
- Verify Hardware Library and drag/drop still work.

## Stage 3 preservation
- Open Call Path.
- Run LOCAL.
- Run NATIONAL.
- Run INTERNATIONAL.
- Run BLACK LIST.
- Confirm path visualization remains readable.

## Resolution pass
- 1280x720.
- 1366x768.
- 1600x900.
- 1920x1080.

Release only after no clipping, traceback, missing command dock, or broken interaction is found.