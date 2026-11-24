from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from .call_engine import CallPath, CallResult
from .design_tokens import get_tokens, normalize_mode


PHASES = ("REQUEST", "ROUTING", "RESOURCE", "CONNECTED", "BLOCKED", "RELEASED")


@dataclass(frozen=True)
class PhaseState:
    active: str
    completed: tuple[str, ...] = ()
    skipped: tuple[str, ...] = ()


def _phase_state(result: CallResult | None) -> PhaseState:
    if result is None:
        return PhaseState("REQUEST")
    if result.code in {"CALL-RELEASED", "CALL-ALREADY-RELEASED"}:
        return PhaseState(
            "RELEASED",
            ("REQUEST", "ROUTING", "RESOURCE", "CONNECTED"),
        )
    if not result.ok:
        if result.code == "CALL-RESOURCE-BUSY":
            return PhaseState("BLOCKED", ("REQUEST", "ROUTING"))
        return PhaseState("BLOCKED", ("REQUEST",), ("RESOURCE",))

    number_type = result.analysis.number_type if result.analysis else ""
    resource_required = number_type in {"NATIONAL", "INTERNATIONAL"}
    completed = ("REQUEST", "ROUTING", "RESOURCE") if resource_required else ("REQUEST", "ROUTING")
    skipped = () if resource_required else ("RESOURCE",)
    return PhaseState("CONNECTED", completed, skipped)


def route_explanation(result: CallResult | None) -> str:
    if result is None:
        return "Choose a caller and dialed number, then START CALL to watch the route."

    if result.code == "CALL-RESOURCE-BUSY":
        return (
            "The route was identified, but the PDC voice resource is full. "
            "The call is blocked before CONNECTED."
        )

    if result.code in {"CALL-BLOCKED", "CALL-PORT-BUSY", "CALL-NO-ROUTE"}:
        if result.analysis and result.analysis.cpt and result.analysis.cpt.eval.upper() == "NO":
            return (
                "CPT returned EVAL=NO, so the route is blocked before any voice "
                "resource is reserved."
            )
        if result.code == "CALL-PORT-BUSY":
            return "The destination or caller line is busy, so the call cannot become connected."
        if result.code == "CALL-NO-ROUTE":
            return "Number analysis did not produce a valid route, so switching cannot proceed."
        return result.message

    if result.code in {"CALL-RELEASED", "CALL-ALREADY-RELEASED"}:
        return "The call was released. Any reserved PDC resource was returned to the available pool."

    if result.analysis:
        route_type = result.analysis.number_type
        if route_type == "LOCAL":
            return (
                "LOCAL: the call stays inside the local exchange path "
                "DLU → SN → destination DLU. No PDC voice reservation is required."
            )
        if route_type == "NATIONAL":
            return (
                "NATIONAL: CPT selects the remote LAC route, then the call crosses "
                "LTG → SN → LTG. One PDC voice channel is reserved."
            )
        if route_type == "INTERNATIONAL":
            return (
                "INTERNATIONAL: the call crosses LTG → SN → International Gateway. "
                "One PDC voice channel is reserved."
            )
        if route_type == "SERVICE":
            return "SERVICE: the call is delivered from the local switching path to the selected service."

    return result.message


