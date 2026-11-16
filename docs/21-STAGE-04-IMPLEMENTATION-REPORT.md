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
- source line numbers are preserved in parser and execution logs.

### Scheduling
- HH:MM scheduling.
- persisted scheduled_at value.
- explicit virtual clock.
- manual clock advance.
- due-file execution when the virtual clock reaches the scheduled time.
- deterministic midnight rollover handling.
- completed/failed scheduled files clear scheduled_at and cannot be re-fired accidentally.

### OMT / MML
Supported:
> execmdfile: file=block-demo;
> execmdfile: file=block-demo, time=02:00;

The scheduled form records an Accepted command file with its run time. The immediate form executes the same stored command file synchronously through the existing MML engine.

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

## Automated hardening coverage
- virtual clock validation and rollover.
- source line preservation.
- malformed command rejection.
- nested EXECMDFILE rejection.
- Accepted → Started → Finished → Executed lifecycle.
- failure/fail-fast lifecycle.
- persisted execution logs and event sequence.
- scheduling and due execution.
- no duplicate scheduled execution.
- EXECMDFILE scheduling and immediate execution.

## Release gate

Automated QA is ready for the CI release gate. Windows manual QA is still required before Stage 4 can be closed.
