from __future__ import annotations

from collections.abc import Iterable
import re

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QTableWidget,
    QToolButton,
    QWidget,
)

from .design_tokens import get_tokens, normalize_mode


FOCUS_BEGIN = "/* DLU_STAGE17_FOCUS_BEGIN */"
FOCUS_END = "/* DLU_STAGE17_FOCUS_END */"

_INTERACTIVE_TYPES = (
    QPushButton,
    QToolButton,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
    QTextEdit,
    QPlainTextEdit,
    QListWidget,
    QTableWidget,
    QTabWidget,
    QAbstractItemView,
)


def contrast_ratio(foreground: str, background: str) -> float:
    def channel(value: int) -> float:
        linear = value / 255.0
        return linear / 12.92 if linear <= 0.04045 else ((linear + 0.055) / 1.055) ** 2.4

    def luminance(value: str) -> float:
        value = value.removeprefix("#")
        red = int(value[0:2], 16)
        green = int(value[2:4], 16)
        blue = int(value[4:6], 16)
        return (
            0.2126 * channel(red)
            + 0.7152 * channel(green)
            + 0.0722 * channel(blue)
        )

    left = luminance(foreground)
    right = luminance(background)
    return (max(left, right) + 0.05) / (min(left, right) + 0.05)


def contrast_report(mode: str = "morning") -> dict[str, float]:
    tokens = get_tokens(mode)
    return {
        "primary_on_surface": contrast_ratio(tokens.primary, tokens.surface),
        "primary_on_bg": contrast_ratio(tokens.primary, tokens.bg),
        "text_on_surface": contrast_ratio(tokens.text_primary, tokens.surface),
        "secondary_on_surface": contrast_ratio(tokens.text_secondary, tokens.surface),
        "muted_on_surface": contrast_ratio(tokens.text_muted, tokens.surface),
        "warning_on_surface": contrast_ratio(tokens.warning, tokens.surface),
        "danger_on_surface": contrast_ratio(tokens.danger, tokens.surface),
    }


def _strip_focus_block(style: str) -> str:
    pattern = re.compile(
        re.escape(FOCUS_BEGIN) + r".*?" + re.escape(FOCUS_END),
        flags=re.DOTALL,
    )
    return pattern.sub("", style).rstrip()


def _focus_css(mode: str) -> str:
    tokens = get_tokens(mode)
    return f"""
{FOCUS_BEGIN}
QPushButton:focus, QToolButton:focus {{
    border: 2px solid {tokens.primary};
}}
QComboBox:focus, QLineEdit:focus {{
    border: 2px solid {tokens.primary};
}}
QCheckBox:focus {{
    border: 2px solid {tokens.primary};
    border-radius: {tokens.radius_sm}px;
    padding: 2px 4px;
}}
QTabBar::tab:focus {{
    border: 2px solid {tokens.primary};
}}
QTextEdit:focus, QPlainTextEdit:focus, QListWidget:focus, QTableWidget:focus {{
    border: 2px solid {tokens.primary};
}}
QAbstractItemView:focus {{
    border: 2px solid {tokens.primary};
}}
{FOCUS_END}
""".strip()


def _patch_focus_styles(window: QWidget, mode: str) -> None:
    css = _focus_css(mode)
    targets = [window, *window.findChildren(QWidget)]
    for widget in targets:
        style = widget.styleSheet()
        if not style:
            continue
        base = _strip_focus_block(style)
        widget.setStyleSheet((base + "\n" + css).strip())


def _set_accessibility(widget: QWidget, name: str, tooltip: str | None = None, description: str | None = None) -> None:
    widget.setAccessibleName(name)
    if tooltip:
        widget.setToolTip(tooltip)
    if description and hasattr(widget, "setAccessibleDescription"):
        widget.setAccessibleDescription(description)


def _find_button(window: QWidget, text: str) -> QPushButton | None:
    for button in window.findChildren(QPushButton):
        if button.text().strip() == text:
            return button
    return None


def _find_tool_button(window: QWidget, text: str) -> QToolButton | None:
    for button in window.findChildren(QToolButton):
        if button.text().strip() == text:
            return button
    return None


