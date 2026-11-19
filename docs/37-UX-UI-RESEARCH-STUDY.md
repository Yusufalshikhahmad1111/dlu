# DLU Lab — Detailed UX/UI Research Study

**Status:** Planning research  
**Date:** 2026-11-19

## 1. Research question

How should a Windows/PySide6 educational telecom simulator present an already-correct technical core so that:

- students can discover the workflow quickly;
- complex telecom state is readable;
- advanced controls do not overwhelm beginners;
- instructors can demonstrate the same system efficiently;
- the redesign remains maintainable in Qt Widgets.

## 2. Repository evidence

### Current product strengths

The repository already contains:

- source-backed hardware data;
- Physical and Logical hardware modes;
- MML parser/engine;
- command files;
- call engine and CPT;
- communications laboratories;
- six formal teaching scenarios;
- backup/restore;
- Windows packaging and release QA.

This means the highest leverage is now **presentation and learning flow**, not another independent simulation layer.

### Current UI constraint

`dlu_app/ui.py` is a large monolithic UI module and currently owns substantial shell/navigation/presentation responsibilities.

`dlu_app/theme.py` currently exposes two themes:

- ivory: brown/ivory;
- silver: dark brown/gray.

The current shell combines:

- top header;
- DLU selection;
- Physical/Logical mode controls;
- theme switch;
- system status;
- severity/traffic/path status strip;
- breadcrumb;
- tools;
- hardware navigation;
- command-oriented surfaces.

This is powerful, but dense.

## 3. External research findings

### 3.1 Progressive disclosure

Nielsen Norman Group describes progressive disclosure as a way to improve learnability by focusing novice users on the most useful features while hiding advanced features until needed.

**DLU implication:** do not expose every advanced telecom operation at the same visual weight. Put advanced controls behind contextual actions, secondary panels, or progressive details.

Source:
https://www.nngroup.com/articles/progressive-disclosure/

### 3.2 Qt production styling

Qt documentation distinguishes between:

- QStyle / custom style for production application styling;
- StyleKit for a declarative style approach;
- Style Sheets for prototyping and smaller/local adjustments.

Qt also notes that changing the application-wide Style Sheet at runtime can produce inconsistent results.

**DLU implication:** Stage 8 should establish a centralized production styling strategy and design-token layer instead of growing a large runtime-switched QSS blob.

Sources:
https://doc.qt.io/qt-6/stylesheet.html
https://doc.qt.io/qt-6.12/qtwidgets-styling-approaches.html

### 3.3 Accessibility and contrast

WCAG 2.2 guidance states:

- normal text should generally have at least 4.5:1 contrast;
- large text can use 3:1;
- non-text UI boundaries/states have their own contrast requirements;
- visible keyboard focus should be clearly distinguishable.

**DLU implication:** the new palette must be checked programmatically, and focus/selection states must not be conveyed only through a subtle color change.

Sources:
https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum
https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast
https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance

## 4. Design direction selected

The recommended direction is:

**Telecom Control Room + Modern University Laboratory**

Visual character:

- deep navy/graphite surfaces;
- bright cyan primary interaction;
- emerald success;
- amber warning;
- red critical/error;
- restrained neutral text;
- thin technical borders;
- compact but breathable cards;
- clear status chips;
- diagrams and equipment remain the visual hero.

The goal is not a generic dashboard. The goal is an **educational network operations laboratory**.

## 5. Proposed palette seed

These values are starting tokens, not an excuse to skip contrast testing:

| Token | Value | Purpose |
|---|---|---|
| background | #0B1220 | application background |
| surface | #111827 | primary surfaces |
| surface-elevated | #172033 | elevated cards/panels |
| primary | #22D3EE | active interaction |
| success | #22C55E | successful/healthy |
| warning | #F59E0B | attention |
| danger | #EF4444 | critical/error |
| text | #F8FAFC | primary text |
| text-muted | #94A3B8 | secondary text |

The automated quality gate must verify every foreground/background pairing actually used by the UI.

## 6. Interaction findings

### Finding A — Context should drive controls

A student examining a port should see:

- state;
- EQN;
- capacity;
- subscriber;
- source;
- relevant actions.

They should not have to navigate through unrelated global controls.

### Finding B — Details should stay near the selected object

Use a context inspector rather than opening many independent dialogs.

### Finding C — Commands and results should be paired

A command should visually connect to:

- what it asks;
- what it changed/read;
- affected hardware;
- result;
- teaching meaning.

### Finding D — Visualization should carry the lesson

Call path, hardware topology, modulation waveform, constellation, and scenario progress should be the primary explanatory surfaces.

### Finding E — Status needs redundant encoding

Do not rely on green/yellow/red alone.

Use:
- color;
- icon or symbol;
- label;
- optional tooltip.

## 7. Recommended design system

Use semantic tokens rather than component-specific hard-coded colors.

Examples:

- `color.bg`
- `color.surface`
- `color.text.primary`
- `color.state.success`
- `color.state.warning`
- `color.state.error`
- `space.1` through `space.6`
- `radius.sm/md/lg`
- `type.body/small/title/display`
- `control.height.compact/normal/large`

## 8. Research conclusion

The correct next move is **not** “make every screen darker.”

The correct move is to introduce a coherent design system, then migrate each learning surface to it while reducing cognitive load.

That is why Stage 8 comes before Stages 9–20.

## 9. Research boundary

This document combines:

1. repository-derived facts;
2. official Qt guidance;
3. W3C accessibility guidance;
4. usability research on progressive disclosure;
5. product design inference specific to DLU Lab.

The last category is design judgment, not course-source fact.
