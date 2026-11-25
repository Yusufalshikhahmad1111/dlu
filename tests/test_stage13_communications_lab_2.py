from PySide6.QtWidgets import QApplication

from dlu_app.stage13_ui import Stage13CommunicationsLabWidget


def _app() -> QApplication:
    app = QApplication.instance()
    return app if app is not None else QApplication([])


def test_stage13_builds_all_five_experiments():
    _app()
    widget = Stage13CommunicationsLabWidget()
    assert widget.lab_combo.count() == 5
    assert widget.stack.count() == 5
    assert widget.live_check.isChecked()
    widget.close()


def test_stage13_analog_updates_visual_measurements():
    _app()
    widget = Stage13CommunicationsLabWidget()
    widget.lab_combo.setCurrentIndex(1)
    widget.analog_mode.setCurrentText("AM")
    widget.analog_mu.setValue(1.2)
    widget._run_analog()
    assert "5" in widget.analog_metrics[0].value.text()
    assert "over-modulation" in widget.analog_explain.text()
    assert widget.analog_canvas.kind == "wave"
    widget.close()


def test_stage13_pulse_pcm_exposes_codes_and_levels():
    _app()
    widget = Stage13CommunicationsLabWidget()
    widget.lab_combo.setCurrentIndex(2)
    widget.pulse_mode.setCurrentText("PCM")
    widget.pulse_samples.setValue(6)
    widget.pulse_bits.setValue(4)
    widget._run_pulse()
    codes = widget.pulse_codes.text()
    assert "PCM codes:" in codes
    assert len(codes.split(":", 1)[1].split()) == 6
    assert widget.pulse_metrics[1].value.text() == "16"
    widget.close()


def test_stage13_digital_qpsk_and_qam_show_constellation_evidence():
    _app()
    widget = Stage13CommunicationsLabWidget()
    widget.lab_combo.setCurrentIndex(3)
    widget.digital_mode.setCurrentText("QPSK")
    widget._run_digital()
    assert widget.digital_constellation.kind == "constellation"
    assert widget.digital_metrics[3].value.text() == "4"
    widget.digital_mode.setCurrentText("16-QAM")
    widget._run_digital()
    assert widget.digital_metrics[3].value.text() == "16"
    widget.close()


def test_stage13_ber_measurement_is_deterministic_and_explained():
    _app()
    widget = Stage13CommunicationsLabWidget()
    widget.lab_combo.setCurrentIndex(4)
    widget.ber_mode.setCurrentText("BPSK")
    widget.ber_seed.setValue(31)
    widget.ber_target.setValue(8)
    widget._run_ber()
    first = widget.ber_metrics[2].value.text()
    widget._run_ber()
    second = widget.ber_metrics[2].value.text()
    assert first == second
    assert "finite bitstream" in widget.ber_explain.text()
    assert widget.ber_canvas.kind == "ber"
    assert widget.ber_constellation.kind == "constellation"
    widget.close()


def test_stage13_live_update_can_be_disabled_and_theme_switches():
    _app()
    widget = Stage13CommunicationsLabWidget()
    widget.live_check.setChecked(False)
    assert not widget.live_check.isChecked()
    widget.set_theme("night")
    assert widget._theme == "night"
    widget.set_theme("morning")
    assert widget._theme == "morning"
    widget.close()
