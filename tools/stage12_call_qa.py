from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from dlu_app.app_style import apply_application_style
from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.stage9_ui import apply_stage9_ui
from dlu_app.stage10_ui import apply_stage10_ui
from dlu_app.stage11_ui import apply_stage11_ui
from dlu_app.stage12_ui import apply_stage12_ui
from dlu_app.ui import DluSimulatorWindow


OUT = Path("artifacts") / "stage12"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    app = QApplication([])
    apply_application_style(app, "morning")
    window = DluSimulatorWindow(Path.home() / "stage12-qa.sqlite3")
    apply_stage8_ui(window, "morning")
    apply_stage9_ui(window, "morning")
    apply_stage10_ui(window, "morning")
    apply_stage11_ui(window, "morning")
    apply_stage12_ui(window, "morning")
    window.resize(1600, 900)
    window.show()
    app.processEvents()

    window.navigate_student_area("CALLS")
    window.call_lab.quick_local()
    app.processEvents()
    window.grab().save(str(OUT / "local-connected-morning.png"))

    window.call_lab.reset()
    window.set_theme("night")
    app.processEvents()
    window.call_lab.quick_national()
    app.processEvents()
    window.grab().save(str(OUT / "national-connected-night.png"))

    window.call_lab.reset()
    window.set_theme("morning")
    window.call_lab.quick_blacklist()
    app.processEvents()
    window.grab().save(str(OUT / "blocked-blacklist-morning.png"))

    window.call_lab.reset()
    window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
