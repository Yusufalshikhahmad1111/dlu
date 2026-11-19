# DLU Lab — Design System Specification

**Status:** Target specification for Stage 8  
**Visual direction:** Deep Navy / Graphite / Cyan / Emerald / Amber

## 1. Purpose

Create one visual language for the complete DLU Lab application.

The system must work across:

- application shell;
- hardware views;
- OMT/MML;
- calls;
- command files;
- communications;
- scenarios;
- dialogs;
- tables;
- inspector panels;
- teaching overlays.

## 2. Color tokens

### Base

`color.bg = #0B1220`
`color.surface = #111827`
`color.surface.elevated = #172033`
`color.surface.interactive = #1D2A3D`

### Content

`color.text.primary = #F8FAFC`
`color.text.secondary = #CBD5E1`
`color.text.muted = #94A3B8`
`color.border = #334155`

### Semantic

`color.primary = #22D3EE`
`color.success = #22C55E`
`color.warning = #F59E0B`
`color.danger = #EF4444`
`color.info = #38BDF8`

### Rule

Semantic colors communicate state, not decoration.

## 3. Typography

Use a safe Windows-first sans-serif stack with no mandatory external font dependency.

Recommended hierarchy:

- Display: 24–32 px equivalent
- H1: 20–24
- H2: 16–20
- Body: 13–15
- Secondary: 11–13
- Micro label: 10–11

Numbers used for telemetry/EQN/capacity should use a font configuration that keeps digits visually stable.

## 4. Spacing

Use a small consistent spacing scale:

- 4
- 8
- 12
- 16
- 20
- 24
- 32

Avoid arbitrary per-widget spacing unless a documented exception is necessary.

## 5. Surfaces

### Page
Main application background.

### Panel
Primary content container.

### Elevated panel
Selected/important content with stronger separation.

### Inspector
Contextual information about the selected hardware/operation.

### Console
Command-oriented area, visually subordinate unless the current task is command work.

## 6. Components

Required shared components:

- PrimaryButton
- SecondaryButton
- DangerButton
- ToolbarButton
- StatusChip
- SectionHeader
- ContextInspector
- MetricCard
- EmptyState
- ErrorState
- SuccessBanner
- WarningBanner
- TabNavigation
- Breadcrumb
- CommandInput
- ResultCard
- DataTable
- Timeline
- StepProgress
- Legend
- Tooltip

Each component must define:

- normal;
- hover;
- pressed;
- focused;
- disabled;
- selected;
- error where relevant.

## 7. State representation

Every important state must have at least two channels of communication.

Example:

ACTIVE → green + explicit ACTIVE label  
MBL → amber + MBL label  
FAULT → red + fault icon/label  
BLOCKED → red/amber distinction + BLOCKED label  
TEST → blue + TEST label

## 8. Focus behavior

Core controls must provide a visible keyboard focus state.

The design should exceed the minimum visibility requirements where practical.

## 9. Layout rules

### Primary shell

Top:
- identity;
- system state;
- global quick actions.

Main navigation:
- six/seven primary learning areas.

Center:
- current task.

Context:
- current selection or operation details.

Secondary/advanced:
- dialogs, menus, or expandable sections.

## 10. Iconography

Use consistent icon semantics.

Do not use icons as decoration where an icon implies an action.

Every icon-only button requires a tooltip and accessible label.

## 11. Motion

Motion should explain state, not distract.

Allowed:
- subtle selection transitions;
- call-flow progression;
- scenario progress;
- panel expand/collapse.

Avoid:
- continuous decorative animation;
- flashing;
- excessive bouncing;
- animation that blocks interaction.

## 12. Production styling strategy

Stage 8 should establish a central style/token layer.

Use Qt's production styling mechanism deliberately. Qt documents QStyle/StyleKit as production-oriented approaches and QSS as useful mainly for prototyping/local adjustments.

Do not grow runtime theme switching through scattered widget-level Style Sheets.

References:
https://doc.qt.io/qt-6.12/qtwidgets-styling-approaches.html
https://doc.qt.io/qt-6/style-aware-widgets.html

## 13. Acceptance

A new component is not accepted unless:

- it uses tokens;
- states are defined;
- keyboard focus is visible;
- labels remain readable;
- no unrelated color is introduced;
- it behaves consistently across the application.
