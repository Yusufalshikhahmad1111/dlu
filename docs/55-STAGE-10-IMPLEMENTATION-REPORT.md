# Stage 10 — Hardware UX 2.0 Implementation Report

## Result
Stage 10 adds a student-facing hardware inspection layer on top of the existing source-backed hardware renderer.

The implementation deliberately avoids:
- database migrations;
- new hardware placements;
- new capacities;
- new MML/domain logic;
- replacement of the existing hardware renderer.

## Implemented

### Hardware Inspector
`dlu_app/hardware_ux2.py` adds a persistent inspector showing:
- object type and identity;
- full parent context;
- explicit state text;
- EQN;
- capacity;
- role/family;
- controller context;
- subscriber context;
- maintenance/fault note;
- direct open action.

Supported context levels:

Exchange → DLU → Side/Controller → Shelf → Module → Port → Subscriber

### Hardware UX integration
`dlu_app/stage10_ui.py` installs the inspector without rewriting the existing hardware renderer.

It adds:
- persistent hardware/inspector splitter;
- hover inspection;
- selection context;
- selection and hover outlines;
- direct inspector navigation;
- theme synchronization.

The existing `show_hardware_home`, `show_dlu`, `show_shelf`, `show_module`, and `select_port` flows remain the source of truth.

### Startup
`main.py` now applies Stage 10 after Stage 8 and Stage 9.

### QA
Added:
- `tests/test_stage10_hardware_ux.py`
- `tools/stage10_hardware_qa.py`
- `.github/workflows/stage10-hardware-qa.yml`

QA targets: 1280×720, 1366×768, 1600×900, 1920×1080, plus module/port and night-mode screenshots.

## Academic integrity
All displayed placements, card types, capacities, controller states, EQNs, and subscriber associations come from the existing database/reference layer. No new telecom facts were introduced.

## Acceptance target
A student can identify the selected hardware object's role, state, capacity, and EQN from one workspace without opening an unrelated dialog.

## Next
Stage 11 — OMT/MML UX 2.0.