def _iter_unique(widgets: Iterable[QWidget | None]) -> list[QWidget]:
    seen: set[int] = set()
    result: list[QWidget] = []
    for widget in widgets:
        if widget is None:
            continue
        marker = id(widget)
        if marker in seen:
            continue
        seen.add(marker)
        result.append(widget)
    return result


def _configure_keyboard_order(window: QWidget) -> None:
    # Main hardware controls are the first predictable keyboard path.
    sequence = _iter_unique(
        [
            getattr(window, "dlu_combo", None),
            getattr(window, "physical_btn", None),
            getattr(window, "logical_btn", None),
            getattr(window, "theme_btn", None),
            getattr(window, "back_btn", None),
            _find_tool_button(window, "TOOLS"),
            _find_button(window, "FIT"),
            getattr(window, "nav_dlu_combo", None),
            getattr(window, "nav_shelf_combo", None),
            getattr(window, "nav_module_combo", None),
            _find_button(window, "OPEN MODULE"),
            _find_tool_button(window, "NAV"),
            _find_button(window, "8-LINE LAB"),
            _find_button(window, "CMRL LAB"),
            _find_button(window, "MAINTENANCE"),
            _find_button(window, "INSPECT"),
        ]
    )
    for before, after in zip(sequence, sequence[1:]):
        QWidget.setTabOrder(before, after)

    stage16 = getattr(window, "instructor_mode", None)
    if stage16 is not None:
        guided = _iter_unique(
            [
                getattr(stage16, "scenario_combo", None),
                getattr(stage16, "run_button", None),
                getattr(stage16, "guide_button", None),
                getattr(stage16, "next_button", None),
                getattr(stage16, "reset_button", None),
                getattr(stage16, "reveal_toggle", None),
                getattr(stage16, "projector_button", None),
            ]
        )
        for before, after in zip(guided, guided[1:]):
            QWidget.setTabOrder(before, after)


def _configure_widget_defaults(window: QWidget) -> None:
    for widget in window.findChildren(QWidget):
        if isinstance(widget, _INTERACTIVE_TYPES):
            if widget.focusPolicy() == Qt.NoFocus:
                widget.setFocusPolicy(Qt.StrongFocus)
    hardware = getattr(window, "hardware", None)
    if hardware is not None:
        # The diagram is mouse-driven; keyboard users use the PATH controls
        # and the technical tabs instead of a focusable canvas.
        hardware.setFocusPolicy(Qt.NoFocus)
        _set_accessibility(
            hardware,
            "Hardware visualization",
            description="Interactive hardware diagram. Use the PATH controls and technical tabs for keyboard navigation.",
        )


def _configure_core_labels(window: QWidget) -> None:
    targets = [
        (
            getattr(window, "status_chip", None),
            "System status",
            "Current simulator system status is shown as text and is never communicated by color alone.",
        ),
        (
            getattr(window, "command_status", None),
            "MML command status",
            "Latest MML command state.",
        ),
        (
            getattr(window, "path_label", None),
            "Call path status",
            "Current call path state.",
        ),
        (
            getattr(window, "details_empty", None),
            "Hardware details empty state",
            "Select a hardware object to see technical details.",
        ),
    ]
    for widget, name, description in targets:
        if widget is not None:
            _set_accessibility(widget, name, description=description)


