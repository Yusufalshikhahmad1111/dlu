from pathlib import Path

from PySide6.QtWidgets import QApplication, QPushButton, QTabWidget

from dlu_app.app_style import apply_application_style
from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.ui import DluSimulatorWindow


def _app() -> QApplication:
    app = QApplication.instance()
    return app if app is not None else QApplication([])


def test_stage8_shell_applies_and_preserves_feature_tabs(tmp_path: Path):
    app = _app()
    apply_application_style(app)

    window = DluSimulatorWindow(tmp_path / "stage8.sqlite3")
    try:
        apply_stage8_ui(window)

        assert window.objectName() == "DLULabStage8"
        assert window.findChild(QPushButton, "ThemeToggle").isHidden()

        nav = window.findChild(QPushButton, "Stage8NavButton")
        assert nav is not None

        tabs = [
            widget for widget in window.findChildren(QTabWidget)
            if "OMT / MML" in [widget.tabText(i) for i in range(widget.count())]
        ]
        assert tabs

        labels = [tabs[0].tabText(i) for i in range(tabs[0].count())]
        assert labels[:5] == [
            "OMT / MML",
            "COMMAND FILES",
            "CALLS",
            "COMMS LAB",
            "SCENARIOS",
        ]
        assert "Hardware" in labels
    finally:
        window.close()
        app.processEvents()


def test_stage8_v2_theme_toggle_and_omt_command_execution(tmp_path: Path):
    app = _app()
    apply_application_style(app, "morning")

    window = DluSimulatorWindow(tmp_path / "stage8-v2.sqlite3")
    try:
        apply_stage8_ui(window, "morning")

        theme_button = window.findChild(QPushButton, "ThemeToggle")
        assert theme_button is not None
        assert not theme_button.isHidden()
        assert "NIGHT" in theme_button.text()

        nav_buttons = {
            button.text(): button
            for button in window.findChildren(QPushButton, "Stage8NavButton")
        }
        assert set(("HARDWARE", "OMT / MML", "CALLS", "COMMANDS", "COMMS LAB", "SCENARIOS")) <= set(nav_buttons)

        nav_buttons["OMT / MML"].click()
        app.processEvents()

        window.input.setText("> help;")
        send = window.findChild(QPushButton, "CommandSend")
        assert send is not None
        send.click()
        app.processEvents()

        terminal_text = window.terminal.toPlainText()
        assert "[OK]" in terminal_text
        assert "Commands:" in terminal_text
        assert "OK · OK" in window.command_status.text()

        window.set_theme("night")
        app.processEvents()
        assert window.property("dlu_theme_mode") == "night"
        assert "DAY" in theme_button.text()

        window.set_theme("morning")
        app.processEvents()
        assert window.property("dlu_theme_mode") == "morning"
        assert "NIGHT" in theme_button.text()
    finally:
        window.close()
        app.processEvents()
