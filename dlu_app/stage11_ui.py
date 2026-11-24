from __future__ import annotations

import re
from functools import wraps

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from .design_tokens import get_tokens, normalize_mode


COMMAND_GUIDE = {
    "HELP": ("Help", "Lists the supported MML commands and working examples."),
    "DISP SUB": ("Display subscriber", "Displays subscriber records and their linked EQN."),
    "DISP DLU": ("Display DLU", "Shows a DLU's controller state, shelves, modules, and subscriber count."),
    "DISP DLUMOD": ("Display module", "Shows one module's card type, role, capacity, state, and subscribers."),
    "DISP DLUPORT": ("Display port", "Shows one EQN port and its subscriber association."),
    "DISP CPT": ("Display CPT", "Displays the current call-prefix translation data."),
    "DISP ALARMS": ("Display alarms", "Lists active simulator alarms."),
    "DISP CALL": ("Display call", "Displays a call session and its route/resource data."),
    "STAT SUB": ("Subscriber status", "Shows subscriber line state and blocking status."),
    "STAT DLU": ("DLU status", "Shows the operational status of a DLU."),
    "STAT DLUMOD": ("Module status", "Shows the current status of a hardware module."),
    "STAT PORT": ("Port status", "Shows the current status of an EQN port."),
    "STATPORT": ("Port status", "Shows the current status of an EQN port."),
    "STAT CALL": ("Call status", "Shows call-session state and resources."),
    "TEST SUB": ("Test subscriber", "Runs the existing subscriber test workflow."),
    "TEST DLU": ("Test DLU", "Runs the existing DLU/controller test workflow."),
    "TEST DLUMOD": ("Test module", "Runs the existing module diagnostic/test workflow."),
    "TEST CALL": ("Test call", "Runs the existing call test workflow."),
    "CR SUB": ("Create subscriber", "Creates a subscriber record at a valid EQN using the existing MML rules."),
    "CR DEST": ("Create destination", "Creates a destination using the existing simulator command semantics."),
    "CAN SUB": ("Cancel subscriber", "Cancels an existing subscriber record."),
    "MOD SUB": ("Modify subscriber", "Changes supported subscriber attributes."),
    "CONF DLU": ("Configure DLU", "Applies a supported DLU/controller state change."),
    "CONF DLUMOD": ("Configure module", "Applies a supported module configuration change."),
    "DIAG DLU": ("Diagnose DLU", "Runs the existing DLU diagnostic workflow."),
    "DIAG DLUMOD": ("Diagnose module", "Runs the existing module diagnostic workflow."),
    "DIAG DLUC": ("Diagnose controller", "Runs the existing DLU controller diagnostic workflow."),
    "EXECMDFILE": ("Execute command file", "Starts an existing command-file workflow through the real MML engine."),
    "EXEC MDFILE": ("Execute command file", "Starts an existing command-file workflow through the real MML engine."),
}

SUPPORTED_VERBS = {
    "HELP", "H", "DISP", "STAT", "STATPORT", "TEST", "CR", "CAN",
    "MOD", "CONF", "DIAG", "EXEC", "EXECMDFILE",
}


def _parse_command(text: str) -> tuple[str, str]:
    body = text.strip()
    if body.startswith(">"):
        body = body[1:].strip()
    body = body.rstrip(";").strip()
    if body.upper() in {"HELP", "H"}:
        return "HELP", ""
    match = re.match(
        r"^(?P<verb>[A-Za-z]+)(?:\s+(?P<object>[A-Za-z]+))?\s*:",
        body,
    )
    if not match:
        return "", ""
    return match.group("verb").upper(), (match.group("object") or "").upper()


def explain_command(text: str) -> tuple[str, str]:
    verb, obj = _parse_command(text)
    key = verb if not obj else f"{verb} {obj}"
    if key in COMMAND_GUIDE:
        return COMMAND_GUIDE[key]
    if verb in SUPPORTED_VERBS:
        return (
            f"{verb} command",
            "The command format is recognized. Press RUN to let the existing MML engine validate and execute it.",
        )
    return (
        "MML command",
        "Use > help; for supported commands, then reuse one of the working examples.",
    )


