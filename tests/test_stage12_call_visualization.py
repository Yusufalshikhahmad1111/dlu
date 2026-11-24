import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from dlu_app.app_style import apply_application_style
from dlu_app.stage8_ui import apply_stage8_ui
from dlu_app.stage9_ui import apply_stage9_ui
from dlu_app.stage10_ui import apply_stage10_ui
from dlu_app.stage11_ui import apply_stage11_ui
from dlu_app.stage12_ui import PHASES, apply_stage12_ui
from dlu_app.ui import DluSimulatorWindow


def _app() -> QApplication:
    app = QApplication.instance()
    return app if app is not None else QApplication([])


def _window(tmp_path: Path) -> DluSimulatorWindow:
    app = _app()
    apply_application_style(app, "morning")
    window = DluSimulatorWindow(tmp_path / "stage12.sqlite3")
    apply_stage8_ui(window, "morning")
    apply_stage9_ui(window, "morning")
    apply_stage10_ui(window, "morning")
    apply_stage11_ui(window, "morning")
    apply_stage12_ui(window, "morning")
    app.processEvents()
    return window


def test_stage12_installs_call_flow_teaching_view(tmp_path: Path):
    window = _window(tmp_path)
    try:
        assert hasattr(window, "call_flow_teaching_panel")
        assert window.call_lab.stage12_view is window.call_flow_teaching_panel
        assert tuple(window.call_flow_teaching_panel.phase_labels) == PHASES
    finally:
        window.close()


def test_stage12_local_call_explains_no_resource(tmp_path: Path):
    window = _window(tmp_path)
    try:
        window.call_lab.quick_local()
        _app().processEvents()
        panel = window.call_flow_teaching_panel
        assert panel.last_result is not None and panel.last_result.ok
        assert panel.state_label.text() == "CONNECTED"
        assert "NOT REQUIRED" in panel.resource_card.text()
        assert "LOCAL:" in panel.explanation_card.text()
        assert "DLU 50" in panel.route_card.text()
    finally:
        window.call_lab.reset()
        window.close()


def test_stage12_blacklist_explains_pre_reservation_block(tmp_path: Path):
    window = _window(tmp_path)
    try:
        window.call_lab.quick_blacklist()
        _app().processEvents()
        panel = window.call_flow_teaching_panel
        assert panel.last_result is not None and not panel.last_result.ok
        assert panel.state_label.text() == "BLOCKED"
        assert "NOT REQUIRED" in panel.resource_card.text()
        assert "before any voice resource is reserved" in panel.explanation_card.text()
        assert "CPT / BLOCKED" in panel.route_card.text()
    finally:
        window.call_lab.reset()
        window.close()


def test_stage12_national_call_marks_pdc_reservation(tmp_path: Path):
    window = _window(tmp_path)
    try:
        window.call_lab.quick_national()
        _app().processEvents()
        panel = window.call_flow_teaching_panel
        assert panel.last_result is not None and panel.last_result.ok
        assert "RESERVED" in panel.resource_card.text()
        assert "PDC-VOICE" in panel.resource_card.text()
        assert panel.canvas.animating
    finally:
        window.call_lab.reset()
        window.close()


def test_stage12_resource_busy_blocks_before_connected(tmp_path: Path):
    window = _window(tmp_path)
    try:
        caller, _called = window.call_lab.engine.prepare_demo_subscribers()
        analysis = window.call_lab.engine.analyze(caller, "0522233500")
        call_id = "TEST-STAGE12"
        with window.call_lab.engine.db.conn:
            window.call_lab.engine.repo.create_call(
                call_id,
                caller,
                analysis.target_lac or "",
                analysis.normalized,
                analysis.target_dn,
                analysis.number_type,
                "SETUP",
                None,
                analysis.cpt,
            )
            window.call_lab.engine.repo.reserve(call_id, "PDC-VOICE", 120)
        window.call_lab.quick_national()
        _app().processEvents()
        panel = window.call_flow_teaching_panel
        assert panel.last_result is not None and not panel.last_result.ok
        assert panel.last_result.code == "CALL-RESOURCE-BUSY"
        assert panel.state_label.text() == "BLOCKED"
        assert "FULL" in panel.resource_card.text()
        assert "PDC voice resource is full" in panel.explanation_card.text()
    finally:
        window.call_lab.reset()
        window.call_lab.engine.repo.release_all("TEST-STAGE12")
        window.close()


def test_stage12_release_becomes_released_state(tmp_path: Path):
    window = _window(tmp_path)
    try:
        window.call_lab.quick_national()
        _app().processEvents()
        assert window.call_lab.current_call_id
        window.call_lab.release_call()
        _app().processEvents()
        panel = window.call_flow_teaching_panel
        assert panel.last_result is not None
        assert panel.last_result.code == "CALL-RELEASED"
        assert panel.state_label.text() == "RELEASED"
        assert "RELEASED" in panel.resource_card.text()
    finally:
        window.call_lab.reset()
        window.close()


def test_stage12_theme_sync(tmp_path: Path):
    window = _window(tmp_path)
    try:
        window.set_theme("night")
        assert window.call_flow_teaching_panel.mode == "night"
        window.set_theme("morning")
        assert window.call_flow_teaching_panel.mode == "morning"
    finally:
        window.close()
