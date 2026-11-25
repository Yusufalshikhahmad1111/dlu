from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .design_tokens import get_tokens, normalize_mode
from .teaching_scenarios import ScenarioDefinition, ScenarioResult, TeachingScenarioRunner
from .ui_utils import make_font


class Stage16InstructorWidget(QWidget):
    """Instructor-facing classroom layer over the existing scenario runner.

    This layer is presentation-only: the TeachingScenarioRunner remains the
    sole source of truth for scenario execution and expected results.
    """

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.window = window
        self.runner = TeachingScenarioRunner(window.db, window.mml)
        self._theme = "morning"
        self._result: ScenarioResult | None = None
        self._selected: ScenarioDefinition | None = None
        self._guided_index = -1
        self._projector_mode = False
        self._build()
        self._load_catalog()
        self.set_theme(self._theme)

    def _card(self, title: str):
        box = QGroupBox(title)
        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        return box, layout

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        header = QFrame()
        header.setObjectName("Stage16Header")
        h = QHBoxLayout(header)
        h.setContentsMargins(14, 12, 14, 12)
        title = QLabel("INSTRUCTOR / CLASSROOM MODE")
        title.setObjectName("Stage16Title")
        title.setFont(make_font(18, bold=True))
        h.addWidget(title)
        self.context = QLabel(
            "Project a scenario, control answer visibility, demonstrate the verified flow, and reset the lab."
        )
        self.context.setObjectName("Stage16Context")
        self.context.setWordWrap(True)
        h.addWidget(self.context, 1)
        self.status = QLabel("READY")
        self.status.setObjectName("Stage16Status")
        h.addWidget(self.status)
        self.projector_exit = QPushButton("EXIT PROJECTOR")
        self.projector_exit.setAutoDefault(False)
        self.projector_exit.clicked.connect(lambda: self.set_projector_mode(False))
        self.projector_exit.hide()
        h.addWidget(self.projector_exit)
        root.addWidget(header)

        self.controls = QFrame()
        self.controls.setObjectName("Stage16Controls")
        bar = QHBoxLayout(self.controls)
        bar.setContentsMargins(10, 8, 10, 8)
        bar.addWidget(QLabel("SCENARIO"))
        self.scenario_combo = QComboBox()
        self.scenario_combo.setMinimumWidth(360)
        self.scenario_combo.currentIndexChanged.connect(self._load_selected)
        bar.addWidget(self.scenario_combo, 1)

        self.run_button = QPushButton("RUN SCENARIO")
        self.run_button.setObjectName("Stage16Primary")
        self.run_button.setAutoDefault(False)
        self.run_button.clicked.connect(self.run_selected)
        bar.addWidget(self.run_button)

        self.guide_button = QPushButton("START GUIDED DEMO")
        self.guide_button.setAutoDefault(False)
        self.guide_button.clicked.connect(self.start_guided_demo)
        self.guide_button.setEnabled(False)
        bar.addWidget(self.guide_button)

        self.next_button = QPushButton("NEXT DEMO STEP")
        self.next_button.setAutoDefault(False)
        self.next_button.clicked.connect(self.guided_next)
        self.next_button.setEnabled(False)
        bar.addWidget(self.next_button)

        self.reset_button = QPushButton("RESET DEMO")
        self.reset_button.setAutoDefault(False)
        self.reset_button.clicked.connect(self.reset_demo)
        bar.addWidget(self.reset_button)

        self.reveal_toggle = QCheckBox("REVEAL ANSWERS")
        self.reveal_toggle.stateChanged.connect(self._render)
        bar.addWidget(self.reveal_toggle)

        self.projector_button = QPushButton("PROJECTOR VIEW")
        self.projector_button.setAutoDefault(False)
        self.projector_button.clicked.connect(lambda: self.set_projector_mode(True))
        bar.addWidget(self.projector_button)
        root.addWidget(self.controls)

        summary, summary_layout = self._card("SCENARIO BRIEF")
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)
        grid.addWidget(QLabel("TITLE"), 0, 0)
        self.title_label = QLabel("—")
        self.title_label.setObjectName("Stage16Large")
        self.title_label.setWordWrap(True)
        grid.addWidget(self.title_label, 0, 1)
        grid.addWidget(QLabel("OBJECTIVE"), 1, 0)
        self.objective_label = QLabel("—")
        self.objective_label.setWordWrap(True)
        grid.addWidget(self.objective_label, 1, 1)
        grid.addWidget(QLabel("SUMMARY"), 2, 0)
        self.summary_label = QLabel("—")
        self.summary_label.setWordWrap(True)
        grid.addWidget(self.summary_label, 2, 1)
        summary_layout.addLayout(grid)
        root.addWidget(summary)

        answers, answers_layout = self._card("EXPECTED VS ACTUAL")
        self.answer_card = answers
        self.answer_state = QLabel("Answers are hidden until the instructor enables REVEAL ANSWERS.")
        self.answer_state.setWordWrap(True)
        self.answer_state.setObjectName("Stage16AnswerState")
        answers_layout.addWidget(self.answer_state)
        answer_row = QHBoxLayout()
        expected_box, expected_layout = self._card("EXPECTED")
        self.expected_label = QLabel("HIDDEN")
        self.expected_label.setWordWrap(True)
        expected_layout.addWidget(self.expected_label)
        answer_row.addWidget(expected_box, 1)
        actual_box, actual_layout = self._card("ACTUAL")
        self.actual_label = QLabel("NOT EXECUTED")
        self.actual_label.setWordWrap(True)
        actual_layout.addWidget(self.actual_label)
        answer_row.addWidget(actual_box, 1)
        answers_layout.addLayout(answer_row)
        root.addWidget(answers)

        self.steps_box, steps_layout = self._card("GUIDED DEMONSTRATION")
        self.steps_table = QTableWidget(0, 5)
        self.steps_table.setHorizontalHeaderLabels(
            ["STEP", "KIND", "EXPECTED", "ACTUAL", "STATUS"]
        )
        self.steps_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.steps_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.steps_table.horizontalHeader().setStretchLastSection(True)
        self.steps_table.horizontalHeader().setMinimumSectionSize(110)
        self.steps_table.setMinimumHeight(260)
        steps_layout.addWidget(self.steps_table)
        self.step_hint = QLabel(
            "Run a scenario, then use START GUIDED DEMO to reveal the verified execution one step at a time."
        )
        self.step_hint.setWordWrap(True)
        steps_layout.addWidget(self.step_hint)
        root.addWidget(self.steps_box, 1)

        projector_card, projector_layout = self._card("PROJECTOR SUMMARY")
        self.projector_card = projector_card
        self.projector_title = QLabel("—")
        self.projector_title.setObjectName("Stage16ProjectorTitle")
        self.projector_title.setAlignment(Qt.AlignCenter)
        self.projector_title.setWordWrap(True)
        projector_layout.addWidget(self.projector_title)
        self.projector_objective = QLabel("—")
        self.projector_objective.setObjectName("Stage16ProjectorBody")
        self.projector_objective.setAlignment(Qt.AlignCenter)
        self.projector_objective.setWordWrap(True)
        projector_layout.addWidget(self.projector_objective)
        self.projector_result = QLabel("READY")
        self.projector_result.setObjectName("Stage16ProjectorResult")
        self.projector_result.setAlignment(Qt.AlignCenter)
        self.projector_result.setWordWrap(True)
        projector_layout.addWidget(self.projector_result)
        self.projector_card.hide()
        root.addWidget(projector_card)

        root.addStretch(1)

    def _load_catalog(self):
        self.scenario_combo.clear()
        for definition in self.runner.catalog():
            self.scenario_combo.addItem(definition.title, definition.scenario_id)
        if self.scenario_combo.count():
            self.scenario_combo.setCurrentIndex(0)
            self._load_selected(0)

    def _load_selected(self, _index: int):
        scenario_id = self.scenario_combo.currentData()
        if not scenario_id:
            self._selected = None
            self._result = None
            self._guided_index = -1
            self._render()
            return
        self._selected = next(
            item for item in self.runner.catalog() if item.scenario_id == scenario_id
        )
        self._result = None
        self._guided_index = -1
        self.status.setText("LOADED")
        self._render()

    @property
    def answers_revealed(self) -> bool:
        return self.reveal_toggle.isChecked()

    def run_selected(self):
        if self._selected is None:
            return
        try:
            self._result = self.runner.run(self._selected.scenario_id)
        except Exception as exc:
            self._result = None
            self.status.setText("ERROR")
            self.step_hint.setText(f"Scenario execution error: {exc}")
            self._render()
            return
        self._guided_index = -1
        self.status.setText(
            ("PASS" if self._result.passed else "FAIL")
            if self.answers_revealed
            else "EXECUTED · ANSWERS HIDDEN"
        )
        self.guide_button.setEnabled(True)
        self.next_button.setEnabled(False)
        self._render()

    def start_guided_demo(self):
        if self._result is None:
            self.run_selected()
        if self._result is None:
            return
        self._guided_index = 0 if self._result.steps else -1
        self.next_button.setEnabled(self._guided_index >= 0)
        self._render()

    def guided_next(self):
        if self._result is None or self._guided_index < 0:
            return
        if self._guided_index >= len(self._result.steps) - 1:
            self.next_button.setEnabled(False)
            self.step_hint.setText("GUIDED DEMO COMPLETE · All verified scenario steps are revealed.")
            self._render()
            return
        self._guided_index += 1
        self._render()

    def reset_demo(self):
        resetter = getattr(self.window, "reset_demo", None)
        if resetter is not None:
            resetter()
        self._result = None
        self._guided_index = -1
        self.status.setText("RESET")
        self.guide_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.step_hint.setText("Teaching demo reset. Choose a scenario and run it again.")
        self._render()

    def set_projector_mode(self, enabled: bool):
        self._projector_mode = bool(enabled)
        self.controls.setVisible(not self._projector_mode)
        self.steps_box.setVisible(not self._projector_mode)
        self.answer_card.setVisible(not self._projector_mode)
        self.projector_card.setVisible(self._projector_mode)
        self.projector_exit.setVisible(self._projector_mode)
        self.projector_button.setVisible(not self._projector_mode)
        self.context.setText(
            "PROJECTOR · Scenario title, objective and demonstrated result"
            if self._projector_mode
            else "Project a scenario, control answer visibility, demonstrate the verified flow, and reset the lab."
        )
        self._render()

    def _render(self):
        selected = self._selected
        if selected is None:
            self.title_label.setText("—")
            self.objective_label.setText("—")
            self.summary_label.setText("—")
            self.expected_label.setText("HIDDEN")
            self.actual_label.setText("NOT EXECUTED")
            self.answer_state.setText("Select a scenario.")
            self.steps_table.setRowCount(0)
            return

        self.title_label.setText(selected.title)
        self.objective_label.setText(selected.objective)
        self.summary_label.setText(selected.summary)

        result = self._result
        if not self.answers_revealed:
            self.expected_label.setText("HIDDEN · Instructor answer visibility is OFF.")
            self.actual_label.setText(
                "HIDDEN · Run the scenario and enable REVEAL ANSWERS to show the result."
            )
            self.answer_state.setText(
                "Answers are hidden from the projector/student view. Enable REVEAL ANSWERS only when teaching."
            )
        elif result is None:
            self.expected_label.setText("—")
            self.actual_label.setText("NOT EXECUTED")
            self.answer_state.setText("Answers are visible; execute the scenario to populate actual evidence.")
        else:
            self.expected_label.setText(result.expected_result)
            self.actual_label.setText(result.actual_result)
            self.answer_state.setText(
                f"FINAL RESULT · {'PASS' if result.passed else 'FAIL'} · "
                f"{sum(1 for step in result.steps if step.ok)}/{len(result.steps)} steps passed"
            )

        self.steps_table.setRowCount(0)
        if result is not None:
            visible_count = (
                len(result.steps)
                if self._guided_index < 0
                else min(len(result.steps), self._guided_index + 1)
            )
            for row, step in enumerate(result.steps[:visible_count]):
                self.steps_table.insertRow(row)
                values = (
                    step.label,
                    step.kind,
                    step.expected if self.answers_revealed else "HIDDEN",
                    step.actual if self.answers_revealed else "HIDDEN",
                    ("PASS" if step.ok else "FAIL") if self.answers_revealed else "HIDDEN",
                )
                for col, value in enumerate(values):
                    self.steps_table.setItem(row, col, QTableWidgetItem(str(value)))

            if self._guided_index >= 0 and result.steps:
                if self._guided_index >= len(result.steps) - 1:
                    self.step_hint.setText(
                        "GUIDED DEMO COMPLETE · All verified scenario steps are revealed."
                    )
                else:
                    self.step_hint.setText(
                        f"GUIDED STEP {self._guided_index + 1}/{len(result.steps)} · "
                        "Use NEXT DEMO STEP to continue."
                    )

        self.projector_title.setText(selected.title)
        self.projector_objective.setText(selected.objective)
        if result is None:
            projector_text = "READY · Load the scenario and start the guided demonstration."
        else:
            result_line = "PASS" if result.passed else "FAIL"
            if self.answers_revealed:
                projector_text = (
                    f"{result_line} · {sum(1 for step in result.steps if step.ok)}/{len(result.steps)} steps passed\n"
                    f"{result.expected_result}\n\n{result.actual_result}"
                )
            else:
                projector_text = (
                    "RESULT HIDDEN · Answers remain concealed\n"
                    "Instructor controls answer visibility."
                )
        self.projector_result.setText(projector_text)

        self.next_button.setEnabled(
            result is not None
            and self._guided_index >= 0
            and self._guided_index < len(result.steps) - 1
        )

    def set_theme(self, mode: str):
        self._theme = normalize_mode(mode)
        tokens = get_tokens(self._theme)
        self.setStyleSheet(
            f"""
            QFrame#Stage16Header, QFrame#Stage16Controls {{
                background:{tokens.surface};
                border:1px solid {tokens.border};
                border-radius:{tokens.radius_md}px;
            }}
            QGroupBox {{
                background:{tokens.surface};
                color:{tokens.text_primary};
                border:1px solid {tokens.border};
                border-radius:{tokens.radius_md}px;
                margin-top:8px;
            }}
            QGroupBox::title {{
                subcontrol-origin:margin;
                left:10px;
                padding:0 6px;
                color:{tokens.primary};
                font-weight:900;
            }}
            QLabel {{ color:{tokens.text_primary}; }}
            QLabel#Stage16Title {{ color:{tokens.text_primary}; font-weight:900; }}
            QLabel#Stage16Context {{ color:{tokens.text_secondary}; }}
            QLabel#Stage16Large {{ color:{tokens.text_primary}; font-weight:900; font-size:15pt; }}
            QLabel#Stage16AnswerState {{ color:{tokens.text_secondary}; }}
            QLabel#Stage16ProjectorTitle {{
                color:{tokens.text_primary};
                font-size:30pt;
                font-weight:900;
            }}
            QLabel#Stage16ProjectorBody {{
                color:{tokens.text_secondary};
                font-size:18pt;
                font-weight:800;
            }}
            QLabel#Stage16ProjectorResult {{
                color:{tokens.primary};
                font-size:20pt;
                font-weight:900;
                padding:18px;
            }}
            QLabel#Stage16Status {{
                background:{tokens.surface_elevated};
                color:{tokens.success};
                border:1px solid {tokens.success};
                border-radius:14px;
                padding:6px 12px;
                font-weight:900;
            }}
            QPushButton {{
                background:{tokens.surface_interactive};
                color:{tokens.text_primary};
                border:1px solid {tokens.border};
                border-radius:{tokens.radius_sm}px;
                padding:8px 11px;
                font-weight:800;
            }}
            QPushButton:hover {{
                background:{tokens.primary};
                border-color:{tokens.primary};
                color:{tokens.white};
            }}
            QPushButton#Stage16Primary {{
                background:{tokens.primary};
                border-color:{tokens.primary};
                color:{tokens.white};
            }}
            QComboBox, QTableWidget {{
                background:{tokens.surface_elevated};
                color:{tokens.text_primary};
                border:1px solid {tokens.border};
                border-radius:{tokens.radius_sm}px;
            }}
            QHeaderView::section {{
                background:{tokens.surface_interactive};
                color:{tokens.text_primary};
                border:0;
                padding:8px;
                font-weight:900;
            }}
            QTableWidget {{
                gridline-color:{tokens.border};
                selection-background-color:{tokens.surface_interactive};
                selection-color:{tokens.text_primary};
            }}
            """
        )
        self._render()


