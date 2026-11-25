from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication

from .app_style import apply_application_style
from .stage8_ui import apply_stage8_ui
from .stage9_ui import apply_stage9_ui
from .stage10_ui import apply_stage10_ui
from .stage11_ui import apply_stage11_ui
from .stage12_ui import apply_stage12_ui
from .stage13_ui import apply_stage13_ui
from .stage14_ui import apply_stage14_ui
from .stage15_ui import apply_stage15_ui
from .stage16_ui import apply_stage16_ui
from .stage17_accessibility import apply_stage17_accessibility
from .stage19_academic_ux import apply_stage19_academic_ux
from .ui import DluSimulatorWindow


STAGE_INSTALLERS = (
    apply_stage8_ui,
    apply_stage9_ui,
    apply_stage10_ui,
    apply_stage11_ui,
    apply_stage12_ui,
    apply_stage13_ui,
    apply_stage14_ui,
    apply_stage15_ui,
    apply_stage16_ui,
    apply_stage17_accessibility,
    apply_stage19_academic_ux,
)


def build_window(db_path: str | Path) -> DluSimulatorWindow:
    """Construct the simulator and apply the feature pipeline in one place."""
    window = DluSimulatorWindow(db_path)
    for installer in STAGE_INSTALLERS:
        installer(window)
    return window


def size_window_to_screen(window: DluSimulatorWindow, app: QApplication) -> None:
    """Keep desktop sizing policy outside the main startup script."""
    screen = app.primaryScreen()
    if screen is None:
        return
    available = screen.availableGeometry()
    width = min(1580, max(1180, available.width() - 40))
    height = min(940, max(680, available.height() - 80))
    window.resize(width, height)


def configure_application(app: QApplication) -> None:
    """Apply application-wide presentation settings."""
    apply_application_style(app)
