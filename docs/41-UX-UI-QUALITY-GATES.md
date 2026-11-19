# DLU Lab — UX/UI Quality Gates

## 1. Visual gate

Every UX/UI stage must pass:

- 1280×720
- 1366×768
- 1600×900
- 1920×1080

No clipping, overlapping, unreadable text, or broken splitter behavior.

## 2. Interaction gate

Test:

- mouse;
- keyboard;
- Tab traversal;
- Enter/Space activation where appropriate;
- Escape for dismissible dialogs;
- tooltips;
- context menus;
- double-click actions where documented.

## 3. Accessibility gate

Check:

- normal text contrast target >= 4.5:1;
- large text target >= 3:1;
- non-text UI state contrast;
- visible keyboard focus;
- no state communicated by color alone.

Use W3C guidance as the accessibility reference:
https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum
https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast
https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance

## 4. UX comprehension gate

For the main workflows, a reviewer must be able to answer:

- What is selected?
- What is this object?
- What is its current state?
- What action is recommended?
- What happened after the action?

## 5. Academic preservation gate

All previous academic workflows remain functional:

- hardware inspection;
- card operations;
- OMT/MML;
- call paths;
- command files;
- communications labs;
- six teaching scenarios.

## 6. Regression gate

All automated tests must pass.

No UX stage may silently reduce or remove previously supported behavior.

## 7. Performance gate

The redesign must avoid:

- repeated full-tree restyling for small state changes;
- unnecessary scene rebuilds;
- unbounded widget creation;
- expensive animations;
- UI thread blocking during domain operations.

## 8. Packaging gate

When a stage changes startup or resource behavior:

- packaged Windows smoke test;
- no missing assets;
- no broken icon/font/style resources;
- release workflow remains green when applicable.

## 9. Documentation gate

Every closed stage gets:

- implementation report;
- visual QA report;
- closeout note;
- updated milestone status.
