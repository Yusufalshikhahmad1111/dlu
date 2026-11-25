from __future__ import annotations

import math
from dataclasses import dataclass

from PySide6.QtCore import QLineF, QPointF, QRectF, QTimer, Qt
from PySide6.QtGui import QColor, QBrush, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .communications_lab import (
    BerPoint,
    Waveform,
    analog_waveform,
    ber_curve,
    constellation_points,
    digital_waveform,
    osi_layers,
    pulse_waveform,
    transport_profiles,
)
from .design_tokens import get_tokens, normalize_mode
from .ui_utils import make_font


STEPS = (
    "CONCEPT",
    "PARAMETERS",
    "EXPERIMENT",
    "VISUALIZATION",
    "MEASUREMENT",
    "EXPLANATION",
    "CHALLENGE",
)


@dataclass(frozen=True)
class Palette:
    bg: str
    panel: str
    panel2: str
    border: str
    text: str
    muted: str
    primary: str
    success: str
    warning: str
    danger: str
    deep: str


def _palette(mode: str) -> Palette:
    t = get_tokens(normalize_mode(mode))
    return Palette(
        bg=t.bg,
        panel=t.surface,
        panel2=t.surface_elevated,
        border=t.border,
        text=t.text_primary,
        muted=t.text_muted,
        primary=t.primary,
        success=t.success,
        warning=t.warning,
        danger=t.danger,
        deep=t.deep,
    )


def _section(title: str) -> tuple[QGroupBox, QVBoxLayout]:
    box = QGroupBox(title)
    layout = QVBoxLayout(box)
    layout.setSpacing(7)
    return box, layout