class CallFlowCanvas(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.mode = "morning"
        self.path: CallPath | None = None
        self.result: CallResult | None = None
        self.used = 0
        self.capacity = 0
        self.animating = False
        self._animation_step = 0
        self._animation_steps = 18
        self._timer = QTimer(self)
        self._timer.setInterval(90)
        self._timer.timeout.connect(self._tick)
        self.setMinimumHeight(260)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_mode(self, mode: str) -> None:
        self.mode = normalize_mode(mode)
        self.update()

    def show_result(self, result: CallResult, used: int, capacity: int) -> None:
        self.result = result
        self.path = result.path
        self.used = used
        self.capacity = capacity
        self._animation_step = 0
        self._timer.stop()
        self.animating = bool(result.ok and result.path and len(result.path.nodes) > 1)
        if self.animating:
            self._timer.start()
        self.update()

    def clear(self) -> None:
        self._timer.stop()
        self.animating = False
        self.result = None
        self.path = None
        self._animation_step = 0
        self.used = 0
        self.capacity = 0
        self.update()

    def _tick(self) -> None:
        self._animation_step += 1
        if self._animation_step >= self._animation_steps:
            self._timer.stop()
            self.animating = False
        self.update()

    def _node_color(self, node_type: str) -> str:
        tokens = get_tokens(self.mode)
        return {
            "DLU": tokens.success,
            "SN": tokens.primary,
            "LTG": tokens.info,
            "GATEWAY": tokens.warning,
            "SERVICE": tokens.primary,
            "CPT": tokens.danger,
        }.get(node_type, tokens.border_strong)

    def _node_rects(self) -> list[tuple[tuple[float, float, float, float], tuple[float, float]]]:
        if not self.path or not self.path.nodes:
            return []
        count = len(self.path.nodes)
        margin = 22
        gap = 24
        width = max(128, min(210, (self.width() - 2 * margin - gap * (count - 1)) // count))
        total = width * count + gap * (count - 1)
        start_x = max(margin, (self.width() - total) / 2)
        y = max(86, (self.height() - 96) / 2)
        height = 108
        return [
            (
                (start_x + i * (width + gap), y, width, height),
                (start_x + i * (width + gap) + width / 2, y + height / 2),
            )
            for i in range(count)
        ]

    def _draw_wrapped(self, painter: QPainter, text: str, rect, font: QFont, color: QColor) -> None:
        painter.setFont(font)
        painter.setPen(color)
        painter.drawText(
            int(rect[0]),
            int(rect[1]),
            int(rect[2]),
            int(rect[3]),
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            text,
        )

    def paintEvent(self, _event) -> None:
        tokens = get_tokens(self.mode)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(tokens.surface))

        painter.setPen(QPen(QColor(tokens.border), 1))
        painter.setBrush(QBrush(QColor(tokens.surface_elevated)))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 12, 12)

        painter.setPen(QColor(tokens.text_primary))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(18, 26, "TELECOM SIGNAL FLOW")

        if self.result is None or not self.path:
            painter.setPen(QColor(tokens.text_muted))
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(
                self.rect().adjusted(22, 48, -22, -22),
                Qt.AlignmentFlag.AlignCenter,
                "Run a call case to visualize REQUEST → ROUTING → RESOURCE → CONNECTED.",
            )
            painter.end()
            return

        status_text = "CONNECTED" if self.result.ok else "BLOCKED"
        if self.result.code in {"CALL-RELEASED", "CALL-ALREADY-RELEASED"}:
            status_text = "RELEASED"
        status_color = tokens.success if self.result.ok else tokens.danger

        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QColor(status_color))
        painter.drawText(
            self.width() - 150,
            18,
            126,
            20,
            Qt.AlignmentFlag.AlignRight,
            status_text,
        )

        rects = self._node_rects()
        centers = [item[1] for item in rects]

        for i, edge in enumerate(self.path.edges):
            if i >= len(centers) - 1:
                break
            x1, y1 = centers[i]
            x2, y2 = centers[i + 1]
            line_color = tokens.success if self.result.ok else tokens.danger
            painter.setPen(QPen(QColor(line_color), 3))
            painter.drawLine(int(x1 + 42), int(y1), int(x2 - 42), int(y2))

            arrow_x = int((x1 + x2) / 2)
            arrow_y = int((y1 + y2) / 2)
            painter.setBrush(QBrush(QColor(line_color)))
            painter.drawPolygon(
                [
                    (arrow_x + 6, arrow_y),
                    (arrow_x - 5, arrow_y - 6),
                    (arrow_x - 5, arrow_y + 6),
                ]
            )

            if edge.resource_id:
                pill = edge.resource_id
                pill_w = min(140, max(96, len(pill) * 7))
                painter.setBrush(QBrush(QColor(tokens.deep)))
                painter.setPen(QPen(QColor(tokens.border), 1))
                painter.drawRoundedRect(
                    int((x1 + x2) / 2 - pill_w / 2),
                    int(y1 - 50),
                    int(pill_w),
                    22,
                    8,
                    8,
                )
                painter.setPen(QColor(tokens.primary))
                painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
                painter.drawText(
                    int((x1 + x2) / 2 - pill_w / 2),
                    int(y1 - 46),
                    int(pill_w),
                    18,
                    Qt.AlignmentFlag.AlignCenter,
                    pill,
                )

        for i, node in enumerate(self.path.nodes):
            rect = rects[i][0]
            color = self._node_color(node.node_type)
            painter.setBrush(QBrush(QColor(tokens.card)))
            painter.setPen(QPen(QColor(color), 2))
            painter.drawRoundedRect(
                int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]), 12, 12
            )
            painter.setPen(QColor(color))
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            painter.drawText(
                int(rect[0] + 10),
                int(rect[1] + 12),
                int(rect[2] - 20),
                20,
                Qt.AlignmentFlag.AlignLeft,
                node.node_type,
            )
            self._draw_wrapped(
                painter,
                node.label,
                (rect[0] + 10, rect[1] + 34, rect[2] - 20, 44),
                QFont("Segoe UI", 9, QFont.Weight.Bold),
                QColor(tokens.text_primary),
            )
            node_state = "ACTIVE"
            if not self.result.ok and i == len(self.path.nodes) - 1:
                node_state = "BLOCKED"
            painter.setPen(QColor(tokens.text_muted))
            painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
            painter.drawText(
                int(rect[0] + 10),
                int(rect[1] + rect[3] - 20),
                int(rect[2] - 20),
                16,
                Qt.AlignmentFlag.AlignLeft,
                node_state,
            )

        if self.animating and len(centers) > 1:
            t = self._animation_step / max(1, self._animation_steps - 1)
            edge_count = len(centers) - 1
            position = min(edge_count - 0.001, t * edge_count)
            edge_idx = int(position)
            local_t = position - edge_idx
            x1, y1 = centers[edge_idx]
            x2, y2 = centers[edge_idx + 1]
            sx = x1 + (x2 - x1) * local_t
            sy = y1 + (y2 - y1) * local_t
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(tokens.success)))
            painter.drawEllipse(int(sx - 7), int(sy - 7), 14, 14)

        painter.end()


