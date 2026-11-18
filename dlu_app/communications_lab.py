from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Iterable, Sequence


@dataclass(frozen=True)
class OsiLayer:
    number: int
    name: str
    purpose: str
    examples: tuple[str, ...]


@dataclass(frozen=True)
class TransportProfile:
    name: str
    connection: str
    reliability: str
    ordering: str
    overhead: str
    common_use: str


@dataclass(frozen=True)
class Waveform:
    x: tuple[float, ...]
    y: tuple[float, ...]
    title: str
    formula: str
    summary: str
    metadata: dict[str, str]


@dataclass(frozen=True)
class ConstellationPoint:
    label: str
    i: float
    q: float


@dataclass(frozen=True)
class BerPoint:
    ebn0_db: float
    theoretical: float
    empirical: float | None = None


OSI_LAYERS: tuple[OsiLayer, ...] = (
    OsiLayer(7, "Application", "Network services directly used by applications.", ("HTTP", "DNS", "SMTP")),
    OsiLayer(6, "Presentation", "Data representation, encoding, compression, and encryption concepts.", ("UTF-8", "JPEG", "TLS encoding")),
    OsiLayer(5, "Session", "Dialog/session establishment, coordination, and termination.", ("RPC", "session control")),
    OsiLayer(4, "Transport", "End-to-end delivery, multiplexing, reliability, and flow control.", ("TCP", "UDP")),
    OsiLayer(3, "Network", "Logical addressing and packet forwarding between networks.", ("IP", "routing")),
    OsiLayer(2, "Data Link", "Framing, local delivery, and medium access.", ("Ethernet", "802.11")),
    OsiLayer(1, "Physical", "Bits as electrical, optical, or radio signals.", ("copper", "fiber", "radio")),
)

TRANSPORT_PROFILES: tuple[TransportProfile, ...] = (
    TransportProfile(
        "TCP",
        "Connection-oriented",
        "Reliable byte stream with retransmission and acknowledgements.",
        "Ordered byte stream",
        "Higher",
        "Web pages, APIs, file transfer, reliable application data",
    ),
    TransportProfile(
        "UDP",
        "Connectionless",
        "Best-effort datagrams; the application handles recovery when needed.",
        "No delivery-order guarantee",
        "Lower",
        "Real-time media, telemetry, DNS, latency-sensitive traffic",
    ),
)


def osi_layers() -> tuple[OsiLayer, ...]:
    return OSI_LAYERS


def transport_profiles() -> tuple[TransportProfile, ...]:
    return TRANSPORT_PROFILES


def _validate_positive(name: str, value: float) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be > 0")


def _validate_depth(depth: int) -> None:
    if depth < 1 or depth > 8:
        raise ValueError("quantization bits must be 1..8")


def _linspace(start: float, stop: float, count: int) -> tuple[float, ...]:
    if count < 2:
        raise ValueError("count must be >= 2")
    step = (stop - start) / (count - 1)
    return tuple(start + i * step for i in range(count))


def analog_waveform(
    mode: str,
    *,
    modulation_index: float = 0.7,
    carrier_hz: float = 5.0,
    message_hz: float = 1.0,
    frequency_deviation_hz: float = 2.0,
    phase_sensitivity: float = 1.5,
    samples: int = 320,
) -> Waveform:
    mode = mode.upper()
    if mode not in {"AM", "FM", "PM"}:
        raise ValueError("analog mode must be AM, FM, or PM")
    _validate_positive("carrier_hz", carrier_hz)
    _validate_positive("message_hz", message_hz)
    if samples < 64:
        raise ValueError("samples must be >= 64")
    t = _linspace(0.0, 1.0, samples)

    y: list[float] = []
    for value in t:
        message = math.sin(2.0 * math.pi * message_hz * value)
        carrier_phase = 2.0 * math.pi * carrier_hz * value
        if mode == "AM":
            sample = (1.0 + modulation_index * message) * math.cos(carrier_phase)
            formula = "s(t) = [1 + μ sin(2π fₘ t)] cos(2π f_c t)"
            summary = "Amplitude modulation: the carrier amplitude follows the message."
        elif mode == "FM":
            beta = frequency_deviation_hz / message_hz
            sample = math.cos(carrier_phase + beta * math.sin(2.0 * math.pi * message_hz * value))
            formula = "s(t) = cos(2π f_c t + β sin(2π fₘ t)), β = Δf / fₘ"
            summary = "Frequency modulation: instantaneous frequency varies with the message."
        else:
            sample = math.cos(
                carrier_phase
                + phase_sensitivity * message
            )
            formula = "s(t) = cos(2π f_c t + kₚ sin(2π fₘ t))"
            summary = "Phase modulation: instantaneous phase varies with the message."
        y.append(sample)

    if mode == "AM" and abs(modulation_index) > 1:
        summary += " The selected μ > 1 represents over-modulation and envelope distortion."

    return Waveform(
        t,
        tuple(y),
        f"{mode} waveform",
        formula,
        summary,
        {
            "carrier_hz": f"{carrier_hz:g}",
            "message_hz": f"{message_hz:g}",
        },
    )


