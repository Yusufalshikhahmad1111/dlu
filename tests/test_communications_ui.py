from PySide6.QtWidgets import QApplication

from dlu_app.communications_ui import CommunicationsLabWidget


def _app() -> QApplication:
    app = QApplication.instance()
    return app if app is not None else QApplication([])


def test_communications_widget_builds_and_runs_each_lab():
    _app()
    widget = CommunicationsLabWidget()

    assert widget.lab_combo.count() == 5
    assert widget.stack.count() == 5

    widget._run_analog()
    widget.analog_mode.setCurrentText("FM")
    widget._run_analog()
    widget.analog_mode.setCurrentText("PM")
    widget._run_analog()

    widget._run_pulse()
    widget.pulse_mode.setCurrentText("PWM")
    widget._run_pulse()
    widget.pulse_mode.setCurrentText("PPM")
    widget._run_pulse()
    widget.pulse_mode.setCurrentText("PCM")
    widget._run_pulse()
    assert "PCM codes:" in widget.pulse_codes.text()

    for mode in ("ASK", "FSK", "PSK", "QPSK", "16-QAM"):
        widget.digital_mode.setCurrentText(mode)
        widget._run_digital()

    for mode in ("BPSK", "QPSK", "16-QAM"):
        widget.ber_mode.setCurrentText(mode)
        widget._run_ber()

    widget.set_theme("silver")
    widget.set_theme("ivory")
    widget.close()
