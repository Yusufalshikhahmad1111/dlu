# Stage 10 — Hardware UX 2.0 Plan

## Purpose

Make the hardware workspace the visual teaching centerpiece while preserving the existing source-backed database and simulator engines.

## Scope

The implementation is presentation-only:

- Exchange → DLU → Side/Controller → Shelf → Module → Port → Subscriber context.
- One persistent Hardware Inspector visible beside the hardware canvas.
- Hover inspection without opening dialogs.
- Selection highlighting for interactive hardware targets.
- Explicit state labels, not color alone.
- EQN and capacity always available for the selected object.
- Maintenance/fault state surfaced in the same inspector.
- Existing navigation, MML, maintenance, drag/drop, and database behavior remain the source of truth.

## Deliberate non-goals

- No new hardware placements.
- No new card capacities.
- No new simulator state machine.
- No duplicate MML/domain logic.
- No destructive DB/schema migration.
- No replacement of the existing hardware renderer.

## Acceptance

A student can select or hover an Exchange, DLU, Side/Controller, Shelf, Module, Port, or Subscriber and understand its role, state, capacity, and address context without opening an unrelated dialog.

## Quality gate

Implement → tests → visual QA → manual demo → fix → report → commit.
