from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .design_tokens import get_tokens, normalize_mode
from .ui_utils import make_font


@dataclass(frozen=True)
class LearningPhase:
    key: str
    number: int
    title: str
    subtitle: str
    areas: tuple[str, ...]
    action_area: str
    action_label: str


PHASES = (
    LearningPhase(
        "LEARN", 1, "Learn", "Build the mental model first.",
        ("HARDWARE", "OMT / MML"), "HARDWARE", "OPEN HARDWARE",
    ),
    LearningPhase(
        "PRACTICE", 2, "Practice", "Operate the simulator with real workflows.",
        ("CALLS", "COMMANDS"), "CALLS", "OPEN PRACTICE",
    ),
    LearningPhase(
        "EXPERIMENT", 3, "Experiment", "Observe communications behavior and measurements.",
        ("COMMS LAB",), "COMMS LAB", "OPEN EXPERIMENT",
    ),
    LearningPhase(
        "CHALLENGE", 4, "Challenge", "Apply the concepts in a guided scenario.",
        ("SCENARIOS",), "SCENARIOS", "OPEN CHALLENGE",
    ),
    LearningPhase(
        "VERIFY", 5, "Verify", "Review evidence from the complete learning path.",
        ("HARDWARE", "OMT / MML", "CALLS", "COMMANDS", "COMMS LAB", "SCENARIOS"),
        "VERIFY", "VERIFY LEARNING",
    ),
)


class PhaseCard(QFrame):
    def __init__(self, phase: LearningPhase, on_action: Callable[[str], None], parent=None):
        super().__init__(parent)
        self.phase = phase
        self.on_action = on_action
        self.setObjectName("Stage15PhaseCard")

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(6)

        header = QHBoxLayout()
        self.number = QLabel(str(phase.number))
        self.number.setObjectName("Stage15PhaseNumber")
        self.title = QLabel(phase.title)
        self.title.setFont(make_font(13, bold=True))
        self.status = QLabel("PENDING")
        self.status.setObjectName("Stage15PhaseStatus")
        header.addWidget(self.number)
        header.addWidget(self.title)
        header.addStretch()
        header.addWidget(self.status)
        root.addLayout(header)

        self.subtitle = QLabel(phase.subtitle)
        self.subtitle.setWordWrap(True)
        self.subtitle.setObjectName("Stage15PhaseSubtitle")
        root.addWidget(self.subtitle)

        self.areas = QLabel("")
        self.areas.setWordWrap(True)
        self.areas.setObjectName("Stage15PhaseAreas")
        root.addWidget(self.areas)

        footer = QHBoxLayout()
        self.evidence = QLabel("")
        self.evidence.setWordWrap(True)
        self.evidence.setObjectName("Stage15PhaseEvidence")
        footer.addWidget(self.evidence, 1)

        self.action = QPushButton(phase.action_label)
        self.action.setObjectName("Stage15PhaseAction")
        self.action.setAutoDefault(False)
        self.action.clicked.connect(lambda _checked=False: self.on_action(self.phase.key))
        footer.addWidget(self.action)
        root.addLayout(footer)

    def set_state(self, status: str, evidence: str, available: bool, tokens) -> None:
        self.status.setText(status)
        self.evidence.setText(evidence)
        self.action.setEnabled(available or self.phase.key == "VERIFY")
        self.action.setText("SHOW GAPS" if self.phase.key == "VERIFY" and not available else self.phase.action_label)

        if status == "COMPLETE":
            accent, bg = tokens.success, tokens.surface
        elif status == "READY":
            accent, bg = tokens.primary, tokens.surface_elevated
        elif status == "LOCKED":
            accent, bg = tokens.border, tokens.surface
        else:
            accent, bg = tokens.warning, tokens.surface

        self.setStyleSheet(
            f"""
            QFrame#Stage15PhaseCard {{
                background:{bg};
                border:1px solid {tokens.border};
                border-left:4px solid {accent};
                border-radius:{tokens.radius_md}px;
            }}
            QLabel#Stage15PhaseNumber {{
                min-width:28px;
                max-width:28px;
                min-height:28px;
                max-height:28px;
                padding:4px;
                border-radius:14px;
                background:{accent};
                color:{tokens.deep};
                font-weight:900;
            }}
            QLabel#Stage15PhaseStatus {{
                color:{accent};
                font-size:9pt;
                font-weight:900;
                letter-spacing:0.5px;
            }}
            QLabel#Stage15PhaseSubtitle {{
                color:{tokens.text_primary};
                font-weight:800;
            }}
            QLabel#Stage15PhaseAreas, QLabel#Stage15PhaseEvidence {{
                color:{tokens.text_secondary};
                font-size:9pt;
            }}
            QPushButton#Stage15PhaseAction {{
                background:{tokens.surface_interactive};
                border:1px solid {tokens.border};
                border-radius:{tokens.radius_sm}px;
                color:{tokens.text_primary};
                padding:7px 10px;
                font-weight:900;
            }}
            QPushButton#Stage15PhaseAction:hover {{
                background:{tokens.primary};
                border-color:{tokens.primary};
                color:{tokens.white};
            }}
            QPushButton#Stage15PhaseAction:disabled {{
                color:{tokens.text_muted};
                background:{tokens.surface};
            }}
            """
        )


