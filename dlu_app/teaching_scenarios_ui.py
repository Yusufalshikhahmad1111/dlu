from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .teaching_scenarios import (
    ScenarioResult,
    TeachingScenarioRunner,
)


class TeachingScenariosWidget(QWidget):
    """Unified Stage 6 teaching-scenario workbench."""

    def __init__(
        self,
        db,
        mml,
        *,
        on_state_changed: Callable[[], None] | None = None,
        on_reset_demo: Callable[[], None] | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.runner = TeachingScenarioRunner(db, mml)
        self.on_state_changed = on_state_changed
        self.on_reset_demo = on_reset_demo
        self._result: ScenarioResult | None = None
        self._palette_name = "ivory"
        self._build()
        self._load_catalog()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        header = QFrame()
        header.setObjectName("WorkbenchHeader")
        head = QHBoxLayout(header)
        head.addWidget(QLabel("TEACHING SCENARIOS"))
        head.addWidget(
            QLabel("Formal PASS / FAIL labs backed by the real simulator engines"),
            1,
        )
        self.status_chip = QLabel("READY")
        self.status_chip.setObjectName("StatusChip")
        head.addWidget(self.status_chip)
        root.addWidget(header)

        controls = QFrame()
        controls.setObjectName("CommandDock")
        bar = QHBoxLayout(controls)
        run_btn = QPushButton("RUN SCENARIO")
        run_btn.setObjectName("PrimaryScenario")
        run_btn.clicked.connect(self.run_selected)
        bar.addWidget(run_btn)

        reset_btn = QPushButton("RESET DEMO")
        reset_btn.setToolTip(
            "Restore source-backed demo hardware and clear teaching subscribers."
        )
        reset_btn.clicked.connect(self.reset_demo)
        bar.addWidget(reset_btn)

        copy_btn = QPushButton("COPY COMMANDS")
        copy_btn.clicked.connect(self.copy_commands)
        bar.addWidget(copy_btn)

        bar.addStretch()
        self.prereq_label = QLabel(
            "Repeatable demos: use RESET DEMO before hardware-mutating scenarios."
        )
        self.prereq_label.setObjectName("Legend")
        bar.addWidget(self.prereq_label, 1)
        root.addWidget(controls)

        split = QSplitter(Qt.Horizontal)
        split.setChildrenCollapsible(False)

        self.scenario_list = QListWidget()
        self.scenario_list.currentItemChanged.connect(self._select_item)
        split.addWidget(self.scenario_list)

        detail = QWidget()
        layout = QVBoxLayout(detail)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(7)

        self.title_label = QLabel("Select a scenario")
        self.title_label.setObjectName("Title")
        layout.addWidget(self.title_label)

        self.summary_label = QLabel("—")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        self.objective_label = QLabel("—")
        self.objective_label.setWordWrap(True)
        layout.addWidget(self.objective_label)

        self.eqn_label = QLabel("Affected EQN: —")
        self.eqn_label.setWordWrap(True)
        layout.addWidget(self.eqn_label)

        cards = QHBoxLayout()
        expected_frame = QFrame()
        expected_frame.setObjectName("WorkbenchHeader")
        expected_layout = QVBoxLayout(expected_frame)
        expected_layout.addWidget(QLabel("EXPECTED RESULT"))
        self.expected_text = QLabel("—")
        self.expected_text.setWordWrap(True)
        expected_layout.addWidget(self.expected_text)
        cards.addWidget(expected_frame, 1)

        actual_frame = QFrame()
        actual_frame.setObjectName("WorkbenchHeader")
        actual_layout = QVBoxLayout(actual_frame)
        actual_layout.addWidget(QLabel("ACTUAL RESULT"))
        self.actual_text = QLabel("—")
        self.actual_text.setWordWrap(True)
        actual_layout.addWidget(self.actual_text)
        cards.addWidget(actual_frame, 1)
        layout.addLayout(cards)

        self.steps_table = QTableWidget(0, 5)
        self.steps_table.setHorizontalHeaderLabels(
            ["Step", "Type", "Expected", "Actual", "Result"]
        )
        self.steps_table.verticalHeader().setVisible(False)
        self.steps_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.steps_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.steps_table.horizontalHeader().setStretchLastSection(True)
        self.steps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.steps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.steps_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.steps_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.steps_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        layout.addWidget(self.steps_table, 1)

        self.command_preview = QTextEdit()
        self.command_preview.setReadOnly(True)
        self.command_preview.setMaximumHeight(130)
        self.command_preview.setObjectName("Terminal")
        self.command_preview.setPlaceholderText("Scenario commands will appear here.")
        layout.addWidget(self.command_preview)

        split.addWidget(detail)
        split.setSizes([310, 900])
        root.addWidget(split, 1)

    def _load_catalog(self):
        self.scenario_list.clear()
        for definition in self.runner.catalog():
            item = QListWidgetItem(
                f"{definition.title}"
            )
            item.setData(Qt.UserRole, definition.scenario_id)
            item.setToolTip(definition.summary)
            self.scenario_list.addItem(item)
        if self.scenario_list.count():
            self.scenario_list.setCurrentRow(0)

    def _select_item(self, item, _previous=None):
        if item is None:
            return
        scenario_id = item.data(Qt.UserRole)
        definition = next(
            item
            for item in self.runner.catalog()
            if item.scenario_id == scenario_id
        )
        self.title_label.setText(definition.title)
        self.summary_label.setText(definition.summary)
        self.objective_label.setText(f"Objective: {definition.objective}")
        self.expected_text.setText("Run the scenario to evaluate PASS/FAIL.")
        self.actual_text.setText("—")
        self.eqn_label.setText("Affected EQN: determined at execution.")
        self.steps_table.setRowCount(0)
        self.command_preview.clear()
        self.status_chip.setText("READY")
        self._style_status("READY")

    def run_selected(self):
        item = self.scenario_list.currentItem()
        if item is None:
            return
        scenario_id = item.data(Qt.UserRole)
        try:
            result = self.runner.run(scenario_id)
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Teaching Scenario",
                f"Scenario execution failed unexpectedly:\n{exc}",
            )
            self.status_chip.setText("ERROR")
            self._style_status("ERROR")
            return

        self._result = result
        self._render_result(result)
        if self.on_state_changed:
            self.on_state_changed()

    def _render_result(self, result: ScenarioResult):
        self.status_chip.setText("PASS" if result.passed else "FAIL")
        self._style_status("PASS" if result.passed else "FAIL")
        self.expected_text.setText(result.expected_result)
        self.actual_text.setText(result.actual_result)
        self.eqn_label.setText(
            "Affected EQN: " + (
                " · ".join(result.affected_eqns)
                if result.affected_eqns
                else "—"
            )
        )
        self.steps_table.setRowCount(0)
        commands = []

        for row, step in enumerate(result.steps):
            self.steps_table.insertRow(row)
            values = [
                step.label,
                step.kind,
                step.expected,
                step.actual,
                "PASS" if step.ok else "FAIL",
            ]
            for col, value in enumerate(values):
                cell = QTableWidgetItem(str(value))
                self.steps_table.setItem(row, col, cell)
            if step.command:
                commands.append(step.command)

        self.command_preview.setPlainText(
            "\n".join(commands) if commands else "No MML commands in this scenario."
        )
        self.title_label.setText(result.title)

    def copy_commands(self):
        if self._result is None:
            return
        commands = [
            step.command
            for step in self._result.steps
            if step.command
        ]
        if not commands:
            return
        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText("\n".join(commands))
        self.status_chip.setText("COMMANDS COPIED")

    def reset_demo(self):
        if self.on_reset_demo is None:
            return
        self.on_reset_demo()
        self._result = None
        self.status_chip.setText("RESET")
        self._style_status("RESET")
        self._select_item(self.scenario_list.currentItem())

    def set_theme(self, name: str):
        self._palette_name = name

    def _style_status(self, status: str):
        from .theme import THEMES

        palette = THEMES.get(self._palette_name, THEMES["ivory"])
        color = palette.GREEN
        if status == "FAIL" or status == "ERROR":
            color = palette.RED
        elif status == "RESET":
            color = palette.YELLOW
        elif status == "COMMANDS COPIED":
            color = palette.CYAN
        self.status_chip.setStyleSheet(
            "background:%s;color:%s;border:1px solid %s;"
            "border-radius:14px;padding:6px 12px;font-weight:900;"
            % (palette.PANEL3, color, color)
        )
