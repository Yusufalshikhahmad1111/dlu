# Stage 6 — Teaching Scenarios Plan

## Goal

Turn the existing hardware, MML, Call Engine and Command File demonstrations into a formal teaching-scenario layer with one consistent PASS/FAIL model.

## Academic boundary

Stage 6 must reuse the already implemented rules instead of inventing parallel behavior:

- source-backed hardware placements remain authoritative;
- MML remains the command execution surface;
- maintenance follows the documented FAULT → MBL → DIAG → REMOVE → INSTALL → ACTIVATE → VERIFY flow;
- subscriber billing suspension uses the existing `blk=accsusp` / `cblk` semantics;
- international blacklist uses the existing CPT `EVAL=NO` rule;
- overnight execution uses the Stage 4 deterministic virtual clock and command-file lifecycle.

## Scenario suite

1. **Aleppo 8-Line Expansion**
   - Build eight subscriber lines on the verified DLU 50 / Shelf 0 / Module 15 SLMA8.
   - Verify ports 0..7 and resulting subscriber records.

2. **CMRL Capacity Limit**
   - Build six CMRL lines on DLU 10 / Shelf 1 / Module 7.
   - Attempt port 6 and require the capacity guard to reject it.

3. **DLU / Card Maintenance**
   - Find a configured source-backed card with no subscriber assignment.
   - Inject a fault, diagnose it, remove the card, install the same verified replacement, activate it, and verify ACT + clear fault.

4. **Billing Block**
   - Use the existing demo subscriber.
   - Apply `blk=accsusp`, verify BLOCKED/accsusp, then `cblk` and verify service restoration.

5. **International Blacklist**
   - Resolve destination `00972`.
   - Attempt the call and require CALL-BLOCKED, path `DLU 50 → CPT / BLOCKED`, PDC 0/120 and caller IDLE.

6. **Command File Overnight Run**
   - Create a real Stage 4 command file.
   - Schedule it for 00:05, move virtual time from 23:55 across midnight, and verify one execution only.

## Definition of done

- All six scenarios have a shared result model.
- Every scenario reports commands/actions, affected EQN(s), expected result, actual result and PASS/FAIL.
- Scenarios execute through the real simulator services.
- Automated tests cover every scenario and the UI workbench.
- Existing Stage 1–5 tests remain green.
- README, milestones and release documentation reflect Stage 6.
- No new runtime dependency is introduced.
- Stage 6 is merged to main only after CI is green and release checks are reviewed.
