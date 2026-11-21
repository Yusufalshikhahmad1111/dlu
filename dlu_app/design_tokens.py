from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stage8Tokens:
    """Shared visual tokens for the DLU Lab light/dark product themes."""

    bg: str
    surface: str
    surface_elevated: str
    surface_interactive: str
    border: str
    border_strong: str
    text_primary: str
    text_secondary: str
    text_muted: str
    primary: str
    success: str
    warning: str
    danger: str
    info: str
    white: str
    black: str
    deep: str
    card: str

    radius_sm: int = 6
    radius_md: int = 10
    radius_lg: int = 14

    space_1: int = 4
    space_2: int = 8
    space_3: int = 12
    space_4: int = 16
    space_5: int = 20
    space_6: int = 24
    space_7: int = 32

    control_height_sm: int = 32
    control_height_md: int = 38
    control_height_lg: int = 44


MORNING = Stage8Tokens(
    bg="#F5F7F2",
    surface="#FFFFFF",
    surface_elevated="#EFF4EC",
    surface_interactive="#E5EEE2",
    border="#D5DED2",
    border_strong="#AFBDA9",
    text_primary="#203027",
    text_secondary="#506057",
    text_muted="#76837B",
    primary="#2F7D5B",
    success="#2E8B57",
    warning="#B67A22",
    danger="#C94D3F",
    info="#5E8D73",
    white="#FFFFFF",
    black="#15231B",
    deep="#EAF1E7",
    card="#FBFCF9",
)

NIGHT = Stage8Tokens(
    bg="#111814",
    surface="#172019",
    surface_elevated="#1D2A22",
    surface_interactive="#24352A",
    border="#34463B",
    border_strong="#4B5F52",
    text_primary="#F3F7F2",
    text_secondary="#CFD9D1",
    text_muted="#97A89E",
    primary="#79B992",
    success="#82C99C",
    warning="#D7AA59",
    danger="#E07A6C",
    info="#8AB99E",
    white="#FFFFFF",
    black="#0A110D",
    deep="#0E1511",
    card="#1A271F",
)

TOKENS = MORNING


def normalize_mode(mode: str | None) -> str:
    value = (mode or "").strip().lower()
    if value in {"dark", "night", "silver", "control_room"}:
        return "night"
    return "morning"


def get_tokens(mode: str | None = None) -> Stage8Tokens:
    return NIGHT if normalize_mode(mode) == "night" else MORNING


def semantic_color(state: str, mode: str | None = None) -> str:
    """Map simulator states to semantic colors without relying on hue alone."""
    tokens = get_tokens(mode)
    value = (state or "").strip().lower()
    if value in {"act", "active", "idle", "pass", "ok", "healthy"}:
        return tokens.success
    if value in {"mbl", "blocked", "warning", "reset"}:
        return tokens.warning
    if value in {"busy", "fault", "fail", "error", "critical"}:
        return tokens.danger
    if value in {"test", "diagnostic", "info"}:
        return tokens.info
    return tokens.border_strong
