from __future__ import annotations

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QTabWidget

from dlu_app.ui import DluSimulatorWindow


def capture(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    with TemporaryDirectory(prefix="dlu-screenshot-") as tmp:
        window = DluSimulatorWindow(Path(tmp) / "screenshot.sqlite3")
        window.resize(1580, 940)
        window.show()
        app.processEvents()

        outputs: list[Path] = []
        home = output_dir / "01-main-workbench.png"
        window.grab().save(home)
        outputs.append(home)

        tabs = window.findChildren(QTabWidget)
        main_tabs = max(tabs, key=lambda widget: widget.count()) if tabs else None
        if main_tabs is not None:
            for tab_name, filename in (
                ("Scenarios", "02-teaching-scenarios.png"),
                ("Call Path", "03-call-path.png"),
                ("Communications", "04-communications.png"),
                ("Command Files", "05-command-files.png"),
            ):
                index = -1
                for i in range(main_tabs.count()):
                    if main_tabs.tabText(i) == tab_name:
                        index = i
                        break
                if index < 0:
                    continue
                main_tabs.setCurrentIndex(index)
                app.processEvents()
                path = output_dir / filename
                window.grab().save(path)
                outputs.append(path)

        window.close()
        QCoreApplication.processEvents()
        return outputs


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
