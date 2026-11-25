# Stage 14 — Teaching Scenarios 2.0 Plan

**Status:** COMPLETE — implementation and QA gates passed

## Goal

Turn the six existing deterministic Teaching Scenarios into guided labs:

**Objective → Observe → Execute → Diagnose → Fix → Verify → Result**

## Academic boundary

Stage 14 is presentation and instructional guidance only.

- TeachingScenarioRunner remains the sole scenario executor.
- MML, DB, Call Engine, CPT, Command File and hardware rules are unchanged.
- Existing expected results remain authoritative.
- No new runtime dependency.
- No database migration.

## Delivered design

The Stage 14 workbench adds:

- phase rail and explicit current phase;
- scenario objective and observation guidance;
- controlled Execute action calling the existing runner;
- step-level diagnosis and first-failure explanation;
- recovery/fix guidance;
- verification summary with passed-step count and affected EQNs;
- rotating hints for every scenario;
- explicit PASS / FAIL symbols and text;
- existing command copy and reset workflows;
- Morning/Night theme synchronization.

## Scenario coverage

All six existing scenarios:

1. Aleppo 8-Line Expansion
2. CMRL Capacity Limit
3. DLU / Card Maintenance
4. Billing Block
5. International Blacklist
6. Command File Overnight Run

## Quality gates

- compile;
- UI static audit;
- focused Stage 14 + existing scenario tests;
- full regression;
- Windows functional visual QA with screenshots;
- documentation synchronized before merge.

## Execution rule

Implement → Tests → Visual QA → Manual Demo → Fix → Report → Commit.
