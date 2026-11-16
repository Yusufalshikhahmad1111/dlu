# Stage 1 — Runnable GUI / OMT Implementation Report

## Delivered

This stage adds the first runnable desktop implementation to the repository.

### GUI

- Windows desktop UI built with PySide6.
- DLU 10 / DLU 50 selector.
- DLUC0 and DLUC1 operational state.
- Shelf 0..7.
- Module positions 0..15.
- Shelf drill-down.
- Module/card drill-down.
- Port view with state LEDs.
- DN ↔ EQN inspection panel.
- Zoom with mouse wheel and pan with the view.

### OMT

Implemented commands:
- DISP DLU
- DISP SLOT
- DISP SUB
- STAT DLU
- STAT SUB
- TEST SUB
- CR SUB
- CAN SUB
- MOD SUB
- CONF DLU
- DIAG DLU

The parser is case-insensitive and supports compact aliases such as CRSUB and DISPSUB.

### Persistence

SQLite is created automatically under the user's local AppData directory.

Seed:
- ALE1
- DLU 10
- DLU 50
- 8 shelves per DLU
- 16 module positions per shelf
- only demo card placements
- unconfigured positions remain UNCONFIGURED

### Tests

Core regression tests cover:
- create/display/cancel
- CMRL capacity guard
- diagnostic maintenance guard

Local validation completed with 3 passed.

## Important scope decision

This is intentionally an educational visual representation. It does not claim to be a factory-accurate PCB drawing or a real EWSD control system.

The visual hierarchy is:

DLU → Shelf → Module → Port → Subscriber

Unknown hardware positions are not fabricated.

## Next stage

The next implementation stage should expand the hardware dataset from verified references, then deepen MML coverage and SYP/call-path behavior without changing the hardware-first model.