def _configure_core_controls(window: QWidget) -> None:
    mapping = [
        (getattr(window, "dlu_combo", None), "Header DLU selector", "Choose the DLU shown in the header."),
        (getattr(window, "physical_btn", None), "Physical hardware mode", "Show the physical rack and module layout."),
        (getattr(window, "logical_btn", None), "Logical hardware mode", "Show the logical signal and resource layout."),
        (getattr(window, "theme_btn", None), "Theme switch", None),
        (getattr(window, "back_btn", None), "Back", "Return to the previous hardware level."),
        (getattr(window, "nav_dlu_combo", None), "Path DLU selector", "Choose a DLU for the hardware path."),
        (getattr(window, "nav_shelf_combo", None), "Path shelf selector", "Choose a shelf within the selected DLU."),
        (getattr(window, "nav_module_combo", None), "Path module selector", "Choose a module within the selected shelf."),
        (getattr(window, "input", None), "MML command input", "Enter an MML command. Press Enter or RUN to execute it."),
        (getattr(window, "terminal", None), "MML execution log", "Read-only execution history and command results."),
        (getattr(window, "details", None), "Hardware details table", "Technical details for the selected DLU, module, port, or subscriber."),
        (getattr(window, "event_log", None), "Hardware event log", "Read-only history for the selected module."),
        (getattr(window, "feature_tabs", None), "Lab workspaces", "Use Tab to focus the workspaces and Ctrl+Tab to switch tabs."),
    ]
    for widget, name, tooltip in mapping:
        if widget is not None:
            _set_accessibility(widget, name, tooltip)

    tool = _find_tool_button(window, "TOOLS")
    if tool is not None:
        _set_accessibility(tool, "Tools menu", "Open backup, restore, theme, library, data folder, and reset actions.")
    nav = _find_tool_button(window, "NAV")
    if nav is not None:
        _set_accessibility(nav, "Navigation menu", "Open DLU, shelf, or module using the current PATH selections.")

    button_map = {
        "FIT": ("Fit hardware view", "Fit the hardware diagram to the available space."),
        "OPEN MODULE": ("Open selected module", "Open the module selected in the PATH controls."),
        "8-LINE LAB": ("Eight-line teaching lab", "Run the eight-subscriber-line teaching demonstration."),
        "CMRL LAB": ("CMRL capacity lab", "Run the CMRL capacity teaching demonstration."),
        "MAINTENANCE": ("Maintenance demonstration", "Open the maintenance teaching workflow."),
        "INSPECT": ("Inspect hardware", "Inspect the currently selected hardware object."),
        "RUN": ("Run MML command", "Execute the command currently in the MML input."),
        "CLEAR": ("Clear MML log", "Clear the read-only MML execution log."),
    }
    for text, (name, tooltip) in button_map.items():
        button = _find_button(window, text)
        if button is not None:
            _set_accessibility(button, name, tooltip)

    stage16 = getattr(window, "instructor_mode", None)
    if stage16 is not None:
        stage_map = [
            (getattr(stage16, "scenario_combo", None), "Instructor scenario selector", "Choose one of the six verified teaching scenarios."),
            (getattr(stage16, "run_button", None), "Run selected teaching scenario", "Execute the real teaching scenario runner."),
            (getattr(stage16, "guide_button", None), "Start guided demonstration", "Reveal the verified scenario result one step at a time."),
            (getattr(stage16, "next_button", None), "Next guided demonstration step", "Reveal the next verified scenario step."),
            (getattr(stage16, "reset_button", None), "Reset teaching demonstration", "Reset the demo using the existing simulator reset lifecycle."),
            (getattr(stage16, "reveal_toggle", None), "Reveal instructor answers", "Show expected, actual, and PASS/FAIL teaching evidence."),
            (getattr(stage16, "projector_button", None), "Projector view", "Hide operational controls and show a projector-friendly summary."),
            (getattr(stage16, "projector_exit", None), "Exit projector view", "Return from projector view to the instructor controls."),
            (getattr(stage16, "steps_table", None), "Guided demonstration results", "Verified scenario steps. Answers are hidden until REVEAL ANSWERS is enabled."),
        ]
        for widget, name, tooltip in stage_map:
            if widget is not None:
                _set_accessibility(widget, name, tooltip)


def apply_stage17_accessibility(window: QWidget, mode: str = "morning") -> None:
    mode = normalize_mode(mode)
    window.setProperty("dlu_stage17_enabled", True)
    window.setProperty("dlu_stage17_wcag_reference", "WCAG 2.2 practical desktop audit")
    _configure_widget_defaults(window)
    _configure_core_controls(window)
    _configure_core_labels(window)

    tabs = getattr(window, "feature_tabs", None)
    if isinstance(tabs, QTabWidget):
        tabs.setFocusPolicy(Qt.StrongFocus)
        tabs.tabBar().setFocusPolicy(Qt.StrongFocus)
        for index in range(tabs.count()):
            page = tabs.widget(index)
            page.setAccessibleName(f"{tabs.tabText(index)} workspace")
            if not page.toolTip():
                page.setToolTip(f"Open the {tabs.tabText(index)} workspace.")

    _configure_keyboard_order(window)
    _patch_focus_styles(window, mode)


def refresh_stage17_accessibility(window: QWidget, mode: str = "morning") -> None:
    if window.property("dlu_stage17_enabled"):
        apply_stage17_accessibility(window, mode)