def pulse_waveform(
    mode: str,
    *,
    message_hz: float = 1.0,
    sample_count: int = 8,
    quantization_bits: int = 3,
    samples: int = 320,
) -> Waveform:
    mode = mode.upper()
    if mode not in {"PAM", "PWM", "PPM", "PCM"}:
        raise ValueError("pulse mode must be PAM, PWM, PPM, or PCM")
    _validate_positive("message_hz", message_hz)
    if sample_count < 2 or sample_count > 32:
        raise ValueError("sample_count must be 2..32")
    _validate_depth(quantization_bits)
    if samples < 64:
        raise ValueError("samples must be >= 64")

    x = _linspace(0.0, 1.0, samples)
    y = [0.0] * samples
    codes: list[str] = []
    levels = 2**quantization_bits

    for sample_index in range(sample_count):
        center = (sample_index + 0.5) / sample_count
        message = math.sin(2.0 * math.pi * message_hz * center)
        if mode == "PAM":
            width = max(1, int(samples / sample_count * 0.35))
            center_index = min(samples - 1, int(center * (samples - 1)))
            amplitude = 0.5 + 0.5 * message
            for j in range(max(0, center_index - width), min(samples, center_index + width)):
                y[j] = amplitude
        elif mode == "PWM":
            duty = 0.1 + 0.8 * (0.5 + 0.5 * message)
            start = int(sample_index / sample_count * samples)
            stop = min(samples, int((sample_index + duty) / sample_count * samples))
            for j in range(start, stop):
                y[j] = 1.0
        elif mode == "PPM":
            base = sample_index / sample_count
            position = base + (0.65 / sample_count) * (0.5 + 0.5 * message)
            center_index = min(samples - 1, int(position * (samples - 1)))
            for j in range(max(0, center_index - 1), min(samples, center_index + 2)):
                y[j] = 1.0
        else:
            level = min(levels - 1, max(0, round((message + 1.0) * 0.5 * (levels - 1))))
            codes.append(format(level, f"0{quantization_bits}b"))
            start = int(sample_index / sample_count * samples)
            stop = int((sample_index + 1) / sample_count * samples)
            quantized = level / (levels - 1)
            for j in range(start, min(samples, stop)):
                y[j] = quantized

    formulas = {
        "PAM": "Pulse amplitude follows each sampled message value.",
        "PWM": "Pulse width (duty cycle) follows each sampled message value.",
        "PPM": "Pulse position within each slot follows each sampled message value.",
        "PCM": "Sample → quantize → encode; each sample becomes a binary code word.",
    }
    summaries = {
        "PAM": "Pulse Amplitude Modulation represents each sample with a different pulse amplitude.",
        "PWM": "Pulse Width Modulation represents each sample by changing pulse duration.",
        "PPM": "Pulse Position Modulation represents each sample by shifting pulse timing.",
        "PCM": f"Pulse Code Modulation quantizes {sample_count} samples into {quantization_bits}-bit words.",
    }
    metadata = {"sample_count": str(sample_count), "message_hz": f"{message_hz:g}"}
    if codes:
        metadata["pcm_codes"] = " ".join(codes)
    return Waveform(x, tuple(y), f"{mode} waveform", formulas[mode], summaries[mode], metadata)


def _normalize_bits(bits: str) -> str:
    cleaned = "".join(bits.split())
    if not cleaned:
        raise ValueError("bitstream must not be empty")
    if any(bit not in "01" for bit in cleaned):
        raise ValueError("bitstream must contain only 0 and 1")
    return cleaned


def _gray_qpsk(bits: str) -> tuple[float, float]:
    mapping = {
        "00": (math.sqrt(0.5), math.sqrt(0.5)),
        "01": (-math.sqrt(0.5), math.sqrt(0.5)),
        "11": (-math.sqrt(0.5), -math.sqrt(0.5)),
        "10": (math.sqrt(0.5), -math.sqrt(0.5)),
    }
    return mapping[bits]


def _gray_16qam(bits: str) -> tuple[float, float]:
    axis = {
        "00": -3.0,
        "01": -1.0,
        "11": 1.0,
        "10": 3.0,
    }
    scale = math.sqrt(10.0)
    return axis[bits[:2]] / scale, axis[bits[2:]] / scale


