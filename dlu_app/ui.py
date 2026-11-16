from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QEvent, QMimeData, QRectF, Qt
from PySide6.QtGui import QColor, QBrush, QDrag, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QMenu,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QToolButton,
)

from .call_engine import CallEngine
from .call_ui import CallLabWidget
from .db import CardReference, Database
from .mml import MmlEngine, MmlResult


BG = "#050914"
PANEL = "#0c1728"
PANEL2 = "#08111f"
PANEL3 = "#102033"
STEEL = "#718aa2"
TEXT = "#f3f8ff"
MUTED = "#8fa6bd"
BORDER = "#28435e"
GREEN = "#39e6a5"
YELLOW = "#ffc857"
RED = "#ff6577"
BLUE = "#66a8ff"
CYAN = "#40d9ff"
VIOLET = "#9b7bff"
AMBER = "#ffc857"
WHITE = "#f7fbff"


def state_color(state: str) -> str:
    value = (state or "").lower()
    if value in {"act", "idle"}:
        return GREEN
    if value in {"mbl", "blocked"}:
        return YELLOW
    if value in {"busy", "fault"}:
        return RED
    if value in {"test", "diagnostic"}:
        return BLUE
    return STEEL


def rounded_path(x: float, y: float, w: float, h: float, radius: float = 10) -> QPainterPath:
    path = QPainterPath()
    path.addRoundedRect(QRectF(x, y, w, h), radius, radius)
    return path


def add_rack_rivets(scene, x: float, y: float, w: float, count: int = 4):
    for i in range(count):
        px = x + 8 + i * max(1.0, (w - 16) / max(1, count - 1))
        scene.addEllipse(
            QRectF(px - 2, y, 4, 4),
            QPen(QColor("#5c7892")),
            QBrush(QColor("#15263a")),
        )


class ClickableRectItem(QGraphicsRectItem):
    def __init__(
        self,
        rect: QRectF,
        on_click,
        data=None,
        tooltip="",
        on_double_click=None,
        on_context=None,
    ):
        super().__init__(rect)
        self.on_click = on_click
        self.data = data
        self.on_double_click = on_double_click
        self.on_context = on_context
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        if tooltip:
            self.setToolTip(tooltip)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton and self.on_context:
            callback = self.on_context
            data = self.data
            callback(data)
            event.accept()
            return
        if event.button() == Qt.LeftButton and self.on_click:
            callback = self.on_click
            data = self.data
            callback(data)
            # The callback may rebuild the scene and delete this QGraphicsItem.
            # Never call into the C++ base object after that point.
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and self.on_double_click:
            callback = self.on_double_click
            data = self.data
            callback(data)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


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
        self.current_shelf = 0
        self.current_module = 15
        self.controller = None
        self.setAcceptDrops(True)

    def wheelEvent(self, event):
        factor = 1.18 if event.angleDelta().y() > 0 else 0.85
        self.scale(factor, factor)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-dlu-card"):
            event.acceptProposedAction()
            return
        event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-dlu-card"):
            event.acceptProposedAction()
            return
        event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasFormat("application/x-dlu-card"):
            event.ignore()
            return
        card = bytes(event.mimeData().data("application/x-dlu-card")).decode("utf-8")
        scene_pos = self.mapToScene(event.position().toPoint())
        item = self.scene_obj.itemAt(scene_pos, self.transform())
        target = item
        while target is not None and not isinstance(target, ClickableRectItem):
            target = target.parentItem()
        if (
            isinstance(target, ClickableRectItem)
            and isinstance(target.data, tuple)
            and len(target.data) == 3
            and self.controller is not None
        ):
            dlu, shelf, module = target.data
            self.controller.install_card_at(
                int(dlu), int(shelf), int(module), card
            )
            event.acceptProposedAction()
            return
        event.ignore()

    def reset_zoom(self):
        self.resetTransform()
        rect = self.scene().itemsBoundingRect().adjusted(-30, -30, 30, 30)
        if rect.width() > 0 and rect.height() > 0:
            self.fitInView(rect, Qt.KeepAspectRatio)

class HardwareSelectorDialog(QDialog):
    def __init__(self, db: Database, parent=None, card_type: str | None = None):
        super().__init__(parent)
        self.db = db
        self.card_type = card_type
        self.selected: tuple[int, int, int] | None = None
        self.setWindowTitle("Select hardware" + (f" · {card_type}" if card_type else ""))
        self.resize(560, 320)

        root = QVBoxLayout(self)
        heading = QLabel(
            "Choose the physical location" if not card_type
            else f"Choose a {card_type} module"
        )
        heading.setObjectName("SectionTitle")
        root.addWidget(heading)

        form = QFormLayout()
        self.dlu_combo = QComboBox()
        self.shelf_combo = QComboBox()
        self.module_combo = QComboBox()
        for row in self.db.list_dlus():
            self.dlu_combo.addItem(str(row["dlu_id"]))
        self.shelf_combo.addItems([str(i) for i in range(8)])
        form.addRow("DLU", self.dlu_combo)
        form.addRow("Shelf", self.shelf_combo)
        form.addRow("Module", self.module_combo)
        root.addLayout(form)

        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setObjectName("Legend")
        root.addWidget(self.status)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.ok_button = buttons.button(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        self.dlu_combo.currentTextChanged.connect(self.refresh_modules)
        self.shelf_combo.currentTextChanged.connect(self.refresh_modules)
        self.module_combo.currentIndexChanged.connect(self.refresh_status)
        self.refresh_modules()

    def refresh_modules(self):
        if not self.dlu_combo.currentText() or not self.shelf_combo.currentText():
            return
        dlu = int(self.dlu_combo.currentText())
        shelf = int(self.shelf_combo.currentText())
        self.module_combo.blockSignals(True)
        self.module_combo.clear()
        rows = {r["module"]: r for r in self.db.list_shelf(dlu, shelf)}
        for module in range(16):
            row = rows[module]
            self.module_combo.addItem(
                f"{module} · {row['card_type']} · {row['port_count']}P",
                module,
            )
        self.module_combo.blockSignals(False)
        self.refresh_status()

    def refresh_status(self):
        module = self.module_combo.currentData()
        if module is None:
            self.ok_button.setEnabled(False)
            self.status.setText("No module selected.")
            return
        slot = self.db.get_slot(
            int(self.dlu_combo.currentText()),
            int(self.shelf_combo.currentText()),
            int(module),
        )
        if slot is None:
            self.ok_button.setEnabled(False)
            self.status.setText("Module not found.")
            return
        if self.card_type and slot.card_type != self.card_type:
            self.ok_button.setEnabled(False)
            self.status.setText(
                f"Not compatible: {slot.card_type}. Required {self.card_type}. "
                "Empty positions stay visible instead of being hidden."
            )
        else:
            self.ok_button.setEnabled(True)
            self.status.setText(
                f"Compatible · {slot.card_type} · {slot.port_count} ports · "
                f"EQN base {slot.dlu_id}-{slot.shelf}-{slot.module}"
            )

    def accept(self):
        if not self.ok_button.isEnabled():
            return
        self.selected = (
            int(self.dlu_combo.currentText()),
            int(self.shelf_combo.currentText()),
            int(self.module_combo.currentData()),
        )
        super().accept()


class ReferenceDialog(QDialog):
    def __init__(self, ref: CardReference, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Hardware Reference · {ref.code}")
        self.resize(640, 450)
        layout = QVBoxLayout(self)

        title = QLabel(ref.display_name)
        title.setObjectName("Title")
        layout.addWidget(title)

        table = QTableWidget(0, 2)
        table.setHorizontalHeaderLabels(["Field", "Value"])
        table.horizontalHeader().setStretchLastSection(True)
        data = {
            "Type": ref.code,
            "Family": ref.family,
            "Role": ref.role,
            "Capacity": ref.port_count,
            "Port range": (
                f"{ref.port_start}..{ref.port_end}"
                if ref.port_count
                else "Not specified"
            ),
            "Subscriber type": ref.subscriber_type or "—",
            "Verified": "YES" if ref.verified else "NO",
            "Source ID": ref.source_id or "—",
            "Source": ref.source_title or "—",
            "Course page": ref.source_page or "—",
            "Source note": ref.source_note or "—",
        }
        for k, v in data.items():
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(str(k)))
            table.setItem(row, 1, QTableWidgetItem(str(v)))
        layout.addWidget(table)

        lesson = QLabel(
            "What the student should learn: identify the hardware role, "
            "capacity, placement address, and how the card affects subscriber/EQN state."
        )
        lesson.setWordWrap(True)
        lesson.setObjectName("Legend")
        layout.addWidget(lesson)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class CardLibraryList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item is None:
            return
        code = item.data(Qt.UserRole)
        if not code or code == "UNCONFIGURED":
            return
        mime = QMimeData()
        mime.setData("application/x-dlu-card", str(code).encode("utf-8"))
        mime.setText(str(code))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.CopyAction)

