from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QTabWidget, QToolButton, QWidget

from .app_style import apply_application_style
from .design_tokens import get_tokens, normalize_mode


NAV_TARGETS = {
    "HARDWARE": {"hardware", "Hardware"},
    "OMT / MML": {"OMT / MML", "OMT"},
    "CALLS": {"CALLS", "Call Path"},
    "COMMANDS": {"COMMAND FILES", "Command Files"},
    "COMMS LAB": {"COMMS LAB", "Communications"},
    "SCENARIOS": {"SCENARIOS", "Scenarios"},
}


def _main_tabs(window: QWidget) -> QTabWidget | None:
    candidates = window.findChildren(QTabWidget)
    ranked = []
    for widget in candidates:
        labels = [widget.tabText(i) for i in range(widget.count())]
        score = sum(
            any(label in aliases for aliases in NAV_TARGETS.values())
            for label in labels
        )
        ranked.append((score, widget))
    ranked.sort(key=lambda item: (item[0], item[1].count()), reverse=True)
    return ranked[0][1] if ranked and ranked[0][0] else None


def _remove_legacy_theme_menu(window: QWidget) -> None:
    for button in window.findChildren(QToolButton):
        if button.text() != "TOOLS" or button.menu() is None:
            continue
        for action in list(button.menu().actions()):
            submenu = action.menu()
            if submenu is not None and submenu.title().strip().upper() == "THEME":
                button.menu().removeAction(action)


def _build_navigation(window: QWidget) -> QFrame:
    existing = window.findChild(QFrame, "Stage8Nav")
    if existing is not None:
        return existing

    nav = QFrame(window)
    nav.setObjectName("Stage8Nav")
    layout = QHBoxLayout(nav)
    layout.setContentsMargins(12, 7, 12, 7)
    layout.setSpacing(5)

    lab_label = QLabel("LAB", nav)
    lab_label.setObjectName("Stage8NavTitle")
    layout.addWidget(lab_label)

    tabs = _main_tabs(window)
    buttons: list[QPushButton] = []

    for label, aliases in NAV_TARGETS.items():
        button = QPushButton(label, nav)
        button.setObjectName("Stage8NavButton")
        button.setCheckable(True)
        button.setAutoDefault(False)
        buttons.append(button)
        layout.addWidget(button)

        def activate(
            checked: bool = False,
            aliases: set[str] = aliases,
            button: QPushButton = button,
        ):
            if "hardware" in aliases and hasattr(window, "show_hardware_home"):
                window.show_hardware_home()
            elif tabs is not None:
                for index in range(tabs.count()):
                    if tabs.tabText(index) in aliases:
                        tabs.setCurrentIndex(index)
                        break
            for other in buttons:
                other.setChecked(other is button)

        button.clicked.connect(activate)

    layout.addStretch(1)

    hint = QLabel("University communications laboratory", nav)
    hint.setObjectName("Stage8NavHint")
    layout.addWidget(hint)

    return nav


