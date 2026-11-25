from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from PySide6.QtCore import QEvent, QMimeData, QRectF, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QBrush, QDrag, QPainter, QPainterPath, QPen, QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QMenu,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QToolButton,
)

from .backup_restore import BackupError, DatabaseBackupManager
from .call_engine import CallEngine
from .command_file_ui import CommandFileLab
from .communications_ui import CommunicationsLabWidget
from .teaching_scenarios_ui import TeachingScenariosWidget
from .call_ui import CallLabWidget
from .db import CardReference, Database
from .mml import MmlEngine, MmlResult
from .navigation import StudentNavigationState
from .student_home import LearningHomeWidget
from .theme import THEMES
from .ui_utils import make_font
from .hardware_view import (
    CardLibraryDialog,
    ClickableRectItem,
    HardwareSelectorDialog,
    HardwareView,
    HardwareWorkspaceMixin,
    ReferenceDialog,
    apply_hardware_theme,
)


_PALETTE = THEMES["ivory"]
BG = _PALETTE.BG
PANEL = _PALETTE.PANEL
PANEL2 = _PALETTE.PANEL2
PANEL3 = _PALETTE.PANEL3
STEEL = _PALETTE.STEEL
TEXT = _PALETTE.TEXT
MUTED = _PALETTE.MUTED
BORDER = _PALETTE.BORDER
GREEN = _PALETTE.GREEN
YELLOW = _PALETTE.YELLOW
RED = _PALETTE.RED
BLUE = _PALETTE.BLUE
CYAN = _PALETTE.CYAN
VIOLET = _PALETTE.VIOLET
AMBER = _PALETTE.AMBER
WHITE = _PALETTE.WHITE
CARD = _PALETTE.CARD
DEEP = _PALETTE.DEEP


THEME_NAME = "morning"




def apply_theme_palette(name: str):
    global BG, PANEL, PANEL2, PANEL3, STEEL, TEXT, MUTED, BORDER
    global GREEN, YELLOW, RED, BLUE, CYAN, VIOLET, AMBER, WHITE, CARD, DEEP
    global THEME_NAME
    palette = THEMES.get(name, THEMES["ivory"])
    for key in palette.__dataclass_fields__:
        globals()[key] = getattr(palette, key)
    THEME_NAME = name


apply_theme_palette("morning")
def state_color(state: str) -> str:
    value = (state or "").lower()
    if value in {"act", "idle"}:
        return GREEN
    if value in {"mbl", "blocked"}:
        return YELLOW
    if value in {"busy", "fault"}:
        return RED
    if value in {"test", "diagnostic"}:
        return BLUE
    return STEEL


def rounded_path(x: float, y: float, w: float, h: float, radius: float = 10) -> QPainterPath:
    path = QPainterPath()
    path.addRoundedRect(QRectF(x, y, w, h), radius, radius)
    return path


def add_rack_rivets(scene, x: float, y: float, w: float, count: int = 4):
    for i in range(count):
        px = x + 8 + i * max(1.0, (w - 16) / max(1, count - 1))
        scene.addEllipse(
            QRectF(px - 2, y, 4, 4),
            QPen(QColor(BORDER)),
            QBrush(QColor(DEEP)),
        )


