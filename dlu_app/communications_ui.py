from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QLineF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QBrush
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .communications_lab import (
    BerPoint,
    ConstellationPoint,
    Waveform,
    analog_waveform,
    ber_curve,
    constellation_points,
    digital_waveform,
    lab_catalog,
    pulse_waveform,
    osi_layers,
    transport_profiles,
)
from .theme import THEMES
from .ui_utils import make_font


class SignalPlot(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._palette = THEMES["ivory"]
        self._mode = "wave"
        self._waveform: Waveform | None = None
        self._points: tuple[ConstellationPoint, ...] = ()
        self._ber: tuple[BerPoint, ...] = ()
        self.setMinimumHeight(250)

    def set_theme(self, name: str):
        self._palette = THEMES.get(name, THEMES["ivory"])
        self.update()

    def set_waveform(self, waveform: Waveform):
        self._mode = "wave"
        self._waveform = waveform
        self._points = ()
        self._ber = ()
        self.update()

    def set_constellation(self, points: tuple[ConstellationPoint, ...]):
        self._mode = "constellation"
        self._points = points
        self._waveform = None
        self._ber = ()
        self.update()

    def set_ber(self, points: tuple[BerPoint, ...]):
        self._mode = "ber"
        self._ber = points
        self._waveform = None
        self._points = ()
        self.update()

    def clear(self):
        self._waveform = None
        self._points = ()
        self._ber = ()
        self.update()

    def _plot_rect(self) -> QRectF:
        return QRectF(52, 26, max(60, self.width() - 72), max(80, self.height() - 54))

    @staticmethod
    def _scale(value: float, low: float, high: float, out_low: float, out_high: float) -> float:
        if math.isclose(low, high):
            return (out_low + out_high) / 2
        ratio = (value - low) / (high - low)
        return out_low + ratio * (out_high - out_low)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        palette = self._palette
        painter.fillRect(self.rect(), QColor(palette.PANEL2))

        rect = self._plot_rect()
        painter.setPen(QPen(QColor(palette.BORDER), 1))
        painter.setBrush(QBrush(QColor(palette.DEEP)))
        painter.drawRoundedRect(rect, 8, 8)

        # Grid
        painter.setPen(QPen(QColor(palette.BORDER), 1, Qt.DotLine))
        for i in range(1, 5):
            x = rect.left() + i * rect.width() / 5
            painter.drawLine(x, rect.top(), x, rect.bottom())
            y = rect.top() + i * rect.height() / 5
            painter.drawLine(rect.left(), y, rect.right(), y)

        if self._mode == "wave" and self._waveform:
            self._draw_wave(painter, rect, self._waveform)
        elif self._mode == "constellation" and self._points:
            self._draw_constellation(painter, rect, self._points)
        elif self._mode == "ber" and self._ber:
            self._draw_ber(painter, rect, self._ber)
        else:
            painter.setPen(QColor(palette.MUTED))
            painter.setFont(make_font(11))
            painter.drawText(rect, Qt.AlignCenter, "Run the lab to generate a plot.")

    def _title(self, painter: QPainter, title: str):
        painter.setPen(QColor(self._palette.TEXT))
        painter.setFont(make_font(12, bold=True))
        painter.drawText(12, 18, title)

    def _draw_wave(self, painter: QPainter, rect: QRectF, waveform: Waveform):
        self._title(painter, waveform.title)
        if not waveform.y:
            return
        low, high = min(waveform.y), max(waveform.y)
        pad = max(0.08, (high - low) * 0.08)
        low -= pad
        high += pad
        path = []
        for x, y in zip(waveform.x, waveform.y):
            px = self._scale(x, min(waveform.x), max(waveform.x), rect.left(), rect.right())
            py = self._scale(y, low, high, rect.bottom(), rect.top())
            path.append((px, py))
        painter.setPen(QPen(QColor(self._palette.CYAN), 2))
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            painter.drawLine(QLineF(x1, y1, x2, y2))

        painter.setPen(QColor(self._palette.MUTED))
        painter.setFont(make_font(8))
        painter.drawText(QPointF(rect.left(), rect.bottom() + 19), "time")
        painter.drawText(QPointF(8, rect.top() + 10), f"{high:.2f}")
        painter.drawText(QPointF(12, rect.bottom()), f"{low:.2f}")

    def _draw_constellation(self, painter: QPainter, rect: QRectF, points: tuple[ConstellationPoint, ...]):
        self._title(painter, "Constellation")
        extent = max(
            1.2,
            max(abs(point.i) for point in points),
            max(abs(point.q) for point in points),
        ) + 0.25
        for value in (-extent, 0.0, extent):
            px = self._scale(value, -extent, extent, rect.left(), rect.right())
            py = self._scale(value, -extent, extent, rect.bottom(), rect.top())
            painter.setPen(QPen(QColor(self._palette.BORDER), 1, Qt.DashLine))
            painter.drawLine(px, rect.top(), px, rect.bottom())
            painter.drawLine(rect.left(), py, rect.right(), py)

        for point in points:
            px = self._scale(point.i, -extent, extent, rect.left(), rect.right())
            py = self._scale(point.q, -extent, extent, rect.bottom(), rect.top())
            painter.setPen(QPen(QColor(self._palette.GREEN), 1.5))
            painter.setBrush(QBrush(QColor(self._palette.CYAN)))
            painter.drawEllipse(QRectF(px - 5, py - 5, 10, 10))
            painter.setPen(QColor(self._palette.TEXT))
            painter.setFont(make_font(8, bold=True))
            painter.drawText(px + 7, py - 5, point.label)

        painter.setPen(QColor(self._palette.MUTED))
        painter.setFont(make_font(8))
        painter.drawText(QPointF(rect.center().x(), rect.bottom() + 19), "I (in-phase)")
        painter.drawText(QPointF(rect.left() - 1, rect.top() + 10), "Q")
        painter.drawText(QPointF(rect.right() - 34, rect.bottom() + 19), "+I")

    def _draw_ber(self, painter: QPainter, rect: QRectF, points: tuple[BerPoint, ...]):
        self._title(painter, "BER vs Eb/N0")
        ys = [max(point.theoretical, point.empirical or 0.0) for point in points]
        top = max(1e-5, max(ys))
        bottom = 1e-5

        def y_log(value: float) -> float:
            value = max(bottom, value)
            ratio = (math.log10(value) - math.log10(bottom)) / (math.log10(top) - math.log10(bottom) or 1.0)
            return rect.bottom() - ratio * rect.height()

        theoretical_path = []
        empirical_path = []
        for point in points:
            px = self._scale(point.ebn0_db, points[0].ebn0_db, points[-1].ebn0_db, rect.left(), rect.right())
            theoretical_path.append((px, y_log(point.theoretical)))
            if point.empirical is not None:
                empirical_path.append((px, y_log(point.empirical)))

        painter.setPen(QPen(QColor(self._palette.CYAN), 2))
        for a, b in zip(theoretical_path, theoretical_path[1:]):
            painter.drawLine(QLineF(a[0], a[1], b[0], b[1]))

        painter.setPen(QPen(QColor(self._palette.YELLOW), 1.5))
        painter.setBrush(QBrush(QColor(self._palette.YELLOW)))
        for x, y in empirical_path:
            painter.drawEllipse(QRectF(x - 3, y - 3, 6, 6))
        for a, b in zip(empirical_path, empirical_path[1:]):
            painter.drawLine(*a, *b)

        painter.setPen(QColor(self._palette.MUTED))
        painter.setFont(make_font(8))
        painter.drawText(QPointF(rect.center().x(), rect.bottom() + 19), "Eb/N0 (dB)")
        painter.drawText(QPointF(8, rect.top() + 10), f"{top:.3g}")
        painter.drawText(QPointF(8, rect.bottom()), f"{bottom:.0e}")


class CommunicationsLabWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._theme = "ivory"
        self.setMinimumWidth(420)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        header = QGroupBox("COMMUNICATIONS LAB")
        header_layout = QHBoxLayout(header)
        title = QLabel("Signals · Networks · Modulation")
        title.setFont(make_font(15, bold=True))
        header_layout.addWidget(title)
        header_layout.addWidget(QLabel("Educational normalized models"), 1, Qt.AlignLeft)
        root.addWidget(header)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("LAB"))
        self.lab_combo = QComboBox()
        self.lab_combo.addItems(lab_catalog())
        toolbar.addWidget(self.lab_combo, 1)
        root.addLayout(toolbar)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)
        self.lab_combo.currentIndexChanged.connect(self.stack.setCurrentIndex)

        self.stack.addWidget(self._build_osi_page())
        self.stack.addWidget(self._build_analog_page())
        self.stack.addWidget(self._build_pulse_page())
        self.stack.addWidget(self._build_digital_page())
        self.stack.addWidget(self._build_ber_page())

    def _build_osi_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        info = QLabel(
            "OSI is a teaching model. TCP and UDP are Layer 4 transport protocols; "
            "the lab focuses on their engineering trade-offs rather than packet-level networking."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        table = QTableWidget(len(osi_layers()), 4)
        table.setHorizontalHeaderLabels(["Layer", "Name", "Purpose", "Examples"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for row, layer in enumerate(osi_layers()):
            values = [
                str(layer.number),
                layer.name,
                layer.purpose,
                ", ".join(layer.examples),
            ]
            for col, value in enumerate(values):
                table.setItem(row, col, QTableWidgetItem(value))
        layout.addWidget(table, 1)

        transport = QTableWidget(len(transport_profiles()), 6)
        transport.setHorizontalHeaderLabels(
            ["Protocol", "Connection", "Reliability", "Ordering", "Overhead", "Typical use"]
        )
        transport.verticalHeader().setVisible(False)
        transport.setEditTriggers(QAbstractItemView.NoEditTriggers)
        transport.setSelectionMode(QAbstractItemView.NoSelection)
        transport.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for row, profile in enumerate(transport_profiles()):
            values = [
                profile.name,
                profile.connection,
                profile.reliability,
                profile.ordering,
                profile.overhead,
                profile.common_use,
            ]
            for col, value in enumerate(values):
                transport.setItem(row, col, QTableWidgetItem(value))
        layout.addWidget(QLabel("TCP vs UDP"), 0)
        layout.addWidget(transport)
        return self._scroll(page)

    def _build_analog_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        form = QFormLayout()

        self.analog_mode = QComboBox()
        self.analog_mode.addItems(["AM", "FM", "PM"])
        self.analog_mu = QDoubleSpinBox()
        self.analog_mu.setRange(0.0, 1.8)
        self.analog_mu.setValue(0.7)
        self.analog_mu.setSingleStep(0.1)

        self.analog_carrier = QDoubleSpinBox()
        self.analog_carrier.setRange(1.0, 20.0)
        self.analog_carrier.setValue(5.0)

        self.analog_message = QDoubleSpinBox()
        self.analog_message.setRange(0.2, 5.0)
        self.analog_message.setValue(1.0)

        self.analog_delta = QDoubleSpinBox()
        self.analog_delta.setRange(0.1, 8.0)
        self.analog_delta.setValue(2.0)

        self.analog_phase = QDoubleSpinBox()
        self.analog_phase.setRange(0.1, 5.0)
        self.analog_phase.setValue(1.5)

        form.addRow("Mode", self.analog_mode)
        form.addRow("AM μ", self.analog_mu)
        form.addRow("Carrier f₍c₎", self.analog_carrier)
        form.addRow("Message f₍m₎", self.analog_message)
        form.addRow("FM Δf", self.analog_delta)
        form.addRow("PM kₚ", self.analog_phase)
        layout.addLayout(form)

        run = QPushButton("GENERATE ANALOG WAVEFORM")
        run.clicked.connect(self._run_analog)
        layout.addWidget(run)

        self.analog_formula = QLabel("Formula: —")
        self.analog_formula.setWordWrap(True)
        layout.addWidget(self.analog_formula)
        self.analog_summary = QLabel("Choose a mode and generate the waveform.")
        self.analog_summary.setWordWrap(True)
        layout.addWidget(self.analog_summary)

        self.analog_plot = SignalPlot()
        layout.addWidget(self.analog_plot, 1)
        return self._scroll(page)

    def _build_pulse_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
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
        layout.addLayout(form)

        run = QPushButton("GENERATE PULSE WAVEFORM")
        run.clicked.connect(self._run_pulse)
        layout.addWidget(run)

        self.pulse_formula = QLabel("Formula: —")
        self.pulse_formula.setWordWrap(True)
        layout.addWidget(self.pulse_formula)
        self.pulse_summary = QLabel("PAM/PWM/PPM/PCM share sampling, but encode sample information differently.")
        self.pulse_summary.setWordWrap(True)
        layout.addWidget(self.pulse_summary)

        self.pulse_codes = QLabel("PCM codes: —")
        self.pulse_codes.setWordWrap(True)
        layout.addWidget(self.pulse_codes)

        self.pulse_plot = SignalPlot()
        layout.addWidget(self.pulse_plot, 1)
        return self._scroll(page)

    def _build_digital_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        form = QFormLayout()

        self.digital_mode = QComboBox()
        self.digital_mode.addItems(["ASK", "FSK", "PSK", "QPSK", "16-QAM"])
        self.digital_bits = QLineEdit("0011011011001011")
        self.digital_carrier = QDoubleSpinBox()
        self.digital_carrier.setRange(1.0, 15.0)
        self.digital_carrier.setValue(4.0)
        self.digital_shift = QDoubleSpinBox()
        self.digital_shift.setRange(0.2, 8.0)
        self.digital_shift.setValue(2.0)

        form.addRow("Modulation", self.digital_mode)
        form.addRow("Bitstream", self.digital_bits)
        form.addRow("Carrier", self.digital_carrier)
        form.addRow("FSK shift", self.digital_shift)
        layout.addLayout(form)

        run = QPushButton("GENERATE DIGITAL WAVEFORM")
        run.clicked.connect(self._run_digital)
        layout.addWidget(run)

        self.digital_summary = QLabel("Use a fixed bitstream so the waveform can be compared between runs.")
        self.digital_summary.setWordWrap(True)
        layout.addWidget(self.digital_summary)

        plots = QHBoxLayout()
        self.digital_plot = SignalPlot()
        self.constellation_plot = SignalPlot()
        plots.addWidget(self.digital_plot, 1)
        plots.addWidget(self.constellation_plot, 1)
        layout.addLayout(plots, 1)

        self.digital_symbols = QLabel("Symbols: —")
        self.digital_symbols.setWordWrap(True)
        layout.addWidget(self.digital_symbols)
        return self._scroll(page)

    def _build_ber_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        form = QFormLayout()

        self.ber_mode = QComboBox()
        self.ber_mode.addItems(["BPSK", "QPSK", "16-QAM"])
        self.ber_seed = QSpinBox()
        self.ber_seed.setRange(0, 99999)
        self.ber_seed.setValue(7)

        self.ber_target = QDoubleSpinBox()
        self.ber_target.setRange(0.0, 14.0)
        self.ber_target.setValue(8.0)

        form.addRow("BER model", self.ber_mode)
        form.addRow("Seed", self.ber_seed)
        form.addRow("Read at Eb/N0", self.ber_target)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        run = QPushButton("RUN BER CURVE")
        run.clicked.connect(self._run_ber)
        buttons.addWidget(run)
        constellation = QPushButton("SHOW CONSTELLATION")
        constellation.clicked.connect(self._show_ber_constellation)
        buttons.addWidget(constellation)
        layout.addLayout(buttons)

        self.ber_summary = QLabel(
            "Theoretical curves use AWGN textbook models; empirical points use a deterministic finite bitstream."
        )
        self.ber_summary.setWordWrap(True)
        layout.addWidget(self.ber_summary)

        self.ber_plot = SignalPlot()
        layout.addWidget(self.ber_plot, 1)

        self.ber_value = QLabel("BER: —")
        self.ber_value.setWordWrap(True)
        layout.addWidget(self.ber_value)
        return self._scroll(page)

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
            self.analog_summary.setText(str(exc))
            return
        self.analog_plot.set_waveform(result)
        self.analog_formula.setText(f"Formula: {result.formula}")
        self.analog_summary.setText(result.summary)

    def _run_pulse(self):
        try:
            result = pulse_waveform(
                self.pulse_mode.currentText(),
                sample_count=self.pulse_samples.value(),
                quantization_bits=self.pulse_bits.value(),
            )
        except ValueError as exc:
            self.pulse_summary.setText(str(exc))
            return
        self.pulse_plot.set_waveform(result)
        self.pulse_formula.setText(f"Model: {result.formula}")
        self.pulse_summary.setText(result.summary)
        self.pulse_codes.setText(f"PCM codes: {result.metadata.get('pcm_codes', '—')}")

    def _run_digital(self):
        try:
            result = digital_waveform(
                self.digital_mode.currentText(),
                self.digital_bits.text(),
                carrier_hz=self.digital_carrier.value(),
                frequency_shift_hz=self.digital_shift.value(),
            )
        except ValueError as exc:
            self.digital_summary.setText(str(exc))
            return
        self.digital_plot.set_waveform(result)
        self.digital_summary.setText(f"{result.summary} Formula: {result.formula}")
        self.digital_symbols.setText(
            f"Symbols: {result.metadata.get('symbols', '—')} · Bits: {result.metadata.get('bits', '—')}"
        )
        mode = self.digital_mode.currentText()
        if mode in {"QPSK", "16-QAM"}:
            self.constellation_plot.set_constellation(constellation_points(mode))
        else:
            self.constellation_plot.clear()

    def _run_ber(self):
        mode = self.ber_mode.currentText()
        points = ber_curve(mode, empirical=True, seed=self.ber_seed.value())
        self.ber_plot.set_ber(points)
        target = self.ber_target.value()
        nearest = min(points, key=lambda point: abs(point.ebn0_db - target))
        empirical = nearest.empirical if nearest.empirical is not None else 0.0
        self.ber_value.setText(
            f"Eb/N0 ≈ {nearest.ebn0_db:.0f} dB · "
            f"theoretical BER={nearest.theoretical:.3g} · empirical BER={empirical:.3g}"
        )

    def _show_ber_constellation(self):
        mode = self.ber_mode.currentText()
        if mode == "BPSK":
            self.ber_summary.setText("BPSK has two antipodal symbols on the I axis.")
            return
        self.constellation_dialog_points = constellation_points(mode)
        plot = SignalPlot()
        plot.set_theme(self._theme)
        plot.set_constellation(self.constellation_dialog_points)
        dialog = QWidget()
        dialog.setWindowTitle(f"Constellation · {mode}")
        layout = QVBoxLayout(dialog)
        layout.addWidget(plot)
        dialog.resize(640, 430)
        dialog.show()
        self._constellation_dialog = dialog

    def _scroll(self, page: QWidget) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(page)
        return scroll

    def set_theme(self, name: str):
        self._theme = name
        for child in self.findChildren(SignalPlot):
            child.set_theme(name)