def syntax_state(text: str) -> tuple[str, str]:
    value = text.strip()
    if not value:
        return "READY", "Type a command or select one from Quick Run."
    if not value.startswith(">"):
        value = "> " + value
    if not value.endswith(";"):
        return "CHECK", "MML commands end with ';'. Add the semicolon before RUN."
    body = value[1:-1].strip()
    if body.upper() in {"HELP", "H"}:
        return "READY", "Syntax looks valid."
    if not re.match(r"^[A-Za-z]+(?:\s+[A-Za-z]+)?\s*:\s*.*$", body):
        return "ERROR", "Expected VERB OBJECT: param=value, ...;"
    return "READY", "Syntax shape looks valid. Semantic checks happen in the real MML engine."


def target_hint(text: str) -> str:
    body = text.strip()
    eqn = re.search(r"\beqn\s*=\s*([^,;]+)", body, re.I)
    if eqn:
        return f"Input target · EQN {eqn.group(1).strip()}"
    dlu = re.search(r"\bdlu\s*=\s*(\d+)", body, re.I)
    shelf = re.search(r"\bshelf\s*=\s*(\d+)", body, re.I)
    module = re.search(r"\bmodule\s*=\s*(\d+)", body, re.I)
    if dlu and shelf and module:
        return (
            f"Input target · DLU {dlu.group(1)} · Shelf {shelf.group(1)} "
            f"· Module {module.group(1)}"
        )
    if dlu:
        return f"Input target · DLU {dlu.group(1)}"
    dn = re.search(r"\bdn\s*=\s*([^,;]+)", body, re.I)
    if dn:
        return f"Input target · DN {dn.group(1).strip()}"
    return "Input target · determined by the MML command"


def result_target(data) -> str:
    rows = []
    if isinstance(data, dict):
        rows = [data]
    elif isinstance(data, list):
        rows = [row for row in data if isinstance(row, dict)]

    targets: list[str] = []
    seen: set[str] = set()

    def add_target(value: str) -> None:
        if value not in seen:
            seen.add(value)
            targets.append(value)

    for item in rows:
        eqn = item.get("eqn")
        if eqn:
            add_target(f"EQN {eqn}")
        elif all(key in item for key in ("dlu", "shelf", "module")):
            add_target(
                f"DLU {item['dlu']} · Shelf {item['shelf']} "
                f"· Module {item['module']}"
            )
        elif item.get("dlu") is not None:
            add_target(f"DLU {item['dlu']}")
        elif item.get("dn"):
            add_target(f"Subscriber DN {item['dn']}")

        subscriber = item.get("subscriber")
        if isinstance(subscriber, dict):
            if subscriber.get("eqn"):
                add_target(f"EQN {subscriber['eqn']}")
            elif subscriber.get("dn"):
                add_target(f"Subscriber DN {subscriber['dn']}")

    if len(targets) == 1:
        return targets[0]
    if len(targets) > 1:
        return f"{len(targets)} linked targets · see detailed output"
    if len(rows) > 1:
        return f"{len(rows)} returned records · see detailed output"
    return "No direct hardware target in this result"


