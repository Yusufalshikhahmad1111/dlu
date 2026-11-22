from __future__ import annotations

from functools import wraps

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QSplitter, QVBoxLayout, QWidget

from .design_tokens import get_tokens, normalize_mode
from .hardware_ux2 import HardwareInspectorPanel
from .ui import ClickableRectItem


class HardwareUXController(QObject):
    def __init__(self, window: QWidget, mode: str = "morning"):
        self.window = window
        self.mode = normalize_mode(mode)
        self.inspector = window.hardware_inspector
        self.hover_item = None
        self.selection_item = None
        self._wrap_navigation_methods()
        window.hardware.viewport().installEventFilter(self)
        window.hardware.setMouseTracking(True)
        window.hardware.viewport().setMouseTracking(True)

    def set_mode(self, mode: str) -> None:
        self.mode = normalize_mode(mode)
        self.inspector.set_mode(self.mode)
        self._refresh_overlays()

    def _wrap(self, name: str, after):
        original = getattr(self.window, name)

        @wraps(original)
        def wrapped(*args, **kwargs):
            result = original(*args, **kwargs)
            after(*args, **kwargs)
            return result

        setattr(self.window, name, wrapped)

    def _wrap_navigation_methods(self) -> None:
        self._wrap(
            "show_hardware_home",
            lambda: self._inspect("exchange", None, "selection"),
        )
        self._wrap(
            "show_dlu",
            lambda dlu_id: self._inspect("dlu", dlu_id, "selection"),
        )
        self._wrap(
            "show_shelf",
            lambda dlu_id, shelf: self._inspect("shelf", (dlu_id, shelf), "selection"),
        )
        self._wrap(
            "show_module",
            lambda dlu_id, shelf, module: self._inspect(
                "module", (dlu_id, shelf, module), "selection"
            ),
        )
        self._wrap(
            "select_port",
            lambda dlu_id, shelf, module, port: self._inspect(
                "port", (dlu_id, shelf, module, port), "selection"
            ),
        )

        original_theme = self.window.set_theme

        @wraps(original_theme)
        def themed(name: str):
            result = original_theme(name)
            self.set_mode(self.window.property("dlu_theme_mode") or name)
            return result

        self.window.set_theme = themed

    def _inspect(self, kind: str, data, source: str) -> None:
        self.inspector.inspect(kind, data, source=source)
        if source == "selection":
            self.selection_item = self._find_item(data)
            self._refresh_overlays()

    def _kind_for_item(self, item: ClickableRectItem) -> tuple[str, object] | None:
        data = item.data
        if isinstance(data, int):
            return "dlu", data
        if not isinstance(data, tuple):
            return None
        if len(data) == 4:
            return "port", data
        if len(data) == 3:
            return "module", data
        if len(data) == 2:
            tooltip = item.toolTip().upper()
            if "SIDE" in tooltip:
                return "side", data
            if self.window.current_view == "dlu":
                return "side", data
            return "shelf", data
        return None

    def _find_item(self, data):
        for item in self.window.hardware.scene_obj.items():
            if isinstance(item, ClickableRectItem) and item.data == data:
                return item
        return None

    def _scene_target(self, pos):
        for item in self.window.hardware.scene_obj.items(pos, Qt.IntersectsItemShape):
            if isinstance(item, ClickableRectItem):
                return item
            parent = item.parentItem()
            while parent is not None:
                if isinstance(parent, ClickableRectItem):
                    return parent
                parent = parent.parentItem()
        return None

    def _remove_overlay(self, attr: str) -> None:
        overlay = getattr(self, attr, None)
        if overlay is None:
            return
        scene = self.window.hardware.scene_obj
        if overlay.scene() is scene:
            scene.removeItem(overlay)
        setattr(self, attr, None)

    def _add_overlay(self, attr: str, item, dashed: bool) -> None:
        self._remove_overlay(attr)
        if item is None:
            return
        tokens = get_tokens(self.mode)
        overlay = QGraphicsRectItem(item.sceneBoundingRect())
        pen = QPen(QColor(tokens.primary), 2.4)
        if dashed:
            pen.setStyle(Qt.DashLine)
        overlay.setPen(pen)
        overlay.setBrush(Qt.NoBrush)
        overlay.setZValue(5000)
        overlay.setAcceptedMouseButtons(Qt.NoButton)
        overlay.setAcceptHoverEvents(False)
        self.window.hardware.scene_obj.addItem(overlay)
        setattr(self, attr, overlay)

    def _refresh_overlays(self) -> None:
        self._remove_overlay("hover_overlay")
        self._add_overlay(
            "selection_overlay",
            self.selection_item,
            dashed=False,
        )

    def eventFilter(self, watched, event):
        if watched is not self.window.hardware.viewport():
            return False
        if event.type() == QEvent.MouseMove:
            pos = self.window.hardware.mapToScene(event.position().toPoint())
            item = self._scene_target(pos)
            if item is not None:
                context = self._kind_for_item(item)
                if context is not None:
                    kind, data = context
                    self.inspector.inspect(kind, data, source="hover")
                    self._remove_overlay("hover_overlay")
                    self._add_overlay("hover_overlay", item, dashed=True)
        elif event.type() == QEvent.Leave:
            self._remove_overlay("hover_overlay")
        return False


def _open_inspector_target(window, kind: str, data) -> None:
    if kind == "exchange":
        window.show_hardware_home()
    elif kind == "dlu":
        window.show_dlu(int(data))
    elif kind == "shelf":
        window.show_shelf(int(data[0]), int(data[1]))
    elif kind == "module":
        window.show_module(int(data[0]), int(data[1]), int(data[2]))
    elif kind in {"port", "subscriber"}:
        dlu_id, shelf, module, port = map(int, data)
        window.show_module(dlu_id, shelf, module)
        window.select_port(dlu_id, shelf, module, port)
    elif kind == "side":
        dlu_id, side = map(int, data)
        window.show_dlu(dlu_id)
        window.hardware_inspector.inspect("side", (dlu_id, side), source="selection")


def apply_stage10_ui(window: QWidget, mode: str = "morning") -> None:
    """Install Hardware UX 2.0 without changing simulator/domain behavior."""
    if getattr(window, "_stage10_enabled", False):
        return

    mode = normalize_mode(mode or window.property("dlu_theme_mode") or "morning")
    window.setProperty("dlu_stage10_enabled", True)

    layout = window.workspace_left.layout()
    if not isinstance(layout, QVBoxLayout):
        return

    hardware = window.hardware
    index = layout.indexOf(hardware)
    if index < 0:
        return

    layout.removeWidget(hardware)

    splitter = QSplitter(Qt.Horizontal, window.workspace_left)
    splitter.setObjectName("HardwareUX2Splitter")
    splitter.setChildrenCollapsible(False)

    hardware.setParent(splitter)
    hardware.setMinimumWidth(500)
    inspector = HardwareInspectorPanel(
        window.db,
        on_open=lambda kind, data: _open_inspector_target(window, kind, data),
        parent=splitter,
    )

    splitter.addWidget(hardware)
    splitter.addWidget(inspector)
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 0)
    splitter.setSizes([760, 320])

    layout.insertWidget(index, splitter, 1)

    window.hardware_splitter = splitter
    window.hardware_inspector = inspector
    inspector.set_mode(mode)

    controller = HardwareUXController(window, mode)
    window._stage10_controller = controller
    window.hardware.controller = window

    window.show_hardware_home()
    controller.set_mode(mode)
