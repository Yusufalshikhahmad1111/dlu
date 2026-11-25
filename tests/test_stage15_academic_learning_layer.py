from PySide6.QtWidgets import QApplication

from dlu_app.navigation import StudentNavigationState
from dlu_app.stage15_ui import PHASES, Stage15AcademicLearningWidget


class DummyWindow:
    def __init__(self):
        self.student_navigation = StudentNavigationState()
        self.targets = []
        self.teaching_scenarios = type("ScenarioView", (), {})()
        self.teaching_scenarios._result = None

    def navigate_student_area(self, area: str):
        self.targets.append(area)
        if area != "VERIFY":
            self.student_navigation.visit(area, area)


def _app() -> QApplication:
    app = QApplication.instance()
    return app if app is not None else QApplication([])


def test_stage15_exposes_five_academic_phases():
    _app()
    window = DummyWindow()
    widget = Stage15AcademicLearningWidget(window, on_navigate=window.navigate_student_area)
    assert [phase.key for phase in PHASES] == ["LEARN", "PRACTICE", "EXPERIMENT", "CHALLENGE", "VERIFY"]
    assert len(widget.phase_cards) == 5
    assert widget.progress_bar.value() == 0
    widget.close()


def test_stage15_progression_uses_existing_learning_areas():
    _app()
    window = DummyWindow()
    widget = Stage15AcademicLearningWidget(window, on_navigate=window.navigate_student_area)
    window.student_navigation.visit("HARDWARE", "Hardware")
    window.student_navigation.visit("OMT / MML", "MML")
    widget.refresh_path()
    assert widget.phase_cards["LEARN"].status.text() == "COMPLETE"
    assert widget.phase_cards["PRACTICE"].status.text() == "READY"

    window.student_navigation.visit("CALLS", "Calls")
    window.student_navigation.visit("COMMANDS", "Commands")
    window.student_navigation.visit("COMMS LAB", "Comms")
    window.student_navigation.visit("SCENARIOS", "Scenarios")
    window.teaching_scenarios._result = type("Result", (), {"passed": True})()
    widget.refresh_path()
    assert widget.phase_cards["PRACTICE"].status.text() == "COMPLETE"
    assert widget.phase_cards["EXPERIMENT"].status.text() == "COMPLETE"
    assert widget.phase_cards["CHALLENGE"].status.text() == "COMPLETE"
    widget.close()


def test_stage15_verify_requires_all_six_existing_areas():
    _app()
    window = DummyWindow()
    widget = Stage15AcademicLearningWidget(window, on_navigate=window.navigate_student_area)
    widget._verify_path()
    assert not widget._verified
    assert "Missing evidence" in widget.evidence_label.text()

    for area in ("HARDWARE", "OMT / MML", "CALLS", "COMMANDS", "COMMS LAB", "SCENARIOS"):
        window.student_navigation.visit(area, area)
    window.teaching_scenarios._result = type("Result", (), {"passed": True})()
    widget._verify_path()
    assert widget._verified
    assert "verified for this session" in widget.evidence_label.text()
    assert widget.phase_cards["VERIFY"].status.text() == "COMPLETE"
    assert widget.progress_bar.value() == 100
    widget.reset_session_verification()
    assert not widget._verified
    widget.close()


def test_stage15_actions_route_only_to_existing_modules():
    _app()
    window = DummyWindow()
    widget = Stage15AcademicLearningWidget(window, on_navigate=window.navigate_student_area)
    for phase in PHASES[:4]:
        widget._phase_action(phase.key)
    assert window.targets == ["HARDWARE", "CALLS", "COMMS LAB", "SCENARIOS"]
    widget.set_theme("night")
    assert widget._theme == "night"
    widget.set_theme("morning")
    assert widget._theme == "morning"
    widget.close()


def test_stage15_is_presentation_only():
    _app()
    window = DummyWindow()
    widget = Stage15AcademicLearningWidget(window, on_navigate=window.navigate_student_area)
    assert not hasattr(window, "db")
    assert not hasattr(window, "call_engine")
    widget.close()


def test_stage15_challenge_and_verify_require_a_real_pass():
    _app()
    window = DummyWindow()
    widget = Stage15AcademicLearningWidget(window, on_navigate=window.navigate_student_area)
    for area in ("HARDWARE", "OMT / MML", "CALLS", "COMMANDS", "COMMS LAB", "SCENARIOS"):
        window.student_navigation.visit(area, area)
    widget.refresh_path()
    assert widget.phase_cards["CHALLENGE"].status.text() != "COMPLETE"
    widget._verify_path()
    assert not widget._verified
    assert "PASS one teaching scenario" in widget.evidence_label.text()

    window.teaching_scenarios._result = type("Result", (), {"passed": True})()
    widget._verify_path()
    assert widget._verified
    assert widget.phase_cards["CHALLENGE"].status.text() == "COMPLETE"
    assert widget.phase_cards["VERIFY"].status.text() == "COMPLETE"
    assert widget.progress_bar.value() == 100
    widget.close()


def test_stage15_progressive_action_opens_first_missing_area():
    _app()
    window = DummyWindow()
    widget = Stage15AcademicLearningWidget(window, on_navigate=window.navigate_student_area)

    window.student_navigation.visit("HARDWARE", "Hardware")
    window.student_navigation.visit("OMT / MML", "MML")
    widget.refresh_path()
    widget._phase_action("PRACTICE")
    assert window.targets[-1] == "CALLS"

    window.student_navigation.visit("CALLS", "Calls")
    widget.refresh_path()
    widget._phase_action("PRACTICE")
    assert window.targets[-1] == "COMMANDS"
    widget.close()
