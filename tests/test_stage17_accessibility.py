from pathlib import Path
from tempfile import TemporaryDirectory

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtTest import QTest

from dlu_app.app_style import apply_application_style
from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.stage9_ui import apply_stage9_ui
from dlu_app.stage10_ui import apply_stage10_ui
from dlu_app.stage11_ui import apply_stage11_ui
from dlu_app.stage12_ui import apply_stage12_ui
from dlu_app.stage13_ui import apply_stage13_ui
from dlu_app.stage14_ui import apply_stage14_ui
from dlu_app.stage15_ui import apply_stage15_ui
from dlu_app.stage16_ui import apply_stage16_ui
from dlu_app.stage17_accessibility import apply_stage17_accessibility, contrast_report
from dlu_app.ui import DluSimulatorWindow


def build_window():
    app = QApplication.instance() or QApplication([])
    apply_application_style(app, "morning")
    tmp = TemporaryDirectory()
    window = DluSimulatorWindow(Path(tmp.name) / "dlu_lab.sqlite3")
    for installer in (
        apply_stage8_ui, apply_stage9_ui, apply_stage10_ui,
        apply_stage11_ui, apply_stage12_ui, apply_stage13_ui,
        apply_stage14_ui, apply_stage15_ui, apply_stage16_ui,
    ):
        installer(window, "morning")
    apply_stage17_accessibility(window, "morning")
    window.show()
    app.processEvents()
    return app, window, tmp


def test_stage17_wcag_aa_contrast():
    for mode in ("morning", "night"):
        assert all(value >= 4.5 for value in contrast_report(mode).values())


def test_stage17_keyboard_accessibility_metadata():
    app, window, tmp = build_window()
    try:
        controls = [
            window.dlu_combo, window.physical_btn, window.logical_btn,
            window.theme_btn, window.nav_dlu_combo, window.nav_shelf_combo,
            window.nav_module_combo, window.input, window.feature_tabs,
            window.instructor_mode.scenario_combo,
            window.instructor_mode.reveal_toggle,
        ]
        for widget in controls:
            assert widget.focusPolicy() != Qt.NoFocus
            assert widget.accessibleName()

        run_buttons = [b for b in window.findChildren(QPushButton) if b.text() == "RUN"]
        assert run_buttons and run_buttons[0].accessibleName() == "Run MML command"
        assert window.theme_btn.toolTip()
        assert window.instructor_mode.projector_button.toolTip()
    finally:
        window.close()
        window.db.close()
        tmp.cleanup()
        app.processEvents()


def test_stage17_focus_and_tab_order():
    app, window, tmp = build_window()
    try:
        window.physical_btn.setFocus()
        app.processEvents()
        assert app.focusWidget() is window.physical_btn
        assert "DLU_STAGE17_FOCUS_BEGIN" in window.styleSheet()
        assert "DLU_STAGE17_FOCUS_BEGIN" in window.instructor_mode.styleSheet()
        window.focusNextChild()
        assert app.focusWidget() is window.logical_btn

        stage16 = window.instructor_mode
        stage16.scenario_combo.setFocus()
        app.processEvents()
        QTest.keyClick(stage16.scenario_combo, Qt.Key_Tab)
        app.processEvents()
        assert app.focusWidget() is stage16.run_button
    finally:
        window.close()
        window.db.close()
        tmp.cleanup()


def test_stage17_empty_state_and_resolution():
    app, window, tmp = build_window()
    try:
        assert window.details_empty.text()
        window._set_details({})
        assert not window.details_empty.isHidden()
        window._set_details({"Hardware": "DLU 50"})
        assert window.details_empty.isHidden()

        assert window.minimumWidth() <= 1180
        assert window.minimumHeight() <= 680
        window.resize(1280, 720)
        app.processEvents()
        assert window.width() <= 1280 and window.height() <= 720
    finally:
        window.close()
        tmp.cleanup()


def test_stage17_instructor_answer_status_is_hidden_until_reveal():
    app, window, tmp = build_window()
    try:
        instructor = window.instructor_mode
        instructor.run_selected()
        assert "PASS" not in instructor.status.text()
        assert "FAIL" not in instructor.status.text()
        assert instructor.status.text().startswith("EXECUTED")
        instructor.reveal_toggle.setChecked(True)
        assert instructor.status.text() in {"PASS", "FAIL"}
    finally:
        window.close()
        tmp.cleanup()