class DluSimulatorWindow(HardwareWorkspaceMixin, QMainWindow):
    def __init__(self, db_path: str | Path):
        super().__init__()
        self.db = Database(db_path)
        self.mml = MmlEngine(self.db)
        self.call_engine = CallEngine(self.db)
        self.history: list[str] = []
        self.history_index = 0
        self.current_view = "home"
        self.mode = "physical"
        self._restart_after_restore = False
        self.selected_eqn: str | None = None
        self.selected_dn: str | None = None
        self.student_navigation = StudentNavigationState()

        self.setWindowTitle("DLU Lab — Siemens EWSD Educational Simulator")
        self.resize(1580, 940)
        self.setMinimumSize(1180, 680)
        self._build_ui()
        self._apply_style()
        self.show_hardware_home()
        self.refresh_status()
        self.terminal.append(
            "<span style='color:{MUTED}'>DLU Lab ready. "
            "University Communications Laboratory. Use QUICK RUN or type &gt; help;</span>"
        )

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(10, 10, 10, 10)
        main.setSpacing(8)

        header = QFrame()
        header.setObjectName("Header")
        h = QHBoxLayout(header)
        h.setContentsMargins(12, 8, 12, 8)

        title = QLabel("DLU LAB")
        title.setObjectName("Title")
        h.addWidget(title)
        h.addWidget(QLabel("Siemens EWSD · Hardware-first training lab"))
        h.addStretch()
        h.addWidget(QLabel("ALE1 · DLU"))
        self.dlu_combo = QComboBox()
        for row in self.db.list_dlus():
            self.dlu_combo.addItem(str(row["dlu_id"]))
        self.dlu_combo.currentTextChanged.connect(
            lambda value: self.show_dlu(int(value)) if value else None
        )
        h.addWidget(self.dlu_combo)

        self.physical_btn = QPushButton("PHYSICAL")
        self.logical_btn = QPushButton("LOGICAL")
        self.physical_btn.clicked.connect(lambda: self.set_mode("physical"))
        self.logical_btn.clicked.connect(lambda: self.set_mode("logical"))
        h.addWidget(self.physical_btn)
        h.addWidget(self.logical_btn)

        self.theme_btn = QPushButton("☾ NIGHT MODE")
        self.theme_btn.setObjectName("ThemeToggle")
        self.theme_btn.setToolTip("Switch to the night theme")
        self.theme_btn.clicked.connect(self.toggle_theme)
        h.addWidget(self.theme_btn)

        self.status_chip = QLabel("SYSTEM ACT")
        self.status_chip.setObjectName("StatusChip")
        h.addWidget(self.status_chip)
        main.addWidget(header)

        self.syp = QFrame()
        self.syp.setObjectName("SYP")
        syp = QHBoxLayout(self.syp)
        syp.setContentsMargins(10, 5, 10, 5)
        self.crit_label = QLabel("CRITICAL 0")
        self.major_label = QLabel("MAJOR 0")
        self.minor_label = QLabel("MINOR 0")
        self.traffic_label = QLabel("PDC 0/120")
        self.path_label = QLabel("PATH —")
        for widget in (
            self.crit_label, self.major_label, self.minor_label,
            self.traffic_label, self.path_label
        ):
            syp.addWidget(widget)
        syp.addStretch()
        main.addWidget(self.syp)

        split = QSplitter(Qt.Horizontal)
        split.setChildrenCollapsible(False)
        self.main_split = split
        main.addWidget(split, 1)

        left = QWidget()
        self.workspace_left = left
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        self.back_btn = QPushButton("←")
        self.back_btn.setToolTip("Back to the previous hardware level")
        self.back_btn.clicked.connect(self.go_back)
        toolbar.addWidget(self.back_btn)

        self.breadcrumb = QLabel("Hardware Selection")
        self.breadcrumb.setObjectName("Breadcrumb")
        toolbar.addWidget(self.breadcrumb, 1)

        self.tools_btn = QToolButton()
        self.tools_btn.setObjectName("ToolsButton")
        self.tools_btn.setText("TOOLS")
        self.tools_btn.setPopupMode(QToolButton.InstantPopup)
        tool_menu = QMenu(self)
        theme_menu = tool_menu.addMenu("THEME")
        ivory_action = theme_menu.addAction("Brown + Ivory")
        silver_action = theme_menu.addAction("Brown + Silver")
        ivory_action.triggered.connect(lambda: self.set_theme("ivory"))
        silver_action.triggered.connect(lambda: self.set_theme("silver"))

        library_action = tool_menu.addAction("Hardware Library")
        library_action.triggered.connect(self.open_library)

        backup_action = tool_menu.addAction("Backup Database")
        backup_action.triggered.connect(self.backup_database)
        restore_action = tool_menu.addAction("Restore Database")
        restore_action.triggered.connect(self.restore_database)
        data_folder_action = tool_menu.addAction("Open Data Folder")
        data_folder_action.triggered.connect(self.open_data_folder)

        reset_action = tool_menu.addAction("Reset Demo")
        reset_action.triggered.connect(self.confirm_reset_demo)
        self.tools_btn.setMenu(tool_menu)
        toolbar.addWidget(self.tools_btn)

        self.fit_btn = QPushButton("FIT")
        self.fit_btn.setObjectName("FitHardwareButton")
        self.fit_btn.setToolTip("Fit hardware to view")
        self.fit_btn.clicked.connect(lambda: self.hardware.reset_zoom())
        toolbar.addWidget(self.fit_btn)
        ll.addLayout(toolbar)

        navigator = QFrame()
        navigator.setObjectName("Navigator")
        nav = QHBoxLayout(navigator)
        nav.setContentsMargins(10, 8, 10, 8)
        nav.setSpacing(7)

        nav_title = QLabel("PATH")
        nav_title.setObjectName("NavigatorTitle")
        nav.addWidget(nav_title)

        self.nav_dlu_combo = QComboBox()
        for row in self.db.list_dlus():
            self.nav_dlu_combo.addItem(str(row["dlu_id"]))
        self.nav_dlu_combo.setToolTip("Choose DLU")
        nav.addWidget(QLabel("DLU"))
        nav.addWidget(self.nav_dlu_combo)

        nav.addWidget(QLabel("SHELF"))
        self.nav_shelf_combo = QComboBox()
        self.nav_shelf_combo.addItems([str(i) for i in range(8)])
        nav.addWidget(self.nav_shelf_combo)

        nav.addWidget(QLabel("MODULE"))
        self.nav_module_combo = QComboBox()
        nav.addWidget(self.nav_module_combo, 1)

        self.open_module_btn = QPushButton("OPEN MODULE")
        self.open_module_btn.setObjectName("OpenModuleButton")
        self.open_module_btn.clicked.connect(self.open_selected_module)
        nav.addWidget(self.open_module_btn)

        self.nav_dlu_combo.currentTextChanged.connect(
            lambda _: self.refresh_nav_modules()
        )
        self.nav_shelf_combo.currentTextChanged.connect(
            lambda _: self.refresh_nav_modules()
        )
        self.nav_menu_btn = QToolButton()
        self.nav_menu_btn.setObjectName("NavigationMenuButton")
        self.nav_menu_btn.setText("NAV")
        self.nav_menu_btn.setPopupMode(QToolButton.InstantPopup)
        nav_menu = QMenu(self)
        nav_dlu_action = nav_menu.addAction("Open DLU")
        nav_dlu_action.triggered.connect(self.open_selected_dlu)
        nav_shelf_action = nav_menu.addAction("Open Shelf")
        nav_shelf_action.triggered.connect(self.open_selected_shelf)
        nav_module_action = nav_menu.addAction("Open Module")
        nav_module_action.triggered.connect(self.open_selected_module)
        self.nav_menu_btn.setMenu(nav_menu)
        nav.addWidget(self.nav_menu_btn)

        ll.addWidget(navigator)
        self.refresh_nav_modules()

        scenarios = QFrame()
        scenarios.setObjectName("ScenarioBar")
        scenario_layout = QHBoxLayout(scenarios)
        scenario_layout.setContentsMargins(10, 8, 10, 8)
        scenario_layout.setSpacing(8)

        scenario_title = QLabel("LAB ACTIONS")
        scenario_title.setObjectName("ScenarioTitle")
        scenario_layout.addWidget(scenario_title)

        self.eight_line_btn = QPushButton("8-LINE LAB")
        self.eight_line_btn.setObjectName("PrimaryScenario")
        self.eight_line_btn.clicked.connect(self.run_8_line)
        self.eight_line_btn.setToolTip("Create eight subscriber lines on an SLMA8")
        scenario_layout.addWidget(self.eight_line_btn)

        self.cmrl_btn = QPushButton("CMRL LAB")
        self.cmrl_btn.setObjectName("PrimaryScenario")
        self.cmrl_btn.clicked.connect(self.run_cmrl)
        self.cmrl_btn.setToolTip("Demonstrate the six-port CMRL capacity guard")
        scenario_layout.addWidget(self.cmrl_btn)

        self.maintenance_btn = QPushButton("MAINTENANCE")
        self.maintenance_btn.clicked.connect(self.run_maintenance_demo)
        scenario_layout.addWidget(self.maintenance_btn)

        self.inspect_btn = QPushButton("INSPECT")
        self.inspect_btn.clicked.connect(self.run_inspect)
        scenario_layout.addWidget(self.inspect_btn)
        scenario_layout.addStretch()
        ll.addWidget(scenarios)

        self.hardware = HardwareView()
        self.hardware.controller = self
        ll.addWidget(self.hardware, 1)

        self.legend = QLabel(
            "Hardware: gray=unconfigured · steel=inactive · green=ACT · "
            "yellow=MBL · red=fault · blue=test | "
            "Ports: gray=unassigned · green=idle · red=busy · yellow=blocked"
        )
        self.legend.setObjectName("Legend")
        ll.addWidget(self.legend)
        split.addWidget(left)

        right = QTabWidget()
        self.feature_tabs = right
        self.learning_home = LearningHomeWidget(
            on_navigate=self.navigate_student_area,
            parent=self,
        )
        right.addTab(self.learning_home, "Learning Home")

        self.omt_tab = QWidget()
        olt = QVBoxLayout(self.omt_tab)
        olt.setContentsMargins(10, 10, 10, 10)
        olt.setSpacing(8)

        omt_header = QFrame()
        omt_header.setObjectName("WorkbenchHeader")
        omt_head = QHBoxLayout(omt_header)
        omt_head.addWidget(QLabel("OMT / MML"))
        omt_head.addWidget(QLabel("Operations & Maintenance · real MML workflow"), 1)
        omt_head.addWidget(QLabel("ONLINE"), 0, Qt.AlignRight)
        olt.addWidget(omt_header)

        command_help = QLabel(
            "Run real MML commands. Examples: > help; · > stat dlu: dlu=50; · "
            "> disp dlumod: dlu=50, shelf=0, module=15;"
        )
        command_help.setObjectName("CommandHint")
        command_help.setWordWrap(True)
        olt.addWidget(command_help)

        command_examples = QFrame()
        command_examples.setObjectName("CommandDock")
        examples_layout = QHBoxLayout(command_examples)
        examples_layout.setContentsMargins(8, 6, 8, 6)
        examples_layout.setSpacing(6)
        examples_layout.addWidget(QLabel("QUICK RUN"))
        self.quick_run_buttons = {}
        for label, command in (
            ("HELP", "> help;"),
            ("DLU STATUS", "> stat dlu: dlu=50;"),
            ("MODULE 50-0-15", "> disp dlumod: dlu=50, shelf=0, module=15;"),
            ("PORT 50-0-15-0", "> statport: eqn=50-0-15-0;"),
        ):
            button = QPushButton(label)
            button.setAutoDefault(False)
            button.clicked.connect(
                lambda _checked=False, value=command: self.set_command_text(value)
            )
            examples_layout.addWidget(button)
            self.quick_run_buttons[label] = button
        clear_button = QPushButton("CLEAR")
        clear_button.setObjectName("ClearTerminalButton")
        clear_button.clicked.connect(lambda: self.terminal.clear())
        examples_layout.addWidget(clear_button)
        self.quick_run_buttons["CLEAR"] = clear_button
        examples_layout.addStretch(1)
        olt.addWidget(command_examples)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setObjectName("Terminal")
        self.terminal.setMinimumHeight(180)
        olt.addWidget(self.terminal, 1)

        command_dock = QFrame()
        command_dock.setObjectName("CommandDock")
        command_layout = QHBoxLayout(command_dock)
        command_layout.setContentsMargins(10, 8, 10, 8)
        command_layout.setSpacing(8)

        prompt = QLabel(">")
        prompt.setObjectName("CommandPrompt")
        command_layout.addWidget(prompt)

        self.input = QLineEdit()
        self.input.setObjectName("MmlInput")
        self.input.setPlaceholderText("Type MML: > statport: eqn=50-0-15-0;")
        self.input.setMinimumHeight(42)
        self.input.returnPressed.connect(self.execute_input)
        self.input.installEventFilter(self)
        command_layout.addWidget(self.input, 1)

        self.execute_button = QPushButton("RUN")
        self.execute_button.setObjectName("CommandSend")
        self.execute_button.setMinimumHeight(42)
        self.execute_button.clicked.connect(self.execute_input)
        command_layout.addWidget(self.execute_button)

        self.command_status = QLabel("READY · Enter a command or use QUICK RUN")
        self.command_status.setObjectName("CommandStatus")
        command_layout.addWidget(self.command_status)

        olt.addWidget(command_dock)
        self.omt_tab.setLayout(olt)
        right.addTab(self.omt_tab, "OMT")

        self.command_file_lab = CommandFileLab(
            self.mml.command_files,
            parent=self,
        )
        right.addTab(self.command_file_lab, "Command Files")

        self.call_lab = CallLabWidget(
            self.call_engine,
            on_state_changed=self._on_call_state_changed,
            parent=self,
        )
        right.addTab(self.call_lab, "Call Path")

        self.communications_lab = CommunicationsLabWidget(parent=self)
        right.addTab(self.communications_lab, "Communications")

        self.teaching_scenarios = TeachingScenariosWidget(
            self.db,
            self.mml,
            on_state_changed=self._on_scenario_state_changed,
            on_reset_demo=self.reset_demo,
            parent=self,
        )
        right.addTab(self.teaching_scenarios, "Scenarios")

        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        self.details_empty = QLabel("Select a hardware object to see technical details.")
        self.details_empty.setObjectName("DetailsEmptyState")
        self.details_empty.setWordWrap(True)
        info_layout.addWidget(self.details_empty)
        self.details = QTableWidget(0, 2)
        self.details.setObjectName("HardwareDetailsTable")
        self.details.setHorizontalHeaderLabels(["Field", "Value"])
        self.details.horizontalHeader().setStretchLastSection(True)
        info_layout.addWidget(self.details, 1)
        self.event_log = QTextEdit()
        self.event_log.setObjectName("HardwareEventLog")
        self.event_log.setReadOnly(True)
        self.event_log.setMaximumHeight(150)
        self.event_log.setObjectName("Terminal")
        info_layout.addWidget(self.event_log)

        buttons = QHBoxLayout()
        self.info_action_buttons = {}
        for label, handler in (
            ("COPY MML", self.copy_selected_mml),
            ("REFERENCE", self.open_selected_reference),
            ("FAULT", self.inject_selected_fault),
            ("DIAG", self.diagnose_selected),
            ("REMOVE", self.remove_selected_card),
            ("INSTALL", self.install_selected_card),
            ("ACTIVATE", self.activate_selected_card),
        ):
            b = QPushButton(label)
            b.clicked.connect(handler)
            buttons.addWidget(b)
            self.info_action_buttons[label] = b
        info_layout.addLayout(buttons)
        info_tab.setLayout(info_layout)
        right.addTab(info_tab, "Hardware")
        right.addTab(self.learning_home, "Learning Home")

        split.addWidget(right)
        split.setSizes([1060, 500])
        self.learning_home.setMinimumWidth(560)

        self.nav_dlu_combo.currentTextChanged.connect(
            lambda _: self.sync_header_dlu()
        )

    def _apply_style(self):
        self.setStyleSheet(
            f"""
            QWidget {{
                background:{BG};
                color:{TEXT};
                font-family:Segoe UI;
                font-size:13px;
            }}
            QMainWindow {{
                background:{BG};
            }}
            QFrame#Header {{
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {PANEL}, stop:0.62 {PANEL3}, stop:1 {PANEL3});
                border:1px solid {BORDER};
                border-radius:12px;
            }}
            QFrame#SYP, QFrame#Navigator, QFrame#ScenarioBar, QFrame#WorkbenchHeader,
            QFrame#CommandDock {{
                background:{PANEL};
                border:1px solid {BORDER};
                border-radius:10px;
            }}
            QLabel#Title {{
                font-size:26px;
                font-weight:900;
                letter-spacing:1px;
            }}
            QLabel#Breadcrumb {{
                color:{TEXT};
                font-size:14px;
                font-weight:800;
                padding-left:6px;
            }}
            QLabel#NavigatorTitle {{
                color:{CYAN};
                font-weight:900;
                letter-spacing:1px;
            }}
            QLabel#ScenarioTitle {{
                color:{CYAN};
                font-weight:900;
                letter-spacing:1px;
            }}
            QLabel#Legend {{
                color:{MUTED};
                padding:3px 6px;
            }}
            QPushButton#ThemeToggle {{
                background:{PANEL3};
                color:{TEXT};
                border:1px solid {CYAN};
                border-radius:9px;
                padding:8px 11px;
                font-weight:900;
            }}
            QPushButton#ThemeToggle:hover {{
                background:{CARD};
                border-color:{AMBER};
            }}
            QLabel#StatusChip {{
                background:{PANEL3};
                color:{GREEN};
                border:1px solid {GREEN};
                border-radius:14px;
                padding:6px 12px;
                font-weight:900;
            }}
            QLabel#CommandPrompt {{
                color:{CYAN};
                font-size:18px;
                font-weight:900;
            }}
            QFrame#WorkbenchHeader QLabel {{
                color:{MUTED};
                font-weight:700;
            }}
            QFrame#WorkbenchHeader QLabel:first-child {{
                color:{TEXT};
                font-size:16px;
                font-weight:900;
            }}
            QFrame#CommandDock {{
                background:{PANEL2};
                border:1px solid {BORDER};
            }}
            QPushButton, QToolButton {{
                background:{PANEL2};
                border:1px solid {BORDER};
                border-radius:8px;
                padding:8px 12px;
                color:{TEXT};
                font-weight:700;
            }}
            QPushButton:hover, QToolButton:hover {{
                background:{PANEL3};
                border-color:{CYAN};
            }}
            QPushButton:pressed, QToolButton:pressed {{
                background:{PANEL3};
            }}
            QPushButton:disabled {{
                color:{MUTED};
                background:{DEEP};
                border-color:{BORDER};
            }}
            QPushButton#PrimaryScenario {{
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {PANEL3}, stop:1 {PANEL3});
                border:1px solid {CYAN};
                min-width:120px;
                padding:10px 14px;
                font-weight:900;
            }}
            QPushButton#PrimaryScenario:hover {{
                background:{CARD};
            }}
            QPushButton#CommandSend {{
                background:{PANEL3};
                border:1px solid {CYAN};
                min-width:88px;
                font-weight:900;
            }}
            QComboBox {{
                background:{DEEP};
                border:1px solid {BORDER};
                border-radius:8px;
                padding:7px 9px;
                min-height:28px;
            }}
            QComboBox:hover {{
                border-color:{CYAN};
            }}
            QLineEdit {{
                background:{DEEP};
                border:1px solid {BORDER};
                border-radius:8px;
                padding:8px 10px;
                color:{TEXT};
            }}
            QLineEdit:focus {{
                border:2px solid {CYAN};
                background:{PANEL};
            }}
            QComboBox, QLineEdit, QTextEdit, QTableWidget, QListWidget {{
                selection-background-color:{PANEL3};
                selection-color:{WHITE};
            }}
            QTextEdit#Terminal {{
                background:{DEEP};
                border:1px solid {BORDER};
                border-radius:9px;
                font-family:Cascadia Mono, Consolas, monospace;
                font-size:12px;
                padding:10px;
            }}
            QTableWidget {{
                background:{PANEL2};
                border:1px solid {BORDER};
                gridline-color:{BORDER};
            }}
            QHeaderView::section {{
                background:{PANEL3};
                color:{TEXT};
                border:0;
                padding:7px;
                font-weight:800;
            }}
            QTabWidget::pane {{
                background:{PANEL2};
                border:1px solid {BORDER};
                border-radius:9px;
            }}
            QTabBar::tab {{
                background:{PANEL2};
                color:{MUTED};
                border:1px solid {BORDER};
                border-bottom:0;
                padding:9px 16px;
                margin-right:3px;
                border-top-left-radius:8px;
                border-top-right-radius:8px;
                font-weight:800;
            }}
            QTabBar::tab:selected {{
                background:{PANEL3};
                color:{TEXT};
                border-color:{CYAN};
            }}
            QMenu {{
                background:{PANEL2};
                color:{TEXT};
                border:1px solid {BORDER};
            }}
            QMenu::item:selected {{
                background:{PANEL3};
            }}
            QSplitter::handle {{
                background:{DEEP};
            }}
            """
        )

    def toggle_theme(self):
        self.set_theme("night" if THEME_NAME == "morning" else "morning")

    def set_theme(self, name: str):
        resolved = "night" if name in {"night", "dark", "silver", "control_room"} else "morning"
        apply_theme_palette(resolved)
        apply_hardware_theme(resolved)
        self.hardware.setBackgroundBrush(QColor(BG))
        if hasattr(self, "theme_btn"):
            self.theme_btn.setText(
                "☾ NIGHT MODE" if resolved == "morning" else "☀ DAY MODE"
            )
            self.theme_btn.setToolTip(
                "Switch to the night theme"
                if resolved == "morning"
                else "Switch to the morning theme"
            )
        self._apply_style()
        from .app_style import apply_application_style
        from .stage8_ui import restyle_stage8_ui
        from .stage9_ui import update_stage9_context, update_stage9_theme
        app = QApplication.instance()
        if app is not None:
            apply_application_style(app, resolved)
        if hasattr(self, "call_lab") and hasattr(self.call_lab, "set_theme"):
            self.call_lab.set_theme(resolved)
        if hasattr(self, "communications_lab") and hasattr(self.communications_lab, "set_theme"):
            self.communications_lab.set_theme(resolved)
        if hasattr(self, "teaching_scenarios") and hasattr(self.teaching_scenarios, "set_theme"):
            self.teaching_scenarios.set_theme(resolved)
        if hasattr(self, "learning_home"):
            self.learning_home.set_theme(resolved)
        restyle_stage8_ui(self, resolved)
        if self.property("dlu_stage9_enabled"):
            update_stage9_theme(self, resolved)
        self._refresh_current_view()
        if self.property("dlu_stage17_enabled"):
            from .stage17_accessibility import refresh_stage17_accessibility
            refresh_stage17_accessibility(self, resolved)

    def set_mode(self, mode: str):
        self.mode = mode
        self._refresh_current_view()
        self.physical_btn.setEnabled(mode != "physical")
        self.logical_btn.setEnabled(mode != "logical")

    def _set_details(self, details: dict):
        self.details.setRowCount(0)
        if hasattr(self, "details_empty"):
            self.details_empty.setVisible(not bool(details))
        for k,v in details.items():
            row=self.details.rowCount()
            self.details.insertRow(row)
            self.details.setItem(row,0,QTableWidgetItem(str(k)))
            self.details.setItem(row,1,QTableWidgetItem(str(v)))

    def focus_result(self, result: MmlResult):
        data = result.data
        candidates = []
        if isinstance(data, dict):
            candidates = [data]
        elif isinstance(data, list):
            candidates = [x for x in data if isinstance(x, dict)]

        # Prefer an exact EQN target, otherwise an explicit DLU/Shelf/Module target.
        for item in candidates:
            eqn = item.get("eqn")
            if eqn:
                try:
                    dlu, shelf, module, port = map(int, str(eqn).split("-"))
                except ValueError:
                    continue
                self._sync_location(dlu, shelf, module)
                self.show_module(dlu, shelf, module)
                self.select_port(dlu, shelf, module, port)
                self.breadcrumb.setText(
                    f"DLU {dlu}  /  SHELF {shelf}  /  MODULE {module}  /  PORT {port}"
                )
                return

        for item in candidates:
            if all(k in item for k in ("dlu", "shelf", "module")):
                dlu = int(item["dlu"])
                shelf = int(item["shelf"])
                module = int(item["module"])
                self._sync_location(dlu, shelf, module)
                self.show_module(dlu, shelf, module)
                self.breadcrumb.setText(
                    f"DLU {dlu}  /  SHELF {shelf}  /  MODULE {module}"
                )
                return

    def refresh_event_log(self):
        if not hasattr(self, "event_log"):
            return
        if self.current_view != "module":
            self.event_log.setPlainText("No module selected.")
            return
        rows = self.db.conn.execute(
            """
            SELECT event_type, old_card, new_card, note, created_at
            FROM hardware_events
            WHERE dlu_id=? AND shelf=? AND module=?
            ORDER BY event_id DESC
            LIMIT 12
            """,
            (
                self.hardware.current_dlu,
                self.hardware.current_shelf,
                self.hardware.current_module,
            ),
        ).fetchall()
        if not rows:
            self.event_log.setPlainText("Maintenance timeline: no events.")
            return
        lines = ["MAINTENANCE TIMELINE"]
        for row in rows:
            lines.append(
                f"{row['created_at']} · {row['event_type']} · "
                f"{row['old_card'] or '—'} → {row['new_card'] or '—'} · "
                f"{row['note'] or ''}"
            )
        self.event_log.setPlainText("\\n".join(lines))

    def set_command_text(self, command: str):
        self.input.setText(command)
        self.input.setFocus()
        self.input.selectAll()
        if hasattr(self, "command_status"):
            self.command_status.setText("READY · Review the command and press RUN")

    def execute_input(self):
        command = self.input.text().strip()
        if not command:
            if hasattr(self, "command_status"):
                self.command_status.setText("READY · Enter a command first")
            self.input.setFocus()
            return
        if not command.startswith(">"):
            command = "> " + command
        self.history.append(command)
        self.history_index = len(self.history)
        self.input.clear()
        self._execute_command(command)

    def _execute_command(self, command: str):
        self.terminal.append(
            f"<span style='color:{TEXT}'>&gt; {command[1:].strip()}</span>"
        )
        try:
            result = self.mml.execute(command)
        except Exception as exc:
            self.terminal.append(
                f"<span style='color:{RED}'>[UI-EXEC-ERROR] {exc}</span>"
            )
            if hasattr(self, "command_status"):
                self.command_status.setText("ERROR · Command execution raised an exception")
            self.input.setFocus()
            return

        color = GREEN if result.ok else RED
        self.terminal.append(
            f"<span style='color:{color}'>[{result.code}] {result.message}</span>"
        )
        if result.data is not None:
            pretty = json.dumps(
                result.data,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
            self.terminal.append(
                f"<pre style='color:{MUTED}'>{pretty}</pre>"
            )
        if hasattr(self, "command_status"):
            self.command_status.setText(
                f"{'OK' if result.ok else 'ERROR'} · {result.code} · {result.message}"
            )
        if hasattr(self, "stage11_controller"):
            self.stage11_controller.on_command_result(command, result)
        self.student_navigation.visit(
            "OMT / MML",
            f"OMT / MML · {'Command succeeded' if result.ok else 'Command failed'}",
        )
        self._refresh_learning_home()
        QTimer.singleShot(0, lambda result=result: self.focus_result(result))
        self.refresh_status()
        self.input.setFocus()

    def copy_selected_mml(self):
        if not self.selected_eqn:
            return
        command = (
            f"> statport: eqn={self.selected_eqn};"
            if self.selected_dn else
            f"> disp dlupport: eqn={self.selected_eqn};"
        )
        QApplication.clipboard().setText(command)
        self.terminal.append(
            f"<span style='color:{GREEN}'>Copied: {command}</span>"
        )

    def open_selected_reference(self):
        card = None
        if self.current_view == "module":
            slot = self._slot_mapping(
                self.db.get_slot(
                    self.hardware.current_dlu,
                    self.hardware.current_shelf,
                    self.hardware.current_module
                )
            )
            if slot:
                card = slot.get("card_type")
        if card:
            ref=self.db.get_card_reference(card)
            if ref:
                ReferenceDialog(ref,self).exec()

    def open_library(self):
        if getattr(self, "library_dialog", None) is not None:
            self.library_dialog.raise_()
            self.library_dialog.activateWindow()
            return
        self.library_dialog = CardLibraryDialog(self.db, self)
        self.library_dialog.setWindowModality(Qt.NonModal)
        self.library_dialog.setAttribute(Qt.WA_DeleteOnClose, True)
        self.library_dialog.destroyed.connect(
            lambda: setattr(self, "library_dialog", None)
        )
        self.library_dialog.show()

    def inject_selected_fault(self):
        if self.current_view != "module":
            QMessageBox.information(self,"Select module","Open a module first.")
            return
        try:
            self.db.inject_fault(
                self.hardware.current_dlu,
                self.hardware.current_shelf,
                self.hardware.current_module
            )
            self.terminal.append(
                f"<span style='color:{YELLOW}'>Fault injected on "
                f"{self.hardware.current_dlu}-{self.hardware.current_shelf}-{self.hardware.current_module}</span>"
            )
            self._refresh_current_view()
        except ValueError as exc:
            QMessageBox.warning(self,"Fault",str(exc))

    def diagnose_selected(self):
        if self.current_view != "module":
            return
        dlu=self.hardware.current_dlu
        shelf=self.hardware.current_shelf
        module=self.hardware.current_module
        result=self.mml.execute(
            f"> diag dlumod: dlu={dlu}, shelf={shelf}, module={module};"
        )
        self._show_result(result)
        self._refresh_current_view()

    def remove_selected_card(self):
        if self.current_view != "module":
            return
        try:
            old=self.db.remove_card(
                self.hardware.current_dlu,
                self.hardware.current_shelf,
                self.hardware.current_module
            )
            self.terminal.append(
                f"<span style='color:{GREEN}'>Removed {old} from "
                f"{self.hardware.current_dlu}-{self.hardware.current_shelf}-{self.hardware.current_module}</span>"
            )
            self._refresh_current_view()
        except ValueError as exc:
            QMessageBox.warning(self,"Remove Card",str(exc))

    def install_card_at(self, dlu: int, shelf: int, module: int, card_type: str):
        slot = self._slot_mapping(
            self.db.get_slot(dlu, shelf, module)
        )
        if not slot:
            QMessageBox.warning(self, "Install Card", "Target module does not exist.")
            return
        if slot.get("card_type") != "UNCONFIGURED":
            QMessageBox.warning(
                self,
                "Install Card",
                f"Module {dlu}-{shelf}-{module} already contains {slot.get('card_type')}.",
            )
            return
        ref = self.db.get_card_reference(card_type)
        if ref is None or not ref.verified:
            QMessageBox.warning(
                self,
                "Install Card",
                f"{card_type} is not in the verified hardware registry.",
            )
            return
        try:
            self.db.install_card(dlu, shelf, module, card_type)
            self.show_module(dlu, shelf, module)
            self.terminal.append(
                f"<span style='color:{GREEN}'>Drag&Drop installed "
                f"{card_type} at {dlu}-{shelf}-{module}</span>"
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Install Card", str(exc))

    def install_selected_card(self):
        if self.current_view != "module":
            return
        dialog=QDialog(self)
        dialog.setWindowTitle("Install verified replacement")
        form=QFormLayout(dialog)
        combo=QComboBox()
        for ref in self.db.list_card_references():
            if ref.verified and ref.code not in {"UNCONFIGURED"}:
                combo.addItem(
                    f"{ref.code} · {ref.port_count}P · {ref.role}",
                    ref.code
                )
        form.addRow("Card",combo)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addWidget(buttons)
        if dialog.exec()!=QDialog.Accepted:
            return
        try:
            card=combo.currentData()
            installed=self.db.install_card(
                self.hardware.current_dlu,
                self.hardware.current_shelf,
                self.hardware.current_module,
                card
            )
            self.terminal.append(
                f"<span style='color:{GREEN}'>Installed {installed} in "
                f"{self.hardware.current_dlu}-{self.hardware.current_shelf}-{self.hardware.current_module}</span>"
            )
            self._refresh_current_view()
        except ValueError as exc:
            QMessageBox.warning(self,"Install Card",str(exc))

    def activate_selected_card(self):
        if self.current_view != "module":
            return
        try:
            card=self.db.activate_card(
                self.hardware.current_dlu,
                self.hardware.current_shelf,
                self.hardware.current_module
            )
            self.terminal.append(
                f"<span style='color:{GREEN}'>Activated {card}</span>"
            )
            self._refresh_current_view()
        except ValueError as exc:
            QMessageBox.warning(self,"Activate",str(exc))

    def run_8_line(self):
        dialog=HardwareSelectorDialog(self.db,self,card_type="SLMA8")
        if dialog.exec()!=QDialog.Accepted or dialog.selected is None:
            return
        dlu,shelf,module=dialog.selected
        self.show_module(dlu,shelf,module)
        for i in range(8):
            command=(
                f"> cr sub: dlu={dlu}, type=ms, "
                f"eqn={dlu}-{shelf}-{module}-{i}, lac=021, dn={2233500+i};"
            )
            self._execute_command(command)

    def run_cmrl(self):
        dialog=HardwareSelectorDialog(self.db,self,card_type="CMRL")
        if dialog.exec()!=QDialog.Accepted or dialog.selected is None:
            return
        dlu,shelf,module=dialog.selected
        self.show_module(dlu,shelf,module)
        for i in range(6):
            self._execute_command(
                f"> cr sub: dlu={dlu}, type=cmrl, "
                f"eqn={dlu}-{shelf}-{module}-{i}, lac=021, dn={2250500+i};"
            )
        self._execute_command(
            f"> cr sub: dlu={dlu}, type=cmrl, "
            f"eqn={dlu}-{shelf}-{module}-6, lac=021, dn=2250506;"
        )
        self.terminal.append(
            f"<span style='color:{AMBER}'>CMRL guard demo: next port 6 must be rejected.</span>"
        )

    def run_maintenance_demo(self):
        if self.current_view != "module":
            QMessageBox.information(
                self,"Maintenance",
                "Open a configured module, then use Maintenance."
            )
            return
        self.inject_selected_fault()

    def run_inspect(self):
        dlu=self.hardware.current_dlu
        shelf=self.hardware.current_shelf
        module=self.hardware.current_module
        self._execute_command(
            f"> disp dlumod: dlu={dlu}, shelf={shelf}, module={module};"
        )

    def _show_result(self,result:MmlResult):
        color=GREEN if result.ok else RED
        self.terminal.append(
            f"<span style='color:{color}'>[{result.code}] {result.message}</span>"
        )
        if result.data is not None:
            self.terminal.append(
                f"<pre style='color:{MUTED}'>{json.dumps(result.data,ensure_ascii=False,indent=2,default=str)}</pre>"
            )
        if hasattr(self, "stage11_controller"):
            self.stage11_controller.on_command_result(None, result)
        self.focus_result(result)

    def _student_tab_index(self, area: str) -> int | None:
        aliases = {
            "OMT / MML": {"OMT / MML", "OMT"},
            "CALLS": {"CALLS", "Call Path"},
            "COMMANDS": {"COMMANDS", "COMMAND FILES", "Command Files"},
            "COMMS LAB": {"COMMS LAB", "Communications"},
            "SCENARIOS": {"SCENARIOS", "Scenarios"},
            "HARDWARE": {"HARDWARE", "Hardware"},
        }
        targets = aliases.get(area, set())
        for index in range(self.feature_tabs.count()):
            if self.feature_tabs.tabText(index) in targets:
                return index
        return None

    def _learning_home_status(self) -> str:
        alarms = len(self.db.list_active_alarms())
        used, capacity = self.call_engine.resource_usage()
        current = self.db.get_dlu(self.hardware.current_dlu)
        system = "ACTIVE" if current and (
            current["dluc0_state"] == "act" or current["dluc1_state"] == "act"
        ) else "DEGRADED"
        return f"System {system} · Alarms {alarms} · PDC {used}/{capacity}"

    def _refresh_learning_home(self) -> None:
        if not hasattr(self, "learning_home"):
            return
        context = self.student_navigation.current_context
        visited = self.student_navigation.visited_count
        if visited == 0:
            continue_target = "HARDWARE"
            next_step = "Start with Hardware: identify the DLU hierarchy before using advanced tools."
        elif "HARDWARE" not in self.student_navigation.visited_areas:
            continue_target = "HARDWARE"
            next_step = "Explore Hardware to connect the physical DLU hierarchy with MML."
        elif "OMT / MML" not in self.student_navigation.visited_areas:
            continue_target = "OMT / MML"
            next_step = "Run a simple MML status command and see it focus the matching object."
        elif "CALLS" not in self.student_navigation.visited_areas:
            continue_target = "CALLS"
            next_step = "Trace a call and explain its route and resource state."
        elif "COMMS LAB" not in self.student_navigation.visited_areas:
            continue_target = "COMMS LAB"
            next_step = "Run one communications experiment and compare the visual result."
        elif "SCENARIOS" not in self.student_navigation.visited_areas:
            continue_target = "SCENARIOS"
            next_step = "Practice a guided scenario and verify the expected result."
        else:
            continue_target = "COMMANDS"
            next_step = "Revisit any lab or practice Command Files for a multi-step workflow."

        try:
            from .stage9_ui import update_stage9_context
            update_stage9_context(self, context)
        except ImportError:
            pass
        self.learning_home.update_snapshot(
            current_context=context,
            continue_target=continue_target,
            progress_percent=self.student_navigation.progress_percent,
            visited_count=visited,
            recent_activity=list(self.student_navigation.recent_activity),
            hardware_status=self._learning_home_status(),
            next_step=next_step,
        )

    def show_learning_home(self):
        self.current_view = "learning_home"
        self.back_btn.setEnabled(False)
        self.breadcrumb.setText("LEARNING HOME")
        self.workspace_left.hide()
        self.feature_tabs.setCurrentWidget(self.learning_home)
        if not self.student_navigation.visited_areas:
            self.student_navigation.current_context = "Learning Home"
        if hasattr(self, "main_split"):
            self.main_split.setSizes([0, max(1, self.main_split.width())])
        self.student_navigation.visit("HOME", "Learning Home · choose your next step")
        self._refresh_learning_home()
        self.refresh_status()

    def navigate_student_area(self, area: str):
        area = area.strip()
        if area == "HOME":
            self.show_learning_home()
            for button in self.findChildren(QPushButton, "Stage8NavButton"):
                button.setChecked(False)
            home = self.findChild(QPushButton, "Stage9HomeButton")
            if home is not None:
                home.setChecked(True)
            return

        self.workspace_left.show()
        if hasattr(self, "main_split"):
            total = max(1, self.main_split.width())
            left_size = max(700, int(total * 0.68))
            self.main_split.setSizes([left_size, max(1, total - left_size)])

        if area == "HARDWARE":
            self.show_hardware_home()
            self.student_navigation.visit("HARDWARE", "HARDWARE · DLU Fleet")
        else:
            index = self._student_tab_index(area)
            if index is None:
                return
            self.feature_tabs.setCurrentIndex(index)
            self.student_navigation.visit(area, area)
        for button in self.findChildren(QPushButton, "Stage8NavButton"):
            button.setChecked(button.text() == area)
        home = self.findChild(QPushButton, "Stage9HomeButton")
        if home is not None:
            home.setChecked(False)
        self._refresh_learning_home()

    def _refresh_current_view(self):
        if self.current_view=="learning_home":
            self._refresh_learning_home()
            self.feature_tabs.setCurrentWidget(self.learning_home)
        elif self.current_view=="home":
            self.show_hardware_home()
        elif self.current_view=="dlu":
            self.show_dlu(self.hardware.current_dlu)
        elif self.current_view=="shelf":
            self.show_shelf(self.hardware.current_dlu,self.hardware.current_shelf)
        else:
            self.show_module(
                self.hardware.current_dlu,
                self.hardware.current_shelf,
                self.hardware.current_module
            )

    def eventFilter(self,watched,event):
        if watched is self.input and event.type()==QEvent.Type.KeyPress:
            if event.key()==Qt.Key_Up and self.history:
                self.history_index=max(0,self.history_index-1)
                self.input.setText(self.history[self.history_index])
                return True
            if event.key()==Qt.Key_Down and self.history:
                self.history_index=min(len(self.history),self.history_index+1)
                self.input.setText(
                    self.history[self.history_index]
                    if self.history_index<len(self.history) else ""
                )
                return True
        return super().eventFilter(watched,event)

    def go_back(self):
        if self.current_view=="module":
            self.show_shelf(self.hardware.current_dlu,self.hardware.current_shelf)
        elif self.current_view=="shelf":
            self.show_dlu(self.hardware.current_dlu)
        elif self.current_view=="dlu":
            self.show_hardware_home()
        else:
            self.show_hardware_home()

    def refresh_status(self):
        if not hasattr(self, "hardware") or self.hardware.scene() is None:
            return
        current=self.db.get_dlu(self.hardware.current_dlu)
        if current:
            act=current["dluc0_state"]=="act" or current["dluc1_state"]=="act"
            color=GREEN if act else YELLOW
            self.status_chip.setText(
                f"DLU {current['dlu_id']} · SYSTEM {'ACT' if act else 'DEGRADED'}"
            )
            self.status_chip.setStyleSheet(
                f"background:{PANEL3};color:{color};border:1px solid {color};"
                "border-radius:14px;padding:6px 12px;font-weight:900;"
            )
        counts={}
        for row in self.db.list_active_alarms():
            counts[row["severity"]]=counts.get(row["severity"],0)+1
        self.crit_label.setText(f"CRITICAL {counts.get('CRITICAL',0)}")
        self.major_label.setText(f"MAJOR {counts.get('MAJOR',0)}")
        self.minor_label.setText(f"MINOR {counts.get('MINOR',0)}")
        used, capacity = self.call_engine.resource_usage()
        active_calls = self.call_engine.active_call_count()
        self.traffic_label.setText(f"PDC {used}/{capacity}")
        self.path_label.setText("PATH ACTIVE" if active_calls else "PATH —")

    def _on_call_state_changed(self):
        if hasattr(self, "call_lab"):
            self.call_lab.refresh_subscribers()
        self.refresh_status()
        if getattr(self, "current_view", "home") == "module":
            self._refresh_current_view()

    def _on_scenario_state_changed(self):
        if hasattr(self, "call_lab"):
            self.call_lab.refresh_subscribers()
        self.refresh_status()
        if getattr(self, "current_view", "home") == "module":
            self._refresh_current_view()

    def confirm_reset_demo(self):
        answer = QMessageBox.question(
            self,
            "Reset Demo",
            "Reset teaching data, alarms, command files and subscriber records to the "
            "source-backed demo state?\\n\\nThis cannot be undone unless you have a backup.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self.reset_demo()

    def reset_demo(self):
        self.db.reset_demo()
        self.call_engine.repo.reset_demo()
        if hasattr(self, "call_lab"):
            self.call_lab.reset()
        if hasattr(self, "teaching_scenarios") and hasattr(self.teaching_scenarios, "reset_view_state"):
            self.teaching_scenarios.reset_view_state()
        if hasattr(self, "instructor_mode") and hasattr(self.instructor_mode, "reset_view_state"):
            self.instructor_mode.reset_view_state()
        if hasattr(self, "learning_home") and hasattr(self.learning_home, "reset_session_verification"):
            self.learning_home.reset_session_verification()
        self.student_navigation.recent_activity.insert(0, "Reset teaching demo · source-backed state restored")
        self.student_navigation.recent_activity = self.student_navigation.recent_activity[:8]
        self.student_navigation.current_context = "Learning Home" if self.current_view == "learning_home" else self.student_navigation.current_context
        self._refresh_learning_home()
        self.terminal.append(
            f"<span style='color:{YELLOW}'>"
            "[RESET] Source-backed hardware restored; subscriber demo state cleared."
            "</span>"
        )
        self._refresh_current_view()

    def backup_database(self):
        default_dir = DatabaseBackupManager.default_backup_dir(self.db.path)
        default_dir.mkdir(parents=True, exist_ok=True)
        default_name = default_dir / "dlu_lab_backup.sqlite3"
        target, _ = QFileDialog.getSaveFileName(
            self,
            "Backup DLU Lab database",
            str(default_name),
            "SQLite backup (*.sqlite3);;All files (*.*)",
        )
        if not target:
            return
        try:
            target_path = Path(target).resolve()
            if target_path == Path(self.db.path).resolve():
                raise BackupError("Backup target cannot be the live database file.")
            info = DatabaseBackupManager.create_backup(self.db.path, target_path)
            self.terminal.append(
                f"<span style='color:{GREEN}'>"
                f"[BACKUP] Created {info.path} · {info.size_bytes:,} bytes · integrity=ok"
                "</span>"
            )
            QMessageBox.information(
                self,
                "Backup Complete",
                f"Backup created successfully.\\n\\n{info.path}\\n\\nSQLite integrity: OK",
            )
        except BackupError as exc:
            QMessageBox.critical(self, "Backup Failed", str(exc))

    def restore_database(self):
        source, _ = QFileDialog.getOpenFileName(
            self,
            "Select DLU Lab backup",
            str(DatabaseBackupManager.default_backup_dir(self.db.path)),
            "SQLite backup (*.sqlite3);;All files (*.*)",
        )
        if not source:
            return
        try:
            info = DatabaseBackupManager.validate_backup(source)
        except BackupError as exc:
            QMessageBox.critical(self, "Invalid Backup", str(exc))
            return

        answer = QMessageBox.warning(
            self,
            "Restore Database",
            "This will replace the current database on application restart. "
            "A safety backup of the current database will be created automatically.\\n\\n"
            f"Selected: {info.path}\\n\\nContinue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return

        try:
            pending = DatabaseBackupManager.prepare_restore(self.db.path, info.path)
            self._restart_after_restore = True
            self.terminal.append(
                f"<span style='color:{YELLOW}'>"
                f"[RESTORE] Validated and staged {pending.name}. Application will restart."
                "</span>"
            )
            QMessageBox.information(
                self,
                "Restore Ready",
                "The backup is valid and staged safely. The application will now close. "
                "Launch DLU Lab again to continue with the restored database.",
            )
            self.close()
        except BackupError as exc:
            QMessageBox.critical(self, "Restore Failed", str(exc))

    def open_data_folder(self):
        data_dir = Path(self.db.path).resolve().parent
        data_dir.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(data_dir)))

    def closeEvent(self,event):
        db_path = Path(self.db.path).resolve()
        self.db.close()

        if self._restart_after_restore:
            try:
                DatabaseBackupManager.apply_pending_restore(db_path)
                subprocess.Popen([sys.executable, *sys.argv], close_fds=True)
            except (BackupError, OSError) as exc:
                QMessageBox.critical(
                    None,
                    "Restore Restart Failed",
                    f"The restore was validated but could not be applied/restarted.\\n\\n{exc}",
                )
        event.accept()
