from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication

from dlu_app.ui import DluSimulatorWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("DLU Lab")
    app.setOrganizationName("PEU")
    data_dir = Path.home() / "AppData" / "Local" / "DLULab"
    db_path = data_dir / "dlu_lab.sqlite3"
    window = DluSimulatorWindow(db_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