class MetricCard(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("Stage13MetricCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        self.title = QLabel(title.upper())
        self.value = QLabel("—")
        self.detail = QLabel("")
        self.value.setFont(make_font(14, bold=True))
        self.detail.setWordWrap(True)
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        layout.addWidget(self.detail)
        self.setMinimumHeight(78)

    def set_value(self, value: str, detail: str = "") -> None:
        self.value.setText(value)
        self.detail.setText(detail)


class StepRail(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.labels: list[QLabel] = []
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        for i, step in enumerate(STEPS, start=1):
            label = QLabel(f"{i} {step}")
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumHeight(29)
            label.setToolTip(step.title())
            self.labels.append(label)
            layout.addWidget(label, 1)

    def set_active(self, index: int, p: Palette) -> None:
        for i, label in enumerate(self.labels):
            if i == index:
                label.setStyleSheet(
                    f"background:{p.primary};color:{p.deep};border-radius:7px;"
                    "padding:4px;font-weight:900;"
                )
            else:
                label.setStyleSheet(
                    f"background:{p.panel2};color:{p.muted};border:1px solid {p.border};"
                    "border-radius:7px;padding:4px;"
                )


class ChallengeBox(QGroupBox):
    def __init__(self):
        super().__init__("7 · MINI CHALLENGE")
        self._correct = 0
        self._reasons: tuple[str, ...] = ()
        layout = QVBoxLayout(self)
        self.question = QLabel()
        self.question.setWordWrap(True)
        self.options = QHBoxLayout()
        self.result = QLabel("Choose an answer.")
        self.result.setWordWrap(True)
        layout.addWidget(self.question)
        layout.addLayout(self.options)
        layout.addWidget(self.result)

    def configure(self, question: str, options: tuple[str, ...], correct: int, reasons: tuple[str, ...]) -> None:
        self.question.setText(question)
        self._correct = correct
        self._reasons = reasons
        while self.options.count():
            item = self.options.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for i, option in enumerate(options):
            button = QPushButton(f"{chr(65 + i)} · {option}")
            button.clicked.connect(lambda _=False, choice=i: self._answer(choice))
            self.options.addWidget(button)
        self.result.setText("Choose an answer from the evidence above.")

    def _answer(self, choice: int) -> None:
        reason = self._reasons[choice] if choice < len(self._reasons) else ""
        prefix = "✓ CORRECT" if choice == self._correct else "✗ TRY AGAIN"
        self.result.setText(f"{prefix} · {reason}")


class SignalCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._palette = _palette("morning")
        self.kind = "empty"
        self.wave: Waveform | None = None
        self.points = ()
        self.ber: tuple[BerPoint, ...] = ()
        self.message = "Run the experiment to generate evidence."
        self.setMinimumHeight(265)

    def set_theme(self, mode: str) -> None:
        self._palette = _palette(mode)
        self.update()

    def clear(self, message: str = "Run the experiment to generate evidence.") -> None:
        self.kind, self.wave, self.points, self.ber, self.message = "empty", None, (), (), message
        self.update()

    def set_wave(self, wave: Waveform) -> None:
        self.kind, self.wave, self.points, self.ber = "wave", wave, (), ()
        self.update()

    def set_constellation(self, points, title: str) -> None:
        self.kind, self.wave, self.points, self.ber = "constellation", None, points, ()
        self.message = title
        self.update()

    def set_ber(self, points: tuple[BerPoint, ...]) -> None:
        self.kind, self.wave, self.points, self.ber = "ber", None, (), points
        self.update()

    def _rect(self) -> QRectF:
        return QRectF(58, 34, max(100, self.width() - 82), max(140, self.height() - 76))

    @staticmethod
    def _scale(v: float, lo: float, hi: float, a: float, b: float) -> float:
        if math.isclose(lo, hi):
            return (a + b) / 2
        return a + ((v - lo) / (hi - lo)) * (b - a)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        p = self._palette
        painter.fillRect(self.rect(), QColor(p.panel2))
        rect = self._rect()
        painter.setPen(QPen(QColor(p.border), 1))
        painter.setBrush(QBrush(QColor(p.deep)))
        painter.drawRoundedRect(rect, 10, 10)
        if self.kind == "wave" and self.wave:
            self._waveform(painter, rect, self.wave)
        elif self.kind == "constellation" and self.points:
            self._constellation(painter, rect, self.points, self.message)
        elif self.kind == "ber" and self.ber:
            self._ber_plot(painter, rect, self.ber)
        else:
            painter.setPen(QColor(p.muted))
            painter.setFont(make_font(11, bold=True))
            painter.drawText(rect, Qt.AlignCenter, self.message)

    def _grid(self, painter: QPainter, rect: QRectF):
        p = self._palette
        painter.setPen(QPen(QColor(p.border), 1, Qt.DotLine))
        for i in range(1, 5):
            x = rect.left() + i * rect.width() / 5
            painter.drawLine(QLineF(x, rect.top(), x, rect.bottom()))
        for i in range(1, 5):
            y = rect.top() + i * rect.height() / 5
            painter.drawLine(QLineF(rect.left(), y, rect.right(), y))

    def _title(self, painter: QPainter, text: str):
        painter.setPen(QColor(self._palette.text))
        painter.setFont(make_font(12, bold=True))
        painter.drawText(12, 20, text)

    def _waveform(self, painter: QPainter, rect: QRectF, wave: Waveform):
        p = self._palette
        self._title(painter, wave.title)
        lo, hi = min(wave.y), max(wave.y)
        pad = max(0.08, (hi - lo) * 0.08)
        lo, hi = lo - pad, hi + pad
        self._grid(painter, rect)
        if lo <= 0 <= hi:
            y0 = self._scale(0, lo, hi, rect.bottom(), rect.top())
            painter.setPen(QPen(QColor(p.muted), 1, Qt.DashLine))
            painter.drawLine(QLineF(rect.left(), y0, rect.right(), y0))
        pts = [
            QPointF(
                self._scale(x, min(wave.x), max(wave.x), rect.left(), rect.right()),
                self._scale(y, lo, hi, rect.bottom(), rect.top()),
            )
            for x, y in zip(wave.x, wave.y)
        ]
        painter.setPen(QPen(QColor(p.primary), 2.2))
        for a, b in zip(pts, pts[1:]):
            painter.drawLine(QLineF(a, b))
        painter.setPen(QColor(p.muted))
        painter.setFont(make_font(8))
        painter.drawText(QPointF(rect.left(), rect.bottom() + 18), "time / normalized")
        painter.drawText(QPointF(10, rect.top() + 8), f"{hi:.2f}")
        painter.drawText(QPointF(12, rect.bottom()), f"{lo:.2f}")
        painter.drawText(QPointF(rect.right() - 86, rect.bottom() - 8), f"{len(wave.y)} samples")

    def _constellation(self, painter: QPainter, rect: QRectF, points, title: str):
        p = self._palette
        self._title(painter, title)
        extent = max(1.2, max(abs(x.i) for x in points), max(abs(x.q) for x in points)) + 0.35
        self._grid(painter, rect)
        x0 = self._scale(0, -extent, extent, rect.left(), rect.right())
        y0 = self._scale(0, -extent, extent, rect.bottom(), rect.top())
        painter.setPen(QPen(QColor(p.muted), 1.2))
        painter.drawLine(QLineF(x0, rect.top(), x0, rect.bottom()))
        painter.drawLine(QLineF(rect.left(), y0, rect.right(), y0))
        for point in points:
            x = self._scale(point.i, -extent, extent, rect.left(), rect.right())
            y = self._scale(point.q, -extent, extent, rect.bottom(), rect.top())
            painter.setPen(QPen(QColor(p.primary), 1.2))
            painter.setBrush(QBrush(QColor(p.primary)))
            painter.drawEllipse(QRectF(x - 5, y - 5, 10, 10))
            painter.setPen(QColor(p.text))
            painter.setFont(make_font(8, bold=True))
            painter.drawText(QPointF(x + 7, y - 5), point.label)
        painter.setPen(QColor(p.muted))
        painter.setFont(make_font(8))
        painter.drawText(QPointF(rect.right() - 25, y0 - 6), "+I")
        painter.drawText(QPointF(x0 + 5, rect.top() + 10), "+Q")
        painter.drawText(QPointF(rect.left(), rect.bottom() + 18), f"{len(points)} symbols")

    @staticmethod
    def _log_y(value: float, top: float, bottom: float, rect: QRectF) -> float:
        value = max(bottom, value)
        span = math.log10(top) - math.log10(bottom)
        ratio = (math.log10(top) - math.log10(value)) / (span or 1.0)
        return rect.top() + ratio * rect.height()

    def _ber_plot(self, painter: QPainter, rect: QRectF, points: tuple[BerPoint, ...]):
        p = self._palette
        self._title(painter, "BER vs Eb/N0")
        top = max(
            1e-5,
            max(max(point.theoretical, point.empirical or 0.0, 1e-5) for point in points),
        )
        bottom = 1e-5
        self._grid(painter, rect)
        for decade in (1e-1, 1e-2, 1e-3, 1e-4, 1e-5):
            if bottom <= decade <= top * 1.2:
                y = self._log_y(decade, top, bottom, rect)
                painter.setPen(QPen(QColor(p.border), 1, Qt.DashLine))
                painter.drawLine(QLineF(rect.left(), y, rect.right(), y))
                painter.setPen(QColor(p.muted))
                painter.setFont(make_font(8))
                painter.drawText(QPointF(8, y - 2), f"{decade:.0e}")
        def x_map(v: float) -> float:
            return self._scale(v, points[0].ebn0_db, points[-1].ebn0_db, rect.left(), rect.right())
        theory = [
            QPointF(x_map(point.ebn0_db), self._log_y(point.theoretical, top, bottom, rect))
            for point in points
        ]
        painter.setPen(QPen(QColor(p.primary), 2.2))
        for a, b in zip(theory, theory[1:]):
            painter.drawLine(QLineF(a, b))
        painter.setPen(QPen(QColor(p.warning), 1.5))
        painter.setBrush(QBrush(QColor(p.warning)))
        for point in points:
            if point.empirical is not None:
                x = x_map(point.ebn0_db)
                y = self._log_y(point.empirical, top, bottom, rect)
                painter.drawEllipse(QRectF(x - 3, y - 3, 6, 6))
        painter.setPen(QColor(p.muted))
        painter.setFont(make_font(8))
        painter.drawText(QPointF(rect.left(), rect.bottom() + 18), "Eb/N0 (dB)")
        painter.drawText(QPointF(rect.right() - 120, rect.top() - 8), "— theory  •  ● empirical")


class Stage13CommunicationsLabWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._theme = "morning"
        self._palette = _palette(self._theme)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.run_current)
        self._build()
        self.set_theme(self._theme)
        self.run_current()

    def _scroll(self, page: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(page)
        return scroll

    def _intro(self, layout: QVBoxLayout, text: str):
        box, inner = _section("1 · CONCEPT")
        label = QLabel(text)
        label.setWordWrap(True)
        inner.addWidget(label)
        layout.addWidget(box)

    def _metrics(self, layout: QVBoxLayout, titles: tuple[str, ...]) -> list[MetricCard]:
        box, inner = _section("5 · MEASUREMENT")
        row = QHBoxLayout()
        cards = [MetricCard(title) for title in titles]
        for card in cards:
            row.addWidget(card, 1)
        inner.addLayout(row)
        layout.addWidget(box)
        return cards

    def _explanation(self, layout: QVBoxLayout):
        box, inner = _section("6 · EXPLANATION")
        label = QLabel("Run the experiment to generate a plain-language explanation.")
        label.setWordWrap(True)
        inner.addWidget(label)
        layout.addWidget(box)
        return label

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        header = QFrame()
        h = QHBoxLayout(header)
        h.setContentsMargins(8, 6, 8, 6)
        title = QLabel("COMMUNICATIONS LAB 2.0")
        title.setFont(make_font(16, bold=True))
        subtitle = QLabel("Concept → Parameters → Experiment → Visualization → Measurement → Explanation → Challenge")
        subtitle.setWordWrap(True)
        self.lab_combo = QComboBox()
        self.lab_combo.addItems([
            "OSI / TCP / UDP",
            "AM / FM / PM",
            "PAM / PWM / PPM / PCM",
            "ASK / FSK / PSK / QPSK / 16-QAM",
            "Constellation / BER",
        ])
        self.live_check = QCheckBox("LIVE UPDATE")
        self.live_check.setChecked(True)
        reset = QPushButton("RESET VIEW")
        reset.clicked.connect(self.run_current)
        h.addWidget(title)
        h.addWidget(subtitle, 1)
        h.addWidget(QLabel("LAB"))
        h.addWidget(self.lab_combo)
        h.addWidget(self.live_check)
        h.addWidget(reset)
        root.addWidget(header)

        self.rail = StepRail()
        root.addWidget(self.rail)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)
        self.lab_combo.currentIndexChanged.connect(self.stack.setCurrentIndex)
        self.lab_combo.currentIndexChanged.connect(lambda _: self.run_current())

        self.stack.addWidget(self._build_osi())
        self.stack.addWidget(self._build_analog())
        self.stack.addWidget(self._build_pulse())
        self.stack.addWidget(self._build_digital())
        self.stack.addWidget(self._build_ber())

    def _build_osi(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self._intro(layout, "Use the layer model to connect transport choices to real engineering trade-offs instead of memorizing protocol names.")

        params, inner = _section("2 · PARAMETERS")
        self.osi_protocol = QComboBox()
        self.osi_protocol.addItems(["TCP", "UDP"])
        inner.addWidget(QLabel("Transport profile"))
        inner.addWidget(self.osi_protocol)
        layout.addWidget(params)

        experiment, inner = _section("3 · EXPERIMENT")
        run = QPushButton("COMPARE TRANSPORT")
        run.clicked.connect(self._run_osi)
        inner.addWidget(run)
        self.osi_layers = QLabel()
        self.osi_layers.setWordWrap(True)
        self.osi_layers.setText(" → ".join(f"L{x.number} {x.name}" for x in osi_layers()))
        inner.addWidget(self.osi_layers)
        layout.addWidget(experiment)

        visual, inner = _section("4 · VISUALIZATION")
        self.osi_visual = QLabel()
        self.osi_visual.setWordWrap(True)
        inner.addWidget(self.osi_visual)
        layout.addWidget(visual)

        self.osi_metrics = self._metrics(layout, ("Connection", "Reliability", "Ordering", "Overhead"))
        self.osi_explain = self._explanation(layout)
        challenge, inner = _section("7 · MINI CHALLENGE")
        self.osi_challenge = ChallengeBox()
        self.osi_challenge.configure(
            "A live sensor tolerates occasional packet loss. Which transport is the better fit?",
            ("TCP", "UDP"),
            1,
            ("TCP favors reliable ordered delivery.", "UDP is lighter and suits loss-tolerant, latency-sensitive updates."),
        )
        inner.addWidget(self.osi_challenge)
        layout.addWidget(challenge)
        self.osi_protocol.currentTextChanged.connect(lambda _: self._schedule())
        return self._scroll(page)

    def _build_analog(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self._intro(layout, "AM varies amplitude, FM varies instantaneous frequency, and PM varies instantaneous phase. Change a parameter and watch the normalized waveform respond.")

        params, inner = _section("2 · PARAMETERS")
        form = QFormLayout()
        self.analog_mode = QComboBox()
        self.analog_mode.addItems(["AM", "FM", "PM"])
        self.analog_mu = QDoubleSpinBox()
        self.analog_mu.setRange(0, 1.8)
        self.analog_mu.setValue(0.7)
        self.analog_carrier = QDoubleSpinBox()
        self.analog_carrier.setRange(1, 20)
        self.analog_carrier.setValue(5)
        self.analog_message = QDoubleSpinBox()
        self.analog_message.setRange(0.2, 5)
        self.analog_message.setValue(1)
        self.analog_delta = QDoubleSpinBox()
        self.analog_delta.setRange(0.1, 8)
        self.analog_delta.setValue(2)
        self.analog_phase = QDoubleSpinBox()
        self.analog_phase.setRange(0.1, 5)
        self.analog_phase.setValue(1.5)
        form.addRow("Mode", self.analog_mode)
        form.addRow("AM μ", self.analog_mu)
        form.addRow("Carrier f₍c₎", self.analog_carrier)
        form.addRow("Message f₍m₎", self.analog_message)
        form.addRow("FM Δf", self.analog_delta)
        form.addRow("PM kₚ", self.analog_phase)
        inner.addLayout(form)
        layout.addWidget(params)

        experiment, inner = _section("3 · EXPERIMENT")
        run = QPushButton("GENERATE / UPDATE WAVEFORM")
        run.clicked.connect(self._run_analog)
        inner.addWidget(run)
        layout.addWidget(experiment)

        visual, inner = _section("4 · VISUALIZATION")
        self.analog_canvas = SignalCanvas()
        inner.addWidget(self.analog_canvas)
        layout.addWidget(visual)

        self.analog_metrics = self._metrics(layout, ("Carrier", "Message", "Peak", "Range"))
        self.analog_explain = self._explanation(layout)
        challenge, inner = _section("7 · MINI CHALLENGE")
        self.analog_challenge = ChallengeBox()
        self.analog_challenge.configure(
            "For AM, what does μ > 1 represent in this model?",
            ("A faster carrier", "Over-modulation / envelope distortion"),
            1,
            ("Carrier frequency is a separate parameter.", "The domain model explicitly reports over-modulation and envelope distortion."),
        )
        inner.addWidget(self.analog_challenge)
        layout.addWidget(challenge)

        for widget in (self.analog_mode, self.analog_mu, self.analog_carrier, self.analog_message, self.analog_delta, self.analog_phase):
            signal = getattr(widget, "valueChanged", None) or widget.currentTextChanged
            signal.connect(lambda *_: self._schedule())
        return self._scroll(page)

    def _build_pulse(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self._intro(layout, "PAM, PWM, PPM, and PCM share sampling, but carry the sample in different pulse properties. The visualization should make that difference visible.")

        params, inner = _section("2 · PARAMETERS")
        form = QFormLayout()
        self.pulse_mode = QComboBox()
        self.pulse_mode.addItems(["PAM", "PWM", "PPM", "PCM"])
        self.pulse_samples = QSpinBox()
        self.pulse_samples.setRange(2, 32)
        self.pulse_samples.setValue(8)
        self.pulse_bits = QSpinBox()
        self.pulse_bits.setRange(1, 8)
        self.pulse_bits.setValue(3)
        form.addRow("Mode", self.pulse_mode)
        form.addRow("Sample count", self.pulse_samples)
        form.addRow("PCM bits", self.pulse_bits)
        inner.addLayout(form)
        layout.addWidget(params)

        experiment, inner = _section("3 · EXPERIMENT")
        run = QPushButton("GENERATE / UPDATE PULSE TRAIN")
        run.clicked.connect(self._run_pulse)
        inner.addWidget(run)
        self.pulse_codes = QLabel("PCM codes: —")
        self.pulse_codes.setWordWrap(True)
        inner.addWidget(self.pulse_codes)
        layout.addWidget(experiment)

        visual, inner = _section("4 · VISUALIZATION")
        self.pulse_canvas = SignalCanvas()
        inner.addWidget(self.pulse_canvas)
        layout.addWidget(visual)

        self.pulse_metrics = self._metrics(layout, ("Samples", "Levels", "Peak", "Code width"))
        self.pulse_explain = self._explanation(layout)
        challenge, inner = _section("7 · MINI CHALLENGE")
        challenge_box = ChallengeBox()
        challenge_box.configure(
            "Which parameter changes the number of PCM levels?",
            ("Sample count", "Quantization bits"),
            1,
            ("Sample count changes how often the message is sampled.", "Levels are 2^bits, so quantization bits control the code resolution."),
        )
        inner.addWidget(challenge_box)
        layout.addWidget(challenge)

        self.pulse_mode.currentTextChanged.connect(lambda _: self._schedule())
        self.pulse_samples.valueChanged.connect(lambda _: self._schedule())
        self.pulse_bits.valueChanged.connect(lambda _: self._schedule())
        return self._scroll(page)

    def _build_digital(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self._intro(layout, "Digital modulation maps bits to amplitude, frequency, phase, or a two-dimensional constellation. QPSK groups 2 bits; 16-QAM groups 4.")

        params, inner = _section("2 · PARAMETERS")
        form = QFormLayout()
        self.digital_mode = QComboBox()
        self.digital_mode.addItems(["ASK", "FSK", "PSK", "QPSK", "16-QAM"])
        self.digital_bits = QLineEdit("0011011011001011")
        self.digital_carrier = QDoubleSpinBox()
        self.digital_carrier.setRange(1, 15)
        self.digital_carrier.setValue(4)
        self.digital_shift = QDoubleSpinBox()
        self.digital_shift.setRange(0.2, 8)
        self.digital_shift.setValue(2)
        form.addRow("Modulation", self.digital_mode)
        form.addRow("Bitstream", self.digital_bits)
        form.addRow("Carrier", self.digital_carrier)
        form.addRow("FSK shift", self.digital_shift)
        inner.addLayout(form)
        layout.addWidget(params)

        experiment, inner = _section("3 · EXPERIMENT")
        run = QPushButton("GENERATE / UPDATE DIGITAL SIGNAL")
        run.clicked.connect(self._run_digital)
        inner.addWidget(run)
        self.digital_symbols = QLabel("Symbols: —")
        self.digital_symbols.setWordWrap(True)
        inner.addWidget(self.digital_symbols)
        layout.addWidget(experiment)

        visual, inner = _section("4 · VISUALIZATION")
        self.digital_canvas = SignalCanvas()
        self.digital_constellation = SignalCanvas()
        inner.addWidget(QLabel("TIME-DOMAIN WAVEFORM"))
        inner.addWidget(self.digital_canvas)
        inner.addWidget(QLabel("SYMBOL-SPACE EVIDENCE"))
        inner.addWidget(self.digital_constellation)
        layout.addWidget(visual)

        self.digital_metrics = self._metrics(layout, ("Mode", "Symbols", "Amplitude", "Constellation"))
        self.digital_explain = self._explanation(layout)
        challenge, inner = _section("7 · MINI CHALLENGE")
        challenge_box = ChallengeBox()
        challenge_box.configure(
            "Which modulation carries 4 bits in one symbol?",
            ("QPSK", "16-QAM"),
            1,
            ("QPSK uses 2-bit symbol groups.", "16-QAM uses 4-bit groups to select one of 16 points."),
        )
        inner.addWidget(challenge_box)
        layout.addWidget(challenge)

        self.digital_mode.currentTextChanged.connect(lambda _: self._schedule())
        self.digital_bits.textChanged.connect(lambda _: self._schedule())
        self.digital_carrier.valueChanged.connect(lambda _: self._schedule())
        self.digital_shift.valueChanged.connect(lambda _: self._schedule())
        return self._scroll(page)

    def _build_ber(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self._intro(layout, "BER links a noisy-channel experiment to theory. The empirical run is deterministic and intentionally finite for repeatable classroom comparisons.")

        params, inner = _section("2 · PARAMETERS")
        form = QFormLayout()
        self.ber_mode = QComboBox()
        self.ber_mode.addItems(["BPSK", "QPSK", "16-QAM"])
        self.ber_seed = QSpinBox()
        self.ber_seed.setRange(0, 99999)
        self.ber_seed.setValue(7)
        self.ber_target = QDoubleSpinBox()
        self.ber_target.setRange(0, 14)
        self.ber_target.setValue(8)
        form.addRow("BER model", self.ber_mode)
        form.addRow("Seed", self.ber_seed)
        form.addRow("Read at Eb/N0", self.ber_target)
        inner.addLayout(form)
        layout.addWidget(params)

        experiment, inner = _section("3 · EXPERIMENT")
        run = QPushButton("RUN / UPDATE BER CURVE")
        run.clicked.connect(self._run_ber)
        inner.addWidget(run)
        layout.addWidget(experiment)

        visual, inner = _section("4 · VISUALIZATION")
        self.ber_canvas = SignalCanvas()
        self.ber_constellation = SignalCanvas()
        inner.addWidget(self.ber_canvas)
        inner.addWidget(self.ber_constellation)
        layout.addWidget(visual)

        self.ber_metrics = self._metrics(layout, ("Eb/N0", "Theory", "Empirical", "Gap"))
        self.ber_explain = self._explanation(layout)
        challenge, inner = _section("7 · MINI CHALLENGE")
        challenge_box = ChallengeBox()
        challenge_box.configure(
            "For a fixed modulation, what should generally happen to BER as Eb/N0 increases?",
            ("BER should fall", "BER should rise"),
            0,
            ("Higher energy per bit relative to noise generally improves decisions.", "The teaching curve shows the opposite trend."),
        )
        inner.addWidget(challenge_box)
        layout.addWidget(challenge)

        self.ber_mode.currentTextChanged.connect(lambda _: self._schedule())
        self.ber_seed.valueChanged.connect(lambda _: self._schedule())
        self.ber_target.valueChanged.connect(lambda _: self._schedule())
        return self._scroll(page)

    def _schedule(self):
        if self.live_check.isChecked():
            self._timer.start(120)

    def run_current(self):
        index = self.lab_combo.currentIndex()
        (self._run_osi, self._run_analog, self._run_pulse, self._run_digital, self._run_ber)[index]()

    @staticmethod
    def _range(values: tuple[float, ...]) -> str:
        return f"{min(values):.2f} → {max(values):.2f}"

    def _finish_run(self):
        self.rail.set_active(3, self._palette)

    def _run_osi(self):
        profile = next(x for x in transport_profiles() if x.name == self.osi_protocol.currentText())
        self.osi_visual.setText(
            f"L4 selected: {profile.name} · {profile.connection} · {profile.reliability} · "
            f"{profile.ordering} · overhead={profile.overhead}."
        )
        values = (profile.connection, "Reliable" if profile.name == "TCP" else "Best-effort", profile.ordering, profile.overhead)
        for card, value, detail in zip(self.osi_metrics, values, ("setup", "delivery", "ordering", "relative cost")):
            card.set_value(value, detail)
        self.osi_explain.setText(
            f"{profile.name} is chosen because its transport behavior is {profile.connection.lower()}, "
            f"with {profile.reliability.lower()}. The key lesson is the trade-off between delivery guarantees and overhead."
        )
        self._finish_run()

    def _run_analog(self):
        try:
            result = analog_waveform(
                self.analog_mode.currentText(),
                modulation_index=self.analog_mu.value(),
                carrier_hz=self.analog_carrier.value(),
                message_hz=self.analog_message.value(),
                frequency_deviation_hz=self.analog_delta.value(),
                phase_sensitivity=self.analog_phase.value(),
            )
        except ValueError as exc:
            self.analog_canvas.clear(str(exc))
            self.analog_explain.setText(f"Input check: {exc}")
            return
        self.analog_canvas.set_wave(result)
        cards = (
            (self.analog_metrics[0], f"{self.analog_carrier.value():g} Hz", "carrier"),
            (self.analog_metrics[1], f"{self.analog_message.value():g} Hz", "message"),
            (self.analog_metrics[2], f"{max(result.y):.2f}", "observed peak"),
            (self.analog_metrics[3], self._range(result.y), "observed min → max"),
        )
        for card, value, detail in cards:
            card.set_value(value, detail)
        self.analog_explain.setText(
            f"{result.summary} The normalized plot makes the selected parameter effect visible; "
            "compare shape and relative changes rather than interpreting it as an RF power model."
        )
        self._finish_run()

    def _run_pulse(self):
        try:
            result = pulse_waveform(
                self.pulse_mode.currentText(),
                sample_count=self.pulse_samples.value(),
                quantization_bits=self.pulse_bits.value(),
            )
        except ValueError as exc:
            self.pulse_canvas.clear(str(exc))
            self.pulse_explain.setText(f"Input check: {exc}")
            return
        self.pulse_canvas.set_wave(result)
        self.pulse_codes.setText(f"PCM codes: {result.metadata.get('pcm_codes', '—')}")
        cards = (
            (self.pulse_metrics[0], str(self.pulse_samples.value()), "message samples"),
            (self.pulse_metrics[1], str(2 ** self.pulse_bits.value()), "quantization levels"),
            (self.pulse_metrics[2], f"{max(result.y):.2f}", "observed pulse peak"),
            (self.pulse_metrics[3], f"{self.pulse_bits.value()} bit", "PCM code width"),
        )
        for card, value, detail in cards:
            card.set_value(value, detail)
        self.pulse_explain.setText(
            f"{result.summary} Watch which pulse property carries the sample: amplitude, width, position, or code."
        )
        self._finish_run()

    def _run_digital(self):
        try:
            result = digital_waveform(
                self.digital_mode.currentText(),
                self.digital_bits.text(),
                carrier_hz=self.digital_carrier.value(),
                frequency_shift_hz=self.digital_shift.value(),
            )
        except ValueError as exc:
            self.digital_canvas.clear(str(exc))
            self.digital_constellation.clear(str(exc))
            self.digital_explain.setText(f"Input check: {exc}")
            return
        self.digital_canvas.set_wave(result)
        mode = self.digital_mode.currentText()
        points = constellation_points(mode) if mode in {"QPSK", "16-QAM"} else ()
        if points:
            self.digital_constellation.set_constellation(points, f"{mode} constellation")
        else:
            self.digital_constellation.clear("Constellation evidence is shown for QPSK and 16-QAM.")
        symbols = result.metadata.get("symbols", "").split()
        self.digital_symbols.setText(f"Symbols: {' '.join(symbols)} · Bits: {result.metadata.get('bits', '—')}")
        cards = (
            (self.digital_metrics[0], mode, "selected modulation"),
            (self.digital_metrics[1], str(len(symbols)), "symbol groups"),
            (self.digital_metrics[2], self._range(result.y), "observed waveform"),
            (self.digital_metrics[3], str(len(points)) if points else "—", "constellation points"),
        )
        for card, value, detail in cards:
            card.set_value(value, detail)
        self.digital_explain.setText(
            f"{result.summary} The waveform shows the carrier response; "
            f"{'the constellation makes symbol spacing and labels explicit.' if points else 'no I/Q constellation is needed for this binary view.'}"
        )
        self._finish_run()

    def _run_ber(self):
        try:
            points = ber_curve(self.ber_mode.currentText(), empirical=True, seed=self.ber_seed.value())
        except ValueError as exc:
            self.ber_canvas.clear(str(exc))
            self.ber_constellation.clear(str(exc))
            self.ber_explain.setText(f"Input check: {exc}")
            return
        self.ber_canvas.set_ber(points)
        mode = self.ber_mode.currentText()
        self.ber_constellation.set_constellation(constellation_points(mode), f"{mode} constellation")
        target = self.ber_target.value()
        nearest = min(points, key=lambda x: abs(x.ebn0_db - target))
        empirical = nearest.empirical or 0.0
        gap = empirical - nearest.theoretical
        for card, value, detail in (
            (self.ber_metrics[0], f"{nearest.ebn0_db:.0f} dB", "nearest sampled point"),
            (self.ber_metrics[1], f"{nearest.theoretical:.3g}", "theoretical"),
            (self.ber_metrics[2], f"{empirical:.3g}", "deterministic empirical"),
            (self.ber_metrics[3], f"{gap:+.3g}", "empirical − theory"),
        ):
            card.set_value(value, detail)
        self.ber_explain.setText(
            f"At Eb/N0 ≈ {nearest.ebn0_db:.0f} dB, theory={nearest.theoretical:.3g} and empirical={empirical:.3g}. "
            "The small gap is expected because the empirical run uses a short finite bitstream; the main lesson is the downward BER trend."
        )
        self._finish_run()

    def _apply_style(self):
        p = self._palette
        self.setStyleSheet(
            f"""
            QGroupBox {{
                background:{p.panel};
                color:{p.text};
                border:1px solid {p.border};
                border-radius:9px;
                margin-top:8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left:10px;
                padding:0 5px;
                color:{p.primary};
                font-weight:900;
            }}
            QFrame#Stage13MetricCard {{
                background:{p.panel2};
                border:1px solid {p.border};
                border-radius:8px;
            }}
            QFrame#Stage13MetricCard QLabel:first-child {{
                color:{p.muted};
            }}
            """
        )
        for card in self.findChildren(MetricCard):
            card.title.setStyleSheet(f"color:{p.muted};font-size:9px;font-weight:800;")
            card.value.setStyleSheet(f"color:{p.text};")
            card.detail.setStyleSheet(f"color:{p.muted};font-size:9px;")
        for canvas in self.findChildren(SignalCanvas):
            canvas.set_theme(self._theme)
        self.rail.set_active(3, p)

    def set_theme(self, mode: str):
        self._theme = normalize_mode(mode)
        self._palette = _palette(self._theme)
        self._apply_style()
        self.update()


class Stage13Controller:
    def __init__(self, window: QWidget, mode: str = "morning"):
        self.window = window
        self.mode = normalize_mode(mode)
        self.view: Stage13CommunicationsLabWidget | None = None

    def install(self):
        tabs: QTabWidget | None = getattr(self.window, "feature_tabs", None)
        legacy = getattr(self.window, "communications_lab", None)
        if tabs is None or legacy is None:
            return
        index = tabs.indexOf(legacy)
        if index < 0:
            return
        title = tabs.tabText(index) or "COMMS LAB"
        view = Stage13CommunicationsLabWidget(tabs)
        view.set_theme(self.mode)
        tabs.removeTab(index)
        legacy.setParent(None)
        legacy.deleteLater()
        tabs.insertTab(index, view, title)
        self.window.stage13_legacy_communications_lab = legacy
        self.window.communications_lab = view
        self.view = view
        self.window.stage13_controller = self
        self.window.setProperty("dlu_stage13_enabled", True)

    def set_mode(self, mode: str):
        self.mode = normalize_mode(mode)
        if self.view is not None:
            self.view.set_theme(self.mode)


def apply_stage13_ui(window: QWidget, mode: str = "morning") -> None:
    controller = getattr(window, "stage13_controller", None)
    if controller is None:
        controller = Stage13Controller(window, mode)
        controller.install()
    else:
        controller.set_mode(mode)
