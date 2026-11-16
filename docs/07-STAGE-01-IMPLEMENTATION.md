# 07 — Stage 1 Implementation Plan

## Objective

Build the smallest executable foundation that proves the model is correct before any advanced UI work.

The output of Stage 1 is not a pretty interface. It is a tested local database plus a deterministic domain layer that can answer:

- What card exists at EQN?
- How many ports does that card expose?
- Is the port free or occupied?
- Which DN owns it?
- Is the DLU side active, standby, or maintenance?
- Can the next command legally execute?

## Proposed source layout

~~~text
src/
  core/
    domain/
      eqn/
      dlu/
      subscriber/
      cpt/
      alarms/
      events/
    mml/
    application/
  infrastructure/
    db/
      migrations/
      repositories/
      seed/
  ui/
    app/
    components/

src-tauri/
  src/
  capabilities/
~~~

The domain core remains UI-independent.

## Stage 1 database schema

Implement the tables defined in docs/02-DATABASE-SPEC.md:

- exchanges
- dlus
- slots
- subscribers
- cpt_routes
- alarms
- command_files
- event_log

Use SQL constraints for structural invariants and TypeScript policies for educational/business rules.

## Seed order

1. Create ALE1.
2. Create DLU 10.
3. Create DLU 50.
4. Create the 8 shelves per DLU.
5. Create the 16 slots per shelf.
6. Place only the cards required for the first academic scenarios.
7. Seed CPT.
8. Seed the first subscriber/demo data.

Do not prepopulate every theoretical card or subscriber. A smaller deterministic seed makes tests and demonstrations easier to understand.

## First repository API

~~~ts
interface SubscriberRepository {
  findByDn(lac: string, dn: string): Promise<Subscriber | null>;
  findByEqn(eqn: EqnAddress): Promise<Subscriber | null>;
  create(input: CreateSubscriberInput): Promise<Subscriber>;
  remove(lac: string, dn: string): Promise<void>;
  update(lac: string, dn: string, patch: SubscriberPatch): Promise<Subscriber>;
}
~~~

Equivalent repositories will exist for DLU, Slot, CPT, and alarms.

## First domain policies

### CardCapacityPolicy

Returns the legal port range:

- CMRL → 0..5
- SLMA8 → 0..7
- SLMA16 → 0..15
- SLMD → defined separately when its teaching behavior is implemented

### EqnPolicy

Validates:

- DLU identifier.
- shelf 0..7.
- module 0..15.
- port capacity by card.

### DluStatePolicy

Validates:

- active/standby relation.
- maintenance requirement before diag.
- no invalid dual state.

## First automated tests

Minimum target before Stage 2:

1. Valid EQN parses.
2. Invalid shelf is rejected.
3. Invalid module is rejected.
4. SLMA8 port 7 succeeds.
5. SLMA8 port 8 fails.
6. CMRL port 5 succeeds.
7. CMRL port 6 fails.
8. Duplicate DN fails.
9. Duplicate EQN fails.
10. Cancel releases the port.
11. DLU active → mbl is valid.
12. diag on act is rejected.
13. diag on mbl is accepted.
14. No-active-side creates CRITICAL alarm.
15. SQLite transaction rolls back on a failed multi-step operation.

## Stage 1 demo

The first runnable demo should execute a scripted sequence without the graphical DLU:

~~~text
CREATE ALE1
LOAD DLU 50
LOAD SLMA8 AT 50-1-5

> cr sub: dn=2233500, eqn=50-1-5-0, lac=021, class=ms, c/s=PB;
> disp sub: dn=2233500;
> can sub: lac=021, dn=2233500;
~~~

Expected result:

- create succeeds.
- display returns the correct DN/EQN.
- cancel succeeds.
- port is free again.

This proves that the core model is working before we spend time on visual rendering.

## Stage 1 exit criteria

Stage 1 is complete only when:

- SQLite schema is created from migration(s).
- seed is deterministic.
- repository tests pass.
- all academic address/capacity rules above pass.
- transaction rollback is tested.
- no UI code contains domain rules.
- the Stage 1 report can explain every failed test.

## What comes next

Stage 2 will implement the MML Lexer/Parser/Normalizer/Validator/Dispatcher on top of this foundation and convert the academic test cases into executable MML tests.
