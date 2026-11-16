from __future__ import annotations

from pathlib import Path
import json

from PySide6.QtCore import QEvent, QRectF, Qt
from PySide6.QtGui import QColor, QBrush, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .db import Database
from .mml import MmlEngine, MmlResult


BG = "#0b1117"
PANEL = "#101922"
PANEL2 = "#0e171f"
BORDER = "#243443"
TEXT = "#d7e2ec"
MUTED = "#7f95a8"
GREEN = "#42d392"
YELLOW = "#f2c94c"
RED = "#f25f5c"
BLUE = "#59a6ff"
STEEL = "#6f8192"


class ClickableRectItem(QGraphicsRectItem):
    def __init__(self, rect: QRectF, on_click, data=None):
        super().__init__(rect)
        self.on_click = on_click
        self.data = data
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setSelected(True)
            if self.on_click:
                self.on_click(self.data)
        super().mousePressEvent(event)


class HardwareView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_obj = QGraphicsScene(self)
        self.setScene(self.scene_obj)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setBackgroundBrush(QColor(BG))
        self.current_dlu = 50
        self.current_shelf = None
        self.current_module = None
        self.controller = None

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 0.87
        self.scale(factor, factor)

    def reset_zoom(self):
        self.resetTransform()
        rect = self.scene().itemsBoundingRect().adjusted(-20, -20, 20, 20)
        self.fitInView(rect, Qt.KeepAspectRatio)


