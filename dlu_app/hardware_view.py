from __future__ import annotations

from PySide6.QtCore import QMimeData, QRectF, Qt
from PySide6.QtGui import QColor, QBrush, QDrag, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from .db import CardReference, Database
from .theme import THEMES
from .ui_utils import make_font


_PALETTE = THEMES["ivory"]
BG = _PALETTE.BG
PANEL = _PALETTE.PANEL
PANEL2 = _PALETTE.PANEL2
PANEL3 = _PALETTE.PANEL3
STEEL = _PALETTE.STEEL
TEXT = _PALETTE.TEXT
MUTED = _PALETTE.MUTED
BORDER = _PALETTE.BORDER
GREEN = _PALETTE.GREEN
YELLOW = _PALETTE.YELLOW
RED = _PALETTE.RED
BLUE = _PALETTE.BLUE
CYAN = _PALETTE.CYAN
VIOLET = _PALETTE.VIOLET
AMBER = _PALETTE.AMBER
WHITE = _PALETTE.WHITE
CARD = _PALETTE.CARD
DEEP = _PALETTE.DEEP


THEME_NAME = "morning"




def apply_theme_palette(name: str):
    global BG, PANEL, PANEL2, PANEL3, STEEL, TEXT, MUTED, BORDER
    global GREEN, YELLOW, RED, BLUE, CYAN, VIOLET, AMBER, WHITE, CARD, DEEP
    global THEME_NAME
    palette = THEMES.get(name, THEMES["ivory"])
    for key in palette.__dataclass_fields__:
        globals()[key] = getattr(palette, key)
    THEME_NAME = name


apply_theme_palette("morning")
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
            QPen(QColor(BORDER)),
            QBrush(QColor(DEEP)),
        )

def apply_hardware_theme(name: str):
    """Synchronize the hardware feature palette with the application theme."""
    apply_theme_palette(name)


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