def _symbol_groups(modulation: str, bits: str) -> tuple[str, ...]:
    widths = {"ASK": 1, "FSK": 1, "PSK": 1, "QPSK": 2, "QAM": 4}
    width = widths[modulation]
    groups = []
    value = bits
    while len(value) % width:
        value += "0"
    for index in range(0, len(value), width):
        groups.append(value[index:index + width])
    return tuple(groups)


def digital_waveform(
    mode: str,
    bits: str = "00110110",
    *,
    carrier_hz: float = 4.0,
    frequency_shift_hz: float = 2.0,
    samples_per_symbol: int = 28,
) -> Waveform:
    mode = mode.upper().replace("-", "")
    aliases = {"16QAM": "QAM"}
    mode = aliases.get(mode, mode)
    allowed = {"ASK", "FSK", "PSK", "QPSK", "QAM"}
    if mode not in allowed:
        raise ValueError("digital mode must be ASK, FSK, PSK, QPSK, or 16QAM")
    _validate_positive("carrier_hz", carrier_hz)
    if samples_per_symbol < 12:
        raise ValueError("samples_per_symbol must be >= 12")

    clean = _normalize_bits(bits)
    groups = _symbol_groups(mode, clean)
    y: list[float] = []
    x: list[float] = []
    duration_per_symbol = 1.0 / max(carrier_hz * 2.0, 1.0)

    for symbol_index, group in enumerate(groups):
        if mode == "ASK":
            amplitude = 1.0 if group == "1" else 0.0
            frequency = carrier_hz
            phase = 0.0
        elif mode == "FSK":
            amplitude = 1.0
            frequency = carrier_hz + (frequency_shift_hz if group == "1" else -frequency_shift_hz)
            phase = 0.0
        elif mode == "PSK":
            amplitude = 1.0
            frequency = carrier_hz
            phase = 0.0 if group == "0" else math.pi
        elif mode == "QPSK":
            i_value, q_value = _gray_qpsk(group)
            amplitude = 1.0
            frequency = carrier_hz
            phase = math.atan2(q_value, i_value)
        else:
            i_value, q_value = _gray_16qam(group)
            amplitude = math.hypot(i_value, q_value)
            frequency = carrier_hz
            phase = math.atan2(q_value, i_value)

        for offset in range(samples_per_symbol):
            local_t = offset / samples_per_symbol
            t = (symbol_index + local_t) * duration_per_symbol
            x.append(t)
            y.append(amplitude * math.cos(2.0 * math.pi * frequency * t + phase))

    descriptions = {
        "ASK": "Amplitude Shift Keying: bit value changes carrier amplitude.",
        "FSK": "Frequency Shift Keying: bit value selects between two frequencies.",
        "PSK": "Binary Phase Shift Keying: bit value selects 0° or 180° phase.",
        "QPSK": "Quadrature PSK: two bits select one of four carrier phases.",
        "QAM": "16-QAM: four bits select one of sixteen amplitude/phase constellation points.",
    }
    formula = {
        "ASK": "s(t) = A_b cos(2π f_c t)",
        "FSK": "s(t) = cos(2π f_b t), f_b ∈ {f₀, f₁}",
        "PSK": "s(t) = cos(2π f_c t + φ_b)",
        "QPSK": "s(t) = I cos(2πf_ct) − Q sin(2πf_ct)",
        "QAM": "s(t) = I cos(2πf_ct) − Q sin(2πf_ct)",
    }[mode]
    return Waveform(
        tuple(x),
        tuple(y),
        f"{'16-QAM' if mode == 'QAM' else mode} digital waveform",
        formula,
        descriptions[mode],
        {"bits": clean, "symbols": " ".join(groups), "mode": mode},
    )


def constellation_points(mode: str) -> tuple[ConstellationPoint, ...]:
    mode = mode.upper().replace("-", "")
    if mode == "QPSK":
        mapping = {
            "00": (math.sqrt(0.5), math.sqrt(0.5)),
            "01": (-math.sqrt(0.5), math.sqrt(0.5)),
            "11": (-math.sqrt(0.5), -math.sqrt(0.5)),
            "10": (math.sqrt(0.5), -math.sqrt(0.5)),
        }
        return tuple(ConstellationPoint(bits, i, q) for bits, (i, q) in mapping.items())
    if mode in {"QAM", "16QAM"}:
        labels = ("00", "01", "11", "10")
        values = (-3.0, -1.0, 1.0, 3.0)
        scale = math.sqrt(10.0)
        points: list[ConstellationPoint] = []
        for ii, i_value in zip(labels, values):
            for qq, q_value in zip(labels, values):
                points.append(
                    ConstellationPoint(
                        ii + qq,
                        i_value / scale,
                        q_value / scale,
                    )
                )
        return tuple(points)
    raise ValueError("constellation is available for QPSK or 16QAM")


