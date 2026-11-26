# DLU Lab 2.0.0 — User Manual

## 1. What is DLU Lab?

DLU Lab is a local Windows 11 educational simulator for Siemens EWSD DLU training. It is designed for the Principles of Communications course and keeps the hardware dataset source-backed.

## 2. Recommended release

Use the Windows onefile executable produced by the Stage 7 release workflow. No Python installation is required for the packaged executable.

For development from source:

```bat
run.bat
```

## 3. Main learning flow

Hardware → OMT/MML → Call Path → Command Files → Communications → Scenarios

Start at **Learning Home**. Follow the visible **YOU ARE HERE / NEXT** context, then move through Hardware → OMT/MML → Call Path → Communications → Scenarios. Use Instructor / Classroom mode for projector-safe demonstrations.

## 4. Teaching Scenarios

Six formal scenarios are available:

- Aleppo 8-Line Expansion
- CMRL Capacity Limit
- DLU / Card Maintenance
- Billing Block
- International Blacklist
- Command File Overnight Run

Every scenario reports affected EQN(s), the expected result, the actual result and step-level PASS/FAIL.

## 5. Backup

Open **TOOLS → Backup Database**.

Choose a `.sqlite3` destination. DLU Lab creates a SQLite backup using the database backup API, checks SQLite integrity and writes a small metadata sidecar.

Recommended practice: create a backup before a large teaching session or before resetting demo state.

## 6. Restore

Open **TOOLS → Restore Database** and select a valid backup.

The backup is validated first. DLU Lab stages the file, closes the current application, creates an automatic pre-restore safety backup, replaces the database, and starts the application again.

Never interrupt the computer during the restore/restart step.

## 7. Reset Demo

**TOOLS → Reset Demo** restores the source-backed hardware placement and clears teaching subscribers, alarms, command files and hardware-event history. A confirmation dialog is shown.

Use Backup first when the current state matters.

## 8. Data location

Live application data is stored under:

```text
%USERPROFILE%\\AppData\\Local\\DLULab
```

The **TOOLS → Open Data Folder** action opens this directory.

## 9. MML examples

```text
> stat dlu: dlu=50;
> disp dlumod: dlu=50, shelf=0, module=15;
> disp dlupport: eqn=50-0-15-0;
> statport: eqn=50-0-15-0;
> cr sub: dlu=50, type=ms, eqn=50-0-15-0, lac=021, dn=2233500;
```

## 10. Instructor / Classroom mode

The Instructor workspace supports scenario selection, Reset Demo, hidden answers, REVEAL ANSWERS, guided demonstration, and projector mode. Answers remain hidden until explicitly revealed.

## 11. Academic boundary

The simulator intentionally keeps unknown physical placement as UNCONFIGURED and does not invent capacities or placements that are not supported by the course dataset.
## 12. Release identity

**DLU Lab 2.0.0 — Stage 20 final release**

The current Stage 0→20 roadmap is complete after the final Windows release gates pass.
