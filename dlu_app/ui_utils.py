from __future__ import annotations

from PySide6.QtGui import QFont


MIN_FONT_SIZE = 8


def make_font(size: object, bold: bool = False, family: str = "Segoe UI") -> QFont:
    try:
        point_size = int(float(size))
    except (TypeError, ValueError):
        point_size = 12
    point_size = max(MIN_FONT_SIZE, point_size)
    font = QFont(family)
    font.setPointSize(point_size)
    font.setBold(bool(bold))
    return font