def _restyle_window(window: QWidget, mode: str | None = None) -> None:
    mode = normalize_mode(mode or window.property("dlu_theme_mode") or "morning")
    tokens = get_tokens(mode)
    window.setProperty("dlu_theme_mode", mode)
    window.setObjectName("DLULabStage8")

    window.setStyleSheet(
        f"""
        QMainWindow#DLULabStage8 {{
            background: {tokens.bg};
        }}
        QFrame#Header {{
            background: {tokens.surface};
            border: 1px solid {tokens.border};
            border-top: 3px solid {tokens.primary};
            border-radius: {tokens.radius_lg}px;
        }}
        QLabel#Title {{
            color: {tokens.text_primary};
            font-size: 24px;
            font-weight: 900;
            letter-spacing: 1px;
        }}
        QLabel#StatusChip {{
            color: {tokens.success};
            background: {tokens.surface_elevated};
            border: 1px solid {tokens.success};
            border-radius: 14px;
            padding: 5px 10px;
            font-weight: 900;
        }}
        QFrame#SYP {{
            background: {tokens.surface_elevated};
            border: 1px solid {tokens.border};
            border-radius: {tokens.radius_md}px;
        }}
        QFrame#SYP QLabel {{
            color: {tokens.text_secondary};
            padding: 3px 8px;
            font-weight: 700;
        }}
        QFrame#Navigator, QFrame#ScenarioBar, QFrame#WorkbenchHeader, QFrame#CommandDock {{
            background: {tokens.surface};
            border: 1px solid {tokens.border};
            border-radius: {tokens.radius_md}px;
        }}
        QLabel#Breadcrumb {{
            color: {tokens.text_secondary};
            font-size: 13px;
            font-weight: 800;
        }}
        QLabel#NavigatorTitle, QLabel#ScenarioTitle {{
            color: {tokens.primary};
            font-weight: 900;
            letter-spacing: .8px;
        }}
        QLabel#Legend {{
            color: {tokens.text_muted};
        }}
        QFrame#Stage8Nav {{
            background: {tokens.surface};
            border: 1px solid {tokens.border};
            border-radius: {tokens.radius_md}px;
        }}
        QLabel#Stage8NavTitle {{
            color: {tokens.primary};
            font-weight: 900;
            letter-spacing: 1px;
            padding: 0 8px;
        }}
        QLabel#Stage8NavHint {{
            color: {tokens.text_muted};
            padding: 0 8px;
        }}
        QPushButton#Stage8NavButton {{
            min-height: 32px;
            padding: 5px 10px;
            background: transparent;
            border: 1px solid transparent;
            color: {tokens.text_secondary};
            font-weight: 800;
        }}
        QPushButton#Stage8NavButton:hover {{
            background: {tokens.surface_interactive};
            border-color: {tokens.border_strong};
            color: {tokens.text_primary};
        }}
        QPushButton#Stage8NavButton:checked {{
            background: {tokens.surface_interactive};
            border-color: {tokens.primary};
            color: {tokens.text_primary};
        }}
        QTextEdit#Terminal {{
            background: {tokens.deep};
            color: {tokens.text_primary};
            border: 1px solid {tokens.border};
            border-radius: {tokens.radius_md}px;
            font-family: "Cascadia Mono", "Consolas", monospace;
            padding: 10px;
            selection-background-color: {tokens.surface_interactive};
        }}
        QLabel#CommandPrompt {{
            color: {tokens.primary};
            font-size: 18px;
            font-weight: 900;
        }}
        QLabel#CommandHint {{
            color: {tokens.text_muted};
        }}
        QLabel#CommandStatus {{
            color: {tokens.success};
            font-weight: 800;
        }}
        QPushButton#PrimaryScenario, QPushButton#CommandSend {{
            background: {tokens.primary};
            color: {tokens.white};
            border: 1px solid {tokens.primary};
            font-weight: 900;
        }}
        QPushButton#PrimaryScenario:hover, QPushButton#CommandSend:hover {{
            background: {tokens.success};
            border-color: {tokens.success};
        }}
        QPushButton#ThemeToggle {{
            min-height: 32px;
            min-width: 108px;
            padding: 5px 10px;
            background: {tokens.surface_elevated};
            color: {tokens.text_primary};
            border: 1px solid {tokens.border};
            border-radius: 9px;
            font-weight: 800;
        }}
        QPushButton#ThemeToggle:hover {{
            background: {tokens.surface_interactive};
            border-color: {tokens.primary};
        }}
        QSplitter::handle {{
            background: {tokens.border};
        }}
        QSplitter::handle:hover {{
            background: {tokens.primary};
        }}
        """
    )

    for frame in window.findChildren(QFrame):
        if frame.objectName() in {
            "Header",
            "SYP",
            "Navigator",
            "ScenarioBar",
            "WorkbenchHeader",
            "CommandDock",
            "Stage8Nav",
        }:
            frame.setAttribute(Qt.WA_StyledBackground, True)


def restyle_stage8_ui(window: QWidget, mode: str | None = None) -> None:
    """Refresh only the Stage 8 shell after a theme change."""
    _restyle_window(window, mode)


def _select_initial_nav(window: QWidget) -> None:
    for button in window.findChildren(QPushButton, "Stage8NavButton"):
        if button.text() == "HARDWARE":
            button.setChecked(True)
            break


def apply_stage8_ui(window: QWidget, mode: str = "morning") -> None:
    """Install the redesigned Stage 8 shell without changing simulator behavior."""
    mode = normalize_mode(mode or window.property("dlu_theme_mode") or "morning")
    app = QApplication.instance()
    if app is not None:
        apply_application_style(app, mode)

    window.setProperty("dlu_theme_mode", mode)
    _remove_legacy_theme_menu(window)

    theme_button = window.findChild(QPushButton, "ThemeToggle")
    if theme_button is not None:
        theme_button.show()
        theme_button.setText("☾ NIGHT MODE" if mode == "morning" else "☀ DAY MODE")
        theme_button.setToolTip(
            "Switch to the night theme" if mode == "morning"
            else "Switch to the morning theme"
        )

    for label in window.findChildren(QLabel):
        text = label.text().strip()
        if text == "Siemens EWSD · Hardware-first training lab":
            label.setText("Siemens EWSD · University Communications Laboratory")
        elif text == "THEME: IVORY":
            label.hide()

    if hasattr(window, "physical_btn"):
        window.physical_btn.setText("PHYSICAL VIEW")
    if hasattr(window, "logical_btn"):
        window.logical_btn.setText("LOGICAL VIEW")
    if hasattr(window, "status_chip"):
        window.status_chip.setText("SYSTEM · ACTIVE")

    window.setMinimumSize(1180, 680)

    tabs = _main_tabs(window)
    if tabs is not None:
        replacements = {
            "OMT": "OMT / MML",
            "Command Files": "COMMAND FILES",
            "Call Path": "CALLS",
            "Communications": "COMMS LAB",
            "Scenarios": "SCENARIOS",
        }
        for index in range(tabs.count()):
            tabs.setTabText(
                index,
                replacements.get(tabs.tabText(index), tabs.tabText(index)),
            )
        tabs.setDocumentMode(True)

    nav = _build_navigation(window)
    central = window.centralWidget()
    layout = central.layout() if central is not None else None
    if layout is not None and layout.indexOf(nav) < 0:
        layout.insertWidget(1, nav)

    _restyle_window(window, mode)
    _select_initial_nav(window)

    if hasattr(window, "hardware"):
        QTimer.singleShot(0, window.hardware.reset_zoom)
