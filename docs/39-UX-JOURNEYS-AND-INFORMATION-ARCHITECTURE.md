# DLU Lab — UX Journeys & Information Architecture

**Status:** Target architecture  
**Baseline:** Existing academic modules preserved

## 1. Primary navigation

Primary learning areas:

1. LAB
2. HARDWARE
3. OMT
4. CALLS
5. COMMANDS
6. COMMUNICATIONS
7. SCENARIOS

Administrative/support actions stay secondary:

- Hardware Library
- Backup
- Restore
- Reset Demo
- Data Folder
- About

## 2. Student home

The future home screen should answer immediately:

- Where am I?
- What can I learn here?
- What did I last do?
- What should I do next?

Recommended blocks:

- Continue Learning
- Current Lab
- Recent Experiments
- Hardware Status
- Quick Start
- Scenario Progress

## 3. Hardware journey

Exchange
→ DLU
→ Side/Controller
→ Shelf
→ Module
→ Port
→ Subscriber

At every level, the user can see the parent context and move back without losing orientation.

## 4. MML journey

Command intent
→ command construction
→ syntax check
→ execution
→ result
→ affected object
→ explanation

## 5. Call journey

Origin
→ route classification
→ CPT
→ resource reservation
→ switch path
→ destination
→ release / blocked result

## 6. Communications journey

Concept
→ parameters
→ experiment
→ visualization
→ measurement
→ interpretation
→ challenge

## 7. Scenario journey

Objective
→ observe
→ execute
→ diagnose
→ fix
→ verify
→ result

## 8. Instructor journey

Choose mode
→ choose scenario
→ prepare/reset
→ demonstrate
→ reveal explanation
→ compare expected/actual
→ conclude

## 9. Context model

A student should not lose context when opening a detail.

Every major view should expose a small context trail, for example:

`Communications / Digital Modulation / QPSK`

or:

`Hardware / DLU 50 / Shelf 0 / Module 15 / Port 0`

## 10. Progressive disclosure policy

Default view:
- the few controls needed for the immediate task.

Expanded view:
- secondary details.

Advanced view:
- expert controls, source metadata, raw diagnostics, or deeper telemetry.

This follows the usability principle of progressive disclosure.

## 11. Empty/error/loading states

Every major surface must explicitly design:

- no selection;
- no data;
- invalid command;
- failed command;
- unavailable resource;
- busy state;
- reset state;
- recovery action.

## 12. Navigation acceptance

A student should be able to answer these questions at every screen:

1. What module am I in?
2. What object am I looking at?
3. What can I do next?
4. What happened after my last action?

If the UI cannot answer one of these, the navigation design is incomplete.
