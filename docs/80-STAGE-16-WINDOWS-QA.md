# Stage 16 — Windows QA

**Status:** COMPLETE — Windows QA passed

## Visual coverage

The functional runner captures:

1. Instructor home — Morning.
2. Scenario result with answers hidden — Morning.
3. Guided demonstration with answers revealed — Morning.
4. Projector mode — Night.
5. Reset state — Night.

## Functional coverage

- six scenarios load;
- real scenario execution reaches PASS;
- answer visibility is off by default;
- expected/actual and PASS/FAIL remain hidden until explicitly revealed;
- guided demonstration reveals existing result steps progressively;
- reset delegates to the real demo reset;
- projector mode hides operational clutter;
- projector mode can be exited;
- Morning/Night styling is accepted.

## Final quality gates

- compile check: PASS;
- UI static audit: PASS;
- Stage 16 focused tests: **7/7 PASS**;
- full pytest regression: **129 passed in 809.92s**;
- Windows functional visual QA: PASS;
- screenshot upload: PASS;
- screenshot artifact: `DLU-Stage16-Instructor-Classroom-QA`;
- artifact ID: `15033479880`;
- five screenshots uploaded successfully.

## Defect found and fixed

The first focused run exposed an offscreen Qt visibility assertion that checked `isVisible()` on a widget whose parent was not shown. The test was corrected to assert the widget's hidden/visible state directly. A second review also removed PASS/FAIL leakage while answer visibility was disabled, including projector mode.

