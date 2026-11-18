# Stage 6 — Windows QA

## Automated gate

- Python compilation.
- UI static audit.
- Full pytest regression.
- Stage 6 scenario tests.
- Teaching Scenarios UI smoke test.

## Manual teaching checklist

### 1. Aleppo 8-Line Expansion

Open **Scenarios → Aleppo 8-Line Expansion**.

Expected:
- eight CREATE steps PASS;
- EQN 50-0-15-0..7 listed;
- final inventory reports 8 subscribers;
- overall PASS.

### 2. CMRL Capacity Limit

Run **CMRL Capacity Limit**.

Expected:
- ports 0..5 PASS;
- port 6 reports expected failure `MML-VALIDATION`;
- overall PASS.

### 3. DLU / Card Maintenance

Run **DLU / Card Maintenance** on a clean demo state.

Expected:
- FAULT-INJECTED;
- DIAG-FAULT;
- card removed;
- same verified card installed;
- replacement activated;
- final module ACT + clear fault;
- overall PASS.

### 4. Billing Block

Run **Billing Block**.

Expected:
- `blk=accsusp` creates BLOCKED / accsusp;
- `cblk` restores IDLE / NORMAL;
- overall PASS.

### 5. International Blacklist

Run **International Blacklist**.

Expected:
- CPT resolution identifies BLACK LIST;
- call returns CALL-BLOCKED;
- path is `DLU 50 → CPT / BLOCKED`;
- PDC remains 0/120;
- caller remains IDLE;
- overall PASS.

### 6. Command File Overnight Run

Run **Command File Overnight Run**.

Expected:
- file accepted;
- scheduled at 00:05;
- virtual clock crosses 23:55 → 00:05;
- exactly one execution;
- `scheduled_at` clears;
- overall PASS.

## Preservation gate

After scenarios, verify:
- Physical and Logical hardware views still open.
- OMT still accepts MML.
- Command Files still open.
- Call Path still works.
- Communications still opens.
- Hardware Library and Maintenance actions remain available.

## Repeatability note

Hardware-mutating scenarios intentionally do not wipe user data automatically. Use the existing **RESET DEMO** action before a clean teaching run when a previous scenario occupied the same training hardware.
