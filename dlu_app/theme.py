from __future__ import annotations

from dataclasses import dataclass

from .design_tokens import get_tokens, normalize_mode


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


def _palette(mode: str) -> ThemePalette:
    tokens = get_tokens(mode)
    return ThemePalette(
        BG=tokens.bg,
        PANEL=tokens.surface,
        PANEL2=tokens.surface_elevated,
        PANEL3=tokens.surface_interactive,
        STEEL=tokens.border_strong,
        TEXT=tokens.text_primary,
        MUTED=tokens.text_muted,
        BORDER=tokens.border,
        GREEN=tokens.success,
        YELLOW=tokens.warning,
        RED=tokens.danger,
        BLUE=tokens.info,
        CYAN=tokens.primary,
        VIOLET=tokens.primary,
        AMBER=tokens.warning,
        WHITE=tokens.white,
        CARD=tokens.card,
        DEEP=tokens.deep,
    )


MORNING = _palette("morning")
NIGHT = _palette("night")

# Compatibility aliases for existing feature widgets and saved test fixtures.
THEMES: dict[str, ThemePalette] = {
    "morning": MORNING,
    "night": NIGHT,
    "light": MORNING,
    "dark": NIGHT,
    "ivory": MORNING,
    "silver": NIGHT,
    "control_room": NIGHT,
}


def resolve_theme(name: str | None) -> str:
    return normalize_mode(name)
