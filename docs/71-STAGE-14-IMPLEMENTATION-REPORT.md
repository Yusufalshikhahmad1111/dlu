# Stage 14 — Teaching Scenarios 2.0 Implementation Report

**Status:** Implemented on stage-14-teaching-scenarios-2

## Delivered

Added \`dlu_app/stage14_ui.py\` as a presentation layer over the existing TeachingScenarioRunner.

The UI now guides each scenario through:

1. Objective
2. Observe
3. Execute
4. Diagnose
5. Fix
6. Verify
7. Result

### Student guidance

- scenario-specific observation instructions;
- scenario-specific recovery guidance;
- rotating hints;
- first failing step explanation;
- explicit expected vs actual;
- affected EQN verification;
- passed-step count;
- unambiguous PASS / FAIL labels;
- existing command-copy and RESET DEMO actions retained.

### Domain preservation

The Stage 14 widget calls the existing \`TeachingScenarioRunner.run()\` and does not reproduce its rules.

No changes were made to:
- \`teaching_scenarios.py\` semantics;
- MML;
- CallEngine/CPT;
- hardware database;
- command-file engine;
- SQLite schema.

## QA infrastructure

Added:
- \`tests/test_stage14_teaching_scenarios_2.py\`
- \`tools/stage14_scenarios_qa.py\`
- \`.github/workflows/stage14-scenarios-qa.yml\`

