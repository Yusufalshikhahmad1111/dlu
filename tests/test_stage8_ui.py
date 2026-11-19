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
        assert labels == [
            "OMT / MML",
            "COMMAND FILES",
            "CALLS",
            "COMMS LAB",
            "SCENARIOS",
        ]
    finally:
        window.close()
        app.processEvents()