class HardwareWorkspaceMixin:
    """Presentation boundary for the hardware workspace.

    The existing hardware rendering and interaction behavior stays intact;
    this mixin only moves the feature surface out of the application shell.
    """


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
        item = self.hardware.scene_obj.addText(str(text))
        item.setFont(make_font(size, bold=bold))
        item.setDefaultTextColor(QColor(str(color)))
        item.setPos(x, y)
        return item

    def add_scene_rounded_rect(
        self,
        rect: QRectF,
        x_radius: float,
        y_radius: float,
        pen: QPen,
        brush: QBrush,
    ):
        path = QPainterPath()
        path.addRoundedRect(rect, x_radius, y_radius)
        return self.hardware.scene_obj.addPath(path, pen, brush)

    def show_hardware_home(self):
        self.current_view = "home"
        self.workspace_left.show()
        if self.property("dlu_stage9_enabled"):
            self.student_navigation.current_context = "HARDWARE · DLU Fleet"
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
                QPen(QColor(BORDER)),
                QBrush(QColor(BORDER)),
            )

        card_w, card_h = 182, 126
        cols = 5
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
                QPen(QColor(BORDER), 1.8),
                QBrush(QColor(CARD)),
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
                self.add_scene_rounded_rect(
                    QRectF(x + 98, sy, 82, 7),
                    2, 2,
                    QPen(QColor(BORDER), 0.8),
                    QBrush(QColor(PANEL2)),
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
        self._refresh_learning_home()


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
        self.student_navigation.visit("HARDWARE", f"Hardware / DLU {dlu_id}")
        self._refresh_learning_home()
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
            QPen(QColor("{BORDER}"), 2.2),
            QBrush(QColor("{DEEP}")),
        )
        # Rack rails.
        self.add_scene_rounded_rect(
            QRectF(36, 102, 12, 754),
            5, 5,
            QPen(QColor("{BORDER}")),
            QBrush(QColor("{PANEL3}")),
        )
        self.add_scene_rounded_rect(
            QRectF(1060, 102, 12, 754),
            5, 5,
            QPen(QColor("{BORDER}")),
            QBrush(QColor("{PANEL3}")),
        )
        add_rack_rivets(scene, 54, 98, 1010, 4)

        # Identification plate.
        plate = rounded_path(62, 108, 360, 78, 10)
        scene.addPath(
            plate,
            QPen(QColor("{BORDER}"), 1.4),
            QBrush(QColor("{PANEL3}")),
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
                QBrush(QColor(CARD)),
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
                QPen(QColor("{BORDER}"), 1),
                QBrush(QColor(DEEP)),
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
            QPen(QColor(BORDER), 1.2),
            QBrush(QColor(PANEL2)),
        )
        self.add_scene_rounded_rect(
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
            accent = RED if fault else (GREEN if configured else BORDER)
            fill = PANEL2 if configured else DEEP
            if fault:
                fill = PANEL3

            visual = rounded_path(mx, y + 10, 52, 42, 5)
            scene.addPath(
                visual,
                QPen(QColor(accent), 1.1),
                QBrush(QColor(fill)),
            )
            scene.addLine(
                mx + 7, y + 18, mx + 45, y + 18,
                QPen(QColor(BORDER), 1),
            )
            scene.addEllipse(
                QRectF(mx + 7, y + 28, 6, 6),
                QPen(QColor(accent)),
                QBrush(QColor(accent)),
            )
            self.add_text(mx + 18, y + 22, str(slot["module"]), 7, TEXT, True)
            if not configured:
                module_state = "EMPTY"
                module_state_color = MUTED
            elif fault:
                module_state = "FAULT"
                module_state_color = RED
            else:
                module_state = slot["ost"].upper()
                module_state_color = state_color(slot["ost"])
            self.add_text(
                mx + 16, y + 36,
                module_state,
                6, module_state_color, True
            )

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
        scene = self.hardware.scene_obj

        self.add_text(34, 18, f"DLU {dlu_id} · LOGICAL SIGNAL MAP", 26, TEXT, True)
        self.add_text(
            34, 52,
            "Control → Interface → Subscriber Module → Port / EQN",
            11, MUTED, True
        )

        # Technical diagram backdrop.
        backdrop = rounded_path(26, 88, 1100, 430, 18)
        scene.addPath(
            backdrop,
            QPen(QColor("{BORDER}"), 1.5),
            QBrush(QColor(DEEP)),
        )

        nodes = [
            ("DLU", 70, 230, 170, 86, f"DLU {dlu_id}", GREEN),
            ("DLUC0", 310, 120, 170, 86, dlu["dluc0_state"].upper(), GREEN),
            ("DLUC1", 310, 355, 170, 86, dlu["dluc1_state"].upper(), YELLOW),
            ("DIUD", 560, 230, 170, 86, "DIGITAL INTERFACE", CYAN),
            ("SLM", 810, 230, 170, 86, "SUBSCRIBER MODULE", VIOLET),
            ("PORT", 1010, 230, 92, 86, "EQN", BLUE),
        ]

        for kind, x, y, w, h, label, accent in nodes:
            path = rounded_path(x, y, w, h, 12)
            scene.addPath(
                path,
                QPen(QColor(accent), 1.8),
                QBrush(QColor(PANEL)),
            )
            self.add_scene_rounded_rect(
                QRectF(x + 8, y + 8, w - 16, 22),
                6, 6,
                QPen(QColor(BORDER), 1),
                QBrush(QColor(PANEL3)),
            )
            self.add_text(x + 16, y + 11, kind, 8, accent, True)
            self.add_text(
                x + 16, y + 42,
                label,
                9 if w < 110 else 10,
                TEXT,
                True,
            )
            scene.addEllipse(
                QRectF(x + w - 20, y + 12, 7, 7),
                QPen(QColor(accent)),
                QBrush(QColor(accent)),
            )

        routes = [
            ((240, 273), (310, 163), GREEN),
            ((240, 273), (310, 398), YELLOW),
            ((480, 163), (560, 273), GREEN),
            ((480, 398), (560, 273), YELLOW),
            ((730, 273), (810, 273), CYAN),
            ((980, 273), (1010, 273), VIOLET),
        ]
        for (x1, y1), (x2, y2), color in routes:
            scene.addLine(
                x1, y1, x2, y2,
                QPen(QColor(color), 3)
            )
            scene.addEllipse(
                QRectF(x2 - 5, y2 - 5, 10, 10),
                QPen(QColor(color)),
                QBrush(QColor(color)),
            )

        self.add_text(
            64, 470,
            "Logical mode shows relationships; Physical mode shows equipment.",
            11, MUTED, True
        )
        scene.setSceneRect(0, 0, 1160, 560)
        self.hardware.reset_zoom()

        self._set_details({
            "DLU": dlu_id,
            "Mode": "Logical",
            "DLUC0": dlu["dluc0_state"],
            "DLUC1": dlu["dluc1_state"],
            "Flow": "DLU → Controller → DIUD → SLM → Port → DN",
        })


    def show_shelf(self, dlu_id: int, shelf: int):
        self._sync_location(dlu_id, shelf)
        self.current_view = "shelf"
        self.student_navigation.visit(
            "HARDWARE", f"Hardware / DLU {dlu_id} / Shelf {shelf}"
        )
        self._refresh_learning_home()
        self.clear_scene()
        self.back_btn.setEnabled(True)
        self.breadcrumb.setText(f"DLU {dlu_id}  /  SHELF {shelf}")
        self.add_text(34, 18, f"SHELF {shelf}", 26, TEXT, True)
        self.add_text(
            34, 52,
            f"DLU {dlu_id} · EQUIPMENT BAY · 16 MODULE POSITIONS",
            11, MUTED, True
        )

        scene = self.hardware.scene_obj
        rack = rounded_path(24, 88, 1055, 735, 18)
        scene.addPath(
            rack,
            QPen(QColor("{BORDER}"), 2.2),
            QBrush(QColor("{DEEP}")),
        )

        # Metal top rail + rack depth.
        self.add_scene_rounded_rect(
            QRectF(42, 108, 1018, 44),
            8, 8,
            QPen(QColor(BORDER), 1.2),
            QBrush(QColor(PANEL3)),
        )
        self.add_text(62, 121, f"DLU {dlu_id} / SHELF {shelf}", 13, CYAN, True)
        self.add_text(62, 140, "MODULE FRONT PANELS", 8, MUTED, True)
        add_rack_rivets(scene, 850, 122, 180, 4)

        slots = self.db.list_shelf(dlu_id, shelf)
        for i, slot in enumerate(slots):
            row = i // 8
            col = i % 8
            x = 52 + col * 126
            y = 175 + row * 300
            self.draw_full_module_slot(slot, x, y, 112, 260)

        scene.setSceneRect(0, 0, 1110, 860)
        self.hardware.reset_zoom()
        self._set_details({
            "DLU": dlu_id,
            "Shelf": shelf,
            "Positions": "Module 0..15",
            "View": "Physical Equipment Bay",
        })


    def draw_full_module_slot(self, slot, x, y, w, h):
        scene = self.hardware.scene_obj
        slot = self._slot_mapping(slot)
        configured = slot["card_type"] != "UNCONFIGURED"
        fault = slot["fault_state"] == "fault"
        accent = RED if fault else (GREEN if configured else BORDER)
        body_fill = PANEL2 if configured else DEEP
        if fault:
            body_fill = PANEL3

        # Physical faceplate.
        body = rounded_path(x, y, w, h, 9)
        scene.addPath(
            body,
            QPen(QColor(accent), 1.5),
            QBrush(QColor(body_fill)),
        )
        self.add_scene_rounded_rect(
            QRectF(x + 7, y + 7, w - 14, 26),
            5, 5,
            QPen(QColor(BORDER), 0.8),
            QBrush(QColor(DEEP)),
        )
        add_rack_rivets(scene, x + 10, y + 12, w - 20, 2)

        self.add_text(x + 12, y + 12, f"M{slot['module']}", 8, CYAN, True)
        self.add_text(
            x + 12, y + 42,
            slot["card_type"] if configured else "EMPTY MODULE",
            10, accent if configured else MUTED, True
        )
        self.add_text(x + 12, y + 62, f"{slot['port_count']} PORTS", 8, TEXT, True)

        # Small status cluster.
        module_state = (
            "EMPTY" if not configured
            else "FAULT" if fault
            else slot["ost"].upper()
        )
        self.add_text(
            x + 12, y + 83,
            module_state,
            8,
            RED if fault else MUTED if not configured else state_color(slot["ost"]),
            True,
        )
        scene.addEllipse(
            QRectF(x + w - 28, y + 81, 8, 8),
            QPen(QColor(state_color(slot["ost"]))),
            QBrush(QColor(state_color(slot["ost"]))),
        )
        scene.addEllipse(
            QRectF(x + w - 16, y + 81, 8, 8),
            QPen(QColor(RED if fault else BORDER)),
            QBrush(QColor(RED if fault else BORDER)),
        )

        max_ports = min(slot["port_count"], 64)
        mini_cols = 4 if max_ports <= 16 else 4
        for port in range(max_ports):
            px = x + 12 + (port % mini_cols) * 23
            py = y + 112 + (port // mini_cols) * 18
            sub = self.db.get_port_subscriber(
                slot["dlu_id"], slot["shelf"], slot["module"], port
            )
            color = state_color(sub["line_state"]) if sub else STEEL
            self.add_scene_rounded_rect(
                QRectF(px, py, 16, 11),
                3, 3,
                QPen(QColor(BORDER), 0.8),
                QBrush(QColor(DEEP)),
            )
            scene.addEllipse(
                QRectF(px + 5, py + 3, 5, 5),
                QPen(QColor(color)),
                QBrush(QColor(color)),
            )
            self.add_text(px + 1, py + 10, str(port), 5, MUTED)

        item = ClickableRectItem(
            QRectF(x, y, w, h),
            lambda data: self.show_module(*data),
            (slot["dlu_id"], slot["shelf"], slot["module"]),
            f"Module {slot['module']} · {slot['card_type']} · {slot['port_count']} ports",
            on_double_click=lambda data: self.show_module(*data),
            on_context=lambda data: self.open_hardware_context(data),
        )
        item.setBrush(Qt.NoBrush)
        item.setPen(Qt.NoPen)
        scene.addItem(item)


    @staticmethod
    def _slot_mapping(slot) -> dict:
        if slot is None:
            return {}
        if isinstance(slot, dict):
            return slot
        if hasattr(slot, "keys"):
            try:
                return {key: slot[key] for key in slot.keys()}
            except Exception:
                pass
        fields = (
            "dlu_id", "shelf", "module", "card_type", "ost",
            "port_count", "role", "family", "fault_state", "source_id",
        )
        return {field: getattr(slot, field, None) for field in fields}

    def show_module(self, dlu_id: int, shelf: int, module: int):
        self._sync_location(dlu_id, shelf, module)
        self.current_view = "module"
        self.student_navigation.visit(
            "HARDWARE",
            f"Hardware / DLU {dlu_id} / Shelf {shelf} / Module {module}",
        )
        self._refresh_learning_home()
        self.clear_scene()
        self.back_btn.setEnabled(True)

        slot = self._slot_mapping(
            self.db.get_slot(dlu_id, shelf, module)
        )
        if not slot:
            slot = {}
        self.breadcrumb.setText(
            f"DLU {dlu_id}  /  SHELF {shelf}  /  MODULE {module}"
        )
        if slot is None:
            self.add_text(34, 30, "MODULE NOT FOUND", 20, RED, True)
            return

        configured = slot["card_type"] != "UNCONFIGURED"
        fault = slot["fault_state"] == "fault"
        ost = (slot["ost"] or "").lower()
        accent = RED if fault else (GREEN if ost == "act" else YELLOW if ost == "mbl" else BORDER)
        state_label = "FAULT" if fault else ost.upper() if ost else "UNKNOWN"
        state_meaning = (
            "Hardware fault detected" if fault
            else "Operating / active" if ost == "act"
            else "Maintenance / blocked" if ost == "mbl"
            else "Ready / inactive"
        )

        self.add_text(
            34, 18,
            f"MODULE {module}  ·  {slot['card_type']}",
            26, TEXT, True
        )
        self.add_text(
            34, 52,
            f"EQN BASE {dlu_id}-{shelf}-{module}  ·  {slot['role'] or 'EMPTY MODULE'}",
            11, MUTED, True
        )

        scene = self.hardware.scene_obj
        card_x, card_y, card_w, card_h = 34, 96, 450, 700
        panel_x, panel_y = 520, 96
        port_count = int(slot.get("port_count") or 0)
        panel_w = 760 if port_count >= 32 else 560

        # Physical telecom faceplate.
        face = rounded_path(card_x, card_y, card_w, card_h, 16)
        scene.addPath(
            face,
            QPen(QColor(accent), 2.4),
            QBrush(QColor(PANEL2 if configured else DEEP)),
        )
        self.add_scene_rounded_rect(
            QRectF(card_x + 16, card_y + 16, card_w - 32, 70),
            9, 9,
            QPen(QColor(BORDER), 1.2),
            QBrush(QColor(PANEL3)),
        )
        add_rack_rivets(scene, card_x + 24, card_y + 28, card_w - 48, 4)

        self.add_text(
            card_x + 34, card_y + 25,
            slot["card_type"] if configured else "EMPTY MODULE",
            22, TEXT if configured else MUTED, True
        )
        self.add_text(
            card_x + 34, card_y + 56,
            slot["role"] or "No card installed",
            9, MUTED, True
        )
        self.add_text(
            card_x + 340, card_y + 27,
            f"{slot['port_count']}P",
            18, accent, True
        )
        self.add_text(
            card_x + 340, card_y + 53,
            state_label,
            9, accent, True
        )

        # Large status badge: always visible.
        badge = rounded_path(card_x + 24, card_y + 112, card_w - 48, 72, 10)
        scene.addPath(
            badge,
            QPen(QColor(accent), 1.5),
            QBrush(QColor(PANEL3)),
        )
        scene.addEllipse(
            QRectF(card_x + 40, card_y + 128, 14, 14),
            QPen(QColor(accent), 1),
            QBrush(QColor(accent)),
        )
        self.add_text(card_x + 68, card_y + 120, "OPERATING STATE", 8, MUTED, True)
        self.add_text(card_x + 68, card_y + 143, state_label, 14, accent, True)
        self.add_text(card_x + 68, card_y + 163, state_meaning, 8, TEXT, False)

        # Hardware identity blocks.
        blocks = [
            (card_x + 24, "EQN BASE", f"{dlu_id}-{shelf}-{module}"),
            (card_x + 204, "CAPACITY", f"{slot['port_count']} PORTS"),
        ]
        for bx, label, value in blocks:
            self.add_scene_rounded_rect(
                QRectF(bx, card_y + 206, 162, 58),
                8, 8,
                QPen(QColor(BORDER), 1),
                QBrush(QColor(DEEP)),
            )
            self.add_text(bx + 12, card_y + 216, label, 7, MUTED, True)
            self.add_text(bx + 12, card_y + 238, value, 10, CYAN if "EQN" in label else TEXT, True)

        # Reference/source block.
        ref_text = slot["source_id"] or "SOURCE NOT SPECIFIED"
        self.add_scene_rounded_rect(
            QRectF(card_x + 24, card_y + 286, card_w - 48, 64),
            8, 8,
            QPen(QColor(BORDER), 1),
            QBrush(QColor(DEEP)),
        )
        self.add_text(card_x + 36, card_y + 297, "ACADEMIC REFERENCE", 7, MUTED, True)
        self.add_text(card_x + 36, card_y + 319, ref_text, 10, CYAN, True)
        ref = self.db.get_card_reference(slot["card_type"]) if configured else None
        if ref and ref.source_page:
            self.add_text(card_x + 220, card_y + 319, f"COURSE PAGE {ref.source_page}", 8, MUTED, True)

        # Card condition block.
        self.add_scene_rounded_rect(
            QRectF(card_x + 24, card_y + 372, card_w - 48, 72),
            8, 8,
            QPen(QColor(BORDER), 1),
            QBrush(QColor(DEEP)),
        )
        self.add_text(card_x + 36, card_y + 383, "CARD CONDITION", 7, MUTED, True)
        condition = "FAULT" if fault else "NORMAL"
        self.add_text(card_x + 36, card_y + 405, condition, 10, RED if fault else GREEN, True)
        self.add_text(
            card_x + 150, card_y + 405,
            f"OST {ost.upper()}",
            9, state_color(ost), True
        )

        if not configured:
            self.add_text(card_x + 36, card_y + 492, "EMPTY MODULE", 18, YELLOW, True)
            self.add_text(
                card_x + 36, card_y + 522,
                "Use Hardware Library to install a verified card.",
                9, MUTED
            )
        else:
            self.add_text(
                card_x + 36, card_y + 490,
                "CARD FACEPLATE",
                8, MUTED, True
            )
            self.add_text(
                card_x + 36, card_y + 518,
                f"{slot['family'].upper()} · {slot['port_count']}P",
                11, TEXT, True
            )
            self.add_text(
                card_x + 36, card_y + 548,
                "Click a port to inspect subscriber/EQN state.",
                8, MUTED
            )

        # Port bank gets its own visible work area.
        panel = rounded_path(panel_x - 12, panel_y, panel_w, 700, 16)
        scene.addPath(
            panel,
            QPen(QColor(BORDER), 1.5),
            QBrush(QColor(PANEL)),
        )

        if configured:
            self.draw_port_grid(
                dlu_id, shelf, module, slot,
                panel_x, panel_y
            )

        scene.setSceneRect(
            0,
            0,
            max(1120 if port_count <= 16 else 1280, panel_x + panel_w + 40),
            max(840, card_y + card_h + 50),
        )
        self.hardware.reset_zoom()

        self._set_details({
            "DLU": dlu_id,
            "Shelf": shelf,
            "Module": module,
            "Card": slot["card_type"],
            "Role": slot["role"],
            "Family": slot["family"],
            "Capacity": slot["port_count"],
            "OST": slot["ost"],
            "Fault": slot["fault_state"],
            "EQN Base": f"{dlu_id}-{shelf}-{module}",
            "Source": slot["source_id"] or "—",
        })
        self.refresh_event_log()


    def draw_port_grid(self, dlu_id, shelf, module, slot, x, y):
        scene = self.hardware.scene_obj
        slot = self._slot_mapping(slot)
        capacity = int(slot.get("port_count") or 0)

        if capacity >= 32:
            cols, cell_w = 8, 92
        elif capacity > 16:
            cols, cell_w = 4, 118
        elif capacity >= 8:
            cols, cell_w = 4, 108
        else:
            cols, cell_w = 3, 160

        cell_h = 72
        rows = (capacity + cols - 1) // cols
        bank_w = max(440, cols * cell_w + 10)
        bank_h = max(180, rows * (cell_h + 10) + 68)

        bank = rounded_path(x, y, bank_w, bank_h, 14)
        bank_item = scene.addPath(
            bank,
            QPen(QColor(BORDER), 1.4),
            QBrush(QColor(PANEL2)),
        )
        bank_item.setData(9001, "PORT_PANEL")

        self.add_text(x + 18, y + 14, "PORT BANK", 10, CYAN, True)
        self.add_text(
            x + 118, y + 14,
            f"{capacity} CONNECTORS",
            9, MUTED, True
        )
        self.add_text(
            x + bank_w - 78, y + 14,
            f"{capacity}P",
            10, AMBER, True
        )

        for port in range(capacity):
            px = x + 12 + (port % cols) * cell_w
            py = y + 48 + (port // cols) * (cell_h + 10)

            sub = self.db.get_port_subscriber(dlu_id, shelf, module, port)
            if not sub:
                color = STEEL
                label = "EMPTY"
                state_label = "UNASSIGNED"
            else:
                color = state_color(sub["line_state"])
                label = sub["dn"]
                state_label = sub["line_state"].upper()
                if sub["blk_reason"]:
                    color = YELLOW
                    state_label = "BLOCKED"

            socket = rounded_path(px, py, cell_w - 10, cell_h, 9)
            item_socket = scene.addPath(
                socket,
                QPen(QColor(BORDER), 1),
                QBrush(QColor(DEEP)),
            )
            item_socket.setData(9001, "PORT_PANEL")

            connector = rounded_path(px + 9, py + 14, 38, 42, 7)
            connector_item = scene.addPath(
                connector,
                QPen(QColor(STEEL), 1),
                QBrush(QColor(BG)),
            )
            connector_item.setData(9001, "PORT_PANEL")

            for pin in range(3):
                dot = scene.addEllipse(
                    QRectF(px + 17 + pin * 9, py + 22, 5, 5),
                    QPen(QColor(color)),
                    QBrush(QColor(color)),
                )
                dot.setData(9001, "PORT_PANEL")

            led = scene.addEllipse(
                QRectF(px + cell_w - 28, py + 11, 9, 9),
                QPen(QColor(color)),
                QBrush(QColor(color)),
            )
            led.setData(9001, "PORT_PANEL")

            self.add_text(px + 58, py + 9, f"PORT {port}", 9, TEXT, True)
            self.add_text(px + 58, py + 29, label, 9, color, True)
            self.add_text(px + 58, py + 49, state_label, 7, color, True)
            self.add_text(
                px + cell_w - 75, py + 50,
                f"{dlu_id}-{shelf}-{module}-{port}",
                6, MUTED
            )

            clickable = ClickableRectItem(
                QRectF(px, py, cell_w - 10, cell_h),
                lambda data: self.select_port(*data),
                (dlu_id, shelf, module, port),
                f"EQN {dlu_id}-{shelf}-{module}-{port}",
                on_context=lambda data: self.port_context(*data),
            )
            clickable.setBrush(Qt.NoBrush)
            clickable.setPen(Qt.NoPen)
            clickable.setZValue(1)
            scene.addItem(clickable)



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
            f"<span style='color:{CYAN}'>Selected {eqn}</span>"
        )

