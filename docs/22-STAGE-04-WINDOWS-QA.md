# Stage 4 — Windows QA Checklist

## 1. Open
- Start with run.bat.
- Open Command Files tab.

## 2. Demo
- Press LOAD DEMO.
- Confirm file name block-demo.
- Confirm the editor contains:
  - block-demo header.
  - MOD SUB command.
  - DISP SUB command.
  - END FILE.

## 3. Accept
- Press ACCEPT.
- Confirm status becomes ACCEPTED.
- Confirm block-demo appears in the file list.

## 4. Execute
- Press EXECUTE.
- Confirm status becomes EXECUTED.
- Confirm execution log contains each command result.
- Confirm the subscriber state changed according to the MOD command.
- Confirm the executed file no longer shows a pending scheduled time.

## 5. Schedule
- Load the demo again.
- Set schedule time to a future virtual time.
- Press ACCEPT, then SCHEDULE.
- Confirm file shows ACCEPTED with @HH:MM.

## 6. Virtual Clock
- Confirm the clock is visible.
- Advance time with +5 MIN or +1 HOUR.
- Before the scheduled time, the file remains ACCEPTED.
- At/after the scheduled time, it executes automatically.
- Confirm status becomes EXECUTED.
- Confirm its scheduled time is cleared after execution.
- Repeat once more and confirm it does not execute a second time.
- Test a schedule crossing midnight.

## 7. Failure
- Create a file with a valid command followed by an invalid/nonexistent target.
- ACCEPT.
- EXECUTE.
- Confirm status becomes FAILED.
- Confirm execution log shows the successful command followed by the failed command.
- Confirm the file is not still pending for scheduled execution.

## 8. Parser safety
- Verify malformed commands are rejected with the correct source line number.
- Verify nested EXECMDFILE is rejected.

## 9. OMT integration
Use:
> execmdfile: file=block-demo;

Then:
> execmdfile: file=block-demo, time=02:00;

Confirm the same stored command file is used by OMT and the Command Files workbench.

## 10. Regression
- OMT direct commands still work.
- Call Path still works.
- Hardware still works.
- Stage 1–3 behavior remains unchanged.
