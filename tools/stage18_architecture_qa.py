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

OUT = Path("artifacts/stage18")
TARGETS = ((1280, 720), (1366, 768), (1600, 900), (1920, 1080))

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    app = QApplication([])
    window = build_window(Path.home() / "stage18-qa.sqlite3")
    try:
        window.show()
        app.processEvents()
        for index, (width, height) in enumerate(TARGETS, start=1):
            window.set_theme("morning")
            window.resize(width, height)
            window.show_hardware_home()
            app.processEvents()
            assert window.width() <= width and window.height() <= height
            assert window.hardware.scene().items()
            window.grab().save(str(OUT / f"{index:02d}-{width}x{height}-morning.png"))
        window.set_theme("night")
        window.resize(1366, 768)
        window.show_dlu(50)
        app.processEvents()
        assert window.hardware.scene().items()
        window.grab().save(str(OUT / "05-dlu-night-1366x768.png"))
        window.show_shelf(50, 0)
        app.processEvents()
        assert window.hardware.scene().items()
        window.grab().save(str(OUT / "06-shelf-night-1366x768.png"))
        window.show_module(50, 0, 0)
        app.processEvents()
        assert window.hardware.scene().items()
        window.grab().save(str(OUT / "07-module-night-1366x768.png"))
        return 0
    finally:
        window.close()
        window.db.close()
        app.processEvents()

if __name__ == "__main__":
    raise SystemExit(main())
