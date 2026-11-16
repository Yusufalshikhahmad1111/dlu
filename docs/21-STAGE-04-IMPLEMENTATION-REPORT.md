# Stage 4 — Command Files Implementation Report

## Implemented

Stage 4 adds deterministic command-file execution on top of the existing MML engine.

### Command file engine
- parser for command-file text.
- optional file header and END FILE wrapper.
- validation that executable lines use the simulator MML format.
- nested EXECMDFILE rejection.
- persistent file records through the existing command_files table.
- lifecycle states:
  - Accepted
  - Started
  - Finished
  - Executed
  - Failed
- per-command execution log.
- fail-fast behavior on the first failed command.

### Scheduling
- HH:MM scheduling.
- persisted scheduled_at value.
- explicit virtual clock.
- manual clock advance.
- due-file execution when virtual time reaches the scheduled time.

### OMT / MML
Supported:
> execmdfile: file=block-demo;
> execmdfile: file=block-demo, time=02:00;

The scheduled form records an Accepted command file with its run time. The immediate form executes the file synchronously through the existing MML engine.

### UI
New Command Files workbench:
- file name.
- command editor.
- ACCEPT.
- EXECUTE.
- SCHEDULE.
- LOAD DEMO.
- virtual clock.
- +5 MIN.
- +1 HOUR.
- SET CLOCK.
- RESET CLOCK.
- file list with status.
- execution log.

## Architectural boundary

Command files never bypass MML.

The execution flow is:

Command File
→ Parser
→ MML Engine
→ Existing Stage 1–3 use cases
→ SQLite / Event Log
→ Command File execution log

This preserves one source of truth for command behavior.

## QA coverage

Automated coverage includes:
- virtual clock.
- parser.
- Accepted state.
- successful execution.
- persistent execution log.
- schedule and due execution.
- fail-fast behavior.
- EXECMDFILE scheduling.
- immediate EXECMDFILE execution.

## Release gate

Windows manual QA is still required for the Command Files workbench and the documented demonstration scenario.
