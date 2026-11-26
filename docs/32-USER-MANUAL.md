# DLU Lab 2.0.0 — User Manual

## 1. What is DLU Lab?

DLU Lab is a local Windows 11 educational simulator for Siemens EWSD DLU training. It is designed for the Principles of Communications course and keeps the hardware dataset source-backed.

The application is deterministic and local. It is a teaching laboratory, not a full physical-network or RF simulator.

## 2. Start the application

### Packaged Windows release

Use the DLU Lab 2.0.0 onefile executable. No Python installation is required.

### From source

run.bat

Or:
py -3.12 -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py

## 3. Recommended learning flow

Learning Home
→ Hardware
→ OMT / MML
→ Call Path
→ Command Files
→ Communications
→ Scenarios

The current workspace displays its academic context and recommended NEXT action.

## 4. Hardware

Follow:

Exchange → DLU → Side/Controller → Shelf → Module → Port → Subscriber.

Use the Inspector to read:

- object;
- state;
- EQN;
- capacity;
- role/family;
- subscriber context.

Physical placement that is not supported by the dataset remains UNCONFIGURED.

## 5. OMT / MML

Enter a real command in the OMT/MML workspace.

The result should be read as:

Intent → Command → Result → Affected object → Explanation

Starting examples:

stat dlu: dlu=50;
disp dlumod: dlu=50, shelf=0, module=15;
disp dlupport: eqn=50-0-15-0;
statport: eqn=50-0-15-0;
cr sub: dlu=50, type=ms, eqn=50-0-15-0, lac=021, dn=2233500;

## 6. Call Path

Observe:

Origin → CPT → Resource → Switching → Destination

Use the visible state and explanation to determine why the call connected, was blocked, or was released.

## 7. Command Files

Use the Command Files workspace to:

- compose commands;
- schedule HH:MM execution;
- inspect lifecycle state;
- execute due files through the real MML engine.

## 8. Communications

Work through:

Concept → Parameters → Experiment → Visualization → Measurement → Interpretation → Challenge

The lab contains OSI, TCP/UDP, analog, pulse, digital modulation, constellation and BER teaching surfaces.

## 9. Teaching Scenarios

Six formal scenarios are available:

- Aleppo 8-Line Expansion
- CMRL Capacity Limit
- DLU / Card Maintenance
- Billing Block
- International Blacklist
- Command File Overnight Run

Every scenario reports commands/actions, affected EQN, expected result, actual result and the final PASS/FAIL state.

The guided flow is:

Objective → Observe → Execute → Diagnose → Fix → Verify → Result

## 10. Instructor / Classroom mode

Instructor mode is separate from normal student workspaces.

It supports:

- scenario selection;
- reset;
- real execution;
- REVEAL ANSWERS;
- expected vs actual;
- guided demonstration;
- projector mode.

Expected/actual and PASS/FAIL are hidden until answers are explicitly revealed.

## 11. Morning / Night

Use the visible theme control to switch between Morning and Night. Projector use is supported through the Instructor projector mode.

## 12. Backup

Open TOOLS → Backup Database.

Choose a .sqlite3 destination.

DLU Lab creates a SQLite backup through the database backup API, validates integrity and writes metadata.

Recommended practice: create a backup before a large teaching session or before resetting important state.

## 13. Restore

Open TOOLS → Restore Database and select a valid backup.

The backup is validated first. DLU Lab stages the restore, closes the active database safely, creates an automatic pre-restore safety backup, replaces the database and starts the application again.

Do not interrupt the computer during the restart step.

## 14. Reset Demo

Open TOOLS → Reset Demo.

Reset restores the source-backed hardware placement and clears teaching subscribers, alarms, command files and hardware-event history. Stage 19 also synchronizes the Scenario and Instructor view state so stale PASS/FAIL/READY information is not carried into the reset state.

Use Backup first when the current state matters.

## 15. Data location

Live application data is stored under:

%USERPROFILE%\\AppData\\Local\\DLULab

TOOLS → Open Data Folder opens this directory.

## 16. Academic boundary

The simulator intentionally keeps unknown physical placement as UNCONFIGURED and does not invent capacities, placements or telecom semantics that are not supported by the course dataset.

## 17. Documentation

For lesson planning use:

- Academic Learning Guide: docs/97-STAGE-20-ACADEMIC-GUIDE.md
- Instructor / Classroom Guide: docs/98-STAGE-20-INSTRUCTOR-GUIDE.md
