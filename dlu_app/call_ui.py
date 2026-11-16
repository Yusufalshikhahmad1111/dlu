from __future__ import annotations

import json

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QBrush, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .call_engine import CallEngine, CallPath, CallResult


BG = "#071018"
PANEL = "#0e1923"
PANEL2 = "#0a141c"
BORDER = "#243a4b"
TEXT = "#dce8f2"
MUTED = "#7e96aa"
GREEN = "#42d392"
YELLOW = "#f0c75e"
RED = "#ef6262"
BLUE = "#5aa8ff"


class CallPathView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_obj = QGraphicsScene(self)
        self.setScene(self.scene_obj)
        self.setRenderHint(QPainter.Antialiasing)
        self.setBackgroundBrush(QColor(BG))
        self.setMinimumHeight(250)

    def clear(self):
        self.scene_obj.clear()

    def show_path(self, path: CallPath | None, active: bool = True) -> None:
        self.clear()
        if not path:
            return

        x0, y0 = 25, 65
        box_w, box_h, gap = 145, 78, 35
        colors = {
            "DLU": GREEN,
            "SN": BLUE,
            "LTG": YELLOW,
            "GATEWAY": "#b88cff",
            "SERVICE": "#72d6c9",
            "CPT": RED,
        }

        for idx, node in enumerate(path.nodes):
            x = x0 + idx * (box_w + gap)
            color = colors.get(node.node_type, MUTED)
            rounded = QPainterPath()
            rounded.addRoundedRect(
                QRectF(x, y0, box_w, box_h),
                10,
                10,
            )
            self.scene_obj.addPath(
                rounded,
                QPen(QColor(color), 2),
                QBrush(QColor("#101d27")),
            )

            label = self.scene_obj.addText(node.label)
            label.setDefaultTextColor(QColor(TEXT))
            label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            label.setPos(x + 10, y0 + 24)

            if idx:
                line_color = GREEN if active else RED
                self.scene_obj.addLine(
                    x - gap,
                    y0 + box_h / 2,
                    x,
                    y0 + box_h / 2,
                    QPen(QColor(line_color), 3),
                )

        self.scene_obj.setSceneRect(
            0,
            0,
            max(700, x0 + len(path.nodes) * (box_w + gap)),
            220,
        )
        self.fitInView(self.scene_obj.sceneRect(), Qt.KeepAspectRatio)


