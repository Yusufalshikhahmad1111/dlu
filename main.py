from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from dlu_app import APP_NAME, __version__
from dlu_app.backup_restore import BackupError, DatabaseBackupManager
from dlu_app.app_shell import build_window, configure_application, size_window_to_screen


def main() -> int:
    app = QApplication(sys.argv)
    configure_application(app)
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

    window = build_window(db_path)
    size_window_to_screen(window, app)

    if "--smoke-test" in sys.argv[1:]:
        window.show()
        app.processEvents()
        window.close()
        return 0

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
