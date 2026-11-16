# Stage 3.5 — UX/UI + Hardware Visual Redesign

## Status

Implementation complete; Windows visual QA is the release gate.

## Implemented

- Space telecommunications visual system with brighter semantic colors.
- Simplified main toolbar with secondary Tools menu.
- Compact hardware path navigator with primary Open Module action.
- LAB ACTIONS teaching controls with stronger hierarchy for 8-Line and CMRL.
- OMT redesigned with a fixed, always-visible command dock.
- Larger command input and SEND action.
- New visual treatment for tabs, cards, buttons, inputs, tables, and status chips.
- DLU fleet redesigned as telecom rack cards instead of flat inventory rectangles.
- DLU Physical Mode redesigned as a rack/chassis with rails, controller bays, status lights, and shelf bays.
- Shelf redesigned as an equipment bay.
- Modules redesigned as card faceplates with technical areas, status cluster, and connector-style port indicators.
- Port rendering redesigned as connector/LED units while preserving EQN, click, and context interactions.
- Logical mode redesigned as a technical signal map.
- Call Path visual restyled as a futuristic signal-flow laboratory.
- Existing navigation, MML, maintenance, drag/drop, reference, and Call Engine behavior preserved.
- Rounded scene graphics use QPainterPath to avoid the previous QGraphicsScene API mistake.

## Preservation Rules

No Stage 1–3 domain behavior was intentionally changed by the redesign.

Preserved:
- DLU/Shelf/Module/Port addressing.
- EQN semantics.
- card capacities.
- MML behavior.
- CPT behavior.
- Call Engine and PDC accounting.
- existing click/double-click/context/drag-drop interactions.

## Manual QA

Windows runtime verification must confirm:
1. MML command dock is always visible in OMT.
2. Terminal scroll does not hide the command composer.
3. DLU home inventory remains clickable.
4. DLU Physical Mode resembles a rack/chassis.
5. Shelf rows remain clickable.
6. Module faceplates remain clickable and readable.
7. Port states remain readable and selectable.
8. Drag/drop card installation still works.
9. Logical mode opens without traceback.
10. Call Path remains readable.
11. 8-Line, CMRL, Maintenance, and Inspect still work.
12. 1280x720 and 1366x768 remain usable.
13. 1600x900 and 1920x1080 remain comfortable for projection.

## Release Gate

Stage 3.5 will be closed after the Windows visual audit confirms the appearance changes do not hide or break existing functionality.