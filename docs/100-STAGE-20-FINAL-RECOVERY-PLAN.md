# Stage 20 — Final Recovery & Closure Plan

Status: RECOVERY PLAN — NOT COMPLETE

## 1. Post-mortem

A final review found both technical drift and a release-process failure.

- Release run #46 (46078475744) failed at the Stage 20 focused release checks.
- The failing test expected the obsolete --write-version workflow marker after the implementation had already moved to a filesystem trigger/result probe.
- The focused suite therefore ended at 1 failed, 4 passed.
- PR #22 was nevertheless merged into main at merge commit b4e4f28f174c99201fe7dc11ef23cef595ddfcb5.
- After that merge, additional Stage 20 and CI commits continued changing the workflow, main.py, and release tests. This created a moving release target.
- docs/96-STAGE-20-PLAN.md still says IN PROGRESS.
- docs/99-STAGE-20-CLOSEOUT.md still says PENDING FINAL WORKFLOW EVIDENCE.
- README already identifies DLU Lab 2.0.0 as the current release identity, but release identity is not proof of final release-gate success.

## 2. Errors to prevent

### E1 — Never merge on a failed or incomplete release gate

A Stage 20 PR is not considered ready for merge until the exact candidate commit has:

- Stage 20 focused checks green.
- Stage 17, Stage 18, and Stage 19 compatibility green.
- Full regression green.
- Windows visual/accessibility QA green.
- Windows onefile packaging green.
- Packaged smoke test green.
- Packaged version verification green.
- Required release artifacts present.

### E2 — Freeze the release candidate

Do not keep changing the workflow or release code while a run is being used as release evidence.

Any failure-driven change creates a new candidate SHA and invalidates previous release evidence.

### E3 — Keep tests synchronized with the implementation

Release tests must verify the actual current contract:

- current packaged probe mechanism;
- current workflow job structure;
- current artifact names;
- current packaging mode.

No obsolete implementation marker should remain in a release test.

### E4 — Separate CI mechanics from telecom correctness

Stage 20 may change release probes, packaging, QA harnesses, regression orchestration, and documentation.

Stage 20 must not change:

- MML semantics;
- Call Engine decisions;
- Communications calculations;
- Teaching Scenario semantics;
- the database domain model.

### E5 — Do not close the roadmap early

The Stage 20 plan, implementation report, Windows QA, closeout, milestones, and README may only claim COMPLETE after final evidence exists on the final merged main commit.

## 3. Expert recovery sequence

### Gate 0 — Baseline

- Treat current main as the only source of truth.
- Record the current main SHA.
- Compare it to the Stage 19 merge SHA.
- Inventory post-Stage-19 commits.
- Confirm there is one intended release candidate.

### Gate 1 — Freeze

Create one final release branch from current main.

After that:

- no unrelated CI cleanup;
- no cosmetic refactors;
- no new functionality;
- no repeated alternative probe mechanisms.

Only fix a failure observed by the current release gate.

### Gate 2 — Deterministic validation

On the exact candidate SHA:

1. Compile check.
2. UI static audit.
3. Stage 20 focused tests.
4. Stage 17 compatibility.
5. Stage 18 compatibility.
6. Stage 19 compatibility.

Any failure blocks release.

### Gate 3 — Full regression

Run the repository regression suite as the release contract.

Record the exact passed count and tie it to the same candidate SHA.

### Gate 4 — Windows release QA

Run the final Windows QA matrix:

- 1280x720 Morning;
- 1366x768 Morning;
- 1600x900 Morning;
- 1920x1080 Morning;
- 1366x768 Night;
- OMT/MML interaction;
- real Local Call;
- Communications experiment;
- Teaching Scenario result;
- Instructor hidden answers;
- reveal answers;
- projector mode;
- Reset resulting in RESET.

Any failure blocks release.

### Gate 5 — Windows onefile package

On the same candidate SHA:

- build the Windows onefile executable;
- run packaged smoke-test;
- verify the packaged version is exactly DLU Lab 2.0.0;
- upload the Windows executable;
- upload Stage 20 screenshots;
- upload build screenshots.

No artifact is treated as final evidence unless it came from the final green run.

### Gate 6 — Evidence freeze

Record:

- candidate SHA;
- workflow run ID;
- job conclusions;
- Stage 20 focused count;
- Stage 17/18/19 counts;
- regression count;
- Windows QA result;
- packaging result;
- smoke result;
- packaged version result;
- artifact names, IDs, and digests where available.

### Gate 7 — Merge discipline

Only after Gate 6 is green:

- merge the single final PR;
- record the merge commit SHA;
- verify main points to the merged result;
- verify no unexpected files or commits appeared during the merge.

### Gate 8 — Post-merge verification

Because the Stage 20 workflow also runs on main, verify the release workflow on the actual merge commit.

If post-merge verification fails, Stage 20 remains incomplete.

### Gate 9 — Documentation closeout

Only after post-merge verification is green:

- mark docs/96-STAGE-20-PLAN.md COMPLETE;
- finalize docs/97-STAGE-20-IMPLEMENTATION-REPORT.md;
- finalize docs/98-STAGE-20-WINDOWS-QA.md;
- finalize docs/99-STAGE-20-CLOSEOUT.md;
- synchronize docs/05-MILESTONES.md;
- synchronize README.md.

### Gate 10 — Final audit

Confirm:

- Stage 0 to Stage 20 roadmap is internally consistent;
- release version is 2.0.0 everywhere;
- no stale 1.0.0 release claim remains in active release docs;
- no obsolete release-probe contract remains in tests;
- no new telecom semantics were introduced in Stage 20;
- final artifacts and documentation describe the same release.

## 4. Hard stop rules

Stop and repair when:

- a required job is red;
- a required job is unexpectedly skipped or cancelled;
- tested SHA differs from the intended release candidate;
- artifacts are missing;
- docs claim COMPLETE before evidence exists;
- a workflow test checks an obsolete implementation detail;
- the candidate changes after green evidence was collected;
- a merge occurs before the complete release gate is green.

## 5. Final definition of DONE

Stage 20 is COMPLETE only when:

same candidate SHA
-> all release gates green
-> artifacts present
-> PR merged
-> post-merge main verification green
-> documentation synchronized
-> final closeout recorded.

Until then the correct status is RECOVERY / IN PROGRESS.
