import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QSplitter


from dlu_app.app_style import apply_application_style
from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.stage9_ui import apply_stage9_ui
from dlu_app.stage10_ui import apply_stage10_ui
from dlu_app.stage11_ui import apply_stage11_ui, result_target
from dlu_app.ui import DluSimulatorWindow


def _app() -> QApplication:
    app = QApplication.instance()
    return app if app is not None else QApplication([])


def _window(tmp_path: Path) -> DluSimulatorWindow:
    app = _app()
    apply_application_style(app, "morning")
    window = DluSimulatorWindow(tmp_path / "stage11.sqlite3")
    apply_stage8_ui(window, "morning")
    apply_stage9_ui(window, "morning")
    apply_stage10_ui(window, "morning")
    apply_stage11_ui(window, "morning")
    app.processEvents()
    return window


def test_stage11_creates_teaching_panel_and_splitter(tmp_path: Path):
    window = _window(tmp_path)
    try:
        assert hasattr(window, "mml_ux2_panel")
        assert isinstance(window.omt_splitter, QSplitter)
        assert window.mml_ux2_panel is not None
    finally:
        window.close()


def test_stage11_live_syntax_and_explanation(tmp_path: Path):
    window = _window(tmp_path)
    try:
        window.input.setText("> stat dlu: dlu=50;")
        assert window.mml_ux2_panel.syntax_badge.text().startswith("READY")
        assert "DLU status" in window.mml_ux2_panel.explanation_title.text()

        window.input.setText("> stat dlu: dlu=50")
        assert window.mml_ux2_panel.syntax_badge.text().startswith("CHECK")
    finally:
        window.close()


def test_stage11_real_mml_execution_updates_pairing_and_history(tmp_path: Path):
    window = _window(tmp_path)
    try:
        window.navigate_student_area("OMT / MML")
        window.set_command_text("> stat dlu: dlu=50;")
        window.execute_input()
        _app().processEvents()

        assert window.history[-1] == "> stat dlu: dlu=50;"
        assert window.mml_ux2_panel.history_list.count() == 1
        assert "SUCCESS · OK" in window.mml_ux2_panel.result.text()
        assert "DLU 50" in window.mml_ux2_panel.result.text()
        assert window.command_status.text().startswith("OK")
    finally:
        window.close()


def test_stage11_history_reuse(tmp_path: Path):
    window = _window(tmp_path)
    try:
        window.set_command_text("> help;")
        window.execute_input()
        _app().processEvents()

        window.mml_ux2_panel.history_list.setCurrentRow(0)
        window.mml_ux2_panel.use_selected()
        assert window.input.text() == "> help;"
    finally:
        window.close()


def test_stage11_failed_command_updates_result_card(tmp_path: Path):
    window = _window(tmp_path)
    try:
        window.set_command_text("> nonsense: value=1;")
        window.execute_input()
        _app().processEvents()

        assert "ERROR · MML-UNKNOWN-COMMAND" in window.mml_ux2_panel.result.text()
        assert "No direct hardware target" in window.mml_ux2_panel.result.text()
    finally:
        window.close()


def test_stage11_clear_view_preserves_keyboard_history(tmp_path: Path):
    window = _window(tmp_path)
    try:
        window.show()
        window.set_command_text("> help;")
        window.execute_input()
        window.set_command_text("> stat dlu: dlu=50;")
        window.execute_input()
        _app().processEvents()

        original_history = list(window.history)
        assert window.mml_ux2_panel.history_list.count() == 2

        window.mml_ux2_panel.clear_history_view()
        assert window.history == original_history
        assert window.history_index == len(original_history)
        assert window.mml_ux2_panel.history_list.count() == 0

        window.input.setFocus()
        QTest.keyClick(window.input, Qt.Key_Up)
        assert window.input.text() == original_history[-1]
    finally:
        window.close()


def test_stage11_multi_result_target_summary():
    data = [
        {"eqn": "50-0-15-0"},
        {"eqn": "50-0-15-1"},
        {"eqn": "50-0-15-0"},
    ]
    assert result_target(data) == "2 linked targets · see detailed output"


def test_stage11_theme_sync(tmp_path: Path):
    window = _window(tmp_path)
    try:
        window.set_theme("night")
        assert window.mml_ux2_panel.mode == "night"
        window.set_theme("morning")
        assert window.mml_ux2_panel.mode == "morning"
    finally:
        window.close()