def theoretical_ber(modulation: str, ebn0_db: float) -> float:
    mode = modulation.upper().replace("-", "")
    if mode not in {"BPSK", "QPSK", "16QAM"}:
        raise ValueError("BER basics support BPSK, QPSK, or 16QAM")
    ebn0 = 10.0 ** (ebn0_db / 10.0)
    if mode in {"BPSK", "QPSK"}:
        return 0.5 * math.erfc(math.sqrt(ebn0))
    return 0.375 * math.erfc(math.sqrt(0.2 * ebn0))


def _decision_bpsk(value: float) -> int:
    return 1 if value >= 0 else 0


def _decision_qpsk(i_value: float, q_value: float) -> str:
    candidates = {
        bits: coords
        for bits, coords in (
            ("00", _gray_qpsk("00")),
            ("01", _gray_qpsk("01")),
            ("11", _gray_qpsk("11")),
            ("10", _gray_qpsk("10")),
        )
    }
    return min(
        candidates,
        key=lambda bits: (i_value - candidates[bits][0]) ** 2 + (q_value - candidates[bits][1]) ** 2,
    )


def _decision_16qam(i_value: float, q_value: float) -> str:
    levels = (-3.0, -1.0, 1.0, 3.0)
    labels = ("00", "01", "11", "10")
    scale = math.sqrt(10.0)
    def axis(value: float) -> str:
        target = value * scale
        idx = min(range(4), key=lambda pos: abs(target - levels[pos]))
        return labels[idx]
    return axis(i_value) + axis(q_value)


def empirical_ber(
    modulation: str,
    ebn0_db: float,
    *,
    bits: str = "0011011011001011",
    seed: int = 7,
) -> float:
    mode = modulation.upper().replace("-", "")
    clean = _normalize_bits(bits)
    rng = random.Random(seed)
    bits_per_symbol = {"BPSK": 1, "QPSK": 2, "16QAM": 4}.get(mode)
    if bits_per_symbol is None:
        raise ValueError("empirical BER supports BPSK, QPSK, or 16QAM")
    usable = clean[: len(clean) - (len(clean) % bits_per_symbol)]
    if not usable:
        raise ValueError("bitstream is too short for selected BER modulation")

    ebn0 = 10.0 ** (ebn0_db / 10.0)
    noise_std = math.sqrt(1.0 / (2.0 * bits_per_symbol * ebn0))
    errors = 0
    total = 0

    for index in range(0, len(usable), bits_per_symbol):
        group = usable[index:index + bits_per_symbol]
        if mode == "BPSK":
            transmitted = 1.0 if group == "1" else -1.0
            received = transmitted + rng.gauss(0.0, noise_std)
            decoded = str(_decision_bpsk(received))
            original = group
        elif mode == "QPSK":
            i_value, q_value = _gray_qpsk(group)
            decoded = _decision_qpsk(
                i_value + rng.gauss(0.0, noise_std),
                q_value + rng.gauss(0.0, noise_std),
            )
            original = group
        else:
            i_value, q_value = _gray_16qam(group)
            decoded = _decision_16qam(
                i_value + rng.gauss(0.0, noise_std),
                q_value + rng.gauss(0.0, noise_std),
            )
            original = group
        errors += sum(a != b for a, b in zip(decoded, original))
        total += bits_per_symbol

    return errors / total


def ber_curve(
    modulation: str,
    *,
    start_db: float = 0.0,
    stop_db: float = 14.0,
    step_db: float = 2.0,
    empirical: bool = True,
    seed: int = 7,
) -> tuple[BerPoint, ...]:
    if step_db <= 0:
        raise ValueError("step_db must be > 0")
    if stop_db < start_db:
        raise ValueError("stop_db must be >= start_db")
    points: list[BerPoint] = []
    current = start_db
    index = 0
    while current <= stop_db + 1e-9:
        points.append(
            BerPoint(
                current,
                theoretical_ber(modulation, current),
                empirical_ber(modulation, current, seed=seed + index)
                if empirical
                else None,
            )
        )
        current += step_db
        index += 1
    return tuple(points)


def lab_catalog() -> tuple[str, ...]:
    return (
        "OSI / TCP / UDP",
        "AM / FM / PM",
        "PAM / PWM / PPM / PCM",
        "ASK / FSK / PSK / QPSK / 16-QAM",
        "Constellation / BER",
    )


__all__ = [
    "BerPoint",
    "ConstellationPoint",
    "OsiLayer",
    "TransportProfile",
    "Waveform",
    "analog_waveform",
    "ber_curve",
    "constellation_points",
    "digital_waveform",
    "empirical_ber",
    "lab_catalog",
    "osi_layers",
    "pulse_waveform",
    "theoretical_ber",
    "transport_profiles",
]
