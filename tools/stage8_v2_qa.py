from __future__ import annotations

from pathlib import Path
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication, QPushButton

from dlu_app.app_style import apply_application_style
from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.ui import DluSimulatorWindow


def main() -> int:
    output = PROJECT_ROOT / "artifacts" / "stage8-v2"
    output.mkdir(parents=True, exist_ok=True)

    app = QApplication.instance() or QApplication([])
    apply_application_style(app, "morning")
    db_path = output / "qa.sqlite3"
    if db_path.exists():
        db_path.unlink()

    window = DluSimulatorWindow(db_path)
    try:
        apply_stage8_ui(window, "morning")
        window.resize(1280, 720)
        window.show()
        app.processEvents()

        # Functional gate: use the actual navigation button and Run button.
        nav = {
            button.text(): button
            for button in window.findChildren(QPushButton, "Stage8NavButton")
        }
        nav["OMT / MML"].click()
        app.processEvents()

        run = window.findChild(QPushButton, "CommandSend")
        if run is None:
            raise AssertionError("Command Run button not found")

        window.input.setText("> help;")
        run.click()
        app.processEvents()

        text = window.terminal.toPlainText()
        if "[OK]" not in text or "Commands:" not in text:
            raise AssertionError("MML command did not produce the expected help result")

        morning = output / "morning.png"
        if not window.grab().save(str(morning)):
            raise RuntimeError("Failed to save Morning screenshot")

        window.set_theme("night")
        app.processEvents()
        night = output / "night.png"
        if not window.grab().save(str(night)):
            raise RuntimeError("Failed to save Night screenshot")

        if window.property("dlu_theme_mode") != "night":
            raise AssertionError("Night theme property was not applied")

        window.set_theme("morning")
        app.processEvents()
        return 0
    finally:
        window.close()
        app.processEvents()


if __name__ == "__main__":
    raise SystemExit(main())