class Stage15AcademicLearningWidget(QWidget):
    """Session-only academic progression over the existing simulator modules."""

    def __init__(self, window, on_navigate: Callable[[str], None] | None = None, parent=None):
        super().__init__(parent)
        self.window = window
        self.on_navigate = on_navigate
        self._theme = "morning"
        self._verified = False
        self.phase_cards: dict[str, PhaseCard] = {}
        self._build()
        self.set_theme(self._theme)
        self.refresh_path()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(10)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll, 1)

        page = QWidget()
        scroll.setWidget(page)
        root = QVBoxLayout(page)
        root.setContentsMargins(6, 6, 8, 12)
        root.setSpacing(10)

        hero = QFrame()
        hero.setObjectName("Stage15Hero")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(16, 14, 16, 14)
        eyebrow = QLabel("ACADEMIC LEARNING LAYER")
        eyebrow.setObjectName("Stage15Eyebrow")
        hero_layout.addWidget(eyebrow)
        title = QLabel("Learn → Practice → Experiment → Challenge → Verify")
        title.setObjectName("Stage15Title")
        title.setWordWrap(True)
        title.setFont(make_font(19, bold=True))
        hero_layout.addWidget(title)
        self.context_label = QLabel("Session pathway over the existing DLU Lab modules.")
        self.context_label.setObjectName("Stage15Context")
        self.context_label.setWordWrap(True)
        hero_layout.addWidget(self.context_label)

        progress_row = QHBoxLayout()
        self.progress_label = QLabel("0 / 6 learning areas evidenced")
        self.progress_label.setObjectName("Stage15ProgressLabel")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimumHeight(8)
        progress_row.addWidget(self.progress_label)
        progress_row.addWidget(self.progress_bar, 1)
        hero_layout.addLayout(progress_row)
        root.addWidget(hero)

        map_card = QFrame()
        map_card.setObjectName("Stage15Map")
        map_layout = QVBoxLayout(map_card)
        map_layout.setContentsMargins(12, 10, 12, 12)
        map_title = QLabel("COURSE PATH")
        map_title.setObjectName("Stage15SectionTitle")
        map_layout.addWidget(map_title)
        self.map_hint = QLabel(
            "The sequence guides the student through existing capabilities; it does not create a second simulator."
        )
        self.map_hint.setObjectName("Stage15Hint")
        self.map_hint.setWordWrap(True)
        map_layout.addWidget(self.map_hint)

        grid = QGridLayout()
        grid.setHorizontalSpacing(9)
        grid.setVerticalSpacing(9)
        for index, phase in enumerate(PHASES[:4]):
            card = PhaseCard(phase, self._phase_action)
            self.phase_cards[phase.key] = card
            grid.addWidget(card, index // 2, index % 2)
        verify = PhaseCard(PHASES[4], self._phase_action)
        self.phase_cards["VERIFY"] = verify
        grid.addWidget(verify, 2, 0, 1, 2)
        map_layout.addLayout(grid)
        root.addWidget(map_card)

        evidence = QFrame()
        evidence.setObjectName("Stage15Evidence")
        evidence_layout = QVBoxLayout(evidence)
        evidence_layout.setContentsMargins(12, 10, 12, 10)
        evidence_title = QLabel("VERIFY EVIDENCE")
        evidence_title.setObjectName("Stage15SectionTitle")
        evidence_layout.addWidget(evidence_title)
        self.evidence_label = QLabel(
            "Verification checks only session evidence. It does not change simulator state or academic results."
        )
        self.evidence_label.setWordWrap(True)
        self.evidence_label.setObjectName("Stage15EvidenceText")
        evidence_layout.addWidget(self.evidence_label)
        self.verify_button = QPushButton("VERIFY LEARNING PATH")
        self.verify_button.setObjectName("Stage15Verify")
        self.verify_button.setAutoDefault(False)
        self.verify_button.clicked.connect(self._verify_path)
        evidence_layout.addWidget(self.verify_button, 0, Qt.AlignLeft)
        root.addWidget(evidence)

        recent = QFrame()
        recent.setObjectName("Stage15Recent")
        recent_layout = QVBoxLayout(recent)
        recent_layout.setContentsMargins(12, 10, 12, 10)
        recent_title = QLabel("RECENT ACTIVITY")
        recent_title.setObjectName("Stage15SectionTitle")
        recent_layout.addWidget(recent_title)
        self.recent_label = QLabel("No session activity yet.")
        self.recent_label.setWordWrap(True)
        self.recent_label.setObjectName("Stage15RecentText")
        recent_layout.addWidget(self.recent_label)
        root.addWidget(recent)
        root.addStretch(1)

    def _visited(self) -> set[str]:
        state = getattr(self.window, "student_navigation", None)
        return set(getattr(state, "visited_areas", set()))

    def _phase_complete(self, phase: LearningPhase, visited: set[str]) -> bool:
        return self._verified if phase.key == "VERIFY" else all(area in visited for area in phase.areas)

    def _phase_ready(self, index: int, visited: set[str]) -> bool:
        return index == 0 or self._phase_complete(PHASES[index - 1], visited)

    def _phase_action(self, phase_key: str):
        if phase_key == "VERIFY":
            self._verify_path()
            return
        phase = next(item for item in PHASES if item.key == phase_key)
        if self.on_navigate is not None:
            self.on_navigate(phase.action_area)

    def _verify_path(self):
        visited = self._visited()
        required = ("HARDWARE", "OMT / MML", "CALLS", "COMMANDS", "COMMS LAB", "SCENARIOS")
        missing = [area for area in required if area not in visited]
        if missing:
            self._verified = False
            self.evidence_label.setText(
                "Verification is not ready yet. Missing session evidence: "
                + ", ".join(missing)
                + ". Open those learning areas, then return here."
            )
        else:
            self._verified = True
            self.evidence_label.setText(
                "✓ Learning path verified for this session. "
                "All six existing learning areas have been visited without adding a second simulator engine."
            )
        self.refresh_path()

    def refresh_path(self):
        visited = self._visited()
        tokens = get_tokens(self._theme)
        for index, phase in enumerate(PHASES):
            complete = self._phase_complete(phase, visited)
            ready = self._phase_ready(index, visited)
            if complete:
                status, evidence = (
                    "COMPLETE",
                    "All evidence complete." if phase.key != "VERIFY" else "All six learning areas verified.",
                )
            elif ready:
                missing = [area for area in phase.areas if area not in visited]
                status = "READY"
                evidence = "Start here." if not missing else "Still needed: " + ", ".join(missing)
            else:
                status, evidence = "LOCKED", "Complete the previous phase first."
            card = self.phase_cards[phase.key]
            card.areas.setText("Areas · " + " + ".join(phase.areas))
            card.set_state(status, evidence, ready, tokens)

        count = len(visited)
        percent = round((count / 6) * 100)
        self.progress_label.setText(f"{count} / 6 learning areas evidenced · {percent}%")
        self.progress_bar.setValue(percent)
        self.context_label.setText(
            "Verified learning path for the current session."
            if self._verified
            else "Session-only academic progression over the existing Hardware, MML, Calls, Command Files, Communications and Scenarios modules."
        )
        state = getattr(self.window, "student_navigation", None)
        recent = getattr(state, "recent_activity", [])
        self.recent_label.setText(" · ".join(recent[:5]) if recent else "No session activity yet.")

    def update_snapshot(self, **_snapshot):
        self.refresh_path()

    def set_theme(self, mode: str):
        self._theme = normalize_mode(mode)
        tokens = get_tokens(self._theme)
        self.setStyleSheet(
            f"""
            QFrame#Stage15Hero, QFrame#Stage15Map, QFrame#Stage15Evidence, QFrame#Stage15Recent {{
                background:{tokens.surface};
                border:1px solid {tokens.border};
                border-radius:{tokens.radius_lg}px;
            }}
            QFrame#Stage15Hero {{
                background:{tokens.surface_elevated};
                border-top:3px solid {tokens.primary};
            }}
            QLabel#Stage15Eyebrow {{
                color:{tokens.primary};
                font-size:9pt;
                font-weight:900;
                letter-spacing:1px;
            }}
            QLabel#Stage15Title {{
                color:{tokens.text_primary};
                font-weight:900;
            }}
            QLabel#Stage15Context, QLabel#Stage15Hint, QLabel#Stage15RecentText,
            QLabel#Stage15EvidenceText, QLabel#Stage15ProgressLabel {{
                color:{tokens.text_secondary};
            }}
            QLabel#Stage15SectionTitle {{
                color:{tokens.text_primary};
                font-size:10pt;
                font-weight:900;
                letter-spacing:0.6px;
            }}
            QProgressBar {{
                background:{tokens.surface};
                border:1px solid {tokens.border};
                border-radius:5px;
            }}
            QProgressBar::chunk {{
                background:{tokens.primary};
                border-radius:5px;
            }}
            QPushButton#Stage15Verify {{
                background:{tokens.primary};
                color:{tokens.white};
                border:1px solid {tokens.primary};
                border-radius:{tokens.radius_sm}px;
                padding:8px 12px;
                font-weight:900;
            }}
            QPushButton#Stage15Verify:hover {{
                background:{tokens.success};
                border-color:{tokens.success};
            }}
            """
        )
        self.refresh_path()

    def reset_session_verification(self):
        self._verified = False
        self.evidence_label.setText(
            "Verification checks only session evidence. It does not change simulator state or academic results."
        )
        self.refresh_path()


class Stage15Controller:
    def __init__(self, window, mode: str = "morning"):
        self.window = window
        self.mode = normalize_mode(mode)
        self.view: Stage15AcademicLearningWidget | None = None
        self.legacy = None

    def install(self):
        tabs = getattr(self.window, "feature_tabs", None)
        legacy = getattr(self.window, "learning_home", None)
        if tabs is None or legacy is None:
            return
        index = tabs.indexOf(legacy)
        if index < 0:
            return
        view = Stage15AcademicLearningWidget(
            self.window,
            on_navigate=self.window.navigate_student_area,
            parent=tabs,
        )
        tabs.removeTab(index)
        self.legacy = legacy
        legacy.setParent(None)
        legacy.deleteLater()
        tabs.insertTab(index, view, "Learning Home")
        self.window.learning_home = view
        self.view = view
        self.window.stage15_controller = self
        self.window.setProperty("dlu_stage15_enabled", True)
        view.set_theme(self.mode)

    def set_mode(self, mode: str):
        self.mode = normalize_mode(mode)
        if self.view is not None:
            self.view.set_theme(self.mode)


def apply_stage15_ui(window, mode: str = "morning"):
    controller = getattr(window, "stage15_controller", None)
    if controller is None:
        controller = Stage15Controller(window, mode)
        controller.install()
    else:
        controller.set_mode(mode)
