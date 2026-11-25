from __future__ import annotations

import inspect
from pathlib import Path
from tempfile import TemporaryDirectory

from PySide6.QtWidgets import QApplication

from dlu_app.app_shell import STAGE_INSTALLERS, build_window
from dlu_app.hardware_view import HardwareWorkspaceMixin
from dlu_app.ui import DluSimulatorWindow

def _app():
    return QApplication.instance() or QApplication([])

def test_stage18_app_shell_owns_feature_installation_order():
    names = [installer.__name__ for installer in STAGE_INSTALLERS]
    assert names == [
        "apply_stage8_ui",
        "apply_stage9_ui",
        "apply_stage10_ui",
        "apply_stage11_ui",
        "apply_stage12_ui",
        "apply_stage13_ui",
        "apply_stage14_ui",
        "apply_stage15_ui",
        "apply_stage16_ui",
        "apply_stage17_accessibility",
        "apply_stage19_academic_ux",
    ]

def test_stage18_hardware_feature_has_explicit_boundary():
    assert issubclass(DluSimulatorWindow, HardwareWorkspaceMixin)
    for name in (
        "show_hardware_home",
        "show_dlu",
        "show_shelf",
        "show_module",
        "draw_physical_dlu",
        "draw_logical_dlu",
        "draw_port_grid",
        "select_port",
    ):
        assert name in HardwareWorkspaceMixin.__dict__

def test_stage18_shell_and_feature_modules_keep_domain_boundary_clean():
    root = Path(__file__).resolve().parents[1]
    hardware_source = (root / "dlu_app" / "hardware_view.py").read_text(encoding="utf-8")
    assert "from .call_engine import" not in hardware_source
    assert "from .mml import" not in hardware_source
    assert "from .teaching_scenarios import" not in hardware_source
    main_source = (root / "main.py").read_text(encoding="utf-8")
    assert "apply_stage8_ui" not in main_source
    assert "apply_stage17_accessibility" not in main_source
    assert "build_window(" in main_source

def test_stage18_monolith_decreased_and_hardware_surface_isolated():
    root = Path(__file__).resolve().parents[1]
    ui_lines = (root / "dlu_app" / "ui.py").read_text(encoding="utf-8").splitlines()
    hardware_lines = (root / "dlu_app" / "hardware_view.py").read_text(encoding="utf-8").splitlines()
    assert len(ui_lines) < 1700
    assert len(hardware_lines) > 900
    assert len(inspect.getmembers(HardwareWorkspaceMixin, inspect.isfunction)) >= 20

def test_stage18_hardware_workflow_survives_feature_extraction():
    app = _app()
    with TemporaryDirectory() as tmp:
        window = build_window(Path(tmp) / "stage18.sqlite3")
        try:
            window.show()
            app.processEvents()
            window.show_hardware_home()
            assert window.current_view == "home"
            assert window.hardware.scene().items()
            window.show_dlu(50)
            assert window.current_view == "dlu"
            assert window.hardware.scene().items()
            window.show_shelf(50, 0)
            assert window.current_view == "shelf"
            assert window.hardware.scene().items()
            window.show_module(50, 0, 0)
            assert window.current_view == "module"
            assert window.hardware.scene().items()
            window.set_theme("night")
            app.processEvents()
            window.show_module(50, 0, 0)
            assert window.hardware.scene().items()
        finally:
            window.close()
            window.db.close()
            app.processEvents()
