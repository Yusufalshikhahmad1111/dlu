from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QTabWidget, QToolButton, QWidget

from .design_tokens import TOKENS


NAV_TARGETS = {
    "HARDWARE": "hardware",
    "OMT / MML": "OMT / MML",
    "CALLS": "CALLS",
    "COMMANDS": "COMMAND FILES",
    "COMMS LAB": "COMMS LAB",
    "SCENARIOS": "SCENARIOS",
}


def build_qpalette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(TOKENS.bg))
    palette.setColor(QPalette.WindowText, QColor(TOKENS.text_primary))
    palette.setColor(QPalette.Base, QColor(TOKENS.surface))
    palette.setColor(QPalette.AlternateBase, QColor(TOKENS.surface_elevated))
    palette.setColor(QPalette.Text, QColor(TOKENS.text_primary))
    palette.setColor(QPalette.Button, QColor(TOKENS.surface_interactive))
    palette.setColor(QPalette.ButtonText, QColor(TOKENS.text_primary))
    palette.setColor(QPalette.Highlight, QColor(TOKENS.primary))
    palette.setColor(QPalette.HighlightedText, QColor(TOKENS.black))
    palette.setColor(QPalette.ToolTipBase, QColor(TOKENS.surface_elevated))
    palette.setColor(QPalette.ToolTipText, QColor(TOKENS.text_primary))
    palette.setColor(QPalette.PlaceholderText, QColor(TOKENS.text_muted))
    return palette


def apply_application_style(app: QApplication) -> None:
    """Install the Stage 8 application palette and shared widget styling."""
    app.setStyle("Fusion")
    app.setPalette(build_qpalette())
    app.setStyleSheet(
        f"""
        QWidget {{
            color: {TOKENS.text_primary};
            font-family: "Segoe UI";
            font-size: 10pt;
        }}
        QToolTip {{
            color: {TOKENS.text_primary};
            background: {TOKENS.surface_elevated};
            border: 1px solid {TOKENS.border};
            padding: 6px 8px;
        }}
        QPushButton, QToolButton {{
            min-height: {TOKENS.control_height_sm}px;
            padding: 6px 12px;
            border: 1px solid {TOKENS.border};
            border-radius: {TOKENS.radius_sm}px;
            background: {TOKENS.surface_interactive};
            color: {TOKENS.text_primary};
            font-weight: 700;
        }}
        QPushButton:hover, QToolButton:hover {{
            background: {TOKENS.surface_elevated};
            border-color: {TOKENS.primary};
        }}
        QPushButton:pressed, QToolButton:pressed {{
            background: {TOKENS.surface};
            border-color: {TOKENS.primary};
        }}
        QPushButton:focus, QToolButton:focus {{
            border: 2px solid {TOKENS.primary};
        }}
        QPushButton:disabled, QToolButton:disabled {{
            color: {TOKENS.text_muted};
            background: {TOKENS.bg};
            border-color: {TOKENS.border};
        }}
        QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {{
            min-height: {TOKENS.control_height_sm}px;
            padding: 5px 9px;
            border: 1px solid {TOKENS.border};
            border-radius: {TOKENS.radius_sm}px;
            background: {TOKENS.surface};
            color: {TOKENS.text_primary};
            selection-background-color: {TOKENS.primary};
            selection-color: {TOKENS.black};
        }}
        QComboBox:hover, QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {TOKENS.primary};
        }}
        QComboBox:focus, QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {TOKENS.primary};
        }}
        QTextEdit, QPlainTextEdit, QListWidget, QTableWidget {{
            border: 1px solid {TOKENS.border};
            border-radius: {TOKENS.radius_md}px;
            background: {TOKENS.surface};
            color: {TOKENS.text_primary};
            selection-background-color: {TOKENS.surface_interactive};
            selection-color: {TOKENS.text_primary};
        }}
        QTableWidget::item:selected, QListWidget::item:selected {{
            background: {TOKENS.surface_interactive};
            border-left: 2px solid {TOKENS.primary};
        }}
        QHeaderView::section {{
            background: {TOKENS.surface_elevated};
            color: {TOKENS.text_secondary};
            border: 0;
            border-bottom: 1px solid {TOKENS.border};
            padding: 8px;
            font-weight: 800;
        }}
        QTabWidget::pane {{
            background: {TOKENS.surface};
            border: 1px solid {TOKENS.border};
            border-radius: {TOKENS.radius_md}px;
        }}
        QTabBar::tab {{
            min-height: 34px;
            padding: 7px 14px;
            margin-right: 3px;
            background: {TOKENS.surface};
            color: {TOKENS.text_muted};
            border: 1px solid {TOKENS.border};
            border-bottom: 0;
            border-top-left-radius: {TOKENS.radius_sm}px;
            border-top-right-radius: {TOKENS.radius_sm}px;
        }}
        QTabBar::tab:hover {{
            color: {TOKENS.text_secondary};
            background: {TOKENS.surface_elevated};
        }}
        QTabBar::tab:selected {{
            color: {TOKENS.text_primary};
            background: {TOKENS.surface_elevated};
            border-color: {TOKENS.primary};
            border-bottom: 2px solid {TOKENS.primary};
        }}
        QScrollBar:vertical {{
            background: {TOKENS.bg};
            width: 10px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical {{
            background: {TOKENS.border_strong};
            min-height: 30px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {TOKENS.primary};
        }}
        QScrollBar:horizontal {{
            background: {TOKENS.bg};
            height: 10px;
            margin: 2px;
        }}
        QScrollBar::handle:horizontal {{
            background: {TOKENS.border_strong};
            min-width: 30px;
            border-radius: 5px;
        }}
        """
    )


