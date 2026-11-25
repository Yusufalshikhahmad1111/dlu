from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from PySide6.QtWidgets import QApplication

from dlu_app.app_shell import STAGE_INSTALLERS, build_window
from dlu_app.stage19_academic_ux import academic_workflow_snapshot

ACADEMIC_TABS = (
    ("Learning Home", {"Learning Home"}, "LEARNING HOME"),
    ("OMT", {"OMT", "OMT / MML"}, "OMT"),
    ("Command Files", {"Command Files", "COMMAND FILES"}, "COMMAND FILES"),
    ("Call Path", {"Call Path", "CALLS"}, "CALL PATH"),
    ("Communications", {"Communications", "COMMS LAB"}, "COMMUNICATIONS"),
    ("Scenarios", {"Scenarios", "SCENARIOS"}, "SCENARIOS"),
    ("Instructor", {"Instructor"}, "INSTRUCTOR"),
)

def _app() -> QApplication:
    return QApplication.instance() or QApplication([])

def test_stage19_installer_is_last_academic_ux_layer():
    assert STAGE_INSTALLERS[-1].__name__ == "apply_stage19_academic_ux"

def test_stage19_context_and_next_step_follow_each_workspace():
    app = _app()
    with TemporaryDirectory() as tmp:
        window = build_window(Path(tmp) / "stage19-context.sqlite3")
        try:
            window.show()
            app.processEvents()
            for semantic_label, aliases, breadcrumb in ACADEMIC_TABS:
                index = next(
                    i for i in range(window.feature_tabs.count())
                    if window.feature_tabs.tabText(i) in aliases
                )
                window.feature_tabs.setCurrentIndex(index)
                app.processEvents()
                snapshot = academic_workflow_snapshot(window)
                assert snapshot["area"] == semantic_label
                assert snapshot["next_step"]
                assert window.breadcrumb.text() == breadcrumb
                assert "NEXT ·" in window.findChild(type(window.breadcrumb), "Stage8NavHint").text()
                assert window.feature_tabs.tabToolTip(index)
                assert window.feature_tabs.widget(index).accessibleName()
        finally:
            window.close()
            window.db.close()
            app.processEvents()

def test_stage19_student_end_to_end_journey_preserves_real_workflows():
    app = _app()
    with TemporaryDirectory() as tmp:
        window = build_window(Path(tmp) / "stage19-journey.sqlite3")
        try:
            window.show()
            app.processEvents()
            window.navigate_student_area("HARDWARE")
            assert window.breadcrumb.text() == "HARDWARE"
            window.navigate_student_area("OMT / MML")
            window.set_command_text("> stat dlu: dlu=50;")
            window.execute_input()
            app.processEvents()
            assert "ERROR" not in window.command_status.text()
            window.navigate_student_area("CALLS")
            window.call_lab.quick_local()
            app.processEvents()
            assert window.call_lab.status.text()
            assert window.call_lab.stage12_view.last_result is not None
            window.navigate_student_area("COMMUNICATIONS")
            window.communications_lab.run_current()
            app.processEvents()
            assert window.communications_lab.stack.currentWidget() is not None
            window.reset_demo()
            app.processEvents()
            window.navigate_student_area("SCENARIOS")
            window.teaching_scenarios.run_selected()
            app.processEvents()
            assert "PASS" in window.teaching_scenarios.status_chip.text()
            window.reset_demo()
            app.processEvents()
            assert window.teaching_scenarios.status_chip.text() == "RESET"
        finally:
            window.close()
            window.db.close()
            app.processEvents()

def test_stage19_instructor_answer_visibility_remains_safe():
    app = _app()
    with TemporaryDirectory() as tmp:
        window = build_window(Path(tmp) / "stage19-instructor.sqlite3")
        try:
            window.instructor_mode.run_selected()
            app.processEvents()
            assert window.instructor_mode.status.text().startswith("EXECUTED")
            assert "PASS" not in window.instructor_mode.status.text()
            assert "FAIL" not in window.instructor_mode.status.text()
            window.instructor_mode.reveal_toggle.setChecked(True)
            app.processEvents()
            assert window.instructor_mode.status.text() in {"PASS", "FAIL"}
        finally:
            window.close()
            window.db.close()
            app.processEvents()