class CallLabWidget(QWidget):
    def __init__(self, engine: CallEngine, on_state_changed=None, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.on_state_changed = on_state_changed
        self.current_call_id: str | None = None
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        title = QLabel("CALL ENGINE · CPT · CALL PATH")
        title.setStyleSheet("font-size:18px;font-weight:800;")
        root.addWidget(title)

        intro = QLabel(
            "Number Analysis → CPT EVAL → Route → Resource Reservation → Call Path"
        )
        intro.setStyleSheet(f"color:{MUTED};")
        root.addWidget(intro)

        controls = QFrame()
        controls.setStyleSheet(
            f"QFrame {{background:{PANEL};border:1px solid {BORDER};border-radius:8px;}}"
        )
        form = QVBoxLayout(controls)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Caller"))
        self.caller_combo = QComboBox()
        self.caller_combo.setMinimumWidth(260)
        row1.addWidget(self.caller_combo, 1)

        row1.addWidget(QLabel("Dialed"))
        self.dialed = QLineEdit()
        self.dialed.setPlaceholderText(
            "2233501 / 0522233500 / 00964 / 00972"
        )
        row1.addWidget(self.dialed, 1)
        form.addLayout(row1)

        row2 = QHBoxLayout()
        for label, handler in (
            ("PREPARE DEMO", self.prepare_demo),
            ("START CALL", self.start_call),
            ("RELEASE", self.release_call),
        ):
            button = QPushButton(label)
            button.clicked.connect(handler)
            row2.addWidget(button)
        row2.addStretch()
        form.addLayout(row2)

        quick = QHBoxLayout()
        quick.addWidget(QLabel("QUICK CASES"))
        for label, handler in (
            ("LOCAL", self.quick_local),
            ("NATIONAL", self.quick_national),
            ("INTERNATIONAL", self.quick_international),
            ("BLACK LIST", self.quick_blacklist),
        ):
            button = QPushButton(label)
            button.clicked.connect(handler)
            quick.addWidget(button)
        quick.addStretch()
        form.addLayout(quick)

        root.addWidget(controls)

        self.status = QLabel("IDLE · No active call")
        self.status.setStyleSheet(
            f"padding:8px;border:1px solid {BORDER};"
            f"border-radius:6px;color:{GREEN};"
        )
        root.addWidget(self.status)

        path_title = QLabel("CALL PATH")
        path_title.setStyleSheet("font-weight:800;")
        root.addWidget(path_title)

        self.path_view = CallPathView()
        root.addWidget(self.path_view, 1)

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setMaximumHeight(190)
        self.details.setStyleSheet(
            f"background:{PANEL2};border:1px solid {BORDER};font-family:Consolas;"
        )
        root.addWidget(self.details)

        self.refresh_subscribers()

    def refresh_subscribers(self):
        current = self.caller_combo.currentData()
        self.caller_combo.clear()
        rows = self.engine.list_subscribers()

        for row in rows:
            eqn = f"{row['dlu_id']}-{row['shelf']}-{row['module']}-{row['port']}"
            self.caller_combo.addItem(
                f"{row['dn']} · LAC {row['lac']} · {eqn}",
                row["dn"],
            )

        if current:
            idx = self.caller_combo.findData(current)
            if idx >= 0:
                self.caller_combo.setCurrentIndex(idx)

    def _display_result(self, result: CallResult):
        if result.ok:
            route = result.analysis.number_type if result.analysis else ""
            self.status.setText(
                f"{result.code} · {result.message} · {route}"
            )
            self.status.setStyleSheet(
                f"padding:8px;border:1px solid {GREEN};"
                f"border-radius:6px;color:{GREEN};"
            )
        else:
            self.status.setText(f"{result.code} · {result.message}")
            self.status.setStyleSheet(
                f"padding:8px;border:1px solid {RED};"
                f"border-radius:6px;color:{RED};"
            )

        self.path_view.show_path(result.path, active=result.ok)

        details: dict = {
            "ok": result.ok,
            "code": result.code,
            "message": result.message,
            "call_id": result.call_id,
        }

        if result.analysis:
            details["analysis"] = {
                "original": result.analysis.original,
                "normalized": result.analysis.normalized,
                "type": result.analysis.number_type,
                "target_lac": result.analysis.target_lac,
                "target_dn": result.analysis.target_dn,
                "cpt": (
                    {
                        "dest": result.analysis.cpt.dest,
                        "code": result.analysis.cpt.code,
                        "eval": result.analysis.cpt.eval,
                        "name": result.analysis.cpt.name,
                        "match_kind": result.analysis.cpt.match_kind,
                    }
                    if result.analysis.cpt
                    else None
                ),
            }

        if result.path:
            details["path"] = result.path.labels()

        used, capacity = self.engine.resource_usage()
        details["PDC"] = f"{used}/{capacity}"
        self.details.setPlainText(
            json.dumps(details, ensure_ascii=False, indent=2)
        )

        if result.ok and result.call_id:
            self.current_call_id = result.call_id

        if self.on_state_changed:
            self.on_state_changed()

    def _select_caller(self, dn: str):
        self.refresh_subscribers()
        idx = self.caller_combo.findData(dn)
        if idx >= 0:
            self.caller_combo.setCurrentIndex(idx)

    def prepare_demo(self):
        try:
            caller, called = self.engine.prepare_demo_subscribers()
            self._select_caller(caller)
            self.dialed.setText(called)
            self.status.setText(f"Demo ready · {caller} → {called}")
            self.status.setStyleSheet(
                f"padding:8px;border:1px solid {BLUE};"
                f"border-radius:6px;color:{BLUE};"
            )
            if self.on_state_changed:
                self.on_state_changed()
        except ValueError as exc:
            QMessageBox.warning(self, "Prepare Demo", str(exc))

    def start_call(self):
        caller = self.caller_combo.currentData()
        if not caller:
            QMessageBox.information(
                self, "Call", "No caller subscriber is available."
            )
            return
        number = self.dialed.text().strip()
        if not number:
            QMessageBox.information(
                self, "Call", "Enter a dialed number."
            )
            return
        result = self.engine.start_call(caller, number)
        self._display_result(result)

    def release_call(self):
        if not self.current_call_id:
            QMessageBox.information(self, "Release", "No active call.")
            return
        result = self.engine.release_call(self.current_call_id)
        self._display_result(result)
        self.current_call_id = None

    def quick_local(self):
        self.prepare_demo()
        self.start_call()

    def quick_national(self):
        try:
            caller, _called = self.engine.prepare_demo_subscribers()
        except ValueError as exc:
            QMessageBox.warning(self, "National", str(exc))
            return
        self._select_caller(caller)
        self.dialed.setText("0522233500")
        self.start_call()

    def quick_international(self):
        try:
            caller, _called = self.engine.prepare_demo_subscribers()
        except ValueError as exc:
            QMessageBox.warning(self, "International", str(exc))
            return
        self._select_caller(caller)
        self.dialed.setText("00964")
        self.start_call()

    def quick_blacklist(self):
        try:
            caller, _called = self.engine.prepare_demo_subscribers()
        except ValueError as exc:
            QMessageBox.warning(self, "Black List", str(exc))
            return
        self._select_caller(caller)
        self.dialed.setText("00972")
        self.start_call()

    def reset(self):
        self.engine.repo.reset_demo()
        self.current_call_id = None
        self.path_view.clear()
        self.status.setText("IDLE · No active call")
        self.details.clear()
        self.refresh_subscribers()
