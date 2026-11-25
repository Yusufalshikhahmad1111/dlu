from pathlib import Path
from tempfile import TemporaryDirectory

from PySide6.QtWidgets import QApplication

from dlu_app.db import Database
from dlu_app.mml import MmlEngine
from dlu_app.stage16_ui import Stage16InstructorWidget


class DummyWindow:
    def __init__(self):
        self.tmp = TemporaryDirectory()
        self.db = Database(Path(self.tmp.name) / "dlu_lab.sqlite3")
        self.mml = MmlEngine(self.db)
        self.reset_calls = 0

    def reset_demo(self):
        self.reset_calls += 1
        self.db.reset_demo()

    def close(self):
        self.db.close()
        self.tmp.cleanup()


def _app():
    app = QApplication.instance()
    return app if app is not None else QApplication([])


def test_stage16_builds_instructor_catalog():
    _app()
    window = DummyWindow()
    try:
        widget = Stage16InstructorWidget(window)
        assert widget.scenario_combo.count() == 6
        assert widget.scenario_combo.currentData() == "aleppo-8-line"
        assert not widget.answers_revealed
        assert not widget._projector_mode
        widget.close()
    finally:
        window.close()


def test_stage16_scenario_loading_is_presentation_only():
    _app()
    window = DummyWindow()
    try:
        widget = Stage16InstructorWidget(window)
        widget.scenario_combo.setCurrentIndex(4)
        assert widget._selected.scenario_id == "international-blacklist"
        assert widget._result is None
        assert widget.title_label.text() == "International Blacklist"
        assert widget.answer_state.text().startswith("Answers are hidden")
        widget.close()
    finally:
        window.close()


def test_stage16_runs_existing_runner_and_reveals_expected_vs_actual():
    _app()
    window = DummyWindow()
    try:
        widget = Stage16InstructorWidget(window)
        widget.scenario_combo.setCurrentIndex(4)
        widget.run_selected()
        assert widget._result is not None
        assert widget._result.scenario_id == "international-blacklist"
        assert widget._result.passed
        assert widget.status.text() == "PASS"
        assert widget.actual_label.text().startswith("HIDDEN")
        widget.reveal_toggle.setChecked(True)
        assert "EVAL=NO" in widget.expected_label.text()
        assert "CALL-BLOCKED" in widget.actual_label.text()
        widget.close()
    finally:
        window.close()


def test_stage16_guided_demo_reveals_one_existing_result_step_at_a_time():
    _app()
    window = DummyWindow()
    try:
        widget = Stage16InstructorWidget(window)
        widget.scenario_combo.setCurrentIndex(3)
        widget.run_selected()
        total = len(widget._result.steps)
        assert total > 1

        widget.start_guided_demo()
        assert widget._guided_index == 0
        assert widget.steps_table.rowCount() == 1

        widget.guided_next()
        assert widget._guided_index == 1
        assert widget.steps_table.rowCount() == 2

        while widget._guided_index < total - 1:
            widget.guided_next()
        assert widget.steps_table.rowCount() == total
        assert not widget.next_button.isEnabled()
        widget.close()
    finally:
        window.close()


def test_stage16_reset_delegates_to_real_window_and_clears_presentation():
    _app()
    window = DummyWindow()
    try:
        widget = Stage16InstructorWidget(window)
        widget.run_selected()
        assert widget._result is not None
        widget.start_guided_demo()
        widget.reset_demo()
        assert window.reset_calls == 1
        assert widget._result is None
        assert widget._guided_index == -1
        assert widget.status.text() == "RESET"
        widget.close()
    finally:
        window.close()


def test_stage16_projector_mode_is_separate_from_student_workbench():
    _app()
    window = DummyWindow()
    try:
        widget = Stage16InstructorWidget(window)
        widget.run_selected()
        widget.set_projector_mode(True)
        assert "RESULT HIDDEN" in widget.projector_result.text()
        assert "PASS" not in widget.projector_result.text()
        widget.reveal_toggle.setChecked(True)
        assert widget._projector_mode
        assert widget.controls.isHidden()
        assert widget.steps_box.isHidden()
        assert not widget.projector_card.isHidden()
        assert not widget.projector_exit.isHidden()
        assert "PASS" in widget.projector_result.text()

        widget.set_projector_mode(False)
        assert not widget._projector_mode
        assert not widget.controls.isHidden()
        assert not widget.steps_box.isHidden()
        assert not widget.answer_card.isHidden()
        widget.close()
    finally:
        window.close()


def test_stage16_morning_night_and_answer_visibility_controls():
    _app()
    window = DummyWindow()
    try:
        widget = Stage16InstructorWidget(window)
        widget.set_theme("night")
        assert widget._theme == "night"
        widget.set_theme("morning")
        assert widget._theme == "morning"

        widget.reveal_toggle.setChecked(False)
        assert not widget.answers_revealed
        widget.reveal_toggle.setChecked(True)
        assert widget.answers_revealed
        widget.close()
    finally:
        window.close()
