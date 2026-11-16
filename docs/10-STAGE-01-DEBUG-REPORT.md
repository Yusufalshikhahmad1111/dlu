# Stage 1 — Debug Report: Hardware Selector

## Issue 1 — Module dropdown appeared empty

Root cause:
- The scenario selector accepted a card type such as `SLMA8`.
- `_refresh_modules()` filtered the module list to only that card type.
- DLU 10 / Shelf 0 has no SLMA8, so the dropdown became empty.

Fix:
- Always show the full physical module position range `0..15`.
- Show card type and capacity in every option.
- Show an explicit compatibility message.
- Disable OK for an incompatible card instead of hiding the module.

## Issue 2 — Scenario location was hard-coded

Fix:
- `8-Line` opens the physical selector first.
- User chooses DLU, Shelf and Module.
- Generated EQNs are derived from that selection.
- `CMRL` follows the same pattern.

## Issue 3 — Windows CI compile failure

Root cause:
`python -m py_compile dlu_app/*.py tests/*.py` was interpreted literally by Windows Python and failed with `[Errno 22] Invalid argument`.

Fix:
- GitHub Actions now uses PowerShell `Get-ChildItem` to construct an explicit list of Python files.
- Compile and pytest run on Windows 2025 / Python 3.12.

## Regression coverage

- 25 DLUs are expected: `10..250` by tens.
- Each DLU has 8 shelves.
- Each shelf has 16 module positions: `0..15`.
- CMRL rejects port 6.
- Diagnostic guard requires maintenance state.
- Create/display/cancel subscriber flow is covered.

## Current UX rule

The simulator must never hide physical positions because they are empty or incompatible.
Empty positions remain visible as `UNCONFIGURED`, while an operation can reject them with an explicit explanation.

## Important hardware rule

We do not silently install or invent cards just to make a scenario work. A scenario requiring `SLMA8` must select an actual `SLMA8` position in the current dataset until a documented card-install/replace operation is implemented.