class Stage16Controller:
    def __init__(self, window, mode: str = "morning"):
        self.window = window
        self.mode = normalize_mode(mode)
        self.view: Stage16InstructorWidget | None = None
        self._tab_index: int | None = None

    def install(self):
        tabs = getattr(self.window, "feature_tabs", None)
        if tabs is None or getattr(self.window, "stage16_controller", None) is not None:
            return
        view = Stage16InstructorWidget(self.window, parent=tabs)
        view.set_theme(self.mode)
        self._tab_index = tabs.addTab(view, "Instructor")
        self.view = view
        self.window.instructor_mode = view
        self.window.stage16_controller = self
        self.window.setProperty("dlu_stage16_enabled", True)
        theme_button = getattr(self.window, "theme_btn", None)
        if theme_button is not None:
            theme_button.clicked.connect(self._sync_theme_from_window)

    def _sync_theme_from_window(self):
        from . import ui as ui_module
        self.set_mode(getattr(ui_module, "THEME_NAME", self.mode))

    def set_mode(self, mode: str):
        self.mode = normalize_mode(mode)
        if self.view is not None:
            self.view.set_theme(self.mode)


def apply_stage16_ui(window, mode: str = "morning"):
    controller = getattr(window, "stage16_controller", None)
    if controller is None:
        controller = Stage16Controller(window, mode)
        controller.install()
    else:
        controller.set_mode(mode)
