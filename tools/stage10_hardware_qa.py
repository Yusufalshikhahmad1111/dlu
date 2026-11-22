from __future__ import annotations

from pathlib import Path
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication

from dlu_app.app_style import apply_application_style
from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.stage9_ui import apply_stage9_ui
from dlu_app.ui import DluSimulatorWindow


TARGETS = (
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
)


def main() -> int:
    output = PROJECT_ROOT / "artifacts" / "stage10-hardware-ux"
    output.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    apply_application_style(app, "morning")

    db_path = output / "qa.sqlite3"
    if db_path.exists():
        db_path.unlink()

    window = DluSimulatorWindow(db_path)
    try:
        apply_stage8_ui(window, "morning")
        apply_stage9_ui(window, "morning")

        for width, height in TARGETS:
            window.resize(width, height)
            window.show()
            window.navigate_student_area("HARDWARE")
            window.show_dlu(50)
            app.processEvents()
            path = output / f"hardware-{width}x{height}.png"
            if not window.grab().save(str(path)):
                raise RuntimeError(f"Failed to save {path}")

        window.show_module(50, 0, 15)
        app.processEvents()
        module_path = output / "module-50-0-15-1600x900.png"
        window.resize(1600, 900)
        window.show()
        app.processEvents()
        if not window.grab().save(str(module_path)):
            raise RuntimeError("Failed to save module screenshot")

        window.select_port(50, 0, 15, 0)
        app.processEvents()
        port_path = output / "port-50-0-15-0-1600x900.png"
        if not window.grab().save(str(port_path)):
            raise RuntimeError("Failed to save port screenshot")

        if window.hardware_inspector.object_type.text() != "PORT":
            raise AssertionError("Port inspector did not activate")
        if window.hardware_inspector.fact_labels["EQN"].text() != "50-0-15-0":
            raise AssertionError("Port EQN missing from inspector")

        window.set_theme("night")
        app.processEvents()
        night_path = output / "module-night-1600x900.png"
        if not window.grab().save(str(night_path)):
            raise RuntimeError("Failed to save night screenshot")
        return 0
    finally:
        window.close()
        app.processEvents()


if __name__ == "__main__":
    raise SystemExit(main())
