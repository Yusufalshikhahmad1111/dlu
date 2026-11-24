# Stage 12 — Closeout

## Status

**COMPLETE — merged to main after CI / Windows gate**

## Acceptance target

Students should be able to read the call story as:

Origin → CPT / Routing → Resource → Destination

and understand CONNECTED, BLOCKED, and RELEASED outcomes from the visual surface and explanation cards.

## Verified gates

- Windows Stage 12 QA: **passed**.
- Stage 12 focused tests: **7/7 passed**.
- Full test suite on the Stage 12 branch: **passed**.
- Main DLU CI: **passed** before merge.
- Functional visual QA: **passed** after fixing the QA runner import path.
- Final merge commit: `086b143b5f71efd904b4cef07c5465768726e228`.

## Technical constraints

- CallEngine semantics unchanged.
- MML semantics unchanged.
- No database migration.
- No new runtime dependency.
- Presentation-only animation.
- Morning/Night preserved.

## Final notes

Two QA-only issues were found and corrected before closure:

1. Blocked BLACK LIST calls were incorrectly inferred as requiring PDC-VOICE from number type alone; reservation display now follows the actual call result, with explicit handling for resource-busy outcomes.
2. The Stage 12 visual QA script was missing the repository root on `sys.path` when executed directly from `tools/`; the runner now adds the project root explicitly.

The Stage 12 QA timeout was also raised from 20 to 40 minutes so the existing full regression suite can complete reliably on the Windows runner.

## Next

Stage 12 is closed. The next roadmap stage is **Stage 13 — Communications Lab 2.0**.
