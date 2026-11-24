from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from dlu_app import APP_NAME, __version__
from dlu_app.app_style import apply_application_style
from dlu_app.backup_restore import BackupError, DatabaseBackupManager
from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.stage9_ui import apply_stage9_ui
from dlu_app.stage10_ui import apply_stage10_ui
from dlu_app.stage11_ui import apply_stage11_ui
from dlu_app.stage12_ui import apply_stage12_ui
from dlu_app.ui import DluSimulatorWindow


def main() -> int:
    app = QApplication(sys.argv)
    apply_application_style(app)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(__version__)
    app.setOrganizationName("PEU")

    if "--version" in sys.argv[1:]:
        print(f"{APP_NAME} {__version__}")
        return 0

    data_dir = Path.home() / "AppData" / "Local" / "DLULab"
    db_path = data_dir / "dlu_lab.sqlite3"

    try:
        DatabaseBackupManager.apply_pending_restore(db_path)
    except BackupError as exc:
        QMessageBox.critical(
            None,
            "DLU Lab Restore Error",
            f"A pending database restore could not be applied safely.\n\n{exc}",
        )
        return 2

    window = DluSimulatorWindow(db_path)
    apply_stage8_ui(window)
    apply_stage9_ui(window)
    apply_stage10_ui(window)
    apply_stage11_ui(window)
    apply_stage12_ui(window)

    # Keep the default desktop presentation within the user's available
    # work area while preserving the larger Stage 8 reference size when space
    # permits.
    screen = app.primaryScreen()
    if screen is not None:
        available = screen.availableGeometry()
        width = min(1580, max(1180, available.width() - 40))
        height = min(940, max(680, available.height() - 80))
        window.resize(width, height)

    if "--smoke-test" in sys.argv[1:]:
        window.show()
        app.processEvents()
        window.close()
        return 0

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
