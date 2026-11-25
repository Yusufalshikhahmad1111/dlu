from pathlib import Path
from tempfile import TemporaryDirectory

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from dlu_app.app_style import apply_application_style
from dlu_app.design_tokens import get_tokens
from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.stage9_ui import apply_stage9_ui
from dlu_app.stage10_ui import apply_stage10_ui
from dlu_app.stage11_ui import apply_stage11_ui
from dlu_app.stage12_ui import apply_stage12_ui
from dlu_app.stage13_ui import apply_stage13_ui
from dlu_app.stage14_ui import apply_stage14_ui
from dlu_app.stage15_ui import apply_stage15_ui
from dlu_app.stage16_ui import apply_stage16_ui
from dlu_app.stage17_accessibility import (
    apply_stage17_accessibility,
    contrast_report,
)
from dlu_app.ui import DluSimulatorWindow


def _app():
    app = QApplication.instance()
    return app if app is not None else QApplication([])


def _window():
    app = _app()
    apply_application_style(app, "morning")
    tmp = TemporaryDirectory()
    window = DluSimulatorWindow(Path(tmp.name) / "dlu_lab.sqlite3")
    apply_stage8_ui(window, "morning")
    apply_stage9_ui(window, "morning")
    apply_stage10_ui(window, "morning")
    apply_stage11_ui(window, "morning")
    apply_stage12_ui(window, "morning")
    apply_stage13_ui(window, "morning")
    apply_stage14_ui(window, "morning")
    apply_stage15_ui(window, "morning")
    apply_stage16_ui(window, "morning")
    apply_stage17_accessibility(window, "morning")
    window.show()
    app.processEvents()
    return app, window, tmp


def test_stage17_wcag_aa_contrast_report():
    for mode in ("morning", "night"):
        report = contrast_report(mode)
        assert all(value >= 4.5 for value in report.values()), report


def test_stage17_core_controls_are_named_and_focusable():
    _app()
    _app_window = _window()
    app, window, tmp = _app_window
    try:
        critical = (
            window.dlu_combo,
            window.physical_btn,
            window.logical_btn,
            window.theme_btn,
            window.nav_dlu_combo,
            window.nav_shelf_combo,
            window.nav_module_combo,
            window.input,
            window.feature_tabs,
            window.instructor_mode.scenario_combo,
            window.instructor_mode.reveal_toggle,
        )
        for widget in critical:
            assert widget.focusPolicy() != Qt.NoFocus
            assert widget.accessibleName()
        assert "Run MML command" == next(
            button.accessibleName()
            for button in window.findChildren(type(window.execute_button))
            if button.text() == "RUN"
        )
    finally:
        window.close()
        tmp.cleanup()
        app.processEvents()


def test_stage17_keyboard_order_and_focus_visibility():
    app, window, tmp = _window()
    try:
        window.physical_btn.setFocus()
        app.processEvents()
        assert app.focusWidget() is window.physical_btn
        assert window.physical_btn.styleSheet().find("DLU_STAGE17_FOCUS_BEGIN") >= 0
        assert window.logical_btn.styleSheet().find("DLU_STAGE17_FOCUS_BEGIN") >= 0
        window.focusNextChild()
        assert app.focusWidget() is window.logical_btn

        stage16 = window.instructor_mode
        stage16.scenario_combo.setFocus()
        app.processEvents()
        assert app.focusWidget() is stage16.scenario_combo
        window.focusNextChild()
        assert app.focusWidget() is stage16.run_button
    finally:
        window.close()
        tmp.cleanup()


def test_stage17_tooltips_cover_ambiguous_actions():
    app, window, tmp = _window()
    try:
        expected = (
            window.theme_btn,
            window.back_btn,
            window.input,
            window.execute_button,
            window.instructor_mode.reveal_toggle,
            window.instructor_mode.projector_button,
        )
        for widget in expected:
            assert widget.toolTip()
    finally:
        window.close()
        tmp.cleanup()


def test_stage17_empty_state_is_explicit():
    app, window, tmp = _window()
    try:
        assert window.details_empty.text()
        window._set_details({})
        assert window.details_empty.isVisible()
        window._set_details({"Hardware": "DLU 50"})
        assert not window.details_empty.isVisible()
    finally:
        window.close()
        tmp.cleanup()


def test_stage17_low_resolution_window_is_not_blocked_by_minimum_size():
    app, window, tmp = _window()
    try:
        assert window.minimumWidth() <= 1180
        assert window.minimumHeight() <= 680
        window.resize(1280, 720)
        app.processEvents()
        assert window.width() <= 1280
        assert window.height() <= 720
    finally:
        window.close()
        tmp.cleanup()


def test_stage17_answer_visibility_hardening_is_preserved():
    app, window, tmp = _window()
    try:
        instructor = window.instructor_mode
        instructor.run_selected()
        status = instructor.status.text()
        assert "PASS" not in status and "FAIL" not in status
        assert status.startswith("EXECUTED")
        instructor.reveal_toggle.setChecked(True)
        assert instructor.status.text() in {"PASS", "FAIL"}
    finally:
        window.close()
        tmp.cleanup()
