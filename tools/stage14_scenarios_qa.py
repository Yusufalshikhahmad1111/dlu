from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from dlu_app.app_style import apply_application_style
from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.stage9_ui import apply_stage9_ui
from dlu_app.stage10_ui import apply_stage10_ui
from dlu_app.stage11_ui import apply_stage11_ui
from dlu_app.stage12_ui import apply_stage12_ui
from dlu_app.stage13_ui import apply_stage13_ui
from dlu_app.stage14_ui import apply_stage14_ui
from dlu_app.ui import DluSimulatorWindow

OUT = Path("artifacts") / "stage14"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    app = QApplication([])
    apply_application_style(app, "morning")
    window = DluSimulatorWindow(Path.home() / "stage14-qa.sqlite3")
    apply_stage8_ui(window, "morning")
    apply_stage9_ui(window, "morning")
    apply_stage10_ui(window, "morning")
    apply_stage11_ui(window, "morning")
    apply_stage12_ui(window, "morning")
    apply_stage13_ui(window, "morning")
    apply_stage14_ui(window, "morning")
    window.resize(1600, 900)
    window.show()
    app.processEvents()

    window.navigate_student_area("SCENARIOS")
    window.teaching_scenarios.scenario_list.setCurrentRow(0)
    app.processEvents()
    window.grab().save(str(OUT / "01-objective-morning.png"))

    window.teaching_scenarios.continue_phase()
    app.processEvents()
    window.grab().save(str(OUT / "02-observe-morning.png"))

    window.teaching_scenarios.continue_phase()
    window.teaching_scenarios.continue_phase()
    app.processEvents()
    window.grab().save(str(OUT / "03-executed-pass-morning.png"))

    window.set_theme("night")
    window.teaching_scenarios.show_hint()
    app.processEvents()
    window.grab().save(str(OUT / "04-hint-night.png"))

    window.teaching_scenarios.scenario_list.setCurrentRow(4)
    window.teaching_scenarios.continue_phase()
    window.teaching_scenarios.continue_phase()
    window.teaching_scenarios.continue_phase()
    app.processEvents()
    window.grab().save(str(OUT / "05-blacklist-diagnosis-night.png"))

    window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
