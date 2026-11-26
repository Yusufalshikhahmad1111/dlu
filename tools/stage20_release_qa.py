from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from dlu_app import APP_NAME, __version__
from dlu_app.app_shell import build_window


OUT = Path("artifacts/stage20")
TARGETS = ((1280, 720), (1366, 768), (1600, 900), (1920, 1080))


def _capture(window, app, filename: str) -> None:
    app.processEvents()
    window.grab().save(str(OUT / filename))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    assert APP_NAME == "DLU Lab"
    assert __version__ == "2.0.0"

    app = QApplication([])
    with tempfile.TemporaryDirectory(prefix="dlu-stage20-") as temp:
        window = build_window(Path(temp) / "dlu_lab.sqlite3")
        try:
            window.show()
            app.processEvents()

            assert window.feature_tabs.count() >= 7
            for index in range(window.feature_tabs.count()):
                assert window.feature_tabs.tabText(index)

            for index, (width, height) in enumerate(TARGETS, start=1):
                window.set_theme("morning")
                window.resize(width, height)
                window.show_learning_home()
                _capture(
                    window,
                    app,
                    f"{index:02d}-learning-home-morning-{width}x{height}.png",
                )

            window.set_theme("night")
            window.resize(1366, 768)
            window.navigate_student_area("OMT / MML")
            _capture(window, app, "05-omt-night-1366x768.png")

            if hasattr(window, "mml_ux2_panel"):
                panel = window.mml_ux2_panel
                if hasattr(panel, "editor"):
                    command = "> stat dlu: dlu=50;"
                    if hasattr(panel.editor, "setText"):
                        panel.editor.setText(command)
                    elif hasattr(panel.editor, "setPlainText"):
                        panel.editor.setPlainText(command)
                    if hasattr(panel, "quick_run"):
                        panel.quick_run()
                        app.processEvents()

            window.navigate_student_area("CALLS")
            window.call_lab.quick_local()
            _capture(window, app, "06-call-local-night-1366x768.png")

            window.navigate_student_area("COMMUNICATIONS")
            if hasattr(window.communications, "run_current"):
                window.communications.run_current()
                app.processEvents()
            _capture(window, app, "07-communications-night-1366x768.png")

            window.reset_demo()
            app.processEvents()
            window.navigate_student_area("SCENARIOS")
            window.teaching_scenarios.run_selected()
            app.processEvents()
            _capture(window, app, "08-scenario-result-morning.png")

            status = window.teaching_scenarios.status_chip.text()
            assert "PASS" in status or "FAIL" in status

            window.navigate_student_area("HOME")
            window.instructor_mode.run_selected()
            app.processEvents()
            hidden = window.instructor_mode.status.text()
            assert "PASS" not in hidden
            assert "FAIL" not in hidden
            _capture(window, app, "09-instructor-hidden.png")

            window.instructor_mode.reveal_toggle.setChecked(True)
            app.processEvents()
            revealed = window.instructor_mode.status.text()
            assert "PASS" in revealed or "FAIL" in revealed
            window.instructor_mode.set_projector_mode(True)
            _capture(window, app, "10-instructor-projector-revealed.png")

            window.reset_demo()
            app.processEvents()
            assert window.teaching_scenarios.status_chip.text() == "RESET"
            _capture(window, app, "11-reset-clean-state.png")
            return 0
        finally:
            window.close()
            window.db.close()
            app.processEvents()


if __name__ == "__main__":
    raise SystemExit(main())
