# Stage 9 — Student-Centered Navigation QA

Status: **PASSED — Windows CI / functional / visual gates verified**

## Functional

- Application opens on Learning Home after Stage 9 is applied.
- HOME is visibly active.
- Continue Learning is enabled.
- Six Quick Start actions exist.
- Opening a learning area restores the technical workspace.
- Active navigation follows the selected area.
- Returning HOME collapses the technical workspace again.
- Direct feature-tab selection synchronizes student context.
- Session progress and recent activity update.
- Morning/Night theme switching remains functional.
- Existing Stage 8 tab ordering remains compatible.

## Keyboard

- Navigation controls are focusable.
- Tab traversal can leave HOME.
- Space activates a focused learning action.
- The regression test explicitly shows the window before checking focus ownership.

## Visual

Windows Stage 9 QA generated and uploaded screenshots for:

- 1280×720
- 1366×768
- 1600×900
- 1920×1080
- OMT/MML at 1600×900
- Night Home at 1600×900

Artifact:
DLU-Stage9-Navigation-QA — GitHub Actions artifact 14698893749.

## Regression

Final branch verification:
- Python compile: PASS.
- UI static audit: PASS.
- Full test suite: 85 passed.
- Stage 8 v2 functional/visual QA: PASS.
- Stage 9 functional/visual QA: PASS.

Main verification after hotfix merge:
- DLU CI: PASS.
- Windows release build + executable smoke-test: PASS.

## Packaging

Windows release artifacts produced from main after Stage 9/hotfix integration:
- DLU-Lab-Windows — artifact 14699850606.
- DLU-Lab-Screenshots — artifact 14699556470.

## Evidence

- Stage 9 QA run: 44883972243.
- Main CI run: 44884189597.
- Windows release run: 44884189584.
