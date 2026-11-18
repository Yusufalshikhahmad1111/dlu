from pathlib import Path
from tempfile import TemporaryDirectory

from PySide6.QtWidgets import QApplication

from dlu_app.db import Database
from dlu_app.mml import MmlEngine
from dlu_app.teaching_scenarios import TeachingScenarioRunner
from dlu_app.teaching_scenarios_ui import TeachingScenariosWidget


def make_runner():
    tmp = TemporaryDirectory()
    db = Database(Path(tmp.name) / "test.sqlite3")
    mml = MmlEngine(db)
    return tmp, db, mml, TeachingScenarioRunner(db, mml)


def test_stage6_catalog_is_complete():
    tmp, db, _mml, runner = make_runner()
    try:
        ids = {item.scenario_id for item in runner.catalog()}
        assert ids == {
            "aleppo-8-line",
            "cmrl-capacity",
            "dlu-maintenance",
            "billing-block",
            "international-blacklist",
            "overnight-command-file",
        }
    finally:
        db.close()
        tmp.cleanup()


def test_aleppo_8_line_scenario():
    tmp, db, _mml, runner = make_runner()
    try:
        result = runner.run("aleppo-8-line")
        assert result.passed
        assert len(result.affected_eqns) == 8
        assert all(step.ok for step in result.steps)
    finally:
        db.close()
        tmp.cleanup()


def test_cmrl_capacity_scenario():
    tmp, db, _mml, runner = make_runner()
    try:
        result = runner.run("cmrl-capacity")
        assert result.passed
        assert "10-1-7-6" in result.affected_eqns
        assert all(step.ok for step in result.steps)
    finally:
        db.close()
        tmp.cleanup()


def test_dlu_maintenance_scenario():
    tmp, db, _mml, runner = make_runner()
    try:
        result = runner.run("dlu-maintenance")
        assert result.passed
        assert any("FAULT-INJECTED" == step.code for step in result.steps)
        assert all(step.ok for step in result.steps)
    finally:
        db.close()
        tmp.cleanup()


def test_billing_block_scenario():
    tmp, db, _mml, runner = make_runner()
    try:
        result = runner.run("billing-block")
        assert result.passed
        assert "50-0-15-0" in result.affected_eqns
        assert all(step.ok for step in result.steps)
    finally:
        db.close()
        tmp.cleanup()


def test_international_blacklist_scenario():
    tmp, db, _mml, runner = make_runner()
    try:
        result = runner.run("international-blacklist")
        assert result.passed
        assert "00972" in result.affected_eqns
        assert all(step.ok for step in result.steps)
    finally:
        db.close()
        tmp.cleanup()


def test_overnight_command_file_scenario():
    tmp, db, _mml, runner = make_runner()
    try:
        result = runner.run("overnight-command-file")
        assert result.passed
        assert any(step.code == "DUPLICATE-GUARD" for step in result.steps)
        assert all(step.ok for step in result.steps)
    finally:
        db.close()
        tmp.cleanup()


def test_teaching_scenarios_widget_builds_and_runs():
    app = QApplication.instance() or QApplication([])
    tmp, db, mml, _runner = make_runner()
    try:
        widget = TeachingScenariosWidget(db, mml)
        assert widget.scenario_list.count() == 6
        assert widget.title_label.text() == "Aleppo 8-Line Expansion"
        widget.run_selected()
        assert widget.status_chip.text() == "PASS"
        widget.set_theme("silver")
        widget.set_theme("ivory")
        widget.close()
        assert app is not None
    finally:
        db.close()
        tmp.cleanup()
