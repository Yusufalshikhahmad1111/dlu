from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .design_tokens import get_tokens, normalize_mode
from .teaching_scenarios import ScenarioDefinition, ScenarioResult, TeachingScenarioRunner
from .ui_utils import make_font


PHASES = ("OBJECTIVE", "OBSERVE", "EXECUTE", "DIAGNOSE", "FIX", "VERIFY", "RESULT")

GUIDES = {
    "aleppo-8-line": (
        "Confirm SLMA8 at DLU 50 / Shelf 0 / Module 15 and ports 0–7.",
        "Run once and watch eight CREATE steps plus final inventory.",
        "Every CREATE and the final inventory must pass.",
        "Use RESET DEMO for a clean state; keep the documented placement.",
        "Verify 8 subscribers and EQNs 50-0-15-0..7.",
        ("Source-backed placement is 50-0-15.", "SLMA8 has eight ports.", "Eight training DNs are expected."),
    ),
    "cmrl-capacity": (
        "Observe CMRL at DLU 10 / Shelf 1 / Module 7 and its six-port capacity.",
        "Run and compare ports 0–5 with port 6.",
        "A PASS contains six creations plus the expected MML-VALIDATION rejection for port 6.",
        "Use RESET DEMO if the training state is dirty; the rejected port is intentional.",
        "Verify exactly six subscribers and intentional rejection of 10-1-7-6.",
        ("CMRL capacity is six.", "Port 6 is the boundary condition.", "The rejection is part of PASS."),
    ),
    "dlu-maintenance": (
        "Observe a configured verified card with no subscriber assignment.",
        "Run FAULT → DIAG → REMOVE → INSTALL → ACTIVATE.",
        "DIAG-FAULT should be followed by replacement and final ACT + clear fault.",
        "Return to a clean demo state before repeating; never invent a card type.",
        "Verify the same verified card is ACT with clear fault.",
        ("Only configured unused cards are candidates.", "DIAG-FAULT is expected.", "Replacement uses the same verified type."),
    ),
    "billing-block": (
        "Observe the demo subscriber before changing account state.",
        "Run the block then restoration flow.",
        "PASS means BLOCKED / accsusp followed by restored service.",
        "Use RESET DEMO if the subscriber is already modified.",
        "Verify IDLE / NORMAL after cblk.",
        ("The teaching block is blk=accsusp.", "The line becomes BLOCKED.", "cblk restores service."),
    ),
    "international-blacklist": (
        "Observe the international destination decision before resource reservation.",
        "Run and inspect CPT, call result, path, and PDC usage.",
        "EVAL=NO must block before resource reservation.",
        "The correct fix is understanding the CPT decision; keep the blacklist rule intact.",
        "Verify CALL-BLOCKED, PDC 0/120, caller IDLE.",
        ("Destination is 00972.", "EVAL=NO is decisive.", "A blocked call must not consume PDC."),
    ),
    "overnight-command-file": (
        "Observe the command-file schedule starting near 23:55.",
        "Follow acceptance, 00:05 scheduling, midnight rollover, and execution.",
        "The file must execute exactly once and clear scheduled_at.",
        "RESET DEMO and repeat the deterministic virtual-clock exercise if needed.",
        "Verify one execution across midnight, not two.",
        ("Scheduled time is 00:05.", "The virtual clock crosses 23:55 → 00:05.", "Execution occurs exactly once."),
    ),
}


