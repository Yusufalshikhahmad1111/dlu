# Stage 8 — Windows UX/UI QA

**Status:** Automated pre-merge gate passed; packaged visual gate runs after merge

## Automated pre-merge gate

- Windows Server runner: PASS
- Compile: PASS
- UI static audit: PASS
- Pytest: **79 passed**
- Stage 8 shell test: PASS
- Design token/contrast tests: PASS

## Visual checklist

Target resolutions:
- 1280×720
- 1366×768
- 1600×900
- 1920×1080

Required screens:
- Main workbench
- Teaching Scenarios
- Calls
- Communications
- Command Files

## Acceptance

The final release gate must confirm:
- deep navy/graphite visual identity is applied;
- old brown/ivory presentation is absent from the primary shell;
- LAB navigation is visible and functional;
- renamed feature tabs are readable;
- no clipping/overlap occurs;
- packaged executable starts successfully;
- screenshots are generated successfully.

## Boundary

The repository toolchain has verified the Windows runner and automated UI construction. A separate physical end-user session on a personal Windows device is not claimed.
