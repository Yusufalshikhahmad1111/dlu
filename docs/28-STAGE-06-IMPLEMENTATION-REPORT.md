# Stage 6 — Teaching Scenarios Implementation Report

## Delivered

Stage 6 adds a formal scenario engine and teaching workbench without duplicating the simulator's business rules.

### New domain layer

`dlu_app/teaching_scenarios.py`

Provides:
- six canonical scenarios;
- deterministic scenario definitions;
- per-step PASS/FAIL results;
- expected vs actual result reporting;
- affected EQN reporting;
- reuse of MML, DB, Call Engine and Command File Engine.

### New UI layer

`dlu_app/teaching_scenarios_ui.py`

Provides:
- scenario catalog;
- objective and summary;
- affected EQN display;
- expected / actual result cards;
- detailed step table;
- command preview/copy;
- explicit RESET DEMO control;
- overall PASS/FAIL state.

### Main application integration

A new **Scenarios** tab is added beside the existing teaching workbenches.

No Stage 1–5 behavior was replaced. The new layer calls the existing services.

## Scenario semantics

The suite covers:
- Aleppo 8-line expansion;
- CMRL six-port capacity guard;
- DLU/card maintenance;
- billing suspension with `accsusp`;
- international blacklist with CPT EVAL=NO;
- overnight command-file execution across midnight.

## Safety / non-destruction rule

Scenario execution does not silently reset the database. The workbench exposes the existing RESET DEMO action for an intentional clean run.

## Validation

The release gate is:
- compile;
- static UI audit;
- complete pytest regression;
- six scenario tests;
- Teaching Scenarios UI smoke test;
- manual preservation of Stage 1–5 workbenches on Windows.

## No new runtime dependency

Stage 6 uses the existing Python + PySide6 + SQLite stack only.
