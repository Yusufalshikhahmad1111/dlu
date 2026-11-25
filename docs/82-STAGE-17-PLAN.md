# Stage 17 — Accessibility & Usability Audit

**Status:** COMPLETE

## Goal

Audit the desktop learning workflow against WCAG 2.2 principles while preserving the simulator's telecom/domain behavior.

## Audit scope

- contrast and semantic state communication;
- keyboard traversal and visible focus;
- text sizing and target-resolution readability;
- tooltips and discoverability;
- empty, error, and local-workflow state communication;
- Instructor/Classroom answer visibility;
- practical Windows/PySide6 adaptations.

## Acceptance

1. No core workflow depends on color alone.
2. Keyboard focus is visible on the primary controls.
3. Core controls have accessible names.
4. Ambiguous actions have tooltips.
5. Empty/error states are explicit.
6. 1280×720 remains usable; 1366×768, 1600×900 and 1920×1080 remain readable.
7. Stage 16 answer visibility cannot leak PASS/FAIL before reveal.
8. Focused, regression, static and Windows QA gates pass.

## Reference

WCAG 2.2 is used as the current W3C reference for this audit.

## Desktop adaptations

This is a native PySide6 application rather than a web page. The audit therefore uses Qt focus policy, tab order, accessible names/descriptions, tooltips, QPalette/QSS focus states, and explicit textual status labels as the desktop equivalents of the relevant accessibility outcomes.

## Final evidence

- Stage 17 focused tests: 5/5 PASS.
- Stage 16 compatibility tests: 7/7 PASS.
- Full regression: 134 PASS.
- Compile and UI static audit: PASS.
- Windows accessibility/resolution QA: PASS.
- PR #18 merged to main at 6d29fa93c7d9f80a3160590554481c78aedaa9e0.
