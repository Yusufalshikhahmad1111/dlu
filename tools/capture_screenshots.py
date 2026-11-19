from __future__ import annotations

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QTabWidget

from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.ui import DluSimulatorWindow


FEATURE_SCREENSHOTS = (
    ("SCENARIOS", "02-teaching-scenarios.png"),
    ("CALLS", "03-call-path.png"),
    ("COMMS LAB", "04-communications.png"),
    ("COMMAND FILES", "05-command-files.png"),
)

VISUAL_QA_SIZES = (
    ((1280, 720), "06-qa-1280x720.png"),
    ((1366, 768), "07-qa-1366x768.png"),
    ((1600, 900), "08-qa-1600x900.png"),
    ((1920, 1080), "09-qa-1920x1080.png"),
)


def _capture_window(window, app, output_dir: Path, size: tuple[int, int], filename: str) -> Path:
    width, height = size
    window.resize(width, height)
    app.processEvents()
    path = output_dir / filename
    if not window.grab().save(str(path)):
        raise RuntimeError(f"Could not save screenshot: {path}")
    return path


def capture(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])

    with TemporaryDirectory(prefix="dlu-screenshot-") as tmp:
        window = DluSimulatorWindow(Path(tmp) / "screenshot.sqlite3")
        try:
            apply_stage8_ui(window)
            window.resize(1580, 940)
            window.show()
            app.processEvents()

            outputs: list[Path] = []

            outputs.append(
                _capture_window(
                    window,
                    app,
                    output_dir,
                    (1580, 940),
                    "01-main-workbench.png",
                )
            )

            tabs = window.findChildren(QTabWidget)
            main_tabs = max(tabs, key=lambda widget: widget.count()) if tabs else None
            if main_tabs is not None:
                for tab_name, filename in FEATURE_SCREENSHOTS:
                    index = -1
                    for i in range(main_tabs.count()):
                        if main_tabs.tabText(i) == tab_name:
                            index = i
                            break
                    if index < 0:
                        continue
                    main_tabs.setCurrentIndex(index)
                    app.processEvents()
                    outputs.append(
                        _capture_window(
                            window,
                            app,
                            output_dir,
                            (1580, 940),
                            filename,
                        )
                    )

            # Return to the main hardware shell before capturing all required
            # resolution QA frames.
            if hasattr(window, "show_hardware_home"):
                window.show_hardware_home()
                app.processEvents()

            for size, filename in VISUAL_QA_SIZES:
                outputs.append(
                    _capture_window(
                        window,
                        app,
                        output_dir,
                        size,
                        filename,
                    )
                )

            return outputs
        finally:
            window.close()
            app.processEvents()
            QCoreApplication.processEvents()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="artifacts/screenshots",
        help="Directory where PNG screenshots are written.",
    )
    args = parser.parse_args()
    outputs = capture(Path(args.output_dir))
    for path in outputs:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