class CardLibraryDialog(QDialog):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Hardware Library")
        self.resize(950, 520)
        root = QVBoxLayout(self)
        list_widget = CardLibraryList()
        details = QTableWidget(0, 2)
        details.setHorizontalHeaderLabels(["Field", "Value"])
        details.horizontalHeader().setStretchLastSection(True)

        refs = self.db.list_card_references()
        for ref in refs:
            item = QListWidgetItem(
                f"{ref.code} · {ref.port_count}P · "
                f"{'VERIFIED' if ref.verified else 'UNVERIFIED'}"
            )
            item.setData(Qt.UserRole, ref.code)
            list_widget.addItem(item)

        split = QSplitter(Qt.Horizontal)
        split.addWidget(list_widget)
        split.addWidget(details)
        split.setSizes([360, 580])
        root.addWidget(split)

        def show_ref(item):
            code = item.data(Qt.UserRole)
            ref = self.db.get_card_reference(code)
            details.setRowCount(0)
            if not ref:
                return
            values = {
                "Type": ref.code,
                "Display": ref.display_name,
                "Family": ref.family,
                "Role": ref.role,
                "Ports": ref.port_count,
                "Range": (
                    f"{ref.port_start}..{ref.port_end}"
                    if ref.port_count else "Not specified"
                ),
                "Source": ref.source_title or "—",
                "Page": ref.source_page or "—",
                "Verified": "YES" if ref.verified else "NO",
            }
            for k, v in values.items():
                row = details.rowCount()
                details.insertRow(row)
                details.setItem(row, 0, QTableWidgetItem(str(k)))
                details.setItem(row, 1, QTableWidgetItem(str(v)))

        list_widget.currentItemChanged.connect(
            lambda current, _previous: show_ref(current) if current else None
        )

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)


