# Stage 8 Rework — UX/UI Reimagination v2 Plan

Status: In progress — supersedes the first Stage 8 visual direction.

## Why v2

The first Stage 8 established a design-system layer but the visual direction was not accepted: it was too blue/dark and the old feature UI remained visually dominant.

The v2 goal is a calmer, more premium university-product experience:

- morning mode: warm white + soft green;
- night mode: charcoal-green + soft mint;
- one component system shared by both modes;
- no blue/black product identity;
- real, visible theme switching;
- MML/Command workbench treated as a first-class learning surface.

## Non-negotiables

1. Do not change EWSD hardware facts, source-backed placements, MML semantics, CallEngine decisions, communications calculations, or scenario expected results.
2. Do not create a second command engine.
3. Do not hide the theme system from the user.
4. Do not rely on color alone for state communication.
5. Test actual button execution, not only widget construction.

## Product direction

Visual language:

University communications laboratory + modern productivity application.

Interaction language:

quiet surfaces → clear hierarchy → one obvious primary action → progressive disclosure.

## v2 acceptance gates

- Morning theme visually coherent.
- Night theme visually coherent.
- Theme toggle works in-place.
- Navigation reaches every major lab.
- OMT/MML command entry executes real commands.
- Command errors remain visible and recoverable.
- Existing domain tests remain green.
- Windows CI remains green.
