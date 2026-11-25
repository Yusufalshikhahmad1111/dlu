from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGroupBox,
    QHeaderView,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QScrollBar,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTextEdit,
    QToolButton,
    QWidget,
)

from .design_tokens import get_tokens, normalize_mode


def build_qpalette(mode: str = "morning") -> QPalette:
    tokens = get_tokens(mode)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(tokens.bg))
    palette.setColor(QPalette.WindowText, QColor(tokens.text_primary))
    palette.setColor(QPalette.Base, QColor(tokens.surface))
    palette.setColor(QPalette.AlternateBase, QColor(tokens.surface_elevated))
    palette.setColor(QPalette.Text, QColor(tokens.text_primary))
    palette.setColor(QPalette.Button, QColor(tokens.surface))
    palette.setColor(QPalette.ButtonText, QColor(tokens.text_primary))
    palette.setColor(QPalette.Highlight, QColor(tokens.primary))
    palette.setColor(QPalette.HighlightedText, QColor(tokens.white))
    palette.setColor(QPalette.ToolTipBase, QColor(tokens.surface_elevated))
    palette.setColor(QPalette.ToolTipText, QColor(tokens.text_primary))
    palette.setColor(QPalette.PlaceholderText, QColor(tokens.text_muted))
    return palette


def apply_application_style(app: QApplication, mode: str = "morning") -> None:
    """Install one coherent product-wide Qt style for the selected mode."""
    mode = normalize_mode(mode)
    tokens = get_tokens(mode)
    app.setProperty("dlu_theme_mode", mode)
    app.setStyle("Fusion")
    app.setPalette(build_qpalette(mode))

    app.setStyleSheet(
        f"""
        QWidget {{
            color: {tokens.text_primary};
            font-family: "Segoe UI";
            font-size: 10pt;
        }}
        QToolTip {{
            color: {tokens.text_primary};
            background: {tokens.surface_elevated};
            border: 1px solid {tokens.border};
            padding: 6px 8px;
        }}
        QPushButton, QToolButton {{
            min-height: {tokens.control_height_sm}px;
            padding: 6px 13px;
            border: 1px solid {tokens.border};
            border-radius: {tokens.radius_sm}px;
            background: {tokens.surface};
            color: {tokens.text_primary};
            font-weight: 700;
        }}
        QPushButton:hover, QToolButton:hover {{
            background: {tokens.surface_interactive};
            border-color: {tokens.primary};
        }}
        QPushButton:pressed, QToolButton:pressed {{
            background: {tokens.surface_elevated};
            border-color: {tokens.primary};
        }}
        QPushButton:focus, QToolButton:focus {{
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
        QPushButton:disabled, QToolButton:disabled {{
            color: {tokens.text_muted};
            background: {tokens.bg};
            border-color: {tokens.border};
        }}
        QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {{
            min-height: {tokens.control_height_sm}px;
            padding: 5px 9px;
            border: 1px solid {tokens.border};
            border-radius: {tokens.radius_sm}px;
            background: {tokens.surface};
            color: {tokens.text_primary};
            selection-background-color: {tokens.primary};
            selection-color: {tokens.white};
        }}
        QComboBox:hover, QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {tokens.primary};
        }}
        QComboBox:focus, QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {tokens.primary};
        }}
        QTextEdit, QPlainTextEdit, QListWidget, QTableWidget {{
            border: 1px solid {tokens.border};
            border-radius: {tokens.radius_md}px;
            background: {tokens.surface};
            color: {tokens.text_primary};
            selection-background-color: {tokens.surface_interactive};
            selection-color: {tokens.text_primary};
        }}
        QHeaderView::section {{
            background: {tokens.surface_elevated};
            color: {tokens.text_secondary};
            border: 0;
            border-bottom: 1px solid {tokens.border};
            padding: 8px;
            font-weight: 800;
        }}
        QTableWidget::item:selected, QListWidget::item:selected {{
            background: {tokens.surface_interactive};
            border-left: 2px solid {tokens.primary};
        }}
        QTabWidget::pane {{
            background: {tokens.surface};
            border: 1px solid {tokens.border};
            border-radius: {tokens.radius_md}px;
        }}
        QTabBar::tab {{
            min-height: {tokens.control_height_sm}px;
            padding: 7px 14px;
            margin-right: 3px;
            background: {tokens.surface};
            color: {tokens.text_muted};
            border: 1px solid {tokens.border};
            border-bottom: 0;
            border-top-left-radius: {tokens.radius_sm}px;
            border-top-right-radius: {tokens.radius_sm}px;
        }}
        QTabBar::tab:hover {{
            color: {tokens.text_primary};
            background: {tokens.surface_interactive};
        }}
        QTabBar::tab:selected {{
            color: {tokens.text_primary};
            background: {tokens.surface_elevated};
            border-color: {tokens.primary};
            border-bottom: 2px solid {tokens.primary};
        }}
        QGroupBox {{
            border: 1px solid {tokens.border};
            border-radius: {tokens.radius_md}px;
            margin-top: 10px;
            padding-top: 10px;
            background: {tokens.surface};
            font-weight: 800;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: {tokens.text_secondary};
        }}
        QCheckBox {{
            spacing: 6px;
        }}
        QScrollBar:vertical {{
            background: {tokens.bg};
            width: 10px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical {{
            background: {tokens.border_strong};
            min-height: 30px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {tokens.primary};
        }}
        QScrollBar:horizontal {{
            background: {tokens.bg};
            height: 10px;
            margin: 2px;
        }}
        QScrollBar::handle:horizontal {{
            background: {tokens.border_strong};
            min-width: 30px;
            border-radius: 5px;
        }}
        """
    )


def restyle_application(app: QApplication, mode: str) -> None:
    apply_application_style(app, mode)