def _main_tabs(window: QWidget) -> QTabWidget | None:
    candidates = window.findChildren(QTabWidget)
    ranked = []
    for widget in candidates:
        labels = [widget.tabText(i) for i in range(widget.count())]
        score = sum(
            label in {
                "OMT",
                "OMT / MML",
                "Command Files",
                "COMMAND FILES",
                "Call Path",
                "CALLS",
                "Communications",
                "COMMS LAB",
                "Scenarios",
                "SCENARIOS",
            }
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
    layout.setContentsMargins(10, 7, 10, 7)
    layout.setSpacing(6)

    lab_label = QLabel("LAB", nav)
    lab_label.setObjectName("Stage8NavTitle")
    layout.addWidget(lab_label)

    tabs = _main_tabs(window)
    buttons: list[QPushButton] = []

    for label, target in NAV_TARGETS.items():
        button = QPushButton(label, nav)
        button.setObjectName("Stage8NavButton")
        button.setCheckable(True)
        button.setAutoDefault(False)
        buttons.append(button)
        layout.addWidget(button)

        def activate(
            checked: bool = False,
            target: str = target,
            button: QPushButton = button,
        ):
            if target == "hardware":
                if hasattr(window, "show_hardware_home"):
                    window.show_hardware_home()
            elif tabs is not None:
                for index in range(tabs.count()):
                    if tabs.tabText(index) == target:
                        tabs.setCurrentIndex(index)
                        break
            for other in buttons:
                other.setChecked(other is button)

        button.clicked.connect(activate)

    layout.addStretch(1)

    hint = QLabel("Interactive EWSD teaching laboratory", nav)
    hint.setObjectName("Stage8NavHint")
    layout.addWidget(hint)

    return nav


def _restyle_window(window: QWidget) -> None:
    window.setObjectName("DLULabStage8")
    window.setStyleSheet(
        f"""
        QMainWindow#DLULabStage8 {{
            background: {TOKENS.bg};
        }}
        QFrame#Header {{
            background: {TOKENS.surface};
            border: 1px solid {TOKENS.border};
            border-top: 2px solid {TOKENS.primary};
            border-radius: {TOKENS.radius_lg}px;
        }}
        QLabel#Title {{
            color: {TOKENS.text_primary};
            font-size: 24px;
            font-weight: 900;
            letter-spacing: 1px;
        }}
        QLabel#StatusChip {{
            color: {TOKENS.success};
            background: {TOKENS.surface_elevated};
            border: 1px solid {TOKENS.success};
            border-radius: 14px;
            padding: 5px 10px;
            font-weight: 900;
        }}
        QFrame#SYP {{
            background: {TOKENS.surface};
            border: 1px solid {TOKENS.border};
            border-radius: {TOKENS.radius_md}px;
        }}
        QFrame#SYP QLabel {{
            color: {TOKENS.text_secondary};
            padding: 3px 8px;
            font-weight: 700;
        }}
        QFrame#Navigator, QFrame#ScenarioBar, QFrame#WorkbenchHeader, QFrame#CommandDock {{
            background: {TOKENS.surface};
            border: 1px solid {TOKENS.border};
            border-radius: {TOKENS.radius_md}px;
        }}
        QLabel#Breadcrumb {{
            color: {TOKENS.text_secondary};
            font-size: 13px;
            font-weight: 800;
        }}
        QLabel#NavigatorTitle, QLabel#ScenarioTitle {{
            color: {TOKENS.primary};
            font-weight: 900;
            letter-spacing: 1px;
        }}
        QLabel#Legend {{
            color: {TOKENS.text_muted};
        }}
        QFrame#Stage8Nav {{
            background: {TOKENS.surface_elevated};
            border: 1px solid {TOKENS.border};
            border-radius: {TOKENS.radius_md}px;
        }}
        QLabel#Stage8NavTitle {{
            color: {TOKENS.primary};
            font-weight: 900;
            letter-spacing: 1.2px;
            padding: 0 8px;
        }}
        QLabel#Stage8NavHint {{
            color: {TOKENS.text_muted};
            padding: 0 8px;
        }}
        QPushButton#Stage8NavButton {{
            min-height: 32px;
            padding: 5px 10px;
            background: transparent;
            border: 1px solid transparent;
            color: {TOKENS.text_secondary};
            font-weight: 800;
        }}
        QPushButton#Stage8NavButton:hover {{
            background: {TOKENS.surface_interactive};
            border-color: {TOKENS.border_strong};
            color: {TOKENS.text_primary};
        }}
        QPushButton#Stage8NavButton:checked {{
            background: {TOKENS.surface_interactive};
            border-color: {TOKENS.primary};
            color: {TOKENS.text_primary};
        }}
        QTextEdit#Terminal {{
            background: {TOKENS.black};
            color: {TOKENS.text_secondary};
            border: 1px solid {TOKENS.border};
            border-radius: {TOKENS.radius_md}px;
            font-family: "Cascadia Mono", "Consolas", monospace;
            padding: 10px;
        }}
        QPushButton#PrimaryScenario, QPushButton#CommandSend {{
            background: {TOKENS.primary};
            color: {TOKENS.black};
            border: 1px solid {TOKENS.primary};
            font-weight: 900;
        }}
        QPushButton#PrimaryScenario:hover, QPushButton#CommandSend:hover {{
            background: {TOKENS.info};
            border-color: {TOKENS.info};
        }}
        QPushButton#ThemeToggle {{
            min-width: 0;
            max-width: 0;
            min-height: 0;
            max-height: 0;
            padding: 0;
            border: 0;
        }}
        QSplitter::handle {{
            background: {TOKENS.border};
        }}
        QSplitter::handle:hover {{
            background: {TOKENS.primary};
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


def _select_initial_nav(window: QWidget) -> None:
    for button in window.findChildren(QPushButton, "Stage8NavButton"):
        if button.text() == "HARDWARE":
            button.setChecked(True)
            break


def apply_stage8_ui(window: QWidget) -> None:
    """Apply the Stage 8 visual shell after the existing feature UI is built."""
    app = QApplication.instance()
    if app is not None:
        apply_application_style(app)

    _remove_legacy_theme_menu(window)

    theme_button = window.findChild(QPushButton, "ThemeToggle")
    if theme_button is not None:
        theme_button.hide()

    for label in window.findChildren(QLabel):
        text = label.text().strip()
        if text == "Siemens EWSD · Hardware-first training lab":
            label.setText("Siemens EWSD · Digital Communications Laboratory")
        elif text == "THEME: IVORY":
            label.hide()

    if hasattr(window, "physical_btn"):
        window.physical_btn.setText("PHYSICAL VIEW")
    if hasattr(window, "logical_btn"):
        window.logical_btn.setText("LOGICAL VIEW")
    if hasattr(window, "status_chip"):
        window.status_chip.setText("SYSTEM · ACTIVE")

    # The legacy window minimum (1250x760) cannot support the Stage 8 QA target
    # of 1280x720. Keep the normal application size unchanged while allowing the
    # smallest supported visual-audit viewport.
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
            tabs.setTabText(index, replacements.get(tabs.tabText(index), tabs.tabText(index)))
        tabs.setDocumentMode(True)

    nav = _build_navigation(window)
    central = window.centralWidget()
    layout = central.layout() if central is not None else None
    if layout is not None and layout.indexOf(nav) < 0:
        layout.insertWidget(1, nav)

    _restyle_window(window)
    _select_initial_nav(window)

    # The hardware scene is built before the final window/layout geometry exists.
    # Re-fit it after the first layout pass so 1280x720 and similar viewports do
    # not inherit an oversized scene transform.
    if hasattr(window, "hardware"):
        QTimer.singleShot(0, window.hardware.reset_zoom)
