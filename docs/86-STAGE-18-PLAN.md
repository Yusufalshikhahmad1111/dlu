# Stage 18 — Performance & Architecture Cleanup

**Status:** IN PROGRESS

## Goal

Reduce the responsibility of the monolithic UI layer without rewriting domain behavior.

## Target boundaries

- `dlu_app/app_shell.py` — startup composition and stage mounting.
- `dlu_app/navigation.py` — navigation state already introduced in earlier stages.
- `dlu_app/design_tokens.py` / `theme.py` — visual tokens and legacy palette compatibility.
- `dlu_app/hardware_view.py` — hardware feature surface and rendering.
- existing feature modules for OMT/MML, Calls, Communications, Scenarios, Academic Learning, Instructor, and Accessibility.
- `dlu_app/ui_utils.py` — shared UI utility boundary.

## Safety rules

1. No MML parsing changes.
2. No CallEngine behavior changes.
3. No TeachingScenario semantics changes.
4. No database schema changes.
5. No new runtime dependency.
6. No visual rewrite.
7. Preserve public methods used by tests and feature adapters.

## First decomposition

The large hardware implementation inside `ui.py` is extracted into `HardwareWorkspaceMixin` in `hardware_view.py` and composed through inheritance. Existing method names and call sites remain unchanged.

The application bootstrap pipeline is extracted into `app_shell.py`. `main.py` remains responsible for process startup, restore handling, and CLI entry behavior only.

## Acceptance

- visual changes remain localized;
- domain modules remain independent;
- hardware rendering can be tested through its feature boundary;
- startup composition is centralized;
- full regression remains green;
- Windows target-resolution screenshots remain valid.
