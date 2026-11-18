import pytest

from dlu_app.communications_lab import (
    analog_waveform,
    ber_curve,
    constellation_points,
    digital_waveform,
    empirical_ber,
    osi_layers,
    pulse_waveform,
    theoretical_ber,
    transport_profiles,
)


def test_osi_layers_are_ordered_and_complete():
    layers = osi_layers()
    assert [layer.number for layer in layers] == list(range(7, 0, -1))
    assert layers[0].name == "Application"
    assert layers[-1].name == "Physical"
    assert all(layer.purpose and layer.examples for layer in layers)


def test_tcp_udp_profiles_expose_teaching_tradeoffs():
    profiles = {profile.name: profile for profile in transport_profiles()}
    assert set(profiles) == {"TCP", "UDP"}
    assert "Reliable" in profiles["TCP"].reliability
    assert "Best-effort" in profiles["UDP"].reliability
    assert profiles["TCP"].connection != profiles["UDP"].connection


@pytest.mark.parametrize("mode", ["AM", "FM", "PM"])
def test_analog_waveforms_are_deterministic(mode):
    first = analog_waveform(mode)
    second = analog_waveform(mode)
    assert first == second
    assert len(first.x) == len(first.y)
    assert len(first.x) >= 64
    assert first.formula
    assert first.summary


def test_am_overmodulation_is_reported():
    result = analog_waveform("AM", modulation_index=1.2)
    assert "over-modulation" in result.summary


@pytest.mark.parametrize("mode", ["PAM", "PWM", "PPM", "PCM"])
def test_pulse_modes_generate_expected_trace(mode):
    result = pulse_waveform(mode, sample_count=8, quantization_bits=3)
    assert len(result.x) == len(result.y)
    assert max(result.y) <= 1.0
    assert min(result.y) >= 0.0
    assert result.formula


def test_pcm_generates_one_code_per_sample():
    result = pulse_waveform("PCM", sample_count=6, quantization_bits=4)
    codes = result.metadata["pcm_codes"].split()
    assert len(codes) == 6
    assert all(len(code) == 4 for code in codes)


@pytest.mark.parametrize("mode", ["ASK", "FSK", "PSK", "QPSK", "16-QAM"])
def test_digital_modes_generate_trace(mode):
    result = digital_waveform(mode, "0011011011001011")
    assert len(result.x) == len(result.y)
    assert len(result.x) > 0
    assert result.metadata["bits"] == "0011011011001011"


def test_digital_invalid_bits_are_rejected():
    with pytest.raises(ValueError, match="only 0 and 1"):
        digital_waveform("ASK", "0102")


def test_qpsk_constellation_has_four_gray_labeled_points():
    points = constellation_points("QPSK")
    assert len(points) == 4
    assert {point.label for point in points} == {"00", "01", "11", "10"}
    assert all(abs(point.i**2 + point.q**2 - 1.0) < 1e-9 for point in points)


def test_16qam_constellation_has_sixteen_points_and_normalized_power():
    points = constellation_points("16-QAM")
    assert len(points) == 16
    assert all(abs(point.i**2 + point.q**2) > 0 for point in points)
    average_power = sum(point.i**2 + point.q**2 for point in points) / len(points)
    assert abs(average_power - 1.0) < 1e-9


@pytest.mark.parametrize("mode", ["BPSK", "QPSK", "16-QAM"])
def test_theoretical_ber_is_bounded(mode):
    values = [theoretical_ber(mode, db) for db in (0, 4, 8, 12)]
    assert all(0.0 < value < 0.5 for value in values)
    assert values == sorted(values, reverse=True)


def test_bpsk_and_qpsk_have_same_awgn_bit_ber_model():
    for db in (0, 2, 6, 10):
        assert theoretical_ber("BPSK", db) == pytest.approx(
            theoretical_ber("QPSK", db)
        )


@pytest.mark.parametrize("mode", ["BPSK", "QPSK", "16-QAM"])
def test_empirical_ber_is_seed_deterministic(mode):
    first = empirical_ber(mode, 6, seed=31)
    second = empirical_ber(mode, 6, seed=31)
    assert first == second
    assert 0.0 <= first <= 1.0


def test_ber_curve_contains_theory_and_empirical_points():
    points = ber_curve("BPSK", start_db=0, stop_db=8, step_db=2, seed=11)
    assert [point.ebn0_db for point in points] == [0, 2, 4, 6, 8]
    assert all(point.empirical is not None for point in points)
    theory = [point.theoretical for point in points]
    assert theory == sorted(theory, reverse=True)


def test_ber_curve_can_disable_empirical_simulation():
    points = ber_curve("QPSK", stop_db=6, step_db=3, empirical=False)
    assert all(point.empirical is None for point in points)


def test_ber_invalid_ranges_are_rejected():
    with pytest.raises(ValueError):
        ber_curve("BPSK", start_db=8, stop_db=0)
    with pytest.raises(ValueError):
        ber_curve("BPSK", step_db=0)


def test_invalid_quantization_bits_are_rejected():
    with pytest.raises(ValueError, match="1..8"):
        pulse_waveform("PCM", quantization_bits=9)
