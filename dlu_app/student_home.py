from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .design_tokens import get_tokens, normalize_mode


class LearningHomeWidget(QWidget):
    """Student-facing landing page for the main simulator journey."""

    ACTIONS = (
        ("HARDWARE", "Explore Hardware", "DLU → Shelf → Module → Port"),
        ("OMT / MML", "Run MML", "Inspect and operate the real command engine"),
        ("CALLS", "Trace a Call", "Follow route, resources, and outcome"),
        ("COMMANDS", "Run Command Files", "Schedule and execute command sequences"),
        ("COMMS LAB", "Open Communications Lab", "Experiment with signals and BER"),
        ("SCENARIOS", "Practice a Scenario", "Work through guided teaching cases"),
    )

    def __init__(self, on_navigate: Callable[[str], None] | None = None, parent=None):
        super().__init__(parent)
        self.on_navigate = on_navigate
        self._mode = "morning"
        self._continue_target = "HARDWARE"
        self._build_ui()
        self.set_theme("morning")

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(12)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll, 1)

        page = QWidget()
        scroll.setWidget(page)
        root = QVBoxLayout(page)
        root.setContentsMargins(6, 6, 8, 12)
        root.setSpacing(12)

        hero = QFrame()
        hero.setObjectName("LearningHero")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(20, 18, 20, 18)
        hero_layout.setSpacing(14)

        text_column = QVBoxLayout()
        text_column.setSpacing(4)
        eyebrow = QLabel("STUDENT LEARNING HOME")
        eyebrow.setObjectName("LearningEyebrow")
        text_column.addWidget(eyebrow)
        self.title = QLabel("Welcome to DLU Lab")
        self.title.setObjectName("LearningTitle")
        text_column.addWidget(self.title)
        self.subtitle = QLabel(
            "One clear next step, persistent context, and quick access to every lab."
        )
        self.subtitle.setObjectName("LearningSubtitle")
        self.subtitle.setWordWrap(True)
        text_column.addWidget(self.subtitle)
        hero_layout.addLayout(text_column, 1)

        continue_column = QVBoxLayout()
        continue_column.setSpacing(5)
        self.continue_label = QLabel("CONTINUE LEARNING")
        self.continue_label.setObjectName("LearningCardKicker")
        continue_column.addWidget(self.continue_label)
        self.continue_context = QLabel("Start with Hardware to learn the DLU hierarchy.")
        self.continue_context.setObjectName("LearningContinue")
        self.continue_context.setWordWrap(True)
        continue_column.addWidget(self.continue_context)
        self.continue_button = QPushButton("CONTINUE")
        self.continue_button.setObjectName("LearningPrimary")
        self.continue_button.clicked.connect(self._continue)
        continue_column.addWidget(self.continue_button, 0, Qt.AlignLeft)
        hero_layout.addLayout(continue_column, 0)
        root.addWidget(hero)

        top_grid = QGridLayout()
        top_grid.setHorizontalSpacing(12)
        top_grid.setVerticalSpacing(12)

        self.context_card = self._card(
            "CURRENT LAB",
            "Where you are right now",
            "Learning Home",
        )
        self.context_value = self.context_card.findChild(QLabel, "LearningCardValue")
        top_grid.addWidget(self.context_card, 0, 0)

        self.progress_card = self._card(
            "COURSE PROGRESS",
            "Session learning coverage",
            "0% complete",
        )
        self.progress_value = self.progress_card.findChild(QLabel, "LearningCardValue")
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("LearningProgress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_card.layout().addWidget(self.progress_bar)
        top_grid.addWidget(self.progress_card, 0, 1)

        self.status_card = self._card(
            "LIVE STATUS",
            "Current simulator health",
            "System active",
        )
        self.status_value = self.status_card.findChild(QLabel, "LearningCardValue")
        top_grid.addWidget(self.status_card, 0, 2)
        root.addLayout(top_grid)

        actions_card = QFrame()
        actions_card.setObjectName("LearningSection")
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setContentsMargins(16, 14, 16, 16)
        actions_layout.setSpacing(9)
        actions_title = QLabel("QUICK START")
        actions_title.setObjectName("LearningSectionTitle")
        actions_layout.addWidget(actions_title)
        actions_hint = QLabel(
            "Choose the learning area that matches what you want to do next."
        )
        actions_hint.setObjectName("LearningMuted")
        actions_layout.addWidget(actions_hint)

        actions_grid = QGridLayout()
        actions_grid.setHorizontalSpacing(8)
        actions_grid.setVerticalSpacing(8)
        self.action_buttons: dict[str, QPushButton] = {}
        for index, (area, label, description) in enumerate(self.ACTIONS):
            button = QPushButton(f"{label}\n{description}")
            button.setObjectName("LearningAction")
            button.setToolTip(description)
            button.setMinimumHeight(58)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button.clicked.connect(
                lambda _checked=False, target=area: self._navigate(target)
            )
            self.action_buttons[area] = button
            actions_grid.addWidget(button, index // 3, index % 3)
        actions_layout.addLayout(actions_grid)
        root.addWidget(actions_card)

        lower = QGridLayout()
        lower.setHorizontalSpacing(12)
        lower.setVerticalSpacing(12)

        recent_card = QFrame()
        recent_card.setObjectName("LearningSection")
        recent_layout = QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(16, 14, 16, 12)
        recent_layout.setSpacing(8)
        recent_title = QLabel("RECENT ACTIVITY")
        recent_title.setObjectName("LearningSectionTitle")
        recent_layout.addWidget(recent_title)
        self.recent_list = QListWidget()
        self.recent_list.setObjectName("LearningRecent")
        self.recent_list.setMinimumHeight(150)
        recent_layout.addWidget(self.recent_list, 1)
        lower.addWidget(recent_card, 0, 0)

        next_card = QFrame()
        next_card.setObjectName("LearningSection")
        next_layout = QVBoxLayout(next_card)
        next_layout.setContentsMargins(16, 14, 16, 12)
        next_layout.setSpacing(8)
        next_title = QLabel("NEXT STEP")
        next_title.setObjectName("LearningSectionTitle")
        next_layout.addWidget(next_title)
        self.next_value = QLabel(
            "Explore Hardware first to understand the DLU hierarchy."
        )
        self.next_value.setObjectName("LearningNext")
        self.next_value.setWordWrap(True)
        next_layout.addWidget(self.next_value)
        self.next_button = QPushButton("OPEN RECOMMENDED AREA")
        self.next_button.setObjectName("LearningSecondary")
        self.next_button.clicked.connect(lambda: self._navigate("HARDWARE"))
        next_layout.addWidget(self.next_button, 0, Qt.AlignLeft)
        lower.addWidget(next_card, 0, 1)

        root.addLayout(lower)
        root.addStretch(1)

    @staticmethod
    def _card(kicker: str, title: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("LearningCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 13, 15, 13)
        layout.setSpacing(3)
        kicker_label = QLabel(kicker)
        kicker_label.setObjectName("LearningCardKicker")
        layout.addWidget(kicker_label)
        title_label = QLabel(title)
        title_label.setObjectName("LearningCardTitle")
        layout.addWidget(title_label)
        value_label = QLabel(value)
        value_label.setObjectName("LearningCardValue")
        value_label.setWordWrap(True)
        layout.addWidget(value_label)
        return card

    def _navigate(self, area: str) -> None:
        if self.on_navigate:
            self.on_navigate(area)

    def _continue(self) -> None:
        self._navigate(self._continue_target)

    def update_snapshot(
        self,
        *,
        current_context: str,
        continue_target: str,
        progress_percent: int,
        visited_count: int,
        recent_activity: list[str],
        hardware_status: str,
        next_step: str,
    ) -> None:
        self._continue_target = continue_target
        self.context_value.setText(current_context)
        self.continue_context.setText(current_context)
        self.progress_value.setText(
            f"{progress_percent}% · {visited_count}/6 learning areas visited"
        )
        self.progress_bar.setValue(progress_percent)
        self.status_value.setText(hardware_status)
        self.next_value.setText(next_step)
        self.recent_list.clear()
        for entry in recent_activity:
            self.recent_list.addItem(QListWidgetItem(entry))

    def set_theme(self, mode: str) -> None:
        self._mode = normalize_mode(mode)
        tokens = get_tokens(self._mode)
        self.setStyleSheet(
            f"""
            QFrame#LearningHero, QFrame#LearningSection, QFrame#LearningCard {{
                background: {tokens.surface};
                border: 1px solid {tokens.border};
                border-radius: {tokens.radius_lg}px;
            }}
            QFrame#LearningHero {{
                background: {tokens.surface_elevated};
                border-top: 3px solid {tokens.primary};
            }}
            QLabel#LearningEyebrow, QLabel#LearningCardKicker {{
                color: {tokens.primary};
                font-weight: 900;
                letter-spacing: 1px;
                font-size: 9pt;
            }}
            QLabel#LearningTitle {{
                color: {tokens.text_primary};
                font-size: 23px;
                font-weight: 900;
            }}
            QLabel#LearningSubtitle, QLabel#LearningMuted {{
                color: {tokens.text_secondary};
            }}
            QLabel#LearningContinue, QLabel#LearningNext {{
                color: {tokens.text_primary};
                font-size: 11pt;
                font-weight: 800;
            }}
            QLabel#LearningCardTitle {{
                color: {tokens.text_secondary};
                font-size: 9pt;
                font-weight: 700;
            }}
            QLabel#LearningCardValue {{
                color: {tokens.text_primary};
                font-size: 12pt;
                font-weight: 900;
            }}
            QLabel#LearningSectionTitle {{
                color: {tokens.text_primary};
                font-size: 11pt;
                font-weight: 900;
            }}
            QPushButton#LearningPrimary {{
                background: {tokens.primary};
                color: {tokens.white};
                border: 1px solid {tokens.primary};
                border-radius: {tokens.radius_sm}px;
                padding: 8px 16px;
                min-height: 36px;
                font-weight: 900;
            }}
            QPushButton#LearningPrimary:hover {{
                background: {tokens.success};
                border-color: {tokens.success};
            }}
            QPushButton#LearningSecondary {{
                background: {tokens.surface};
                color: {tokens.text_primary};
                border: 1px solid {tokens.border_strong};
                border-radius: {tokens.radius_sm}px;
                padding: 8px 14px;
                font-weight: 800;
            }}
            QPushButton#LearningSecondary:hover {{
                background: {tokens.surface_interactive};
                border-color: {tokens.primary};
            }}
            QPushButton#LearningAction {{
                text-align: left;
                background: {tokens.surface};
                color: {tokens.text_primary};
                border: 1px solid {tokens.border};
                border-radius: {tokens.radius_md}px;
                padding: 9px 11px;
                font-weight: 800;
            }}
            QPushButton#LearningAction:hover {{
                background: {tokens.surface_interactive};
                border-color: {tokens.primary};
            }}
            QProgressBar#LearningProgress {{
                min-height: 8px;
                max-height: 8px;
                border: 0;
                border-radius: 4px;
                background: {tokens.surface_interactive};
            }}
            QProgressBar#LearningProgress::chunk {{
                background: {tokens.primary};
                border-radius: 4px;
            }}
            QListWidget#LearningRecent {{
                background: {tokens.surface_elevated};
                border: 1px solid {tokens.border};
                border-radius: {tokens.radius_sm}px;
            }}
            QListWidget#LearningRecent::item {{
                padding: 7px 8px;
                color: {tokens.text_secondary};
            }}
            QListWidget#LearningRecent::item:selected {{
                background: {tokens.surface_interactive};
                color: {tokens.text_primary};
            }}
            """
        )