class MmlTeachingPanel(QFrame):
    def __init__(
        self,
        window: QWidget,
        mode: str = "morning",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.window = window
        self.mode = normalize_mode(mode)
        self.setObjectName("MmlTeachingPanel")
        self._build()
        self.set_mode(self.mode)
        self.refresh_history()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(9)

        header = QLabel("COMMAND GUIDE")
        header.setObjectName("Stage11Title")
        root.addWidget(header)

        self.syntax_badge = QLabel("READY")
        self.syntax_badge.setObjectName("Stage11Badge")
        root.addWidget(self.syntax_badge)

        self.explanation_title = QLabel("Command")
        self.explanation_title.setObjectName("Stage11Section")
        root.addWidget(self.explanation_title)

        self.explanation = QLabel("Type a command to see what it is intended to do.")
        self.explanation.setWordWrap(True)
        self.explanation.setObjectName("Stage11Body")
        root.addWidget(self.explanation)

        self.target = QLabel("Input target · determined by the MML command")
        self.target.setWordWrap(True)
        self.target.setObjectName("Stage11Target")
        root.addWidget(self.target)

        self.result = QLabel("Execution result will appear here.")
        self.result.setWordWrap(True)
        self.result.setObjectName("Stage11Result")
        root.addWidget(self.result)

        section = QLabel("HISTORY")
        section.setObjectName("Stage11Section")
        root.addWidget(section)

        self.history_list = QListWidget()
        self.history_list.setObjectName("Stage11History")
        self.history_list.setMinimumHeight(150)
        self.history_list.itemDoubleClicked.connect(self._use_item)
        root.addWidget(self.history_list, 1)

        actions = QHBoxLayout()
        use_btn = QPushButton("USE")
        use_btn.clicked.connect(self.use_selected)
        copy_btn = QPushButton("COPY")
        copy_btn.clicked.connect(self.copy_selected)
        clear_btn = QPushButton("CLEAR VIEW")
        clear_btn.setToolTip("Clear only the visible history panel; keyboard history is preserved.")
        clear_btn.clicked.connect(self.clear_history_view)
        actions.addWidget(use_btn)
        actions.addWidget(copy_btn)
        actions.addWidget(clear_btn)
        root.addLayout(actions)

        hint = QLabel("↑ / ↓ in the editor also recalls commands.")
        hint.setWordWrap(True)
        hint.setObjectName("Stage11Hint")
        root.addWidget(hint)

    def attach_editor(self, editor) -> None:
        self.editor = editor
        editor.textChanged.connect(self.update_from_editor)
        self.update_from_editor()

    def update_from_editor(self) -> None:
        text = self.editor.text() if hasattr(self, "editor") else ""
        state, detail = syntax_state(text)
        title, explanation = explain_command(text)
        self.syntax_badge.setText(f"{state} · {detail}")
        self.explanation_title.setText(title)
        self.explanation.setText(explanation)
        self.target.setText(target_hint(text))
        self._style_badge(state)

    def refresh_history(self) -> None:
        self.history_list.clear()
        for command in reversed(self.window.history[-30:]):
            self.history_list.addItem(QListWidgetItem(command))

    def _use_item(self, item: QListWidgetItem) -> None:
        self._set_from_history(item)

    def _set_from_history(self, item: QListWidgetItem | None) -> None:
        if item is None:
            return
        self.window.set_command_text(item.text())

    def use_selected(self) -> None:
        self._set_from_history(self.history_list.currentItem())

    def copy_selected(self) -> None:
        item = self.history_list.currentItem()
        if item is None:
            return
        self.window.set_command_text(item.text())
        self.window.input.selectAll()
        self.window.input.copy()
        self.window.command_status.setText("READY · Command copied to clipboard")

    def clear_history_view(self) -> None:
        # Presentation-only: never destroy the real ↑/↓ editor history.
        self.history_list.clear()
        self.result.setText(
            "History view cleared. Keyboard history (↑/↓) and terminal output are unchanged."
        )

    def on_command_result(self, command: str | None, result) -> None:
        command_text = command or "Direct MML action"
        state = "SUCCESS" if result.ok else "ERROR"
        title, explanation = explain_command(command or "")
        self.result.setText(
            f"{state} · {result.code}\n"
            f"{command_text}\n"
            f"{result.message}\n"
            f"Linked target · {result_target(result.data)}"
        )
        self.refresh_history()
        if command:
            self.explanation_title.setText(title)
            self.explanation.setText(explanation)
        self._style_result(result.ok)

    def set_mode(self, mode: str) -> None:
        self.mode = normalize_mode(mode)
        tokens = get_tokens(self.mode)
        self.setStyleSheet(
            f"""
            QFrame#MmlTeachingPanel {{
                background: {tokens.surface};
                border: 1px solid {tokens.border};
                border-radius: 12px;
            }}
            QLabel#Stage11Title {{
                color: {tokens.text_primary};
                font-size: 14px;
                font-weight: 900;
            }}
            QLabel#Stage11Section {{
                color: {tokens.text_secondary};
                font-size: 10px;
                font-weight: 900;
                padding-top: 2px;
            }}
            QLabel#Stage11Body, QLabel#Stage11Hint {{
                color: {tokens.text_secondary};
            }}
            QLabel#Stage11Target {{
                color: {tokens.primary};
                background: {tokens.surface_elevated};
                border: 1px solid {tokens.border};
                border-radius: 8px;
                padding: 7px;
            }}
            QLabel#Stage11Result {{
                color: {tokens.text_primary};
                background: {tokens.surface_elevated};
                border: 1px solid {tokens.border};
                border-radius: 8px;
                padding: 8px;
            }}
            QLabel#Stage11Badge {{
                color: {tokens.primary};
                background: {tokens.deep};
                border: 1px solid {tokens.border};
                border-radius: 8px;
                padding: 6px 8px;
                font-weight: 800;
            }}
            QListWidget#Stage11History {{
                background: {tokens.surface_interactive};
                color: {tokens.text_primary};
                border: 1px solid {tokens.border};
                border-radius: 8px;
                padding: 4px;
            }}
            QListWidget#Stage11History::item {{
                padding: 7px 6px;
                border-radius: 6px;
            }}
            QListWidget#Stage11History::item:selected {{
                background: {tokens.primary};
                color: {tokens.surface};
            }}
            QPushButton {{
                min-height: 34px;
            }}
            """
        )

    def _style_badge(self, state: str) -> None:
        tokens = get_tokens(self.mode)
        color = tokens.primary
        if state == "ERROR":
            color = tokens.danger
        elif state == "CHECK":
            color = tokens.warning
        self.syntax_badge.setStyleSheet(
            f"color:{color}; background:{tokens.deep}; "
            f"border:1px solid {tokens.border}; border-radius:8px; "
            "padding:6px 8px; font-weight:800;"
        )

    def _style_result(self, ok: bool) -> None:
        tokens = get_tokens(self.mode)
        color = tokens.success if ok else tokens.danger
        self.result.setStyleSheet(
            f"color:{tokens.text_primary}; background:{tokens.surface_elevated}; "
            f"border:1px solid {color}; border-radius:8px; padding:8px;"
        )


class Stage11Controller:
    def __init__(self, window: QWidget, mode: str = "morning"):
        self.window = window
        self.mode = normalize_mode(mode)
        self.panel: MmlTeachingPanel | None = None

    def install(self) -> None:
        if getattr(self.window, "_stage11_enabled", False):
            return
        self.window._stage11_enabled = True
        self.window.setProperty("dlu_stage11_enabled", True)

        layout = self.window.omt_tab.layout()
        terminal = self.window.terminal
        if layout is None:
            raise RuntimeError("OMT/MML tab layout is unavailable")
        index = layout.indexOf(terminal)
        if index < 0:
            raise RuntimeError("OMT/MML terminal is unavailable")

        panel = MmlTeachingPanel(self.window, self.mode, self.window.omt_tab)
        splitter = QSplitter(Qt.Horizontal, self.window.omt_tab)
        splitter.setObjectName("MmlUX2Splitter")
        splitter.setChildrenCollapsible(False)

        layout.removeWidget(terminal)
        terminal.setParent(splitter)
        splitter.addWidget(terminal)
        splitter.addWidget(panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([720, 320])
        layout.insertWidget(index, splitter, 1)

        panel.attach_editor(self.window.input)
        self.panel = panel
        self.window.mml_ux2_panel = panel
        self.window.omt_splitter = splitter
        self.window.stage11_controller = self

        original_theme = self.window.set_theme

        @wraps(original_theme)
        def themed(name: str):
            result = original_theme(name)
            self.set_mode(self.window.property("dlu_theme_mode") or name)
            return result

        self.window.set_theme = themed
        panel.set_mode(self.mode)

    def set_mode(self, mode: str) -> None:
        self.mode = normalize_mode(mode)
        if self.panel is not None:
            self.panel.set_mode(self.mode)

    def on_command_result(self, command: str | None, result) -> None:
        if self.panel is not None:
            self.panel.on_command_result(command, result)


def apply_stage11_ui(window: QWidget, mode: str = "morning") -> None:
    controller = getattr(window, "stage11_controller", None)
    if controller is not None:
        controller.set_mode(mode)
        return
    controller = Stage11Controller(window, mode)
    controller.install()
