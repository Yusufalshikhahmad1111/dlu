from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton

from dlu_app.app_style import apply_application_style
from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.stage9_ui import apply_stage9_ui
from dlu_app.ui import DluSimulatorWindow


def _app() -> QApplication:
    app = QApplication.instance()
    return app if app is not None else QApplication([])


def _window(tmp_path: Path) -> DluSimulatorWindow:
    app = _app()
    apply_application_style(app, "morning")
    window = DluSimulatorWindow(tmp_path / "stage9.sqlite3")
    apply_stage8_ui(window, "morning")
    apply_stage9_ui(window, "morning")
    app.processEvents()
    return window


def test_stage9_opens_on_student_home_with_context_and_quick_actions(tmp_path: Path):
    app = _app()
    window = _window(tmp_path)
    try:
        home = window.findChild(QPushButton, "Stage9HomeButton")
        assert home is not None
        assert home.isChecked()
        assert window.current_view == "learning_home"
        assert window.workspace_left.isHidden() is True
        assert window.learning_home.context_value.text() == "Learning Home"
        assert window.learning_home.continue_button.isEnabled()

        assert len(window.learning_home.action_buttons) == 6
        for button in window.learning_home.action_buttons.values():
            assert button.isEnabled()
            assert button.focusPolicy() != Qt.NoFocus

        app.processEvents()
    finally:
        window.close()


def test_stage9_quick_action_keeps_context_and_active_navigation(tmp_path: Path):
    app = _app()
    window = _window(tmp_path)
    try:
        window.learning_home.action_buttons["OMT / MML"].click()
        app.processEvents()

        assert window.workspace_left.isHidden() is False
        assert window.feature_tabs.tabText(window.feature_tabs.currentIndex()) == "OMT / MML"
        assert window.student_navigation.active_area == "OMT / MML"
        assert "OMT / MML" in window.learning_home.context_value.text()

        omt_button = next(
            b for b in window.findChildren(QPushButton, "Stage8NavButton")
            if b.text() == "OMT / MML"
        )
        assert omt_button.isChecked()

        window.findChild(QPushButton, "Stage9HomeButton").click()
        app.processEvents()
        assert window.current_view == "learning_home"
        assert window.workspace_left.isHidden() is True
    finally:
        window.close()


def test_stage9_progress_and_recent_activity_are_session_scoped(tmp_path: Path):
    app = _app()
    window = _window(tmp_path)
    try:
        window.navigate_student_area("HARDWARE")
        window.navigate_student_area("CALLS")
        app.processEvents()

        assert window.student_navigation.visited_count == 2
        assert window.student_navigation.progress_percent == 33
        assert window.learning_home.progress_bar.value() == 33
        recent = [
            window.learning_home.recent_list.item(i).text()
            for i in range(window.learning_home.recent_list.count())
        ]
        assert "CALLS" in recent[0]
        assert "HARDWARE" in recent[1]
    finally:
        window.close()


def test_stage9_tab_clicks_sync_student_navigation(tmp_path: Path):
    app = _app()
    window = _window(tmp_path)
    try:
        calls_index = next(
            i for i in range(window.feature_tabs.count())
            if window.feature_tabs.tabText(i) == "CALLS"
        )
        window.feature_tabs.setCurrentIndex(calls_index)
        app.processEvents()

        assert window.workspace_left.isHidden() is False
        assert window.student_navigation.active_area == "CALLS"

        home_index = next(
            i for i in range(window.feature_tabs.count())
            if window.feature_tabs.tabText(i) == "Learning Home"
        )
        window.feature_tabs.setCurrentIndex(home_index)
        app.processEvents()
        assert window.current_view == "learning_home"
        assert window.workspace_left.isHidden() is True
    finally:
        window.close()


def test_stage9_keyboard_focus_reaches_home_and_action_controls(tmp_path: Path):
    app = _app()
    window = _window(tmp_path)
    try:
        window.show()
        app.processEvents()
        home = window.findChild(QPushButton, "Stage9HomeButton")
        action = window.learning_home.action_buttons["HARDWARE"]

        home.setFocus()
        app.processEvents()
        assert app.focusWidget() is home

        QTest.keyClick(home, Qt.Key_Tab)
        app.processEvents()
        assert app.focusWidget() is not None
        assert app.focusWidget() is not home

        action.setFocus()
        QTest.keyClick(action, Qt.Key_Space)
        app.processEvents()
        assert window.student_navigation.active_area == "HARDWARE"
    finally:
        window.close()
