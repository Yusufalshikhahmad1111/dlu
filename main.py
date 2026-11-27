from __future__ import annotations

import os
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from dlu_app import APP_NAME, __version__
from dlu_app.backup_restore import BackupError, DatabaseBackupManager
from dlu_app.app_shell import build_window, configure_application, size_window_to_screen


def main() -> int:
    args = sys.argv[1:]

    # Release probes exit before Qt startup so the packaged GUI executable
    # can be queried safely from Windows CI without initializing a window.
    if "--write-version" in args:
        index = args.index("--write-version")
        if index + 1 >= len(args):
            return 2
        Path(args[index + 1]).write_text(
            f"{APP_NAME} {__version__}\n", encoding="utf-8"
        )
        return 0

    if "--version" in args:
        version_text = f"{APP_NAME} {__version__}"
        print(version_text)
        version_file = os.environ.get("DLU_VERSION_FILE")
        if version_file:
            Path(version_file).write_text(version_text + "\n", encoding="utf-8")
        return 0

    app = QApplication(sys.argv)
    configure_application(app)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(__version__)
    app.setOrganizationName("PEU")

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

    if "--smoke-test" in args:
        window.show()
        app.processEvents()
        window.close()
        return 0

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
