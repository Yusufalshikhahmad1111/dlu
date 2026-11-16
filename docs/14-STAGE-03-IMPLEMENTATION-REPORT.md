# Stage 3 — Call Engine + CPT + Call Path

## Implemented

Stage 3 adds a deterministic call domain above the Stage 2 DLU/MML core.

### Domain and persistence
- CPT matching with exact, prefix, and numeric range support using the course CPT table.
- Number analysis for LOCAL, NATIONAL, INTERNATIONAL, SERVICE, and UNKNOWN cases.
- Persistent call sessions and call legs.
- Persistent PDC voice resource with capacity 120.
- Resource leases with atomic reservation and release.
- Call states CONNECTED, FAILED, and RELEASED.
- Call event records through the existing event_log mechanism.

### Routes
- Local: DLU → SN → DLU.
- National: DLU → LTG → SN → LTG → logical remote DLU/LAC.
- International: DLU → LTG → SN → International Gateway.
- Service: DLU → SN → Service.
- CPT EVAL=NO blocks before resource reservation.

### UI
- CALL ENGINE · CPT · CALL PATH tab.
- Caller selector backed by SQLite subscribers.
- Dialed-number input.
- PREPARE DEMO using the source-backed SLMA8 at DLU 50 / Shelf 0 / Module 15.
- Quick LOCAL, NATIONAL, INTERNATIONAL, and BLACK LIST cases.
- Visual Call Path boxes.
- Live PDC usage in the call view and SYP.
- Release restores subscriber ports and PDC resources.

## Academic boundary

National remote DLU nodes are displayed as logical DLU-LACxxx endpoints when the physical endpoint is not source-backed in the repository. This is explicitly a teaching route representation and does not claim an invented physical card placement.

## Acceptance

- Local call connects and marks two real subscriber ports busy.
- National call connects and reserves one of 120 PDC voice channels.
- International call connects and reserves one PDC voice channel.
- 00972 is rejected by CPT EVAL=NO with no resource reservation.
- Release restores busy ports and PDC usage.
- Existing Stage 1/2 tests remain part of CI regression.

Windows manual runtime verification remains the final visual release gate.