class CallFlowTeachingPanel(QFrame):
    def __init__(self, mode: str = "morning", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.mode = normalize_mode(mode)
        self.last_result: CallResult | None = None
        self._build()
        self.set_mode(self.mode)

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        header_row = QHBoxLayout()
        title = QLabel("CALL FLOW · TEACHING VIEW")
        title.setObjectName("Stage12Title")
        header_row.addWidget(title)
        header_row.addStretch()
        self.state_label = QLabel("REQUEST")
        self.state_label.setObjectName("Stage12State")
        header_row.addWidget(self.state_label)
        root.addLayout(header_row)

        self.canvas = CallFlowCanvas(self)
        root.addWidget(self.canvas, 1)

        info_row = QHBoxLayout()
        info_row.setSpacing(8)
        self.route_card = QLabel("ROUTE\nChoose a call case to inspect the route.")
        self.route_card.setWordWrap(True)
        self.route_card.setObjectName("Stage12Card")
        info_row.addWidget(self.route_card, 2)

        self.resource_card = QLabel("RESOURCE\nPDC-VOICE · not evaluated yet")
        self.resource_card.setWordWrap(True)
        self.resource_card.setObjectName("Stage12Card")
        info_row.addWidget(self.resource_card, 1)

        self.explanation_card = QLabel(
            "WHY?\nThe visualization will explain the routing decision and the outcome."
        )
        self.explanation_card.setWordWrap(True)
        self.explanation_card.setObjectName("Stage12Card")
        info_row.addWidget(self.explanation_card, 2)
        root.addLayout(info_row)

        self.phase_row = QHBoxLayout()
        self.phase_row.setSpacing(4)
        self.phase_labels: dict[str, QLabel] = {}
        for phase in PHASES:
            label = QLabel(phase)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumHeight(26)
            self.phase_labels[phase] = label
            self.phase_row.addWidget(label, 1)
        root.addLayout(self.phase_row)

    def set_mode(self, mode: str) -> None:
        self.mode = normalize_mode(mode)
        tokens = get_tokens(self.mode)
        self.setStyleSheet(
            f"""
            QFrame#CallFlowTeachingPanel {{
                background:{tokens.surface};
                border:1px solid {tokens.border};
                border-radius:12px;
            }}
            QLabel#Stage12Title {{
                color:{tokens.text_primary};
                font-size:14px;
                font-weight:900;
            }}
            QLabel#Stage12State {{
                color:{tokens.text_primary};
                background:{tokens.deep};
                border:1px solid {tokens.border};
                border-radius:8px;
                padding:6px 10px;
                font-weight:900;
            }}
            QLabel#Stage12Card {{
                color:{tokens.text_primary};
                background:{tokens.surface_elevated};
                border:1px solid {tokens.border};
                border-radius:10px;
                padding:8px;
                min-height:58px;
            }}
            """
        )
        self.canvas.set_mode(self.mode)
        self._refresh_phase_styles()

    def _refresh_phase_styles(self) -> None:
        tokens = get_tokens(self.mode)
        state = _phase_state(self.last_result)
        for phase, label in self.phase_labels.items():
            if phase == state.active:
                color = tokens.success if phase != "BLOCKED" else tokens.danger
                label.setStyleSheet(
                    f"color:{tokens.surface};background:{color};"
                    "border-radius:6px;padding:5px;font-weight:900;"
                )
            elif phase in state.completed:
                label.setStyleSheet(
                    f"color:{tokens.success};background:{tokens.deep};"
                    f"border:1px solid {tokens.border};border-radius:6px;padding:5px;font-weight:800;"
                )
            elif phase in state.skipped:
                label.setStyleSheet(
                    f"color:{tokens.text_muted};background:{tokens.surface_interactive};"
                    f"border:1px solid {tokens.border};border-radius:6px;padding:5px;font-weight:700;"
                )
            else:
                label.setStyleSheet(
                    f"color:{tokens.text_muted};background:{tokens.surface_elevated};"
                    f"border:1px solid {tokens.border};border-radius:6px;padding:5px;font-weight:700;"
                )

    def show_result(self, result: CallResult, used: int, capacity: int) -> None:
        self.last_result = result
        self.canvas.show_result(result, used, capacity)
        state = _phase_state(result)
        self.state_label.setText(state.active)

        route = result.analysis.number_type if result.analysis else "UNKNOWN"
        path_text = " → ".join(result.path.labels()) if result.path else "No route path"
        self.route_card.setText(f"ROUTE · {route}\n{path_text}")

        if result.code == "CALL-RESOURCE-BUSY":
            resource_line = f"PDC-VOICE · FULL · {used}/{capacity} channels in use"
        elif result.code in {"CALL-RELEASED", "CALL-ALREADY-RELEASED"}:
            resource_line = f"PDC-VOICE · RELEASED · {used}/{capacity} channels in use"
        elif result.analysis and result.analysis.number_type in {"NATIONAL", "INTERNATIONAL"}:
            resource_line = f"PDC-VOICE · RESERVED · {used}/{capacity} channels in use"
        else:
            resource_line = f"PDC-VOICE · NOT REQUIRED · {used}/{capacity} channels in use"

        self.resource_card.setText(f"RESOURCE\n{resource_line}")
        self.explanation_card.setText(f"WHY?\n{route_explanation(result)}")
        self._refresh_phase_styles()

    def clear(self) -> None:
        self.last_result = None
        self.canvas.clear()
        self.state_label.setText("REQUEST")
        self.route_card.setText("ROUTE\nChoose a call case to inspect the route.")
        self.resource_card.setText("RESOURCE\nPDC-VOICE · not evaluated yet")
        self.explanation_card.setText(
            "WHY?\nThe visualization will explain the routing decision and the outcome."
        )
        self._refresh_phase_styles()


class Stage12Controller:
    """Installs the Stage 12 presentation layer without changing CallEngine semantics."""

    def __init__(self, window: QWidget, mode: str = "morning"):
        self.window = window
        self.mode = normalize_mode(mode)
        self.call_lab = window.call_lab
        self.panel = CallFlowTeachingPanel(self.mode, self.call_lab)

    def install(self) -> None:
        if getattr(self.window, "_stage12_enabled", False):
            return
        self.window._stage12_enabled = True
        self.window.setProperty("dlu_stage12_enabled", True)

        self.call_lab.attach_call_visualization(self.panel)
        self._original_display = self.call_lab._display_result
        self._original_reset = self.call_lab.reset

        def display_result(result):
            self._original_display(result)
            used, capacity = self.call_lab.engine.resource_usage()
            self.panel.show_result(result, used, capacity)

        def reset():
            self._original_reset()
            self.panel.clear()

        self.call_lab._display_result = display_result
        self.call_lab.reset = reset
        self.window.stage12_controller = self
        self.window.call_flow_teaching_panel = self.panel

    def set_mode(self, mode: str) -> None:
        self.mode = normalize_mode(mode)
        self.panel.set_mode(self.mode)

    def on_theme(self, mode: str) -> None:
        self.set_mode(mode)


def apply_stage12_ui(window: QWidget, mode: str = "morning") -> None:
    controller = getattr(window, "stage12_controller", None)
    if controller is not None:
        controller.set_mode(mode)
        return
    controller = Stage12Controller(window, mode)
    controller.install()
