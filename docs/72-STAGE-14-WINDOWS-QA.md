# Stage 14 — Windows QA

**Status:** COMPLETE — Windows QA passed

## Functional visual coverage

The QA runner captures:

- Objective / Observe — Morning;
- executed PASS scenario — Morning;
- guided Hint state — Night;
- International Blacklist diagnosis — Night.

## Acceptance

The stage is complete only after:

1. focused Stage 14 + existing scenario tests pass;
2. compile check passes;
3. UI static audit passes;
4. full regression passes;
5. Windows functional visual QA passes and screenshots upload successfully;
6. any defects found in QA are fixed and rerun.


## Final evidence

- Windows QA passed compile, static audit, focused tests, full regression, functional visual QA and screenshot upload.
- Artifact: \`DLU-Stage14-Teaching-Scenarios-2-QA\`.
- Five screenshots cover Objective, Observe, executed PASS, Hint/Night, and International Blacklist diagnosis.
- CI screenshot rendering showed some Segoe UI glyphs as square boxes in the headless artifact. This was treated as a runner/font-rendering limitation; no production font change was introduced solely to satisfy the headless renderer.
- The actual guided workflow, state transitions, PASS/FAIL semantics and scenario execution were validated by the functional QA run.
