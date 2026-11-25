# Stage 16 — Windows QA

**Status:** PENDING

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
- guided demonstration reveals existing result steps progressively;
- reset delegates to the real demo reset;
- projector mode hides operational clutter;
- projector mode can be exited;
- Morning/Night styling is accepted.

## Quality gates

The stage closes only after:

- compile check passes;
- UI static audit passes;
- focused Stage 16 tests pass;
- full pytest regression passes;
- Windows functional visual QA passes;
- screenshots upload successfully;
- any QA defects are fixed and rerun.
