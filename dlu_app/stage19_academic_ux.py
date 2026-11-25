from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTabWidget, QWidget

from .design_tokens import get_tokens, normalize_mode


@dataclass(frozen=True)
class AcademicArea:
    label: str
    purpose: str
    next_step: str
    tooltip: str
    accessible_description: str


ACADEMIC_AREAS: tuple[AcademicArea, ...] = (
    AcademicArea("Learning Home", "orient → choose a lab", "Open Hardware first to build the EWSD mental model.", "Learning Home: choose what to learn next.", "Student learning home with progress, recent activity, and the next recommended academic step."),
    AcademicArea("Hardware", "inspect → understand → act", "Inspect a DLU, shelf, module, or port before changing anything.", "Hardware: explore the DLU hierarchy and source-backed state.", "Hardware workspace for physical hierarchy, module state, ports, EQNs, and verified card operations."),
    AcademicArea("OMT", "intent → command → result", "Run one status command and connect it to the selected hardware object.", "OMT: execute real MML and inspect its result.", "Operations and Maintenance workspace for real MML command construction, execution, and explanation."),
    AcademicArea("Command Files", "compose → schedule → execute", "Load or create a deterministic command file, then inspect its execution log.", "Command Files: practice repeatable batch workflows.", "Deterministic command-file lab for acceptance, scheduling, virtual time, execution, and logs."),
    AcademicArea("Call Path", "origin → route → resource → destination", "Prepare a demo call, then inspect route classification and resource state.", "Calls: trace the full call path and resource decision.", "Call-path laboratory covering number analysis, CPT, routing, resource reservation, path, and release."),
    AcademicArea("Communications", "concept → experiment → measurement → interpretation", "Run one experiment and explain what the measurement means.", "Communications: run an experiment and interpret the evidence.", "Communications laboratory for normalized models, visualization, measurement, and interpretation."),
    AcademicArea("Scenarios", "objective → execute → diagnose → verify", "Choose a guided scenario and verify its real simulator result.", "Scenarios: practice a guided academic case.", "Teaching scenario workspace with objective, execution, diagnosis, fix, verification, and result."),
    AcademicArea("Instructor", "prepare → demonstrate → reveal → conclude", "Load a scenario, keep answers hidden while demonstrating, then reveal evidence.", "Instructor: project and demonstrate a verified scenario.", "Instructor classroom workspace for scenario loading, guided demonstration, answer visibility, and expected-versus-actual teaching."),
)


_ALIASES = {
    "Learning Home": {"Learning Home"},
    "Hardware": {"Hardware", "hardware"},
    "OMT": {"OMT", "OMT / MML"},
    "Command Files": {"Command Files", "COMMAND FILES"},
    "Call Path": {"Call Path", "CALLS"},
    "Communications": {"Communications", "COMMS LAB"},
    "Scenarios": {"Scenarios", "SCENARIOS"},
    "Instructor": {"Instructor"},
}


def _tabs(window: QWidget) -> QTabWidget | None:
    tabs = getattr(window, "feature_tabs", None)
    return tabs if isinstance(tabs, QTabWidget) else None


def _area_for_label(label: str) -> AcademicArea:
    for area in ACADEMIC_AREAS:
        if label in _ALIASES[area.label]:
            return area
    return next(area for area in ACADEMIC_AREAS if area.label == "Learning Home")


def academic_workflow_snapshot(window: QWidget) -> dict[str, str]:
    tabs = _tabs(window)
    label = tabs.tabText(tabs.currentIndex()) if tabs is not None and tabs.currentIndex() >= 0 else "Learning Home"
    area = _area_for_label(label)
    current_context = getattr(getattr(window, "student_navigation", None), "current_context", "Learning Home")
    return {
        "area": area.label,
        "purpose": area.purpose,
        "next_step": area.next_step,
        "context": current_context,
    }


def _set_accessibility(tab: QWidget, area: AcademicArea) -> None:
    tab.setAccessibleName(f"{area.label} workspace")
    if hasattr(tab, "setAccessibleDescription"):
        tab.setAccessibleDescription(area.accessible_description)
    tab.setToolTip(area.tooltip)


def _update_context(window: QWidget, label: str | None = None) -> None:
    tabs = _tabs(window)
    if tabs is None:
        return
    label = label or (tabs.tabText(tabs.currentIndex()) if tabs.currentIndex() >= 0 else "Learning Home")
    area = _area_for_label(label)
    hint = window.findChild(QLabel, "Stage8NavHint")
    if hint is not None:
        hint.setText(f"YOU ARE HERE · {area.label.upper()}  |  NEXT · {area.next_step}")
        hint.setToolTip(f"{area.purpose}. {area.next_step}")
        hint.setAccessibleName("Academic workflow guidance")
        if hasattr(hint, "setAccessibleDescription"):
            hint.setAccessibleDescription(
                f"Current academic area: {area.label}. Recommended next step: {area.next_step}"
            )
    breadcrumb = getattr(window, "breadcrumb", None)
    if breadcrumb is not None:
        breadcrumb.setText(area.label.upper())
        breadcrumb.setToolTip(area.tooltip)
    if label != "Learning Home" and getattr(window, "current_view", None) == "learning_home":
        window.current_view = "workspace"


def apply_stage19_academic_ux(window: QWidget, mode: str = "morning") -> None:
    mode = normalize_mode(mode)
    tabs = _tabs(window)
    if tabs is None:
        return
    window.setProperty("dlu_stage19_enabled", True)
    window.setProperty("dlu_stage19_mode", mode)
    for index in range(tabs.count()):
        label = tabs.tabText(index)
        area = _area_for_label(label)
        tab = tabs.widget(index)
        if tab is not None:
            _set_accessibility(tab, area)
        if label in _ALIASES[area.label]:
            tabs.setTabToolTip(index, area.tooltip)
    if not getattr(window, "_stage19_academic_hooked", False):
        def _changed(index: int) -> None:
            if index < 0:
                return
            _update_context(window)
        tabs.currentChanged.connect(_changed)
        window._stage19_academic_hooked = True

        original_navigate = getattr(window, "navigate_student_area", None)
        if original_navigate is not None:
            def _navigate(area: str) -> None:
                original_navigate(area)
                if area.strip() == "HARDWARE":
                    _update_context(window, "Hardware")
            window.navigate_student_area = _navigate

    _update_context(window)


def stage19_theme_style(window: QWidget, mode: str) -> None:
    tokens = get_tokens(normalize_mode(mode))
    hint = window.findChild(QLabel, "Stage8NavHint")
    if hint is None:
        return
    hint.setStyleSheet(
        f"color:{tokens.text_primary}; padding:0 8px; font-weight:800;"
    )

