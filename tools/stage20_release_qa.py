from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from dlu_app import APP_NAME, __version__
from dlu_app.app_shell import build_window

EXPECTED_VERSION = "2.0.0"
TARGETS = (
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
)
STUDENT_AREAS = (
    ("HARDWARE", "02-hardware.png"),
    ("OMT / MML", "03-omt-mml.png"),
    ("CALLS", "04-call-path.png"),
    ("COMMAND FILES", "05-command-files.png"),
    ("COMMUNICATIONS", "06-communications.png"),
    ("SCENARIOS", "07-scenarios.png"),
)


def _save(window, output_dir: Path, filename: str) -> None:
    path = output_dir / filename
    if not window.grab().save(str(path)):
        raise RuntimeError(f"Could not save screenshot: {path}")


def _assert_tab_accessibility(window) -> None:
    assert window.feature_tabs.count() >= 7
    for index in range(window.feature_tabs.count()):
        assert window.feature_tabs.tabText(index)
        assert window.feature_tabs.tabToolTip(index)
        widget = window.feature_tabs.widget(index)
        assert widget is not None
        assert widget.accessibleName()


def _capture_target_resolutions(window, app, output_dir: Path) -> None:
    window.show_learning_home()
    app.processEvents()
    for width, height in TARGETS:
        window.resize(width, height)
        app.processEvents()
        assert window.width() == width
        assert window.height() == height
        _save(window, output_dir, f"10-qa-{width}x{height}.png")


def run(output_dir: Path) -> list[Path]:
    if __version__ != EXPECTED_VERSION:
        raise AssertionError(
            f"Release QA expects {EXPECTED_VERSION}, found {__version__}."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    window = build_window(Path.home() / "dlu-stage20-release.sqlite3")
    captured: list[Path] = []

    try:
        window.show()
        app.processEvents()
        assert APP_NAME == "DLU Lab"
        _assert_tab_accessibility(window)

        window.show_learning_home()
        app.processEvents()
        _save(window, output_dir, "01-learning-home.png")

        for area, filename in STUDENT_AREAS:
            window.navigate_student_area(area)
            app.processEvents()
            assert window.breadcrumb.text()
            _save(window, output_dir, filename)
            if area == "SCENARIOS":
                window.reset_demo()
                app.processEvents()
                window.teaching_scenarios.run_selected()
                app.processEvents()
                assert "PASS" in window.teaching_scenarios.status_chip.text()
                _save(window, output_dir, "08-scenario-pass.png")

        window.feature_tabs.setCurrentWidget(window.instructor_mode)
        app.processEvents()
        window.instructor_mode.run_selected()
        app.processEvents()
        assert window.instructor_mode.status.text().startswith("EXECUTED")
        assert "PASS" not in window.instructor_mode.status.text()
        assert "FAIL" not in window.instructor_mode.status.text()
        _save(window, output_dir, "09-instructor-hidden.png")

        window.instructor_mode.reveal_toggle.setChecked(True)
        app.processEvents()
        assert window.instructor_mode.status.text() in {"PASS", "FAIL"}
        window.set_theme("night")
        window.instructor_mode.set_projector_mode(True)
        app.processEvents()
        _save(window, output_dir, "11-instructor-projector-night.png")

        _capture_target_resolutions(window, app, output_dir)
        captured.extend(sorted(output_dir.glob("*.png")))
        assert len(captured) >= 13
        return captured
    finally:
        window.close()
        try:
            window.db.close()
        finally:
            app.processEvents()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="artifacts/stage20",
        help="Directory for final release screenshots.",
    )
    args = parser.parse_args()
    for path in run(Path(args.output_dir)):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