class PhaseRail(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.labels = []
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        for i, phase in enumerate(PHASES, 1):
            label = QLabel(f"{i} {phase}")
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumHeight(28)
            self.labels.append(label)
            layout.addWidget(label, 1)

    def set_phase(self, index: int, mode: str):
        t = get_tokens(normalize_mode(mode))
        for i, label in enumerate(self.labels):
            if i == index:
                label.setStyleSheet(
                    f"background:{t.primary};color:{t.deep};border-radius:7px;padding:4px;font-weight:900;"
                )
            elif i < index:
                label.setStyleSheet(
                    f"background:{t.success};color:{t.deep};border-radius:7px;padding:4px;font-weight:900;"
                )
            else:
                label.setStyleSheet(
                    f"background:{t.surface_elevated};color:{t.text_muted};border:1px solid {t.border};"
                    "border-radius:7px;padding:4px;"
                )


class Stage14TeachingScenariosWidget(QWidget):
    def __init__(self, db, mml, *, on_state_changed: Callable[[], None] | None = None,
                 on_reset_demo: Callable[[], None] | None = None, parent=None):
        super().__init__(parent)
        self.runner = TeachingScenarioRunner(db, mml)
        self.on_state_changed = on_state_changed
        self.on_reset_demo = on_reset_demo
        self._result: ScenarioResult | None = None
        self._selected: ScenarioDefinition | None = None
        self._phase_index = 0
        self._hint_index = 0
        self._theme = "morning"
        self._build()
        self._load_catalog()
        self._apply_theme()

    @staticmethod
    def _card(title: str):
        box = QGroupBox(title)
        layout = QVBoxLayout(box)
        layout.setSpacing(5)
        return box, layout

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        header = QFrame()
        header.setObjectName("WorkbenchHeader")
        h = QHBoxLayout(header)
        title = QLabel("TEACHING SCENARIOS 2.0")
        title.setFont(make_font(16, bold=True))
        h.addWidget(title)
        h.addWidget(QLabel("Objective → Observe → Execute → Diagnose → Fix → Verify → Result"), 1)
        self.status_chip = QLabel("READY")
        self.status_chip.setObjectName("StatusChip")
        h.addWidget(self.status_chip)
        root.addWidget(header)

        self.rail = PhaseRail()
        root.addWidget(self.rail)

        controls = QFrame()
        controls.setObjectName("CommandDock")
        bar = QHBoxLayout(controls)
        self.continue_btn = QPushButton("START / CONTINUE")
        self.continue_btn.setObjectName("PrimaryScenario")
        self.continue_btn.clicked.connect(self.continue_phase)
        bar.addWidget(self.continue_btn)
        self.hint_btn = QPushButton("HINT")
        self.hint_btn.clicked.connect(self.show_hint)
        bar.addWidget(self.hint_btn)
        reset_btn = QPushButton("RESET DEMO")
        reset_btn.clicked.connect(self.reset_demo)
        bar.addWidget(reset_btn)
        copy_btn = QPushButton("COPY COMMANDS")
        copy_btn.clicked.connect(self.copy_commands)
        bar.addWidget(copy_btn)
        bar.addStretch()
        self.step_hint = QLabel("Select a scenario to begin.")
        self.step_hint.setWordWrap(True)
        bar.addWidget(self.step_hint, 2)
        root.addWidget(controls)

        split = QSplitter(Qt.Horizontal)
        split.setChildrenCollapsible(False)
        self.scenario_list = QListWidget()
        self.scenario_list.currentItemChanged.connect(self._select_item)
        split.addWidget(self.scenario_list)

        detail = QWidget()
        dl = QVBoxLayout(detail)
        dl.setContentsMargins(0, 0, 0, 0)
        dl.setSpacing(7)

        self.title_label = QLabel("Select a scenario")
        self.title_label.setObjectName("Title")
        dl.addWidget(self.title_label)
        self.summary_label = QLabel("—")
        self.summary_label.setWordWrap(True)
        dl.addWidget(self.summary_label)
        self.objective_label = QLabel("—")
        self.objective_label.setWordWrap(True)
        dl.addWidget(self.objective_label)

        self.observe_box, observe_layout = self._card("OBSERVE")
        self.observe_text = QLabel("—")
        self.observe_text.setWordWrap(True)
        observe_layout.addWidget(self.observe_text)
        dl.addWidget(self.observe_box)

        cards = QHBoxLayout()
        expected, expected_layout = self._card("EXPECTED RESULT")
        self.expected_text = QLabel("—")
        self.expected_text.setWordWrap(True)
        expected_layout.addWidget(self.expected_text)
        cards.addWidget(expected, 1)
        actual, actual_layout = self._card("ACTUAL RESULT")
        self.actual_text = QLabel("—")
        self.actual_text.setWordWrap(True)
        actual_layout.addWidget(self.actual_text)
        cards.addWidget(actual, 1)
        dl.addLayout(cards)

        diagnosis, diagnosis_layout = self._card("DIAGNOSE / MISTAKE EXPLANATION")
        self.diagnosis_text = QLabel("Run the scenario to populate diagnosis.")
        self.diagnosis_text.setWordWrap(True)
        diagnosis_layout.addWidget(self.diagnosis_text)
        dl.addWidget(diagnosis)

        fix, fix_layout = self._card("FIX / RECOVERY")
        self.fix_text = QLabel("—")
        self.fix_text.setWordWrap(True)
        fix_layout.addWidget(self.fix_text)
        dl.addWidget(fix)

        self.steps_table = QTableWidget(0, 5)
        self.steps_table.setHorizontalHeaderLabels(["Step", "Type", "Expected", "Actual", "Result"])
        self.steps_table.verticalHeader().setVisible(False)
        self.steps_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.steps_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.steps_table.horizontalHeader().setStretchLastSection(True)
        self.steps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.steps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.steps_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.steps_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.steps_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        dl.addWidget(self.steps_table, 1)

        verify, verify_layout = self._card("VERIFY")
        self.verify_text = QLabel("Verification waits for an executed scenario.")
        self.verify_text.setWordWrap(True)
        verify_layout.addWidget(self.verify_text)
        dl.addWidget(verify)

        self.command_preview = QTextEdit()
        self.command_preview.setReadOnly(True)
        self.command_preview.setMaximumHeight(115)
        self.command_preview.setObjectName("Terminal")
        dl.addWidget(self.command_preview)

        split.addWidget(detail)
        split.setSizes([300, 900])
        root.addWidget(split, 1)

    def _load_catalog(self):
        self.scenario_list.clear()
        for definition in self.runner.catalog():
            item = QListWidgetItem(definition.title)
            item.setData(Qt.UserRole, definition.scenario_id)
            item.setToolTip(definition.summary)
            self.scenario_list.addItem(item)
        if self.scenario_list.count():
            self.scenario_list.setCurrentRow(0)

    def _select_item(self, item, _previous=None):
        if item is None:
            return
        scenario_id = item.data(Qt.UserRole)
        self._selected = next(d for d in self.runner.catalog() if d.scenario_id == scenario_id)
        self._result = None
        self._phase_index = 0
        self._hint_index = 0
        guide = GUIDES[scenario_id]
        self.title_label.setText(self._selected.title)
        self.summary_label.setText(self._selected.summary)
        self.objective_label.setText(f"Objective: {self._selected.objective}")
        self.observe_text.setText(guide[0])
        self.expected_text.setText("Complete the guided lab to evaluate PASS / FAIL.")
        self.actual_text.setText("—")
        self.diagnosis_text.setText("The diagnosis appears after execution.")
        self.fix_text.setText(guide[3])
        self.verify_text.setText("Verification waits for an executed scenario.")
        self.steps_table.setRowCount(0)
        self.command_preview.clear()
        self.status_chip.setText("READY")
        self._update_phase_ui()

    def _update_phase_ui(self):
        self.rail.set_phase(self._phase_index, self._theme)
        if self._selected is None:
            return
        guide = GUIDES[self._selected.scenario_id]
        phase = PHASES[self._phase_index]
        labels = {
            "OBJECTIVE": (f"Goal: {self._selected.objective}", "BEGIN OBSERVE"),
            "OBSERVE": (guide[0], "CONTINUE TO EXECUTE"),
            "EXECUTE": (guide[1], "RUN SCENARIO"),
            "DIAGNOSE": (guide[2], "CONTINUE TO FIX"),
            "FIX": (guide[3], "CONTINUE TO VERIFY"),
            "VERIFY": ("Read the evidence table and verify PASS/FAIL, not only color.", "SHOW RESULT"),
            "RESULT": ("Scenario complete. Choose another scenario or reset for a clean repeat.", "RESTART LAB"),
        }
        self.step_hint.setText(labels[phase][0])
        self.continue_btn.setText(labels[phase][1])

    def continue_phase(self):
        if self._selected is None:
            return
        phase = PHASES[self._phase_index]
        if phase == "EXECUTE":
            self.run_selected()
            return
        if phase == "VERIFY":
            self._phase_index = 6
            self._render_result_summary()
            self._update_phase_ui()
            return
        if phase == "RESULT":
            self._select_item(self.scenario_list.currentItem())
            return
        self._phase_index = min(6, self._phase_index + 1)
        self._update_phase_ui()

    def run_selected(self):
        if self._selected is None:
            return
        try:
            result = self.runner.run(self._selected.scenario_id)
        except Exception as exc:
            QMessageBox.critical(self, "Teaching Scenario", f"Scenario execution failed unexpectedly:\n{exc}")
            self.status_chip.setText("✗ ERROR")
            self._style_status("ERROR")
            return
        self._result = result
        self._phase_index = 3
        self._render_result(result)
        self._update_phase_ui()
        if self.on_state_changed:
            self.on_state_changed()

    def _render_result(self, result: ScenarioResult):
        self.status_chip.setText("✓ PASS" if result.passed else "✗ FAIL")
        self._style_status("PASS" if result.passed else "FAIL")
        self.expected_text.setText(result.expected_result)
        self.actual_text.setText(result.actual_result)
        failed = [step for step in result.steps if not step.ok]
        if result.passed:
            diagnosis = "No learning-blocking error detected. Every expected scenario step passed."
        elif failed:
            first = failed[0]
            diagnosis = (
                f"First failing step: {first.label}. Expected {first.expected}; "
                f"actual {first.actual}. Use the hint/recovery guidance, clean the demo if required, and rerun."
            )
        else:
            diagnosis = "The scenario is FAIL without a step-level failure; inspect actual result and rerun."
        self.diagnosis_text.setText(diagnosis)
        guide = GUIDES[result.scenario_id]
        self.fix_text.setText(
            ("No repair is required for this PASS.\n\n" if result.passed else "") + guide[3]
        )
        self.verify_text.setText(
            f"Verify: overall {'PASS' if result.passed else 'FAIL'}; "
            f"{sum(1 for step in result.steps if step.ok)}/{len(result.steps)} steps passed. "
            f"Affected EQN(s): {', '.join(result.affected_eqns) if result.affected_eqns else '—'}."
        )
        self.steps_table.setRowCount(0)
        commands = []
        for row, step in enumerate(result.steps):
            self.steps_table.insertRow(row)
            for col, value in enumerate(
                (step.label, step.kind, step.expected, step.actual, "PASS" if step.ok else "FAIL")
            ):
                self.steps_table.setItem(row, col, QTableWidgetItem(str(value)))
            if step.command:
                commands.append(step.command)
        self.command_preview.setPlainText(
            "\n".join(commands) if commands else "No MML commands in this scenario."
        )

    def _render_result_summary(self):
        if self._result is None:
            return
        result = self._result
        self.status_chip.setText("✓ PASS" if result.passed else "✗ FAIL")
        self._style_status("PASS" if result.passed else "FAIL")
        self.verify_text.setText(
            f"FINAL RESULT: {'PASS' if result.passed else 'FAIL'} · "
            f"{sum(1 for step in result.steps if step.ok)}/{len(result.steps)} steps passed."
        )

    def show_hint(self):
        if self._selected is None:
            return
        hints = GUIDES[self._selected.scenario_id][5]
        self.step_hint.setText(f"HINT {self._hint_index + 1}/{len(hints)} · {hints[self._hint_index]}")
        self._hint_index = (self._hint_index + 1) % len(hints)

    def copy_commands(self):
        if self._result is None:
            return
        commands = [step.command for step in self._result.steps if step.command]
        if not commands:
            return
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText("\n".join(commands))
        self.status_chip.setText("COMMANDS COPIED")
        self._style_status("COMMANDS COPIED")

    def reset_demo(self):
        if self.on_reset_demo is None:
            return
        self.on_reset_demo()
        self._result = None
        self._phase_index = 0
        self._select_item(self.scenario_list.currentItem())
        self.status_chip.setText("RESET")
        self._style_status("RESET")

    def set_theme(self, name: str):
        self._theme = normalize_mode(name)
        self._apply_theme()

    def _apply_theme(self):
        t = get_tokens(self._theme)
        self.setStyleSheet(
            f"""
            QGroupBox {{ background:{t.surface}; color:{t.text_primary}; border:1px solid {t.border}; border-radius:9px; margin-top:8px; }}
            QGroupBox::title {{ subcontrol-origin:margin; left:10px; padding:0 5px; color:{t.primary}; font-weight:900; }}
            QLabel {{ color:{t.text_primary}; }}
            """
        )
        self._style_status(self.status_chip.text())
        self.rail.set_phase(self._phase_index, self._theme)

    def _style_status(self, status: str):
        t = get_tokens(self._theme)
        color = t.success
        if "FAIL" in status or "ERROR" in status:
            color = t.danger
        elif "RESET" in status:
            color = t.warning
        elif "COPIED" in status:
            color = t.primary
        self.status_chip.setStyleSheet(
            f"background:{t.surface_elevated};color:{color};border:1px solid {color};"
            "border-radius:14px;padding:6px 12px;font-weight:900;"
        )


class Stage14Controller:
    def __init__(self, window: QWidget, mode: str = "morning"):
        self.window = window
        self.mode = normalize_mode(mode)
        self.view: Stage14TeachingScenariosWidget | None = None

    def install(self):
        tabs = getattr(self.window, "feature_tabs", None)
        legacy = getattr(self.window, "teaching_scenarios", None)
        if tabs is None or legacy is None:
            return
        index = tabs.indexOf(legacy)
        if index < 0:
            return
        title = tabs.tabText(index) or "SCENARIOS"
        view = Stage14TeachingScenariosWidget(
            self.window.db,
            self.window.mml,
            on_state_changed=getattr(legacy, "on_state_changed", None),
            on_reset_demo=getattr(legacy, "on_reset_demo", None),
            parent=tabs,
        )
        view.set_theme(self.mode)
        tabs.removeTab(index)
        legacy.setParent(None)
        legacy.deleteLater()
        tabs.insertTab(index, view, title)
        tabs.setCurrentIndex(index)
        self.window.stage14_legacy_teaching_scenarios = legacy
        self.window.teaching_scenarios = view
        self.view = view
        self.window.stage14_controller = self
        self.window.setProperty("dlu_stage14_enabled", True)

    def set_mode(self, mode: str):
        self.mode = normalize_mode(mode)
        if self.view is not None:
            self.view.set_theme(self.mode)


def apply_stage14_ui(window: QWidget, mode: str = "morning") -> None:
    controller = getattr(window, "stage14_controller", None)
    if controller is None:
        controller = Stage14Controller(window, mode)
        controller.install()
    else:
        controller.set_mode(mode)
