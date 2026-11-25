from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from dlu_app.app_style import apply_application_style
from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.stage9_ui import apply_stage9_ui
from dlu_app.stage10_ui import apply_stage10_ui
from dlu_app.stage11_ui import apply_stage11_ui
from dlu_app.stage12_ui import apply_stage12_ui
from dlu_app.stage13_ui import apply_stage13_ui
from dlu_app.ui import DluSimulatorWindow


OUT = Path("artifacts") / "stage13"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    app = QApplication([])
    apply_application_style(app, "morning")
    window = DluSimulatorWindow(Path.home() / "stage13-qa.sqlite3")
    apply_stage8_ui(window, "morning")
    apply_stage9_ui(window, "morning")
    apply_stage10_ui(window, "morning")
    apply_stage11_ui(window, "morning")
    apply_stage12_ui(window, "morning")
    apply_stage13_ui(window, "morning")
    window.resize(1600, 900)
    window.show()
    app.processEvents()

    window.navigate_student_area("COMMS LAB")
    window.communications_lab.lab_combo.setCurrentIndex(0)
    window.communications_lab.osi_protocol.setCurrentText("TCP")
    window.communications_lab._run_osi()
    app.processEvents()
    window.grab().save(str(OUT / "01-osi-morning.png"))

    window.set_theme("night")
    window.communications_lab.lab_combo.setCurrentIndex(1)
    window.communications_lab.analog_mode.setCurrentText("FM")
    window.communications_lab.analog_message.setValue(1.5)
    window.communications_lab._run_analog()
    app.processEvents()
    window.grab().save(str(OUT / "02-analog-night.png"))

    window.communications_lab.lab_combo.setCurrentIndex(3)
    window.communications_lab.digital_mode.setCurrentText("16-QAM")
    window.communications_lab._run_digital()
    app.processEvents()
    window.grab().save(str(OUT / "03-digital-qam-night.png"))

    window.set_theme("morning")
    window.communications_lab.lab_combo.setCurrentIndex(4)
    window.communications_lab.ber_mode.setCurrentText("QPSK")
    window.communications_lab.ber_target.setValue(8)
    window.communications_lab._run_ber()
    app.processEvents()
    window.grab().save(str(OUT / "04-ber-morning.png"))

    window.communications_lab.lab_combo.setCurrentIndex(2)
    window.communications_lab.pulse_mode.setCurrentText("PCM")
    window.communications_lab.pulse_bits.setValue(4)
    window.communications_lab._run_pulse()
    app.processEvents()
    window.grab().save(str(OUT / "05-pcm-morning.png"))

    window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
