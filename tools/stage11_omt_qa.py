from __future__ import annotations

import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication

from dlu_app.app_style import apply_application_style
from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.stage9_ui import apply_stage9_ui
from dlu_app.stage10_ui import apply_stage10_ui
from dlu_app.stage11_ui import apply_stage11_ui
from dlu_app.ui import DluSimulatorWindow


TARGETS = ((1280, 720), (1366, 768), (1600, 900), (1920, 1080))


def main() -> int:
    output = PROJECT_ROOT / "artifacts" / "stage11-omt-ux"
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
        apply_stage10_ui(window, "morning")
        apply_stage11_ui(window, "morning")

        for width, height in TARGETS:
            window.resize(width, height)
            window.show()
            window.navigate_student_area("OMT / MML")
            window.set_command_text("> stat dlu: dlu=50;")
            app.processEvents()
            path = output / f"omt-{width}x{height}.png"
            if not window.grab().save(str(path)):
                raise RuntimeError(f"Failed to save {path}")

        window.execute_input()
        app.processEvents()
        if not window.mml_ux2_panel.result.text().startswith("SUCCESS"):
            raise AssertionError("Stage 11 execution result card did not update")
        if "DLU 50" not in window.mml_ux2_panel.result.text():
            raise AssertionError("Stage 11 result target is missing")

        window.set_theme("night")
        app.processEvents()
        night_path = output / "omt-night-1600x900.png"
        window.resize(1600, 900)
        if not window.grab().save(str(night_path)):
            raise RuntimeError("Failed to save night screenshot")
        return 0
    finally:
        window.close()
        app.processEvents()


if __name__ == "__main__":
    raise SystemExit(main())
