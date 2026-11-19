# DLU Lab — Stage 09→20 Execution Prompts

These are the execution briefs for future stages. Execute one stage at a time.

---

# Stage 09 — Student-Centered Navigation

## Prompt

Act as a senior educational UX architect and PySide6 engineer.

Rework navigation around the student journey.

Target outcomes:

- Learning Home;
- Continue Learning;
- Recent activity;
- Current lab context;
- progress;
- quick actions;
- clear active navigation.

Use progressive disclosure. Keep advanced technical controls secondary.

Acceptance:

- navigation is consistent;
- current context is always visible;
- no dead-end screens;
- keyboard navigation works;
- existing feature behavior remains unchanged;
- visual QA passes all target resolutions.

---

# Stage 10 — Hardware UX 2.0

## Prompt

Act as a telecom UI/UX specialist and PySide6 graphics engineer.

Redesign the hardware experience as the visual centerpiece.

Required hierarchy:

Exchange → DLU → Side → Shelf → Module → Port → Subscriber

Add or improve:

- hover inspection;
- selection highlighting;
- context inspector;
- state LEDs;
- EQN display;
- capacity display;
- fault/maintenance indicators;
- clear parent context.

Do not invent placements or capacities.

Acceptance:

A student can identify the selected object, its role, its state, its capacity, and its EQN without opening multiple unrelated dialogs.

---

# Stage 11 — OMT/MML UX 2.0

## Prompt

Act as an educational terminal UX designer and MML engineer.

Keep real MML behavior but improve discoverability.

Required:

- command editor;
- history;
- clear syntax feedback;
- command explanation;
- execution result;
- affected hardware;
- copy/reuse workflow.

A command result should teach what the command meant.

Do not implement a second MML engine.

Acceptance:

A novice can understand a command/result pair while an experienced user can still work quickly.

---

# Stage 12 — Call & Network Visualization

## Prompt

Act as a telecom network-visualization specialist.

Turn call-path presentation into a readable teaching visualization.

Show:

Origin
→ CPT
→ Resource reservation
→ Switching
→ Destination

Represent:

REQUEST
ROUTING
RESOURCE
CONNECTED
BLOCKED
RELEASED

Use animation only where it improves comprehension.

Do not change CallEngine decisions.

Acceptance:

Students can explain why a path succeeded or was blocked from the visualization and supporting explanation.

---

# Stage 13 — Communications Lab 2.0

## Prompt

Act as a communications-lab UX designer and PySide6 visualization engineer.

Redesign each experiment as:

Concept
→ Parameters
→ Experiment
→ Visualization
→ Measurement
→ Explanation
→ Mini Challenge

Keep the existing deterministic calculations.

Improve:

- controls;
- waveform readability;
- constellation readability;
- parameter labeling;
- measurement cards;
- explanation text.

Acceptance:

A student can change a parameter and immediately understand what changed visually and why.

---

# Stage 14 — Teaching Scenarios 2.0

## Prompt

Act as an instructional-design specialist and telecom simulator UX designer.

Convert each existing scenario into a guided lab:

Objective
→ Observe
→ Execute
→ Diagnose
→ Fix
→ Verify
→ Result

Add:

- progress;
- hints;
- mistake explanation;
- expected vs actual;
- clear PASS/FAIL meaning.

Do not change the underlying scenario engine or academic expected results.

Acceptance:

A student can complete the scenario with the UI itself acting as the guide.

---

# Stage 15 — Academic Learning Layer

## Prompt

Act as an educational-product architect.

Connect the existing modules into:

Learn
→ Practice
→ Experiment
→ Challenge
→ Verify

Do not create new unsupported telecom theory.

Use the repository's current hardware, MML, call, communications, and scenario content.

Acceptance:

The application presents a coherent course-learning progression without duplicating the simulator engines.

---

# Stage 16 — Instructor / Classroom Mode

## Prompt

Act as a university laboratory software designer.

Add an instructor-oriented presentation mode with:

- reset;
- scenario loading;
- answer visibility controls;
- expected vs actual;
- guided demonstration;
- projector-friendly layout.

Keep the student mode unchanged unless explicitly shared by the same component.

Acceptance:

An instructor can project and demonstrate a full scenario without exposing unnecessary student controls.

---

# Stage 17 — Accessibility & Usability Audit

## Prompt

Act as an accessibility and desktop usability auditor.

Audit:

- contrast;
- keyboard navigation;
- focus;
- text size;
- state communication;
- tooltips;
- empty states;
- error states;
- loading states;
- discoverability.

Use WCAG 2.2 guidance as the reference and document any practical desktop-specific adaptations.

Acceptance:

No core workflow depends on color alone; focus is visible; target resolutions remain readable.

---

# Stage 18 — Performance & Architecture Cleanup

## Prompt

Act as a senior Python/PySide6 architect.

Refactor the UI gradually.

Target boundaries:

- app_shell;
- navigation;
- design_tokens;
- feature views;
- shared components.

Preserve domain core and behavior.

Reduce the responsibilities of the monolithic UI module without performing a risky rewrite.

Acceptance:

Visual changes are localized; domain rules remain independent; tests remain green.

---

# Stage 19 — Final Academic UX Audit

## Prompt

Act as an academic examiner, UX auditor, and telecom laboratory instructor.

Test the complete student workflow.

Evaluate:

Hardware
MML
Calls
Communications
Scenarios

For each, answer:

- Can a student understand the goal?
- Can they find the next action?
- Can they understand the result?
- Can they recover from an error?
- Can they explain the telecom concept afterwards?

Acceptance:

No critical learning barrier remains in the primary course workflow.

---

# Stage 20 — DLU Lab 2.0 Release

## Prompt

Act as release lead and final product auditor.

Perform:

- full regression;
- full visual QA;
- accessibility check;
- packaging validation;
- screenshot capture;
- manual update;
- academic guide update;
- instructor guide update;
- final closeout.

Do not call the release complete until:

- all tests pass;
- Windows package passes smoke test;
- screenshots are valid;
- documentation is synchronized;
- Stage 0→20 roadmap is consistent;
- no critical UX regression remains.
