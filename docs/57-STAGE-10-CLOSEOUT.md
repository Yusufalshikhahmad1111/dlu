# Stage 10 — Hardware UX 2.0 Closeout

## Status

**CLOSED**

Stage 10 is merged to `main` and verified on Windows.

## Delivered

- Persistent Hardware Inspector beside the hardware workspace.
- Exchange → DLU → Side/Controller → Shelf → Module → Port → Subscriber context.
- Hover inspection without unrelated dialogs.
- Selection/hover highlighting.
- Explicit state communication.
- EQN and capacity presentation.
- Maintenance/fault visibility.
- Morning/Night theme synchronization.
- Presentation-only interaction targets.
- Safe Qt event-filter and graphics-object lifecycle handling.

## Integrity

No database migration was added.  
No new hardware placement or capacity was invented.  
No MML, Call Engine, Communications, Scenario, or maintenance domain logic was duplicated.  
The existing database and simulator renderer remain the source of truth.

## Verification

- 90/90 Windows tests passed.
- Stage 8 compatibility QA passed.
- Stage 9 compatibility QA passed.
- Stage 10 Windows QA passed.
- Main CI passed.
- Windows onefile build and smoke-test passed.

## Merge

PR #10: `stage10: Hardware UX 2.0`  
Merge SHA: `c01f32b9c030d7bb7d3e7eaa82520c66bcc0da97`

## Next

**Stage 11 — OMT/MML UX 2.0**

The next stage must preserve the same principle: improve the teaching UX around the existing MML engine without duplicating command semantics or domain behavior.
