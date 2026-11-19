# DLU Lab — Target UX/UI Architecture

## 1. Current condition

The repository has a large `dlu_app/ui.py` module that coordinates the primary application window and many presentation responsibilities.

This is not a reason to rewrite the simulator. It is a reason to introduce boundaries progressively.

## 2. Target layers

```
App Shell
 ├── Navigation
 ├── Design System
 ├── Context / Workspace
 └── Feature Views
      ├── Hardware
      ├── OMT/MML
      ├── Calls
      ├── Command Files
      ├── Communications
      └── Scenarios

Domain Core
 ├── Database
 ├── MML
 ├── Call Engine
 ├── Command Files
 ├── Communications Core
 └── Teaching Scenarios
```

## 3. Architectural rule

Feature UI may call domain services.

Feature UI must not create alternative copies of domain rules.

Examples:

- Hardware view asks DB for hardware state.
- OMT view asks MML engine to execute commands.
- Call view asks CallEngine for paths/resources.
- Scenario view asks TeachingScenario model to execute the scenario.
- Communications view asks Communications core for calculations.

## 4. Stage strategy

### Stage 8
Introduce design tokens and shared style primitives.

### Stage 9
Introduce navigation boundaries.

### Stage 10+
Move individual feature surfaces behind small view/controller boundaries.

### Stage 18
Perform larger decomposition only after repeated UX patterns are known.

## 5. Naming direction

Suggested future modules:

- `app_shell.py`
- `navigation.py`
- `design_tokens.py`
- `app_style.py`
- `hardware_view.py`
- `omt_view.py`
- `call_view.py`
- `communications_view.py`
- `scenario_view.py`
- `components/`

Names are target guidance, not mandatory files for Stage 8.

## 6. What must not happen

- no rewrite of the domain core just to move a button;
- no duplicated MML parsing in UI;
- no duplicated call classification;
- no duplicated scenario logic;
- no new data source that conflicts with source-backed hardware data;
- no giant shared utility module containing unrelated UI behavior.

## 7. Architecture acceptance

The UI boundary is good when:

- a visual change does not require editing domain logic;
- a domain rule change does not require rewriting several views;
- reusable visual components can be tested independently;
- feature views can be visually audited in isolation.
