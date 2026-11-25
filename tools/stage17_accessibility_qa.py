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
from dlu_app.stage17_accessibility import apply_stage17_accessibility
from dlu_app.ui import DluSimulatorWindow

OUT = Path("artifacts/stage17")
TARGETS = ((1280, 720), (1366, 768), (1600, 900), (1920, 1080))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    app = QApplication([])
    apply_application_style(app, "morning")
    window = DluSimulatorWindow(Path.home() / "stage17-qa.sqlite3")

    for installer in (
        apply_stage8_ui, apply_stage9_ui, apply_stage10_ui,
        apply_stage11_ui, apply_stage12_ui, apply_stage13_ui,
        apply_stage14_ui, apply_stage15_ui, apply_stage16_ui,
    ):
        installer(window, "morning")
    apply_stage17_accessibility(window, "morning")

    assert window.minimumWidth() <= 1180
    assert window.minimumHeight() <= 680
    window.show()
    app.processEvents()

    for index, (width, height) in enumerate(TARGETS, start=1):
        window.set_theme("morning")
        window.resize(width, height)
        window.feature_tabs.setCurrentIndex(0)
        app.processEvents()
        assert window.width() <= width and window.height() <= height
        window.grab().save(str(OUT / f"{index:02d}-{width}x{height}-morning.png"))

    window.set_theme("night")
    window.resize(1366, 768)
    window.feature_tabs.setCurrentWidget(window.instructor_mode)
    app.processEvents()
    window.grab().save(str(OUT / "06-instructor-night-1366x768.png"))

    window.instructor_mode.run_selected()
    assert "PASS" not in window.instructor_mode.status.text()
    assert "FAIL" not in window.instructor_mode.status.text()
    window.instructor_mode.reveal_toggle.setChecked(True)
    assert window.instructor_mode.status.text() in {"PASS", "FAIL"}

    window.instructor_mode.set_projector_mode(True)
    app.processEvents()
    window.grab().save(str(OUT / "07-instructor-projector-night.png"))

    window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
