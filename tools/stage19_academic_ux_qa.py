from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from dlu_app.app_shell import build_window

OUT = Path("artifacts/stage19")
TARGETS = ((1280, 720), (1366, 768), (1600, 900), (1920, 1080))

def _capture(window, app, area, filename):
    window.navigate_student_area(area)
    app.processEvents()
    assert window.breadcrumb.text()
    assert window.feature_tabs.currentWidget() is not None
    window.grab().save(str(OUT / filename))

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    app = QApplication([])
    window = build_window(Path.home() / "stage19-qa.sqlite3")
    try:
        window.show()
        app.processEvents()
        window.show_learning_home()
        app.processEvents()
        window.grab().save(str(OUT / "01-learning-home.png"))
        for index, (width, height) in enumerate(TARGETS, start=2):
            window.resize(width, height)
            window.navigate_student_area("OMT / MML")
            app.processEvents()
            window.grab().save(str(OUT / f"{index:02d}-omt-{width}x{height}.png"))
        _capture(window, app, "HARDWARE", "06-hardware-context.png")
        _capture(window, app, "CALLS", "07-call-context.png")
        window.call_lab.quick_local()
        app.processEvents()
        window.grab().save(str(OUT / "08-call-local-result.png"))
        _capture(window, app, "COMMUNICATIONS", "09-communications-context.png")
        window.reset_demo()
        app.processEvents()
        _capture(window, app, "SCENARIOS", "10-scenarios-context.png")
        window.teaching_scenarios.run_selected()
        app.processEvents()
        window.grab().save(str(OUT / "11-scenario-result.png"))
        window.navigate_student_area("HOME")
        app.processEvents()
        window.instructor_mode.run_selected()
        app.processEvents()
        assert "PASS" not in window.instructor_mode.status.text()
        assert "FAIL" not in window.instructor_mode.status.text()
        window.grab().save(str(OUT / "12-instructor-hidden.png"))
        return 0
    finally:
        window.close()
        window.db.close()
        app.processEvents()

if __name__ == "__main__":
    raise SystemExit(main())