class DluSimulatorWindow(QMainWindow):
    def __init__(self, db_path: str | Path):
        super().__init__()
        self.db = Database(db_path)
        self.mml = MmlEngine(self.db)
        self.call_engine = CallEngine(self.db)
        self.history: list[str] = []
        self.history_index = 0
        self.current_view = "home"
        self.mode = "physical"
        self.selected_eqn: str | None = None
        self.selected_dn: str | None = None

        self.setWindowTitle("DLU Lab — Siemens EWSD Educational Simulator")
        self.resize(1580, 940)
        self.setMinimumSize(1250, 760)
        self._build_ui()
        self._apply_style()
        self.show_hardware_home()
        self.refresh_status()
        self.terminal.append(
            "<span style='color:#7e96aa'>DLU Lab ready. "
            "Hardware-first mode active. Type &gt; help;</span>"
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
        h.addWidget(title)
        h.addWidget(QLabel("Siemens EWSD · Hardware-first training lab"))
        h.addStretch()
        h.addWidget(QLabel("ALE1 · DLU"))
        self.dlu_combo = QComboBox()
        for row in self.db.list_dlus():
            self.dlu_combo.addItem(str(row["dlu_id"]))
        self.dlu_combo.currentTextChanged.connect(
            lambda value: self.show_dlu(int(value)) if value else None
        )
        h.addWidget(self.dlu_combo)

        self.physical_btn = QPushButton("PHYSICAL")
        self.logical_btn = QPushButton("LOGICAL")
        self.physical_btn.clicked.connect(lambda: self.set_mode("physical"))
        self.logical_btn.clicked.connect(lambda: self.set_mode("logical"))
        h.addWidget(self.physical_btn)
        h.addWidget(self.logical_btn)

        self.status_chip = QLabel("SYSTEM ACT")
        self.status_chip.setObjectName("StatusChip")
        h.addWidget(self.status_chip)
        main.addWidget(header)

        self.syp = QFrame()
        self.syp.setObjectName("SYP")
        syp = QHBoxLayout(self.syp)
        syp.setContentsMargins(10, 5, 10, 5)
        self.crit_label = QLabel("CRITICAL 0")
        self.major_label = QLabel("MAJOR 0")
        self.minor_label = QLabel("MINOR 0")
        self.traffic_label = QLabel("PDC 0/120")
        self.path_label = QLabel("PATH —")
        for widget in (
            self.crit_label, self.major_label, self.minor_label,
            self.traffic_label, self.path_label
        ):
            syp.addWidget(widget)
        syp.addStretch()
        main.addWidget(self.syp)

        split = QSplitter(Qt.Horizontal)
        split.setChildrenCollapsible(False)
        main.addWidget(split, 1)

        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        self.back_btn = QPushButton("←")
        self.back_btn.setToolTip("Back to the previous hardware level")
        self.back_btn.clicked.connect(self.go_back)
        toolbar.addWidget(self.back_btn)

        self.breadcrumb = QLabel("Hardware Selection")
        self.breadcrumb.setObjectName("Breadcrumb")
        toolbar.addWidget(self.breadcrumb, 1)

        tool_btn = QToolButton()
        tool_btn.setText("TOOLS")
        tool_btn.setPopupMode(QToolButton.InstantPopup)
        tool_menu = QMenu(self)
        library_action = tool_menu.addAction("Hardware Library")
        library_action.triggered.connect(self.open_library)
        reset_action = tool_menu.addAction("Reset Demo")
        reset_action.triggered.connect(self.reset_demo)
        tool_btn.setMenu(tool_menu)
        toolbar.addWidget(tool_btn)

        fit_btn = QPushButton("FIT")
        fit_btn.setToolTip("Fit hardware to view")
        fit_btn.clicked.connect(lambda: self.hardware.reset_zoom())
        toolbar.addWidget(fit_btn)
        ll.addLayout(toolbar)

        navigator = QFrame()
        navigator.setObjectName("Navigator")
        nav = QHBoxLayout(navigator)
        nav.setContentsMargins(10, 8, 10, 8)
        nav.setSpacing(7)

        nav_title = QLabel("PATH")
        nav_title.setObjectName("NavigatorTitle")
        nav.addWidget(nav_title)

        self.nav_dlu_combo = QComboBox()
        for row in self.db.list_dlus():
            self.nav_dlu_combo.addItem(str(row["dlu_id"]))
        self.nav_dlu_combo.setToolTip("Choose DLU")
        nav.addWidget(QLabel("DLU"))
        nav.addWidget(self.nav_dlu_combo)

        nav.addWidget(QLabel("SHELF"))
        self.nav_shelf_combo = QComboBox()
        self.nav_shelf_combo.addItems([str(i) for i in range(8)])
        nav.addWidget(self.nav_shelf_combo)

        nav.addWidget(QLabel("MODULE"))
        self.nav_module_combo = QComboBox()
        nav.addWidget(self.nav_module_combo, 1)

        go_btn = QPushButton("OPEN MODULE")
        go_btn.clicked.connect(self.open_selected_module)
        nav.addWidget(go_btn)

        self.nav_dlu_combo.currentTextChanged.connect(
            lambda _: self.refresh_nav_modules()
        )
        self.nav_shelf_combo.currentTextChanged.connect(
            lambda _: self.refresh_nav_modules()
        )
        nav_menu_btn = QToolButton()
        nav_menu_btn.setText("NAV")
        nav_menu_btn.setPopupMode(QToolButton.InstantPopup)
        nav_menu = QMenu(self)
        nav_dlu_action = nav_menu.addAction("Open DLU")
        nav_dlu_action.triggered.connect(self.open_selected_dlu)
        nav_shelf_action = nav_menu.addAction("Open Shelf")
        nav_shelf_action.triggered.connect(self.open_selected_shelf)
        nav_module_action = nav_menu.addAction("Open Module")
        nav_module_action.triggered.connect(self.open_selected_module)
        nav_menu_btn.setMenu(nav_menu)
        nav.addWidget(nav_menu_btn)

        ll.addWidget(navigator)
        self.refresh_nav_modules()

        scenarios = QFrame()
        scenarios.setObjectName("ScenarioBar")
        scenario_layout = QHBoxLayout(scenarios)
        scenario_layout.setContentsMargins(10, 8, 10, 8)
        scenario_layout.setSpacing(8)

        scenario_title = QLabel("LAB ACTIONS")
        scenario_title.setObjectName("ScenarioTitle")
        scenario_layout.addWidget(scenario_title)

        primary8 = QPushButton("8-LINE LAB")
        primary8.setObjectName("PrimaryScenario")
        primary8.clicked.connect(self.run_8_line)
        primary8.setToolTip("Create eight subscriber lines on an SLMA8")
        scenario_layout.addWidget(primary8)

        primary_cmrl = QPushButton("CMRL LAB")
        primary_cmrl.setObjectName("PrimaryScenario")
        primary_cmrl.clicked.connect(self.run_cmrl)
        primary_cmrl.setToolTip("Demonstrate the six-port CMRL capacity guard")
        scenario_layout.addWidget(primary_cmrl)

        maintenance_btn = QPushButton("MAINTENANCE")
        maintenance_btn.clicked.connect(self.run_maintenance_demo)
        scenario_layout.addWidget(maintenance_btn)

        inspect_btn = QPushButton("INSPECT")
        inspect_btn.clicked.connect(self.run_inspect)
        scenario_layout.addWidget(inspect_btn)
        scenario_layout.addStretch()
        ll.addWidget(scenarios)

        self.hardware = HardwareView()
        self.hardware.controller = self
        ll.addWidget(self.hardware, 1)

        self.legend = QLabel(
            "Hardware: gray=unconfigured · steel=inactive · green=ACT · "
            "yellow=MBL · red=fault · blue=test | "
            "Ports: gray=unassigned · green=idle · red=busy · yellow=blocked"
        )
        self.legend.setObjectName("Legend")
        ll.addWidget(self.legend)
        split.addWidget(left)

        right = QTabWidget()
        self.omt_tab = QWidget()
        olt = QVBoxLayout(self.omt_tab)
        olt.setContentsMargins(10, 10, 10, 10)
        olt.setSpacing(8)

        omt_header = QFrame()
        omt_header.setObjectName("WorkbenchHeader")
        omt_head = QHBoxLayout(omt_header)
        omt_head.addWidget(QLabel("OMT"))
        omt_head.addWidget(QLabel("Operations & Maintenance"), 1)
        omt_head.addWidget(QLabel("LIVE"), 0, Qt.AlignRight)
        olt.addWidget(omt_header)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setObjectName("Terminal")
        self.terminal.setMinimumHeight(180)
        olt.addWidget(self.terminal, 1)

        command_dock = QFrame()
        command_dock.setObjectName("CommandDock")
        command_layout = QHBoxLayout(command_dock)
        command_layout.setContentsMargins(10, 8, 10, 8)
        command_layout.setSpacing(8)

        prompt = QLabel(">")
        prompt.setObjectName("CommandPrompt")
        command_layout.addWidget(prompt)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type MML: > statport: eqn=50-0-15-0;")
        self.input.setMinimumHeight(42)
        self.input.returnPressed.connect(self.execute_input)
        self.input.installEventFilter(self)
        command_layout.addWidget(self.input, 1)

        execute_btn = QPushButton("SEND")
        execute_btn.setObjectName("CommandSend")
        execute_btn.setMinimumHeight(42)
        execute_btn.clicked.connect(self.execute_input)
        command_layout.addWidget(execute_btn)

        olt.addWidget(command_dock)
        self.omt_tab.setLayout(olt)
        right.addTab(self.omt_tab, "OMT")

        self.call_lab = CallLabWidget(
            self.call_engine,
            on_state_changed=self._on_call_state_changed,
            parent=self,
        )
        right.addTab(self.call_lab, "Call Path")

        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        self.details = QTableWidget(0, 2)
        self.details.setHorizontalHeaderLabels(["Field", "Value"])
        self.details.horizontalHeader().setStretchLastSection(True)
        info_layout.addWidget(self.details, 1)
        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setMaximumHeight(150)
        self.event_log.setObjectName("Terminal")
        info_layout.addWidget(self.event_log)

        buttons = QHBoxLayout()
        for label, handler in (
            ("COPY MML", self.copy_selected_mml),
            ("REFERENCE", self.open_selected_reference),
            ("FAULT", self.inject_selected_fault),
            ("DIAG", self.diagnose_selected),
            ("REMOVE", self.remove_selected_card),
            ("INSTALL", self.install_selected_card),
            ("ACTIVATE", self.activate_selected_card),
        ):
            b = QPushButton(label)
            b.clicked.connect(handler)
            buttons.addWidget(b)
        info_layout.addLayout(buttons)
        info_tab.setLayout(info_layout)
        right.addTab(info_tab, "Hardware")

        split.addWidget(right)
        split.setSizes([1060, 500])

        self.nav_dlu_combo.currentTextChanged.connect(
            lambda _: self.sync_header_dlu()
        )

    def _apply_style(self):
        self.setStyleSheet(
            f"""
            QWidget {{
                background:{BG};
                color:{TEXT};
                font-family:Segoe UI;
                font-size:13px;
            }}
            QMainWindow {{
                background:{BG};
            }}
            QFrame#Header {{
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {PANEL}, stop:0.62 {PANEL3}, stop:1 #0d2034);
                border:1px solid #31516d;
                border-radius:12px;
            }}
            QFrame#SYP, QFrame#Navigator, QFrame#ScenarioBar, QFrame#WorkbenchHeader,
            QFrame#CommandDock {{
                background:{PANEL};
                border:1px solid {BORDER};
                border-radius:10px;
            }}
            QLabel#Title {{
                font-size:26px;
                font-weight:900;
                letter-spacing:1px;
            }}
            QLabel#Breadcrumb {{
                color:{TEXT};
                font-size:14px;
                font-weight:800;
                padding-left:6px;
            }}
            QLabel#NavigatorTitle {{
                color:{CYAN};
                font-weight:900;
                letter-spacing:1px;
            }}
            QLabel#ScenarioTitle {{
                color:{CYAN};
                font-weight:900;
                letter-spacing:1px;
            }}
            QLabel#Legend {{
                color:{MUTED};
                padding:3px 6px;
            }}
            QLabel#StatusChip {{
                background:#092e28;
                color:{GREEN};
                border:1px solid #31b989;
                border-radius:14px;
                padding:6px 12px;
                font-weight:900;
            }}
            QLabel#CommandPrompt {{
                color:{CYAN};
                font-size:18px;
                font-weight:900;
            }}
            QFrame#WorkbenchHeader QLabel {{
                color:{MUTED};
                font-weight:700;
            }}
            QFrame#WorkbenchHeader QLabel:first-child {{
                color:{TEXT};
                font-size:16px;
                font-weight:900;
            }}
            QFrame#CommandDock {{
                background:#091a2a;
                border:1px solid #3b79a5;
            }}
            QPushButton, QToolButton {{
                background:#0f2133;
                border:1px solid #2d4e69;
                border-radius:8px;
                padding:8px 12px;
                color:{TEXT};
                font-weight:700;
            }}
            QPushButton:hover, QToolButton:hover {{
                background:#16334b;
                border-color:{CYAN};
            }}
            QPushButton:pressed, QToolButton:pressed {{
                background:#1a3f5c;
            }}
            QPushButton:disabled {{
                color:#536a7d;
                background:#0a151f;
                border-color:#1b3042;
            }}
            QPushButton#PrimaryScenario {{
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #12354d, stop:1 #19385a);
                border:1px solid {CYAN};
                min-width:120px;
                padding:10px 14px;
                font-weight:900;
            }}
            QPushButton#PrimaryScenario:hover {{
                background:#1a4864;
            }}
            QPushButton#CommandSend {{
                background:#123e55;
                border:1px solid {CYAN};
                min-width:88px;
                font-weight:900;
            }}
            QComboBox {{
                background:#091b2b;
                border:1px solid #2e4f69;
                border-radius:8px;
                padding:7px 9px;
                min-height:28px;
            }}
            QComboBox:hover {{
                border-color:{CYAN};
            }}
            QLineEdit {{
                background:#061421;
                border:1px solid #2f5875;
                border-radius:8px;
                padding:8px 10px;
                color:{TEXT};
            }}
            QLineEdit:focus {{
                border:2px solid {CYAN};
                background:#071a2b;
            }}
            QComboBox, QLineEdit, QTextEdit, QTableWidget, QListWidget {{
                selection-background-color:#164764;
                selection-color:{WHITE};
            }}
            QTextEdit#Terminal {{
                background:#061421;
                border:1px solid #203d56;
                border-radius:9px;
                font-family:Cascadia Mono, Consolas, monospace;
                font-size:12px;
                padding:10px;
            }}
            QTableWidget {{
                background:#081723;
                border:1px solid {BORDER};
                gridline-color:#1e3548;
            }}
            QHeaderView::section {{
                background:#10283b;
                color:{TEXT};
                border:0;
                padding:7px;
                font-weight:800;
            }}
            QTabWidget::pane {{
                background:{PANEL2};
                border:1px solid {BORDER};
                border-radius:9px;
            }}
            QTabBar::tab {{
                background:#0b1a29;
                color:{MUTED};
                border:1px solid #233f57;
                border-bottom:0;
                padding:9px 16px;
                margin-right:3px;
                border-top-left-radius:8px;
                border-top-right-radius:8px;
                font-weight:800;
            }}
            QTabBar::tab:selected {{
                background:#12344a;
                color:{TEXT};
                border-color:{CYAN};
            }}
            QMenu {{
                background:#0b1724;
                color:{TEXT};
                border:1px solid {BORDER};
            }}
            QMenu::item:selected {{
                background:#12364c;
            }}
            QSplitter::handle {{
                background:#091522;
            }}
            """
        )

    def set_mode(self, mode: str):
        self.mode = mode
        self._refresh_current_view()
        self.physical_btn.setEnabled(mode != "physical")
        self.logical_btn.setEnabled(mode != "logical")

    def sync_header_dlu(self):
        text = self.nav_dlu_combo.currentText()
        if text:
            self.dlu_combo.blockSignals(True)
            self.dlu_combo.setCurrentText(text)
            self.dlu_combo.blockSignals(False)

    def refresh_nav_modules(self):
        if not self.nav_dlu_combo.currentText() or not self.nav_shelf_combo.currentText():
            return
        dlu = int(self.nav_dlu_combo.currentText())
        shelf = int(self.nav_shelf_combo.currentText())
        current = self.nav_module_combo.currentData()
        self.nav_module_combo.blockSignals(True)
        self.nav_module_combo.clear()
        for row in self.db.list_shelf(dlu, shelf):
            self.nav_module_combo.addItem(
                f"{row['module']} · {row['card_type']} · {row['port_count']}P",
                row["module"],
            )
        if current is not None:
            for i in range(self.nav_module_combo.count()):
                if self.nav_module_combo.itemData(i) == current:
                    self.nav_module_combo.setCurrentIndex(i)
                    break
        self.nav_module_combo.blockSignals(False)

    def open_selected_dlu(self):
        if self.nav_dlu_combo.currentText():
            self.show_dlu(int(self.nav_dlu_combo.currentText()))

    def open_selected_shelf(self):
        if self.nav_dlu_combo.currentText() and self.nav_shelf_combo.currentText():
            self.show_shelf(
                int(self.nav_dlu_combo.currentText()),
                int(self.nav_shelf_combo.currentText()),
            )

    def open_selected_module(self):
        if self.nav_module_combo.currentData() is not None:
            self.show_module(
                int(self.nav_dlu_combo.currentText()),
                int(self.nav_shelf_combo.currentText()),
                int(self.nav_module_combo.currentData()),
            )

    def clear_scene(self):
        self.hardware.scene_obj.clear()
        self.hardware.resetTransform()

    def add_text(self, x, y, text, size=12, color=TEXT, bold=False):
        item = self.hardware.scene_obj.addText(text)
        font = QFont("Segoe UI", max(1, int(size)))
        font.setBold(bold)
        item.setFont(font)
        item.setDefaultTextColor(QColor(color))
        item.setPos(x, y)
        return item

    def show_hardware_home(self):
        self.current_view = "home"
        self.clear_scene()
        self.back_btn.setEnabled(False)
        self.breadcrumb.setText("HARDWARE FLEET")
        self.add_text(30, 18, "EWSD HARDWARE LAB", 26, TEXT, True)
        self.add_text(
            30, 54,
            "Choose a DLU chassis, then explore Shelf → Module → Port.",
            12, MUTED
        )

        scene = self.hardware.scene_obj
        # Subtle space texture.
        for i in range(38):
            x = 25 + ((i * 137) % 1060)
            y = 92 + ((i * 83) % 590)
            size = 2 + (i % 3)
            scene.addEllipse(
                QRectF(x, y, size, size),
                QPen(QColor("#183249")),
                QBrush(QColor("#183249")),
            )

        card_w, card_h = 202, 126
        cols = 4
        x0, y0 = 30, 105
        for i, row in enumerate(self.db.list_dlus()):
            rr = i // cols
            cc = i % cols
            x = x0 + cc * (card_w + 18)
            y = y0 + rr * (card_h + 18)
            active = row["dluc0_state"] == "act" or row["dluc1_state"] == "act"
            status = "SYSTEM ACT" if active else "DEGRADED"
            accent = GREEN if active else YELLOW

            # Visual rack/card shell.
            shell = rounded_path(x, y, card_w, card_h, 12)
            scene.addPath(
                shell,
                QPen(QColor("#36526d"), 1.8),
                QBrush(QColor("#0b1a28")),
            )
            rail = QPainterPath()
            rail.addRoundedRect(QRectF(x + 7, y + 9, 8, card_h - 18), 4, 4)
            scene.addPath(
                rail,
                QPen(QColor(accent), 1),
                QBrush(QColor(accent)),
            )
            add_rack_rivets(scene, x + 14, y + 8, card_w - 28, 4)

            # Mini shelves to communicate this is hardware, not a generic card.
            for shelf in range(4):
                sy = y + 58 + shelf * 12
                scene.addRoundedRect(
                    QRectF(x + 98, sy, 82, 7),
                    2, 2,
                    QPen(QColor("#29465e"), 0.8),
                    QBrush(QColor("#102435")),
                )

            item = ClickableRectItem(
                QRectF(x, y, card_w, card_h),
                lambda value: self.show_dlu(value),
                row["dlu_id"],
                f"DLU {row['dlu_id']} · DLUC0 {row['dluc0_state']} · DLUC1 {row['dluc1_state']}",
            )
            item.setBrush(Qt.NoBrush)
            item.setPen(Qt.NoPen)
            scene.addItem(item)

            self.add_text(x + 28, y + 18, f"DLU {row['dlu_id']}", 18, TEXT, True)
            self.add_text(x + 28, y + 44, "DIGITAL LINE UNIT", 9, MUTED, True)
            scene.addEllipse(
                QRectF(x + 28, y + 78, 10, 10),
                QPen(QColor(accent), 1),
                QBrush(QColor(accent)),
            )
            self.add_text(x + 46, y + 72, status, 9, accent, True)
            self.add_text(
                x + 28, y + 95,
                f"DLUC0 {row['dluc0_state'].upper()} · DLUC1 {row['dluc1_state'].upper()}",
                8, MUTED,
            )

        rows = (25 + cols - 1) // cols
        scene.setSceneRect(0, 0, 930, y0 + rows * (card_h + 18) + 35)
        self.hardware.reset_zoom()
        self._set_details({
            "Mode": "Physical",
            "Hardware": "DLU fleet",
            "DLU count": 25,
            "Range": "10..250",
            "Hierarchy": "DLU → Shelf → Module → Port",
        })


    def _sync_location(self, dlu: int, shelf: int | None = None, module: int | None = None):
        self.hardware.current_dlu = dlu
        if shelf is not None:
            self.hardware.current_shelf = shelf
        if module is not None:
            self.hardware.current_module = module
        self.nav_dlu_combo.blockSignals(True)
        self.nav_dlu_combo.setCurrentText(str(dlu))
        self.nav_dlu_combo.blockSignals(False)
        if shelf is not None:
            self.nav_shelf_combo.blockSignals(True)
            self.nav_shelf_combo.setCurrentText(str(shelf))
            self.nav_shelf_combo.blockSignals(False)
        self.refresh_nav_modules()
        if module is not None:
            for i in range(self.nav_module_combo.count()):
                if self.nav_module_combo.itemData(i) == module:
                    self.nav_module_combo.setCurrentIndex(i)
                    break
        self.sync_header_dlu()

    def open_hardware_context(self, data):
        if not isinstance(data, tuple):
            return
        if len(data) == 3:
            dlu, shelf, module = data
            menu = QMenu(self)
            display_action = menu.addAction("Display Module")
            reference_action = menu.addAction("Reference")
            maintenance_action = menu.addAction("Maintenance")
            action = menu.exec(self.cursor().pos())
            if action is display_action:
                self.show_module(dlu, shelf, module)
            elif action is reference_action:
                self.show_module(dlu, shelf, module)
                self.open_selected_reference()
            elif action is maintenance_action:
                self.show_module(dlu, shelf, module)
                self.run_maintenance_demo()
        elif len(data) == 4:
            self.port_context(*data)

    def show_dlu(self, dlu_id: int):
        self._sync_location(dlu_id)
        self.current_view = "dlu"
        self.clear_scene()
        self.back_btn.setEnabled(True)
        self.breadcrumb.setText(f"DLU {dlu_id}")
        if self.mode == "logical":
            self.draw_logical_dlu(dlu_id)
        else:
            self.draw_physical_dlu(dlu_id)
        self.refresh_status()

    def draw_physical_dlu(self, dlu_id: int):
        dlu = self.db.get_dlu(dlu_id)
        scene = self.hardware.scene_obj
        self.add_text(34, 18, f"DLU {dlu_id}", 26, TEXT, True)
        self.add_text(
            34, 52,
            "DIGITAL LINE UNIT · 8 SHELVES · 16 MODULE POSITIONS / SHELF",
            11, MUTED, True
        )

        chassis = rounded_path(24, 86, 1060, 790, 18)
        scene.addPath(
            chassis,
            QPen(QColor("#35516c"), 2.2),
            QBrush(QColor("#091521")),
        )
        # Rack rails.
        scene.addRoundedRect(
            QRectF(36, 102, 12, 754),
            5, 5,
            QPen(QColor("#304c64")),
            QBrush(QColor("#13263a")),
        )
        scene.addRoundedRect(
            QRectF(1060, 102, 12, 754),
            5, 5,
            QPen(QColor("#304c64")),
            QBrush(QColor("#13263a")),
        )
        add_rack_rivets(scene, 54, 98, 1010, 4)

        # Identification plate.
        plate = rounded_path(62, 108, 360, 78, 10)
        scene.addPath(
            plate,
            QPen(QColor("#3a5e7c"), 1.4),
            QBrush(QColor("#0e2132")),
        )
        self.add_text(82, 122, f"DLU {dlu_id} · SYSTEM RACK", 14, TEXT, True)
        self.add_text(82, 148, "SIEMENS EWSD TRAINING CHASSIS", 9, CYAN, True)
        self.add_text(
            82, 166,
            f"DLUC0 {dlu['dluc0_state'].upper()} · DLUC1 {dlu['dluc1_state'].upper()}",
            8, GREEN if dlu["dluc0_state"] == "act" else YELLOW, True
        )

        # Controller / interface section.
        control_y = 112
        for idx, (label, state) in enumerate((
            ("DLUC0", dlu["dluc0_state"]),
            ("DLUC1", dlu["dluc1_state"]),
        )):
            x = 450 + idx * 150
            shell = rounded_path(x, control_y, 132, 70, 9)
            accent = state_color(state)
            scene.addPath(
                shell,
                QPen(QColor(accent), 1.5),
                QBrush(QColor("#0e1e2c")),
            )
            self.add_text(x + 12, control_y + 10, label, 10, TEXT, True)
            self.add_text(x + 12, control_y + 34, state.upper(), 11, accent, True)
            scene.addEllipse(
                QRectF(x + 102, control_y + 13, 10, 10),
                QPen(QColor(accent)),
                QBrush(QColor(accent)),
            )

        for i, name in enumerate(["DIUD0", "DIUD1", "PDC0", "PDC1"]):
            x = 760 + i * 74
            shell = rounded_path(x, 126, 64, 44, 6)
            scene.addPath(
                shell,
                QPen(QColor("#29455d"), 1),
                QBrush(QColor("#0c1a27")),
            )
            self.add_text(x + 7, 138, name, 7, BLUE if name.startswith("DIUD") else MUTED, True)
            scene.addEllipse(
                QRectF(x + 45, 138, 7, 7),
                QPen(QColor(CYAN)),
                QBrush(QColor(CYAN)),
            )

        for shelf in range(8):
            self.draw_shelf_strip(dlu_id, shelf, 54, 212 + shelf * 78)

        scene.setSceneRect(0, 0, 1110, 905)
        self.hardware.reset_zoom()

        self._set_details({
            "DLU": dlu_id,
            "Controller 0": dlu["dluc0_state"],
            "Controller 1": dlu["dluc1_state"],
            "Shelves": "0..7",
            "Modules/Shelf": "0..15",
            "View": "Physical Rack",
        })


    def draw_shelf_strip(self, dlu_id: int, shelf: int, x: float, y: float):
        scene = self.hardware.scene_obj
        label_color = CYAN if shelf == self.hardware.current_shelf else MUTED

        self.add_text(x, y + 14, f"SHELF {shelf}", 9, label_color, True)

        base = rounded_path(x + 72, y, 970, 62, 8)
        scene.addPath(
            base,
            QPen(QColor("#314e67"), 1.2),
            QBrush(QColor("#0c1b29")),
        )
        scene.addRoundedRect(
            QRectF(x + 80, y + 8, 7, 46),
            3, 3,
            QPen(QColor(label_color)),
            QBrush(QColor(label_color)),
        )
        add_rack_rivets(scene, x + 94, y + 5, 940, 5)

        slots = self.db.list_shelf(dlu_id, shelf)
        for slot in slots:
            mx = x + 96 + slot["module"] * 58
            configured = slot["card_type"] != "UNCONFIGURED"
            fault = slot["fault_state"] == "fault"
            accent = RED if fault else (GREEN if configured else "#31485d")
            fill = "#102a2b" if configured else "#0a1722"
            if fault:
                fill = "#2d1820"

            visual = rounded_path(mx, y + 10, 52, 42, 5)
            scene.addPath(
                visual,
                QPen(QColor(accent), 1.1),
                QBrush(QColor(fill)),
            )
            scene.addLine(
                mx + 7, y + 18, mx + 45, y + 18,
                QPen(QColor("#38546c"), 1),
            )
            scene.addEllipse(
                QRectF(mx + 7, y + 28, 6, 6),
                QPen(QColor(accent)),
                QBrush(QColor(accent)),
            )
            self.add_text(mx + 18, y + 24, str(slot["module"]), 7, TEXT, True)

            item = ClickableRectItem(
                QRectF(mx, y + 10, 52, 42),
                lambda data: self.show_module(*data),
                (dlu_id, shelf, slot["module"]),
                f"{dlu_id}-{shelf}-{slot['module']} · {slot['card_type']} · {slot['port_count']} ports",
                on_double_click=lambda data: self.show_module(*data),
                on_context=lambda data: self.open_hardware_context(data),
            )
            item.setBrush(Qt.NoBrush)
            item.setPen(Qt.NoPen)
            scene.addItem(item)


    def draw_logical_dlu(self, dlu_id: int):
        dlu = self.db.get_dlu(dlu_id)
        self.add_text(24, 20, f"DLU {dlu_id} · LOGICAL VIEW", 22, TEXT, True)
        nodes = [
            ("DLU", 60, 110, f"DLU {dlu_id}"),
            ("DLUC0", 270, 60, dlu["dluc0_state"].upper()),
            ("DLUC1", 270, 190, dlu["dluc1_state"].upper()),
            ("DIUD", 500, 110, "DIGITAL INTERFACE"),
            ("SLM", 730, 110, "SUBSCRIBER MODULE"),
            ("PORT", 930, 110, "PORT / EQN"),
        ]
        for kind, x, y, label in nodes:
            node_path = QPainterPath()
            node_path.addRoundedRect(QRectF(x, y, 160, 72), 8, 8)
            self.hardware.scene_obj.addPath(
                node_path,
                QPen(QColor("#365168"), 1.6),
                QBrush(QColor("#13232e")),
            )
            self.add_text(x+12, y+11, kind, 10, BLUE if kind in {"DIUD","PORT"} else GREEN, True)
            self.add_text(x+12, y+38, label, 9, TEXT)
        lines = [
            ((220, 146), (270, 96)),
            ((220, 146), (270, 226)),
            ((430, 96), (500, 146)),
            ((430, 226), (500, 146)),
            ((660, 146), (730, 146)),
            ((890, 146), (930, 146)),
        ]
        for (x1,y1),(x2,y2) in lines:
            self.hardware.scene_obj.addLine(
                x1,y1,x2,y2,QPen(QColor("#4b6e87"),2)
            )
        self.add_text(
            60, 330,
            "Logical mode explains relationships; Physical mode explains equipment.",
            12, MUTED
        )
        self.hardware.scene_obj.setSceneRect(0, 0, 1150, 480)
        self.hardware.reset_zoom()
        self._set_details({
            "DLU":dlu_id,
            "Mode":"Logical",
            "DLUC0":dlu["dluc0_state"],
            "DLUC1":dlu["dluc1_state"],
            "Flow":"DLU → Controller → DIUD → SLM → Port → DN",
        })

    def show_shelf(self, dlu_id: int, shelf: int):
        self._sync_location(dlu_id, shelf)
        self.current_view = "shelf"
        self.clear_scene()
        self.back_btn.setEnabled(True)
        self.breadcrumb.setText(f"DLU {dlu_id} / Shelf {shelf}")
        self.add_text(24, 18, f"DLU {dlu_id} · SHELF {shelf}", 22, TEXT, True)
        self.add_text(24, 52, "16 physical module positions", 11, MUTED)
        rack = QRectF(20, 90, 1060, 700)
        self.hardware.scene_obj.addRect(
            rack, QPen(QColor("#3a5265"),2),
            QBrush(QColor("#0e1820"))
        )
        slots = self.db.list_shelf(dlu_id, shelf)
        for i, slot in enumerate(slots):
            row = i // 8
            col = i % 8
            x = 45 + col * 125
            y = 125 + row * 290
            self.draw_full_module_slot(slot, x, y, 108, 250)
        self.hardware.scene_obj.setSceneRect(0,0,1110,820)
        self.hardware.reset_zoom()
        self._set_details({
            "DLU":dlu_id,
            "Shelf":shelf,
            "Positions":"Module 0..15",
            "View":"Physical Shelf",
        })

    def draw_full_module_slot(self, slot, x, y, w, h):
        configured = slot["card_type"] != "UNCONFIGURED"
        edge = RED if slot["fault_state"] == "fault" else (GREEN if configured else BORDER)
        fill = "#17252e" if not configured else "#143029"
        body = QRectF(x,y,w,h)
        item = ClickableRectItem(
            body,
            lambda data: self.show_module(*data),
            (slot["dlu_id"],slot["shelf"],slot["module"]),
            f"Module {slot['module']} · {slot['card_type']}",
        )
        item.setBrush(QBrush(QColor(fill)))
        item.setPen(QPen(QColor(edge),1.6))
        self.hardware.scene_obj.addItem(item)
        self.add_text(x+10,y+10,f"MODULE {slot['module']}",10,TEXT,True)
        self.add_text(x+10,y+35,slot["card_type"],11,edge,True)
        self.add_text(x+10,y+60,f"{slot['port_count']} PORTS",9,MUTED)
        self.add_text(x+10,y+84,f"OST {slot['ost'].upper()}",8,state_color(slot["ost"]),True)
        self.add_text(x+10,y+110,"FAULT" if slot["fault_state"]=="fault" else "NORMAL",8,RED if slot["fault_state"]=="fault" else GREEN,True)

        max_ports = min(slot["port_count"], 64)
        mini_cols = 8 if max_ports > 16 else 4
        mini_gap_x = 12 if max_ports > 16 else 24
        mini_gap_y = 18 if max_ports > 16 else 24
        for port in range(max_ports):
            px = x+10+(port%mini_cols)*mini_gap_x
            py = y+140+(port//mini_cols)*mini_gap_y
            sub = self.db.get_port_subscriber(slot["dlu_id"],slot["shelf"],slot["module"],port)
            col = state_color(sub["line_state"]) if sub else STEEL
            self.hardware.scene_obj.addEllipse(
                QRectF(px,py,12,12), QPen(QColor(col)), QBrush(QColor(col))
            )
            self.add_text(px-1,py+12,str(port),6,MUTED)

    def show_module(self, dlu_id: int, shelf: int, module: int):
        self._sync_location(dlu_id,shelf,module)
        self.current_view = "module"
        self.clear_scene()
        self.back_btn.setEnabled(True)
        self.breadcrumb.setText(f"DLU {dlu_id} / Shelf {shelf} / Module {module}")
        slot = self.db.get_slot(dlu_id,shelf,module)
        if slot is None:
            self.add_text(24,24,"Module not found",18,RED,True)
            return
        self.add_text(24,18,f"MODULE {module} · {slot.card_type}",22,TEXT,True)
        self.add_text(
            24,52,
            f"EQN base: {dlu_id}-{shelf}-{module} · {slot.role or 'Unconfigured'}",
            11,MUTED
        )

        # Card faceplate
        card = QRectF(40,100,430,690)
        self.hardware.scene_obj.addRect(
            card,QPen(QColor(GREEN if slot.card_type!="UNCONFIGURED" else BORDER),2),
            QBrush(QColor("#12202a"))
        )
        self.add_text(65,120,slot.card_type,20,WHITE,True)
        self.add_text(65,153,slot.role or "Empty slot",10,MUTED)
        self.add_text(65,181,f"CAPACITY: {slot.port_count}",10,TEXT,True)
        self.add_text(65,205,f"OST: {slot.ost.upper()}",10,state_color(slot.ost),True)
        self.add_text(
            65,230,
            f"FAULT: {slot.fault_state.upper()}",
            10,RED if slot.fault_state=="fault" else GREEN,True
        )

        if slot.card_type == "UNCONFIGURED":
            self.add_text(
                65,300,
                "UNCONFIGURED SLOT",
                15,YELLOW,True
            )
            self.add_text(
                65,330,
                "Install a verified card from Hardware Library.",
                10,MUTED
            )
        else:
            self.draw_port_grid(dlu_id,shelf,module,slot,65,280)

        if slot.source_id:
            ref = self.db.get_card_reference(slot.card_type)
            if ref:
                self.add_text(
                    65,710,
                    f"SOURCE: {ref.source_id} · page {ref.source_page}",
                    8,MUTED
                )

        rows_for_card = (
            ((slot.port_count + 7) // 8)
            if slot.port_count >= 32
            else ((slot.port_count + 3) // 4)
            if slot.port_count > 16
            else ((slot.port_count + 1) // 2)
            if slot.port_count
            else 1
        )
        scene_height = max(820, 280 + rows_for_card * 68)
        scene_width = 1120 if slot.port_count <= 16 else 1240
        self.hardware.scene_obj.setSceneRect(0,0,scene_width,scene_height)
        self.hardware.reset_zoom()

        self._set_details({
            "DLU":dlu_id,
            "Shelf":shelf,
            "Module":module,
            "Card":slot.card_type,
            "Role":slot.role,
            "Capacity":slot.port_count,
            "OST":slot.ost,
            "Fault":slot.fault_state,
            "EQN Base":f"{dlu_id}-{shelf}-{module}",
            "Source":slot.source_id or "—",
        })
        self.refresh_event_log()

    def draw_port_grid(self,dlu_id,shelf,module,slot,x,y):
        if slot.port_count >= 32:
            cols = 8
            cell_w = 96
        elif slot.port_count > 16:
            cols = 4
            cell_w = 156
        else:
            cols = 2
            cell_w = 160
        rows = (slot.port_count + cols - 1)//cols
        for port in range(slot.port_count):
            cell_h = 52
            px = x + (port % cols) * cell_w
            py = y + (port // cols) * (cell_h + 10)
            sub = self.db.get_port_subscriber(dlu_id,shelf,module,port)
            if not sub:
                color = STEEL
                label = "UNASSIGNED"
            else:
                color = state_color(sub["line_state"])
                label = sub["dn"]
                if sub["blk_reason"]:
                    color = YELLOW
            item = ClickableRectItem(
                QRectF(px,py,cell_w-6,cell_h),
                lambda data: self.select_port(*data),
                (dlu_id,shelf,module,port),
                f"EQN {dlu_id}-{shelf}-{module}-{port}",
            )
            item.setBrush(QBrush(QColor("#0d1820")))
            item.setPen(QPen(QColor(BORDER),1))
            self.hardware.scene_obj.addItem(item)
            self.hardware.scene_obj.addEllipse(
                QRectF(px+10,py+18,16,16),
                QPen(QColor(color)),QBrush(QColor(color))
            )
            self.add_text(px+35,py+7,f"PORT {port}",8,TEXT,True)
            self.add_text(px+35,py+24,label,8,color,True)
            self.add_text(px+35,py+40,f"{dlu_id}-{shelf}-{module}-{port}",6,MUTED)

    def port_context(self, dlu_id,shelf,module,port):
        eqn = f"{dlu_id}-{shelf}-{module}-{port}"
        menu = QMenu(self)
        inspect_action = menu.addAction("Inspect Port")
        copy_action = menu.addAction("Copy MML")
        action = menu.exec(self.cursor().pos())
        if action is inspect_action:
            self.show_module(dlu_id,shelf,module)
            self.select_port(dlu_id,shelf,module,port)
        elif action is copy_action:
            self.selected_eqn = eqn
            sub = self.db.get_port_subscriber(dlu_id,shelf,module,port)
            self.selected_dn = sub["dn"] if sub else None
            self.copy_selected_mml()

    def select_port(self,dlu_id,shelf,module,port):
        eqn = f"{dlu_id}-{shelf}-{module}-{port}"
        self.selected_eqn = eqn
        sub = self.db.get_port_subscriber(dlu_id,shelf,module,port)
        self.selected_dn = sub["dn"] if sub else None
        details = {
            "EQN":eqn,
            "Port":port,
            "Card":self.db.get_slot(dlu_id,shelf,module).card_type,
        }
        if sub:
            details.update({
                "DN":sub["dn"],
                "LAC":sub["lac"],
                "State":sub["line_state"],
                "Block":sub["blk_reason"] or "NORMAL",
                "Services":sub["cos_flags"] or "—",
                "MML":f"> statport: eqn={eqn};",
            })
        else:
            details["Status"]="UNASSIGNED"
            details["MML"]=f"> disp dlupport: eqn={eqn};"
        self._set_details(details)
        self.terminal.append(
            f"<span style='color:#59a6ff'>Selected {eqn}</span>"
        )

    def _set_details(self, details: dict):
        self.details.setRowCount(0)
        for k,v in details.items():
            row=self.details.rowCount()
            self.details.insertRow(row)
            self.details.setItem(row,0,QTableWidgetItem(str(k)))
            self.details.setItem(row,1,QTableWidgetItem(str(v)))

    def focus_result(self,result:MmlResult):
        data = result.data
        candidates = []
        if isinstance(data, dict):
            candidates = [data]
        elif isinstance(data, list):
            candidates = [x for x in data if isinstance(x,dict)]
        for item in candidates:
            if item.get("eqn"):
                eqn = item["eqn"]
                try:
                    dlu,shelf,module,port = map(int,eqn.split("-"))
                except ValueError:
                    continue
                self.show_module(dlu,shelf,module)
                self.select_port(dlu,shelf,module,port)
                return
            if all(k in item for k in ("dlu","shelf","module")):
                self.show_module(int(item["dlu"]),int(item["shelf"]),int(item["module"]))
                return

    def refresh_event_log(self):
        if not hasattr(self, "event_log"):
            return
        if self.current_view != "module":
            self.event_log.setPlainText("No module selected.")
            return
        rows = self.db.conn.execute(
            """
            SELECT event_type, old_card, new_card, note, created_at
            FROM hardware_events
            WHERE dlu_id=? AND shelf=? AND module=?
            ORDER BY event_id DESC
            LIMIT 12
            """,
            (
                self.hardware.current_dlu,
                self.hardware.current_shelf,
                self.hardware.current_module,
            ),
        ).fetchall()
        if not rows:
            self.event_log.setPlainText("Maintenance timeline: no events.")
            return
        lines = ["MAINTENANCE TIMELINE"]
        for row in rows:
            lines.append(
                f"{row['created_at']} · {row['event_type']} · "
                f"{row['old_card'] or '—'} → {row['new_card'] or '—'} · "
                f"{row['note'] or ''}"
            )
        self.event_log.setPlainText("\\n".join(lines))

    def execute_input(self):
        command=self.input.text().strip()
        if not command:
            return
        if not command.startswith(">"):
            command="> "+command
        self.history.append(command)
        self.history_index=len(self.history)
        self.input.clear()
        self._execute_command(command)

    def _execute_command(self,command:str):
        self.terminal.append(
            f"<span style='color:#dce8f2'>&gt; {command[1:].strip()}</span>"
        )
        result=self.mml.execute(command)
        color=GREEN if result.ok else RED
        self.terminal.append(
            f"<span style='color:{color}'>[{result.code}] {result.message}</span>"
        )
        if result.data is not None:
            pretty=json.dumps(result.data,ensure_ascii=False,indent=2,default=str)
            self.terminal.append(
                f"<pre style='color:#8fb2cf'>{pretty}</pre>"
            )
        self.focus_result(result)
        self.refresh_status()

    def copy_selected_mml(self):
        if not self.selected_eqn:
            return
        command = (
            f"> statport: eqn={self.selected_eqn};"
            if self.selected_dn else
            f"> disp dlupport: eqn={self.selected_eqn};"
        )
        QApplication.clipboard().setText(command)
        self.terminal.append(
            f"<span style='color:{GREEN}'>Copied: {command}</span>"
        )

    def open_selected_reference(self):
        card = None
        if self.current_view == "module":
            slot=self.db.get_slot(
                self.hardware.current_dlu,
                self.hardware.current_shelf,
                self.hardware.current_module
            )
            if slot:
                card=slot.card_type
        if card:
            ref=self.db.get_card_reference(card)
            if ref:
                ReferenceDialog(ref,self).exec()

    def open_library(self):
        if getattr(self, "library_dialog", None) is not None:
            self.library_dialog.raise_()
            self.library_dialog.activateWindow()
            return
        self.library_dialog = CardLibraryDialog(self.db, self)
        self.library_dialog.setWindowModality(Qt.NonModal)
        self.library_dialog.setAttribute(Qt.WA_DeleteOnClose, True)
        self.library_dialog.destroyed.connect(
            lambda: setattr(self, "library_dialog", None)
        )
        self.library_dialog.show()

    def inject_selected_fault(self):
        if self.current_view != "module":
            QMessageBox.information(self,"Select module","Open a module first.")
            return
        try:
            self.db.inject_fault(
                self.hardware.current_dlu,
                self.hardware.current_shelf,
                self.hardware.current_module
            )
            self.terminal.append(
                f"<span style='color:{YELLOW}'>Fault injected on "
                f"{self.hardware.current_dlu}-{self.hardware.current_shelf}-{self.hardware.current_module}</span>"
            )
            self._refresh_current_view()
        except ValueError as exc:
            QMessageBox.warning(self,"Fault",str(exc))

    def diagnose_selected(self):
        if self.current_view != "module":
            return
        dlu=self.hardware.current_dlu
        shelf=self.hardware.current_shelf
        module=self.hardware.current_module
        result=self.mml.execute(
            f"> diag dlumod: dlu={dlu}, shelf={shelf}, module={module};"
        )
        self._show_result(result)
        self._refresh_current_view()

    def remove_selected_card(self):
        if self.current_view != "module":
            return
        try:
            old=self.db.remove_card(
                self.hardware.current_dlu,
                self.hardware.current_shelf,
                self.hardware.current_module
            )
            self.terminal.append(
                f"<span style='color:{GREEN}'>Removed {old} from "
                f"{self.hardware.current_dlu}-{self.hardware.current_shelf}-{self.hardware.current_module}</span>"
            )
            self._refresh_current_view()
        except ValueError as exc:
            QMessageBox.warning(self,"Remove Card",str(exc))

    def install_card_at(self, dlu: int, shelf: int, module: int, card_type: str):
        slot = self.db.get_slot(dlu, shelf, module)
        if slot is None:
            QMessageBox.warning(self, "Install Card", "Target module does not exist.")
            return
        if slot.card_type != "UNCONFIGURED":
            QMessageBox.warning(
                self,
                "Install Card",
                f"Module {dlu}-{shelf}-{module} already contains {slot.card_type}.",
            )
            return
        ref = self.db.get_card_reference(card_type)
        if ref is None or not ref.verified:
            QMessageBox.warning(
                self,
                "Install Card",
                f"{card_type} is not in the verified hardware registry.",
            )
            return
        try:
            self.db.install_card(dlu, shelf, module, card_type)
            self.show_module(dlu, shelf, module)
            self.terminal.append(
                f"<span style='color:{GREEN}'>Drag&Drop installed "
                f"{card_type} at {dlu}-{shelf}-{module}</span>"
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Install Card", str(exc))

    def install_selected_card(self):
        if self.current_view != "module":
            return
        dialog=QDialog(self)
        dialog.setWindowTitle("Install verified replacement")
        form=QFormLayout(dialog)
        combo=QComboBox()
        for ref in self.db.list_card_references():
            if ref.verified and ref.code not in {"UNCONFIGURED"}:
                combo.addItem(
                    f"{ref.code} · {ref.port_count}P · {ref.role}",
                    ref.code
                )
        form.addRow("Card",combo)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addWidget(buttons)
        if dialog.exec()!=QDialog.Accepted:
            return
        try:
            card=combo.currentData()
            installed=self.db.install_card(
                self.hardware.current_dlu,
                self.hardware.current_shelf,
                self.hardware.current_module,
                card
            )
            self.terminal.append(
                f"<span style='color:{GREEN}'>Installed {installed} in "
                f"{self.hardware.current_dlu}-{self.hardware.current_shelf}-{self.hardware.current_module}</span>"
            )
            self._refresh_current_view()
        except ValueError as exc:
            QMessageBox.warning(self,"Install Card",str(exc))

    def activate_selected_card(self):
        if self.current_view != "module":
            return
        try:
            card=self.db.activate_card(
                self.hardware.current_dlu,
                self.hardware.current_shelf,
                self.hardware.current_module
            )
            self.terminal.append(
                f"<span style='color:{GREEN}'>Activated {card}</span>"
            )
            self._refresh_current_view()
        except ValueError as exc:
            QMessageBox.warning(self,"Activate",str(exc))

    def run_8_line(self):
        dialog=HardwareSelectorDialog(self.db,self,card_type="SLMA8")
        if dialog.exec()!=QDialog.Accepted or dialog.selected is None:
            return
        dlu,shelf,module=dialog.selected
        self.show_module(dlu,shelf,module)
        for i in range(8):
            command=(
                f"> cr sub: dlu={dlu}, type=ms, "
                f"eqn={dlu}-{shelf}-{module}-{i}, lac=021, dn={2233500+i};"
            )
            self._execute_command(command)

    def run_cmrl(self):
        dialog=HardwareSelectorDialog(self.db,self,card_type="CMRL")
        if dialog.exec()!=QDialog.Accepted or dialog.selected is None:
            return
        dlu,shelf,module=dialog.selected
        self.show_module(dlu,shelf,module)
        for i in range(6):
            self._execute_command(
                f"> cr sub: dlu={dlu}, type=cmrl, "
                f"eqn={dlu}-{shelf}-{module}-{i}, lac=021, dn={2250500+i};"
            )
        self._execute_command(
            f"> cr sub: dlu={dlu}, type=cmrl, "
            f"eqn={dlu}-{shelf}-{module}-6, lac=021, dn=2250506;"
        )
        self.terminal.append(
            "<span style='color:#e3a83b'>CMRL guard demo: next port 6 must be rejected.</span>"
        )

    def run_maintenance_demo(self):
        if self.current_view != "module":
            QMessageBox.information(
                self,"Maintenance",
                "Open a configured module, then use Maintenance."
            )
            return
        self.inject_selected_fault()

    def run_inspect(self):
        dlu=self.hardware.current_dlu
        shelf=self.hardware.current_shelf
        module=self.hardware.current_module
        self._execute_command(
            f"> disp dlumod: dlu={dlu}, shelf={shelf}, module={module};"
        )

    def _show_result(self,result:MmlResult):
        color=GREEN if result.ok else RED
        self.terminal.append(
            f"<span style='color:{color}'>[{result.code}] {result.message}</span>"
        )
        if result.data is not None:
            self.terminal.append(
                f"<pre style='color:#8fb2cf'>{json.dumps(result.data,ensure_ascii=False,indent=2,default=str)}</pre>"
            )
        self.focus_result(result)

    def _refresh_current_view(self):
        if self.current_view=="home":
            self.show_hardware_home()
        elif self.current_view=="dlu":
            self.show_dlu(self.hardware.current_dlu)
        elif self.current_view=="shelf":
            self.show_shelf(self.hardware.current_dlu,self.hardware.current_shelf)
        else:
            self.show_module(
                self.hardware.current_dlu,
                self.hardware.current_shelf,
                self.hardware.current_module
            )

    def eventFilter(self,watched,event):
        if watched is self.input and event.type()==QEvent.Type.KeyPress:
            if event.key()==Qt.Key_Up and self.history:
                self.history_index=max(0,self.history_index-1)
                self.input.setText(self.history[self.history_index])
                return True
            if event.key()==Qt.Key_Down and self.history:
                self.history_index=min(len(self.history),self.history_index+1)
                self.input.setText(
                    self.history[self.history_index]
                    if self.history_index<len(self.history) else ""
                )
                return True
        return super().eventFilter(watched,event)

    def go_back(self):
        if self.current_view=="module":
            self.show_shelf(self.hardware.current_dlu,self.hardware.current_shelf)
        elif self.current_view=="shelf":
            self.show_dlu(self.hardware.current_dlu)
        elif self.current_view=="dlu":
            self.show_hardware_home()
        else:
            self.show_hardware_home()

    def refresh_status(self):
        if not hasattr(self, "hardware") or self.hardware.scene() is None:
            return
        current=self.db.get_dlu(self.hardware.current_dlu)
        if current:
            act=current["dluc0_state"]=="act" or current["dluc1_state"]=="act"
            color=GREEN if act else YELLOW
            self.status_chip.setText(
                f"DLU {current['dlu_id']} · SYSTEM {'ACT' if act else 'DEGRADED'}"
            )
            self.status_chip.setStyleSheet(
                f"background:#163c2f;color:{color};border:1px solid {color};"
                "border-radius:12px;padding:4px 10px;font-weight:700;"
            )
        counts={}
        for row in self.db.list_active_alarms():
            counts[row["severity"]]=counts.get(row["severity"],0)+1
        self.crit_label.setText(f"CRITICAL {counts.get('CRITICAL',0)}")
        self.major_label.setText(f"MAJOR {counts.get('MAJOR',0)}")
        self.minor_label.setText(f"MINOR {counts.get('MINOR',0)}")
        used, capacity = self.call_engine.resource_usage()
        active_calls = self.call_engine.active_call_count()
        self.traffic_label.setText(f"PDC {used}/{capacity}")
        self.path_label.setText("PATH ACTIVE" if active_calls else "PATH —")

    def _on_call_state_changed(self):
        if hasattr(self, "call_lab"):
            self.call_lab.refresh_subscribers()
        self.refresh_status()
        if getattr(self, "current_view", "home") == "module":
            self._refresh_current_view()

    def reset_demo(self):
        self.db.reset_demo()
        self.call_engine.repo.reset_demo()
        if hasattr(self, "call_lab"):
            self.call_lab.reset()
        self.terminal.append(
            "<span style='color:#f0c75e'>"
            "[RESET] Source-backed hardware restored; subscriber demo state cleared."
            "</span>"
        )
        self._refresh_current_view()

    def closeEvent(self,event):
        self.db.close()
        event.accept()
