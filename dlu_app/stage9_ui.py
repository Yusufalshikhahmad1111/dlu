from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QFrame, QTabWidget, QWidget

from .design_tokens import get_tokens, normalize_mode


AREA_ALIASES = {
    "HARDWARE": {"HARDWARE", "Hardware"},
    "OMT / MML": {"OMT / MML", "OMT"},
    "CALLS": {"CALLS", "Call Path"},
    "COMMANDS": {"COMMAND FILES", "Command Files"},
    "COMMS LAB": {"COMMS LAB", "Communications"},
    "SCENARIOS": {"SCENARIOS", "Scenarios"},
}


def _main_tabs(window: QWidget) -> QTabWidget | None:
    tabs = getattr(window, "feature_tabs", None)
    if isinstance(tabs, QTabWidget):
        return tabs
    for widget in window.findChildren(QTabWidget):
        labels = [widget.tabText(i) for i in range(widget.count())]
        if any("OMT / MML" in label for label in labels):
            return widget
    return None


def _add_home_button(window: QWidget, nav: QFrame) -> QPushButton:
    existing = window.findChild(QPushButton, "Stage9HomeButton")
    if existing is not None:
        return existing
    home = QPushButton("HOME", nav)
    home.setObjectName("Stage9HomeButton")
    home.setCheckable(True)
    home.setAutoDefault(False)
    layout = nav.layout()
    if isinstance(layout, QHBoxLayout):
        layout.insertWidget(1, home)
    home.clicked.connect(lambda: window.navigate_student_area("HOME"))
    return home


def _sync_active(window: QWidget, area: str) -> None:
    for button in window.findChildren(QPushButton, "Stage8NavButton"):
        button.setChecked(button.text() == area)
    home = window.findChild(QPushButton, "Stage9HomeButton")
    if home is not None:
        home.setChecked(area == "HOME")


def apply_stage9_ui(window: QWidget, mode: str = "morning") -> None:
    """Add the student home to the stable Stage 8 shell."""
    mode = normalize_mode(mode or window.property("dlu_theme_mode") or "morning")
    window.setProperty("dlu_stage9_enabled", True)
    nav = window.findChild(QFrame, "Stage8Nav")
    if nav is None:
        return
    home = _add_home_button(window, nav)
    tokens = get_tokens(mode)
    home.setStyleSheet(
        f"""
        QPushButton#Stage9HomeButton {{
            min-height: 32px;
            padding: 5px 11px;
            background: {tokens.surface_elevated};
            border: 1px solid {tokens.border};
            border-radius: {tokens.radius_sm}px;
            color: {tokens.text_primary};
            font-weight: 900;
        }}
        QPushButton#Stage9HomeButton:hover {{
            background: {tokens.surface_interactive};
            border-color: {tokens.primary};
        }}
        QPushButton#Stage9HomeButton:checked {{
            background: {tokens.primary};
            border-color: {tokens.primary};
            color: {tokens.white};
        }}
        """
    )
    label = nav.findChild(QLabel, "Stage8NavTitle")
    if label is not None:
        label.setText("LEARNING LAB")
    _sync_active(window, "HOME")
    if hasattr(window, "show_learning_home"):
        window.show_learning_home()
