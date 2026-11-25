# Stage 13 — Communications Lab 2.0 Implementation Report

**Status:** Implemented on stage-13-communications-lab-2

## What changed

### New teaching studio

Added dlu_app/stage13_ui.py with:

- Stage 13 step rail;
- five experiment pages;
- concept-first introductory copy;
- grouped parameters;
- explicit experiment actions;
- optional live recomputation;
- measurement cards;
- result explanations;
- mini challenges with explicit CORRECT / TRY AGAIN feedback;
- Morning/Night theme support.

### Visualization improvements

The new signal canvas provides:

- readable normalized waveform grid;
- zero-reference line where applicable;
- explicit range/sample labels;
- I/Q axes and labelled constellation points;
- BER log-style grid with theory/empirical distinction;
- vertical evidence layout that remains usable in the narrower feature pane.

### Integration

main.py now installs Stage 13 after Stages 8–12.

The controller replaces only the Communications feature widget and keeps the existing feature-tab position and navigation label.

## Domain preservation

The Stage 13 layer directly calls the existing deterministic functions:

- analog_waveform
- pulse_waveform
- digital_waveform
- constellation_points
- ber_curve
- osi_layers
- transport_profiles

No calculation formulas were reimplemented.

## QA infrastructure

Added:

- tests/test_stage13_communications_lab_2.py
- tools/stage13_comms_qa.py
- .github/workflows/stage13-comms-qa.yml

The workflow performs compile, static audit, focused tests, full regression, and functional screenshot QA on Windows.

## Known verification state

Automated and Windows gates are pending final CI execution on the completed branch.