class DluSimulatorWindow(QMainWindow):
    def __init__(self, db_path: str | Path):
        super().__init__()
        self.db = Database(db_path)
        self.mml = MmlEngine(self.db)
        self.history: list[str] = []
        self.history_index = 0
        self.current_view = "dlu"

        self.setWindowTitle("DLU Lab — Siemens EWSD Educational Simulator")
        self.resize(1500, 900)
        self.setMinimumSize(1200, 720)

        self._build_ui()
        self._apply_style()
        self.show_dlu(50)
        self.refresh_status()
        self.terminal.append(
            "<span style='color:#7f95a8'>DLU Lab ready. "
            "Type &gt; help;</span>"
        )

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(10, 10, 10, 10)
        main.setSpacing(8)

        header = QFrame()
        header.setObjectName("Header")
        h = QHBoxLayout(header)
        h.setContentsMargins(12, 8, 12, 8)

        title = QLabel("DLU LAB")
        title.setObjectName("Title")
        subtitle = QLabel(
            "Siemens EWSD · Hardware-first teaching simulator"
        )
        subtitle.setObjectName("Subtitle")
        h.addWidget(title)
        h.addWidget(subtitle)
        h.addStretch()
        h.addWidget(QLabel("EXCHANGE  ALE1"))
        h.addWidget(QLabel("DLU"))

        self.dlu_combo = QComboBox()
        for row in self.db.list_dlus():
            self.dlu_combo.addItem(str(row["dlu_id"]))
        self.dlu_combo.setCurrentText("50")
        self.dlu_combo.currentTextChanged.connect(
            lambda value: self.show_dlu(int(value))
        )
        h.addWidget(self.dlu_combo)

        self.status_chip = QLabel("SYSTEM ACT")
        self.status_chip.setObjectName("StatusChip")
        h.addWidget(self.status_chip)
        main.addWidget(header)

        self.syp = QFrame()
        self.syp.setObjectName("SYP")
        syp_layout = QHBoxLayout(self.syp)
        syp_layout.setContentsMargins(10, 5, 10, 5)

        self.crit_label = QLabel("CRITICAL 0")
        self.major_label = QLabel("MAJOR 0")
        self.minor_label = QLabel("MINOR 0")
        self.traffic_label = QLabel("PDC 0/120")
        self.path_label = QLabel("PATH —")

        for widget in (
            self.crit_label,
            self.major_label,
            self.minor_label,
            self.traffic_label,
            self.path_label,
        ):
            syp_layout.addWidget(widget)

        syp_layout.addStretch()
        main.addWidget(self.syp)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        main.addWidget(splitter, 1)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.go_back)
        toolbar.addWidget(self.back_btn)

        self.breadcrumb = QLabel("DLU 50")
        self.breadcrumb.setObjectName("Breadcrumb")
        toolbar.addWidget(self.breadcrumb)
        toolbar.addStretch()

        fit_btn = QPushButton("Fit")
        fit_btn.clicked.connect(self.hardware_reset_zoom)
        toolbar.addWidget(fit_btn)

        reset_btn = QPushButton("Reset Demo")
        reset_btn.clicked.connect(self.reset_demo)
        toolbar.addWidget(reset_btn)

        left_layout.addLayout(toolbar)

        self.hardware = HardwareView()
        left_layout.addWidget(self.hardware, 1)

        self.legend = QLabel(
            "Gray: unassigned   Green: idle   Blue/Red: busy   "
            "Yellow: blocked/maintenance"
        )
        self.legend.setObjectName("Legend")
        left_layout.addWidget(self.legend)

        splitter.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.terminal_header = QLabel(
            "OMT · Operations & Maintenance Terminal"
        )
        self.terminal_header.setObjectName("SectionTitle")
        right_layout.addWidget(self.terminal_header)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setObjectName("Terminal")
        right_layout.addWidget(self.terminal, 3)

        cmd = QHBoxLayout()
        self.prompt = QLabel(">")
        self.prompt.setObjectName("Prompt")

        self.input = QLineEdit()
        self.input.setPlaceholderText(
            "e.g. stat dlu: dlu=50;"
        )
        self.input.returnPressed.connect(self.execute_input)
        self.input.installEventFilter(self)

        run = QPushButton("EXECUTE")
        run.clicked.connect(self.execute_input)

        cmd.addWidget(self.prompt)
        cmd.addWidget(self.input, 1)
        cmd.addWidget(run)
        right_layout.addLayout(cmd)

        macro_title = QLabel("Quick Scenarios")
        macro_title.setObjectName("SectionTitle")
        right_layout.addWidget(macro_title)

        macros = QHBoxLayout()
        macro_defs = [
            (
                "8-Line",
                [
                    f"> cr sub: dn={2233500 + i}, eqn=50-1-5-{i}, "
                    "lac=021, class=ms, c/s=PB;"
                    for i in range(8)
                ],
            ),
            (
                "CMRL",
                [
                    "> cr sub: dn=2250500, eqn=10-1-7-0, "
                    "lac=021, class=cmrl, c/s=PB;",
                    "> cr sub: dn=2250506, eqn=10-1-7-6, "
                    "lac=021, class=cmrl, c/s=PB;",
                ],
            ),
            (
                "Diag Guard",
                [
                    "> diag dlu: dlu=10;",
                    "> conf dlu: dlu=10, dluc0=y, ost=mbl;",
                    "> diag dlu: dlu=10;",
                ],
            ),
            (
                "Inspect",
                [
                    "> disp dlu: dlu=50;",
                    "> disp slot: dlu=50, shelf=1, module=5;",
                ],
            ),
        ]

        for label, commands in macro_defs:
            button = QPushButton(label)
            button.clicked.connect(
                lambda _, cmds=commands: self.run_macro(cmds)
            )
            macros.addWidget(button)

        right_layout.addLayout(macros)

        self.details = QTableWidget(0, 2)
        self.details.setHorizontalHeaderLabels(["Field", "Value"])
        self.details.horizontalHeader().setStretchLastSection(True)
        self.details.setObjectName("Details")
        right_layout.addWidget(self.details, 2)

        splitter.addWidget(right)
        splitter.setSizes([980, 520])
        self.hardware.controller = self

    def hardware_reset_zoom(self):
        self.hardware.reset_zoom()

    def _apply_style(self):
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {BG};
                color: {TEXT};
                font-family: Segoe UI;
                font-size: 13px;
            }}
            QFrame#Header, QFrame#SYP {{
                background: {PANEL};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
            QLabel#Title {{
                font-size: 23px;
                font-weight: 800;
            }}
            QLabel#Subtitle, QLabel#Legend {{
                color: {MUTED};
            }}
            QLabel#StatusChip {{
                background: #163c2f;
                color: {GREEN};
                border: 1px solid #2d7157;
                border-radius: 12px;
                padding: 4px 10px;
                font-weight: 700;
            }}
            QLabel#Breadcrumb, QLabel#SectionTitle {{
                font-weight: 700;
            }}
            QLabel#Prompt {{
                color: {GREEN};
                font-size: 18px;
                font-weight: 800;
            }}
            QPushButton {{
                background: #16232d;
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 7px 10px;
            }}
            QPushButton:hover {{
                background: #203340;
            }}
            QLineEdit, QTextEdit, QTableWidget {{
                background: {PANEL2};
                border: 1px solid {BORDER};
                border-radius: 6px;
            }}
            QTextEdit#Terminal {{
                font-family: Consolas;
                font-size: 12px;
                padding: 8px;
            }}
            QHeaderView::section {{
                background: #17242f;
                color: {TEXT};
                border: 0;
                padding: 6px;
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QComboBox {{
                background: #16232d;
                border: 1px solid {BORDER};
                padding: 5px;
            }}
            """
        )

    def eventFilter(self, watched, event):
        if watched is self.input and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key_Up:
                if self.history:
                    self.history_index = max(
                        0, self.history_index - 1
                    )
                    self.input.setText(
                        self.history[self.history_index]
                    )
                return True
            if event.key() == Qt.Key_Down:
                if self.history:
                    self.history_index = min(
                        len(self.history), self.history_index + 1
                    )
                    self.input.setText(
                        self.history[self.history_index]
                        if self.history_index < len(self.history)
                        else ""
                    )
                return True
        return super().eventFilter(watched, event)

    def go_back(self):
        if self.current_view == "module":
            self.show_shelf(
                self.hardware.current_dlu,
                self.hardware.current_shelf,
            )
        elif self.current_view == "shelf":
            self.show_dlu(self.hardware.current_dlu)
        else:
            self.show_dlu(self.hardware.current_dlu)

    def clear_scene(self):
        self.hardware.scene_obj.clear()
        self.hardware.resetTransform()

    def add_text(
        self,
        x,
        y,
        text,
        size=12,
        color=TEXT,
        bold=False,
    ):
        item = self.hardware.scene_obj.addText(text)
        font = QFont("Segoe UI", size)
        font.setBold(bold)
        item.setFont(font)
        item.setDefaultTextColor(QColor(color))
        item.setPos(x, y)
        return item

    def show_dlu(self, dlu_id: int):
        self.hardware.current_dlu = dlu_id
        self.hardware.current_shelf = None
        self.hardware.current_module = None
        self.current_view = "dlu"

        self.clear_scene()
        self.breadcrumb.setText(f"DLU {dlu_id}")
        self.back_btn.setEnabled(False)

        self.add_text(
            20,
            12,
            f"DLU {dlu_id} — DIGITAL LINE UNIT",
            18,
            TEXT,
            True,
        )

        dlu = self.db.get_dlu(dlu_id)
        self.add_text(
            20,
            42,
            f"DLUC0: {dlu['dluc0_state'].upper()}    "
            f"DLUC1: {dlu['dluc1_state'].upper()}",
            11,
            GREEN if dlu["dluc0_state"] == "act" else YELLOW,
            True,
        )
        self.add_text(
            20,
            66,
            "Physical teaching view · 8 shelves × 16 module positions",
            11,
            MUTED,
        )

        self._controller_block(20, 100, dlu_id)

        start_y = 195
        for shelf in range(8):
            y = start_y + shelf * 80
            self._draw_shelf_row(dlu_id, shelf, 20, y)

        self.hardware.scene_obj.setSceneRect(
            0, 0, 1040, start_y + 8 * 80 + 30
        )
        self.hardware.reset_zoom()

        self._set_details(
            {
                "DLU": dlu_id,
                "DLUC0": dlu["dluc0_state"],
                "DLUC1": dlu["dluc1_state"],
                "Shelves": "0..7",
                "Modules/Shelf": "0..15",
            }
        )
        self.refresh_status()

    def _controller_block(self, x, y, dlu_id):
        dlu = self.db.get_dlu(dlu_id)
        items = [
            ("DLUC0", dlu["dluc0_state"]),
            ("DLUC1", dlu["dluc1_state"]),
        ]

        for index, (name, state) in enumerate(items):
            rect = QRectF(
                x + index * 150,
                y,
                130,
                58,
            )
            box = self.hardware.scene_obj.addRect(
                rect,
                QPen(QColor(BORDER)),
                QBrush(QColor("#182631")),
            )
            box.setPen(
                QPen(
                    QColor(
                        BLUE if state == "act" else STEEL
                    ),
                    1.5,
                )
            )
            self.add_text(
                rect.x() + 10,
                rect.y() + 7,
                name,
                11,
                TEXT,
                True,
            )
            self.add_text(
                rect.x() + 10,
                rect.y() + 28,
                state.upper(),
                10,
                GREEN if state == "act" else MUTED,
                True,
            )

    def _draw_shelf_row(self, dlu_id, shelf, x, y):
        slots = self.db.list_shelf(dlu_id, shelf)
        self.add_text(x, y + 4, f"SHELF {shelf}", 11, TEXT, True)

        for slot in slots:
            module_x = x + 90 + slot["module"] * 58
            rect = QRectF(module_x, y, 50, 56)

            if slot["card_type"] == "UNCONFIGURED":
                fill = "#151f27"
                edge = "#2f424f"
            elif slot["card_type"] == "CMRL":
                fill = "#3b3120"
                edge = YELLOW
            else:
                fill = "#142c24"
                edge = GREEN

            item = ClickableRectItem(
                rect,
                lambda data: self.show_shelf(data[0], data[1]),
                (dlu_id, shelf),
            )
            item.setBrush(QBrush(QColor(fill)))
            item.setPen(QPen(QColor(edge), 1.2))
            self.hardware.scene_obj.addItem(item)

            self.add_text(
                module_x + 4,
                y + 4,
                str(slot["module"]),
                9,
                TEXT,
                True,
            )
            label = (
                slot["card_type"]
                if slot["card_type"] != "UNCONFIGURED"
                else "—"
            )
            self.add_text(
                module_x + 4,
                y + 22,
                label,
                7,
                edge,
                True,
            )
            self.add_text(
                module_x + 4,
                y + 38,
                (
                    f"{slot['port_count']}P"
                    if slot["port_count"]
                    else "EMPTY"
                ),
                7,
                MUTED,
            )

    def show_shelf(self, dlu_id: int, shelf: int):
        self.hardware.current_dlu = dlu_id
        self.hardware.current_shelf = shelf
        self.hardware.current_module = None
        self.current_view = "shelf"

        self.clear_scene()
        self.back_btn.setEnabled(True)
        self.breadcrumb.setText(
            f"DLU {dlu_id}  /  Shelf {shelf}"
        )

        self.add_text(
            20,
            15,
            f"DLU {dlu_id} · SHELF {shelf}",
            20,
            TEXT,
            True,
        )
        self.add_text(
            20,
            50,
            "Module positions 0..15",
            11,
            MUTED,
        )

        slots = self.db.list_shelf(dlu_id, shelf)
        for slot in slots:
            x = 25 + (slot["module"] % 4) * 235
            y = 95 + (slot["module"] // 4) * 145
            self._draw_module_card(slot, x, y)

        self.hardware.scene_obj.setSceneRect(0, 0, 980, 720)
        self.hardware.reset_zoom()

        self._set_details(
            {
                "DLU": dlu_id,
                "Shelf": shelf,
                "Modules": "0..15",
            }
        )

    def _draw_module_card(self, slot, x, y):
        card_type = slot["card_type"]
        port_count = slot["port_count"]
        configured = card_type != "UNCONFIGURED"

        outer = QRectF(x, y, 210, 112)
        box = ClickableRectItem(
            outer,
            lambda data: self.show_module(*data),
            (
                slot["dlu_id"],
                slot["shelf"],
                slot["module"],
            ),
        )
        box.setBrush(
            QBrush(
                QColor(
                    "#14231d"
                    if configured
                    else "#131b22"
                )
            )
        )
        box.setPen(
            QPen(
                QColor(
                    GREEN if configured else BORDER
                ),
                1.5,
            )
        )
        self.hardware.scene_obj.addItem(box)

        self.add_text(
            x + 12,
            y + 10,
            f"MODULE {slot['module']}",
            11,
            TEXT,
            True,
        )
        self.add_text(
            x + 12,
            y + 34,
            card_type,
            15,
            GREEN if configured else MUTED,
            True,
        )
        self.add_text(
            x + 12,
            y + 61,
            f"Capacity: {port_count} port(s)",
            10,
            TEXT if configured else MUTED,
        )
        self.add_text(
            x + 12,
            y + 82,
            f"OST: {slot['ost'].upper()}",
            9,
            YELLOW if slot["ost"] == "mbl" else MUTED,
        )

    def show_module(self, dlu_id: int, shelf: int, module: int):
        self.hardware.current_dlu = dlu_id
        self.hardware.current_shelf = shelf
        self.hardware.current_module = module
        self.current_view = "module"

        self.clear_scene()
        self.back_btn.setEnabled(True)
        self.breadcrumb.setText(
            f"DLU {dlu_id}  /  Shelf {shelf}  /  Module {module}"
        )

        slot = self.db.get_slot(dlu_id, shelf, module)
        if slot is None:
            self.add_text(
                20,
                20,
                "Module not found",
                18,
                RED,
                True,
            )
            return

        self.add_text(
            20,
            15,
            f"MODULE {module} · {slot.card_type}",
            20,
            TEXT,
            True,
        )
        self.add_text(
            20,
            50,
            f"EQN base: {dlu_id}-{shelf}-{module}-N    "
            f"Capacity: {slot.port_count}",
            11,
            MUTED,
        )

        if slot.card_type == "UNCONFIGURED":
            self.add_text(
                35,
                105,
                "UNCONFIGURED — no subscriber ports are available",
                13,
                YELLOW,
                True,
            )
        else:
            rows = self.db.conn.execute(
                """
                SELECT * FROM subscribers
                WHERE dlu_id=? AND shelf=? AND module=?
                ORDER BY port
                """,
                (dlu_id, shelf, module),
            ).fetchall()
            by_port = {
                row["port"]: row
                for row in rows
            }

            cols = min(8, max(1, slot.port_count))
            for port in range(slot.port_count):
                x = 35 + (port % cols) * 105
                y = 120 + (port // cols) * 125
                self._draw_port(
                    dlu_id,
                    shelf,
                    module,
                    port,
                    by_port.get(port),
                    x,
                    y,
                )

        self.hardware.scene_obj.setSceneRect(0, 0, 980, 600)
        self.hardware.reset_zoom()

        self._set_details(
            {
                "DLU": dlu_id,
                "Shelf": shelf,
                "Module": module,
                "Card": slot.card_type,
                "Capacity": slot.port_count,
            }
        )

    def _draw_port(
        self,
        dlu_id,
        shelf,
        module,
        port,
        sub,
        x,
        y,
    ):
        state = (
            sub["line_state"]
            if sub
            else "unassigned"
        )

        if not sub:
            color = STEEL
        elif sub["blk_reason"]:
            color = YELLOW
        elif state == "idle":
            color = GREEN
        elif state == "busy":
            color = RED
        else:
            color = YELLOW

        outer = QRectF(x, y, 90, 105)
        item = ClickableRectItem(
            outer,
            lambda data: self.select_port(*data),
            (dlu_id, shelf, module, port),
        )
        item.setBrush(QBrush(QColor("#111b23")))
        item.setPen(QPen(QColor(BORDER), 1.0))
        self.hardware.scene_obj.addItem(item)

        led = self.hardware.scene_obj.addEllipse(
            QRectF(x + 33, y + 17, 24, 24),
            QPen(QColor(color)),
            QBrush(QColor(color)),
        )
        led.setZValue(2)

        self.add_text(
            x + 28,
            y + 45,
            f"PORT {port}",
            9,
            TEXT,
            True,
        )
        self.add_text(
            x + 12,
            y + 68,
            sub["dn"] if sub else "—",
            8,
            color,
            True,
        )
        self.add_text(
            x + 14,
            y + 84,
            state.upper(),
            7,
            MUTED,
        )

    def select_port(
        self,
        dlu_id: int,
        shelf: int,
        module: int,
        port: int,
    ):
        row = self.db.conn.execute(
            """
            SELECT s.*, sl.card_type
            FROM subscribers s
            JOIN slots sl
              ON sl.dlu_id=s.dlu_id
             AND sl.shelf=s.shelf
             AND sl.module=s.module
            WHERE s.dlu_id=? AND s.shelf=? AND s.module=? AND s.port=?
            """,
            (dlu_id, shelf, module, port),
        ).fetchone()

        eqn = f"{dlu_id}-{shelf}-{module}-{port}"

        if not row:
            self._set_details(
                {
                    "EQN": eqn,
                    "Port": port,
                    "Status": "UNASSIGNED",
                }
            )
            return

        self._set_details(
            {
                "EQN": eqn,
                "Port": port,
                "DN": row["dn"],
                "LAC": row["lac"],
                "State": row["line_state"],
                "Card": row["card_type"],
                "Block": row["blk_reason"] or "NORMAL",
                "Services": row["cos_flags"] or "—",
            }
        )

    def _set_details(self, details: dict):
        self.details.setRowCount(0)
        for key, value in details.items():
            row = self.details.rowCount()
            self.details.insertRow(row)
            self.details.setItem(
                row, 0, QTableWidgetItem(str(key))
            )
            self.details.setItem(
                row, 1, QTableWidgetItem(str(value))
            )

    def execute_input(self):
        command = self.input.text().strip()
        if not command:
            return

        if not command.startswith(">"):
            command = "> " + command

        self.history.append(command)
        self.history_index = len(self.history)
        self.input.clear()
        self._execute_command(command)

    def _execute_command(self, command: str):
        self.terminal.append(
            f"<span style='color:#d7e2ec'>&gt; "
            f"{command[1:].strip()}</span>"
        )

        result = self.mml.execute(command)
        self._show_result(result)
        self.refresh_status()
        self._refresh_current_view()

    def _show_result(self, result: MmlResult):
        color = GREEN if result.ok else RED
        self.terminal.append(
            f"<span style='color:{color}'>"
            f"[{result.code}] {result.message}"
            f"</span>"
        )
        if result.data is not None:
            pretty = json.dumps(
                result.data,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
            self.terminal.append(
                f"<pre style='color:#8fb2cf'>{pretty}</pre>"
            )

    def _prepare_macro(self, name: str) -> None:
        if name == "8-Line":
            for dn in range(2233500, 2233508):
                self.db.conn.execute("DELETE FROM subscribers WHERE lac='021' AND dn=?", (str(dn),))
        elif name == "CMRL":
            for dn in range(2250500, 2250507):
                self.db.conn.execute("DELETE FROM subscribers WHERE lac='021' AND dn=?", (str(dn),))
        elif name == "Diag Guard":
            with self.db.conn:
                self.db.conn.execute(
                    "UPDATE dlus SET dluc0_state='act', dluc1_state='standby' WHERE dlu_id=10"
                )
                self.db.clear_active_alarms("DLU 10")

    def run_macro(self, commands: list[str]):
        if commands and commands[0].startswith("> cr sub: dn=223350"):
            scenario_name = "8-Line"
        elif commands and commands[0].startswith("> cr sub: dn=2250500"):
            scenario_name = "CMRL"
        elif commands and commands[0].startswith("> diag dlu: dlu=10"):
            scenario_name = "Diag Guard"
        else:
            scenario_name = "Inspect"

        self._prepare_macro(scenario_name)
        self.terminal.append(
            f"<span style='color:#59a6ff'>-- {scenario_name} start --</span>"
        )
        for command in commands:
            self._execute_command(command)
        self.terminal.append(
            f"<span style='color:#59a6ff'>-- {scenario_name} end --</span>"
        )

    def _refresh_current_view(self):
        if self.current_view == "dlu":
            self.show_dlu(self.hardware.current_dlu)
        elif self.current_view == "shelf":
            self.show_shelf(
                self.hardware.current_dlu,
                self.hardware.current_shelf,
            )
        else:
            self.show_module(
                self.hardware.current_dlu,
                self.hardware.current_shelf,
                self.hardware.current_module,
            )

    def refresh_status(self):
        current = self.db.get_dlu(self.hardware.current_dlu)
        if current:
            system_state = (
                "ACT"
                if current["dluc0_state"] == "act"
                or current["dluc1_state"] == "act"
                else "DEGRADED"
            )
            chip_color = GREEN if system_state == "ACT" else YELLOW
            self.status_chip.setText(
                f"DLU {current['dlu_id']} · SYSTEM {system_state}"
            )
            self.status_chip.setStyleSheet(
                f"background:#163c2f; color:{chip_color}; "
                f"border:1px solid {chip_color}; border-radius:12px; "
                "padding:4px 10px; font-weight:700;"
            )

        rows = list(
            self.db.conn.execute(
                """
                SELECT severity, COUNT(*) AS n
                FROM alarms
                WHERE active=1
                GROUP BY severity
                """
            )
        )
        counts = {
            row["severity"]: row["n"]
            for row in rows
        }

        self.crit_label.setText(
            f"CRITICAL {counts.get('CRITICAL', 0)}"
        )
        self.major_label.setText(
            f"MAJOR {counts.get('MAJOR', 0)}"
        )
        self.minor_label.setText(
            f"MINOR {counts.get('MINOR', 0)}"
        )

        busy = self.db.conn.execute(
            "SELECT COUNT(*) AS n FROM subscribers "
            "WHERE line_state='busy'"
        ).fetchone()["n"]

        self.traffic_label.setText(
            f"PDC {busy}/120"
        )
        self.path_label.setText(
            "PATH —" if not busy else "PATH ACTIVE"
        )

    def reset_demo(self):
        self.db.reset_demo()
        self.terminal.append(
            "<span style='color:#f2c94c'>"
            "[RESET] Demo state restored: all subscribers removed, "
            "DLUC0=ACT, DLUC1=STANDBY"
            "</span>"
        )
        self._refresh_current_view()
        self.refresh_status()

    def closeEvent(self, event):
        self.db.close()
        event.accept()
