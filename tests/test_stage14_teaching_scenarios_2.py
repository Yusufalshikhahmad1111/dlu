from pathlib import Path
from tempfile import TemporaryDirectory

from PySide6.QtWidgets import QApplication

from dlu_app.db import Database
from dlu_app.mml import MmlEngine
from dlu_app.stage14_ui import PHASES, Stage14TeachingScenariosWidget
from dlu_app.teaching_scenarios import ScenarioResult, ScenarioStepResult


def _app() -> QApplication:
    app = QApplication.instance()
    return app if app is not None else QApplication([])


def _widget():
    tmp = TemporaryDirectory()
    db = Database(Path(tmp.name) / "stage14.sqlite3")
    mml = MmlEngine(db)
    widget = Stage14TeachingScenariosWidget(db, mml)
    return tmp, db, widget


def test_stage14_guided_phase_flow_runs_existing_runner():
    _app()
    tmp, db, widget = _widget()
    try:
        assert widget.scenario_list.count() == 6
        assert len(widget.rail.labels) == len(PHASES)
        assert widget._phase_index == 0

        widget.continue_phase()
        widget.continue_phase()
        widget.continue_phase()

        assert widget._result is not None
        assert widget._result.passed
        assert widget.status_chip.text() == "✓ PASS"
        assert widget._phase_index == 3

        widget.continue_phase()
        assert widget._phase_index == 4
        widget.continue_phase()
        assert widget._phase_index == 5
        widget.continue_phase()
        assert widget._phase_index == 6
        assert "FINAL RESULT: PASS" in widget.verify_text.text()
    finally:
        widget.close()
        db.close()
        tmp.cleanup()


def test_stage14_hints_cycle_and_theme_sync():
    _app()
    tmp, db, widget = _widget()
    try:
        first = widget.step_hint.text()
        widget.show_hint()
        second = widget.step_hint.text()
        widget.show_hint()
        third = widget.step_hint.text()
        assert first != second
        assert second != third
        widget.set_theme("night")
        assert widget._theme == "night"
        widget.set_theme("morning")
        assert widget._theme == "morning"
    finally:
        widget.close()
        db.close()
        tmp.cleanup()


def test_stage14_failed_result_has_mistake_explanation_and_recovery():
    _app()
    tmp, db, widget = _widget()
    try:
        result = ScenarioResult(
            scenario_id="cmrl-capacity",
            title="CMRL Capacity Limit",
            passed=False,
            affected_eqns=["10-1-7-6"],
            expected_result="Port 6 is rejected.",
            actual_result="Port 6 unexpectedly created.",
            steps=[
                ScenarioStepResult(
                    label="Reject port 6",
                    kind="MML",
                    expected="MML-VALIDATION · EXPECTED FAILURE",
                    ok=False,
                    code="CREATED",
                    actual="[CREATED] Unexpected acceptance",
                    command="> cr sub: dlu=10, type=cmrl, eqn=10-1-7-6, lac=021, dn=2233526;",
                )
            ],
        )
        widget._render_result(result)
        assert widget.status_chip.text() == "✗ FAIL"
        assert "First failing step" in widget.diagnosis_text.text()
        assert "RESET DEMO" in widget.fix_text.text()
        assert "10-1-7-6" in widget.verify_text.text()
    finally:
        widget.close()
        db.close()
        tmp.cleanup()


def test_stage14_all_scenarios_execute_through_existing_runner():
    _app()
    tmp, db, widget = _widget()
    try:
        for row in range(widget.scenario_list.count()):
            widget.scenario_list.setCurrentRow(row)
            widget.continue_phase()
            widget.continue_phase()
            widget.continue_phase()
            assert widget._result is not None
            assert widget._result.passed
    finally:
        widget.close()
        db.close()
        tmp.cleanup()
