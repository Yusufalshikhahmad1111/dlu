# Stage 15 — Academic Learning Layer Plan

**Status:** COMPLETE — implementation and QA gates passed

## Goal

Connect the existing simulator capabilities into one coherent academic progression:

**Learn → Practice → Experiment → Challenge → Verify**

## Academic mapping

- **Learn:** Hardware + OMT/MML establish the DLU structure and operational vocabulary.
- **Practice:** Calls + Command Files provide repeatable simulator workflows.
- **Experiment:** Communications Lab provides observable signal/modulation/BER experiments.
- **Challenge:** Teaching Scenarios turn the existing rules into guided application tasks.
- **Verify:** Session evidence confirms that the student visited all six existing learning areas.

## Scope

Stage 15 is a presentation and learning-flow layer over existing modules.

It does not replace or duplicate:
- hardware logic;
- MML engine;
- CallEngine/CPT;
- Command File engine;
- communications calculations;
- TeachingScenarioRunner.

## Delivered design

- academic path shown on Learning Home;
- five phase cards with status and evidence;
- contextual action buttons routing to existing learning areas;
- session-only progress over the existing six learning areas;
- explicit verification step based on session evidence;
- verification reset when the teaching demo is reset;
- Morning/Night synchronization;
- no database migration;
- no new runtime dependency.

## Quality gates

- compile;
- UI static audit;
- focused Stage 15 tests;
- full regression;
- Windows functional visual QA;
- screenshots;
- synchronized documentation.

## Execution rule

Implement → Tests → Visual QA → Manual Demo → Fix → Report → Commit.
