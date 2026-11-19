from __future__ import annotations

from dataclasses import dataclass

from .design_tokens import TOKENS


@dataclass(frozen=True)
class ThemePalette:
    BG: str
    PANEL: str
    PANEL2: str
    PANEL3: str
    STEEL: str
    TEXT: str
    MUTED: str
    BORDER: str
    GREEN: str
    YELLOW: str
    RED: str
    BLUE: str
    CYAN: str
    VIOLET: str
    AMBER: str
    WHITE: str
    CARD: str
    DEEP: str


CONTROL_ROOM = ThemePalette(
    BG=TOKENS.bg,
    PANEL=TOKENS.surface,
    PANEL2=TOKENS.surface,
    PANEL3=TOKENS.surface_elevated,
    STEEL=TOKENS.border_strong,
    TEXT=TOKENS.text_primary,
    MUTED=TOKENS.text_muted,
    BORDER=TOKENS.border,
    GREEN=TOKENS.success,
    YELLOW=TOKENS.warning,
    RED=TOKENS.danger,
    BLUE=TOKENS.info,
    CYAN=TOKENS.primary,
    VIOLET="#A78BFA",
    AMBER=TOKENS.warning,
    WHITE=TOKENS.white,
    CARD=TOKENS.surface_interactive,
    DEEP=TOKENS.black,
)

# Compatibility aliases for feature widgets that still accept a legacy theme
# name. All aliases intentionally render the Stage 8 control-room palette.
THEMES: dict[str, ThemePalette] = {
    "control_room": CONTROL_ROOM,
    "ivory": CONTROL_ROOM,
    "silver": CONTROL_ROOM,
}
