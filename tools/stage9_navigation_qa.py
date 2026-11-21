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
from dlu_app.stage9_ui import apply_stage9_ui
from dlu_app.ui import DluSimulatorWindow


TARGETS = (
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
)


def main() -> int:
    output = PROJECT_ROOT / "artifacts" / "stage9-navigation"
    output.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    apply_application_style(app, "morning")

    db_path = output / "qa.sqlite3"
    if db_path.exists():
        db_path.unlink()

    window = DluSimulatorWindow(db_path)
    try:
        apply_stage8_ui(window, "morning")
        apply_stage9_ui(window, "morning")

        home_button = window.findChild(QPushButton, "Stage9HomeButton")
        if home_button is None:
            raise AssertionError("Stage 9 HOME button was not created")

        for width, height in TARGETS:
            window.resize(width, height)
            window.show()
            window.navigate_student_area("HOME")
            app.processEvents()

            if window.current_view != "learning_home":
                raise AssertionError("Learning Home is not active")
            if window.workspace_left.isVisible():
                raise AssertionError("Hardware workspace was not collapsed for Home")
            if window.learning_home.width() < width - 40:
                raise AssertionError("Learning Home does not fill the available workspace")

            home_path = output / f"home-{width}x{height}.png"
            if not window.grab().save(str(home_path)):
                raise RuntimeError(f"Failed to save {home_path}")

        # Interaction gate: navigate to OMT, then return Home.
        window.navigate_student_area("OMT / MML")
        app.processEvents()
        if window.feature_tabs.tabText(window.feature_tabs.currentIndex()) != "OMT / MML":
            raise AssertionError("OMT navigation failed")
        if window.workspace_left.isHidden():
            raise AssertionError("Feature workspace did not reopen")

        omt_path = output / "omt-mml-1600x900.png"
        window.resize(1600, 900)
        window.show()
        app.processEvents()
        if not window.grab().save(str(omt_path)):
            raise RuntimeError("Failed to save OMT screenshot")

        window.navigate_student_area("HOME")
        window.set_theme("night")
        app.processEvents()
        night_path = output / "home-night-1600x900.png"
        if not window.grab().save(str(night_path)):
            raise RuntimeError("Failed to save night screenshot")

        if window.property("dlu_theme_mode") != "night":
            raise AssertionError("Night mode was not applied")

        window.set_theme("morning")
        app.processEvents()
        return 0
    finally:
        window.close()
        app.processEvents()


if __name__ == "__main__":
    raise SystemExit(main())
