from __future__ import annotations

from dataclasses import dataclass


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


THEMES: dict[str, ThemePalette] = {
    "ivory": ThemePalette(
        BG="#f3eadc", PANEL="#fffaf1", PANEL2="#eee3d2", PANEL3="#e4d5c0",
        STEEL="#7d6e5f", TEXT="#2f271f", MUTED="#746658", BORDER="#bda98f",
        GREEN="#2f8a68", YELLOW="#b67825", RED="#bd4f4f", BLUE="#806b5c",
        CYAN="#b66f42", VIOLET="#765e50", AMBER="#b67825", WHITE="#fffdf8",
        CARD="#f0e5d5", DEEP="#e6d8c5",
    ),
    "silver": ThemePalette(
        BG="#292825", PANEL="#3a3834", PANEL2="#2f2e2b", PANEL3="#47443f",
        STEEL="#aaa49a", TEXT="#f3efe8", MUTED="#c4bfb7", BORDER="#766f65",
        GREEN="#66c39b", YELLOW="#d2a35b", RED="#df7777", BLUE="#b2a79b",
        CYAN="#c08b63", VIOLET="#a58f84", AMBER="#d2a35b", WHITE="#fffdf8",
        CARD="#3f3d39", DEEP="#262522",
    ),
}
