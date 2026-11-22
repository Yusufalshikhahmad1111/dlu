from pathlib import Path

from PySide6.QtWidgets import QApplication, QSplitter

from dlu_app.app_style import apply_application_style
from dlu_app.hardware_ux2 import HardwareInspectorPanel
from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.stage9_ui import apply_stage9_ui
from dlu_app.stage10_ui import apply_stage10_ui
from dlu_app.ui import DluSimulatorWindow


def _app() -> QApplication:
    app = QApplication.instance()
    return app if app is not None else QApplication([])


def _window(tmp_path: Path) -> DluSimulatorWindow:
    app = _app()
    apply_application_style(app, "morning")
    window = DluSimulatorWindow(tmp_path / "stage10.sqlite3")
    apply_stage8_ui(window, "morning")
    apply_stage9_ui(window, "morning")
    apply_stage10_ui(window, "morning")
    app.processEvents()
    return window


def test_stage10_hardware_inspector_tracks_hierarchy(tmp_path: Path):
    window = _window(tmp_path)
    try:
        inspector = window.hardware_inspector
        assert isinstance(inspector, HardwareInspectorPanel)

        window.show_hardware_home()
        inspector.inspect("dlu", 50, source="selection")
        assert inspector.object_type.text() == "DLU"
        assert "DLU 50" in inspector.object_title.text()
        assert "8 shelves" in inspector.fact_labels["CAPACITY"].text()

        inspector.inspect("side", (50, 0), source="selection")
        assert inspector.object_type.text() == "SIDE / CONTROLLER"
        assert inspector.fact_labels["CONTROLLER"].text()

        inspector.inspect("module", (50, 0, 15), source="selection")
        assert inspector.fact_labels["EQN"].text() == "50-0-15"
        assert inspector.fact_labels["CAPACITY"].text() == "8 ports"

        inspector.inspect("port", (50, 0, 15, 0), source="selection")
        assert inspector.fact_labels["EQN"].text() == "50-0-15-0"
        assert inspector.fact_labels["CAPACITY"].text() == "1 subscriber line"
    finally:
        window.close()


def test_stage10_hardware_workspace_has_split_inspector(tmp_path: Path):
    window = _window(tmp_path)
    try:
        assert isinstance(window.hardware_splitter, QSplitter)
        assert window.hardware_inspector.isHidden() is False
        assert window.hardware.minimumWidth() >= 500
    finally:
        window.close()


def test_stage10_real_selection_updates_inspector(tmp_path: Path):
    app = _app()
    window = _window(tmp_path)
    try:
        window.show_dlu(50)
        window.select_port(50, 0, 15, 0)
        app.processEvents()
        assert window.hardware_inspector.object_type.text() == "PORT"
        assert window.hardware_inspector.fact_labels["EQN"].text() == "50-0-15-0"
        assert "SELECTED" in window.hardware_inspector.mode_hint.text()
    finally:
        window.close()


def test_stage10_theme_sync(tmp_path: Path):
    window = _window(tmp_path)
    try:
        window.set_theme("night")
        assert window.property("dlu_theme_mode") == "night"
        assert window.hardware_inspector.mode == "night"
        window.set_theme("morning")
        assert window.hardware_inspector.mode == "morning"
    finally:
        window.close()


def test_stage10_hover_classifier_keeps_shelf_and_controller_contexts_distinct(tmp_path: Path):
    window = _window(tmp_path)
    try:
        window.show_dlu(50)
        controller = window._stage10_controller
        items = [
            item
            for item in window.hardware.scene_obj.items()
            if getattr(item, "toolTip", None)
            and isinstance(getattr(item, "data", None), tuple)
            and len(item.data) == 2
        ]
        shelf_item = next(item for item in items if "SHELF" in item.toolTip().upper())
        side_item = next(item for item in items if "SIDE" in item.toolTip().upper())

        assert controller._kind_for_item(shelf_item) == ("shelf", shelf_item.data)
        assert controller._kind_for_item(side_item) == ("side", side_item.data)
    finally:
        window.close()
