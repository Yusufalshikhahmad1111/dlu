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
from dlu_app.stage15_ui import apply_stage15_ui
from dlu_app.stage16_ui import apply_stage16_ui
from dlu_app.ui import DluSimulatorWindow

OUT = Path("artifacts") / "stage16"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    app = QApplication([])
    apply_application_style(app, "morning")
    window = DluSimulatorWindow(Path.home() / "stage16-qa.sqlite3")
    apply_stage8_ui(window, "morning")
    apply_stage9_ui(window, "morning")
    apply_stage10_ui(window, "morning")
    apply_stage11_ui(window, "morning")
    apply_stage12_ui(window, "morning")
    apply_stage13_ui(window, "morning")
    apply_stage14_ui(window, "morning")
    apply_stage15_ui(window, "morning")
    apply_stage16_ui(window, "morning")
    window.resize(1600, 900)
    window.show()
    app.processEvents()

    window.feature_tabs.setCurrentWidget(window.instructor_mode)
    app.processEvents()
    window.grab().save(str(OUT / "01-instructor-home-morning.png"))

    window.instructor_mode.run_selected()
    app.processEvents()
    window.grab().save(str(OUT / "02-scenario-result-hidden-morning.png"))

    window.instructor_mode.reveal_toggle.setChecked(True)
    window.instructor_mode.start_guided_demo()
    app.processEvents()
    window.grab().save(str(OUT / "03-guided-demo-revealed-morning.png"))

    window.set_theme("night")
    if hasattr(window, "stage16_controller"):
        window.stage16_controller.set_mode("night")
    window.instructor_mode.set_projector_mode(True)
    app.processEvents()
    window.grab().save(str(OUT / "04-projector-night.png"))

    window.instructor_mode.set_projector_mode(False)
    window.instructor_mode.reset_demo()
    app.processEvents()
    assert window.instructor_mode._result is None
    window.grab().save(str(OUT / "05-reset-night.png"))

    window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
