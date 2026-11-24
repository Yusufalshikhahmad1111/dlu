# Stage 12 — Call & Network Visualization Plan

## Objective

Transform the existing Call Path screen into a readable teaching visualization without changing any CallEngine decision or MML semantics.

The student should be able to answer:

1. Where did the call originate and where is it going?
2. Did routing require a resource reservation, and was that resource available?
3. Why did the call connect, block, or release?

## Scope

- signal-flow visualization;
- semantic phase strip: REQUEST / ROUTING / RESOURCE / CONNECTED / BLOCKED / RELEASED;
- route explanation;
- PDC resource state;
- blocked-call explanation;
- release explanation;
- one short controlled signal-flow animation after a successful connection;
- Morning/Night synchronization;
- Windows screenshot and regression coverage;
- projector-friendly, quick-case demonstration using the existing CallLab controls.

## Constraints

- \`dlu_app/call_engine.py\` remains the single source of truth.
- No new telecom routing rules.
- No database migration.
- No new runtime dependency.
- Existing CallLab controls and Quick Cases remain available.
- Animation is deterministic and presentation-only.
- State is communicated with labels as well as color.

## Architecture

\`dlu_app/stage12_ui.py\` owns the teaching presentation.

\`dlu_app/call_ui.py\` receives only a small renderer hook:
the existing \`CallPathView\` remains available as a fallback renderer, while the Stage 12 view becomes the visible renderer.

## Acceptance

A student can use LOCAL, NATIONAL, BLACK LIST, PDC-full, and RELEASE cases to explain the route, PDC behavior, and final outcome without reading the JSON details panel.
