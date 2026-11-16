# 12 — Stage 2 Hardware Fidelity Implementation Report

## Status

Implementation is complete in the repository; final Windows CI/manual verification remains the release gate.

## Implemented

### Hardware data
- source-backed registry
- DLU 10..250
- Shelf 0..7
- Module 0..15
- SLMA8 / SLMA16 / SLMA64
- CMRL
- SLMD
- TU / BDE / BDCG / DLUC / DIUD / RGMG / DCC
- authoritative placements from course examples
- unknown placements remain UNCONFIGURED

### Visualizer
- DLU hardware frame
- DLUC0/DLUC1
- DIUD/PDC training blocks
- shelf rendering
- module faceplates
- port LED grid
- hover tooltips
- Physical / Logical mode
- hardware navigator

### OMT
- DLU status
- module display/status
- port display/status
- subscriber display/status/test
- create/cancel/modify subscriber
- DLU/module configuration and diagnostics
- CPT/alarm inspection
- compact and case-insensitive syntax
- result-to-hardware focus

### Maintenance
- fault injection
- maintenance state
- diagnostic guard
- card remove
- verified replacement install
- activate
- hardware event timeline

### Teaching tools
- Hardware Library
- Reference Viewer
- COPY MML
- 8-Line scenario with location picker
- CMRL six-port scenario with port-6 rejection
- maintenance scenario
- Reset Demo

## Source boundary

The course material is treated as the primary hardware source. External references are used only for future details that are not explicit in the course material.

## Acceptance scenario

DLU 50 → Shelf 0 → Module 15 → SLMA8 → Port 0 → DN → OMT STAT/DISP/TEST → Maintenance → Replacement → ACT

## Known validation gate

The GUI cannot be visually exercised inside this repository automation environment. The CI workflow is the authoritative code-level gate; manual Windows execution remains required before calling the Stage release-final.
