from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stage8Tokens:
    """Central visual tokens for the DLU Lab Stage 8 design system."""

    bg: str = "#0B1220"
    surface: str = "#111827"
    surface_elevated: str = "#172033"
    surface_interactive: str = "#1D2A3D"
    border: str = "#334155"
    border_strong: str = "#475569"

    text_primary: str = "#F8FAFC"
    text_secondary: str = "#CBD5E1"
    text_muted: str = "#94A3B8"

    primary: str = "#22D3EE"
    success: str = "#22C55E"
    warning: str = "#F59E0B"
    danger: str = "#EF4444"
    info: str = "#38BDF8"

    white: str = "#FFFFFF"
    black: str = "#020617"

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

    control_height_sm: int = 30
    control_height_md: int = 36
    control_height_lg: int = 42


TOKENS = Stage8Tokens()


def semantic_color(state: str) -> str:
    """Map a simulator/teaching state to a semantic color."""
    value = (state or "").strip().lower()
    if value in {"act", "active", "idle", "pass", "ok", "healthy"}:
        return TOKENS.success
    if value in {"mbl", "blocked", "warning", "reset"}:
        return TOKENS.warning
    if value in {"busy", "fault", "fail", "error", "critical"}:
        return TOKENS.danger
    if value in {"test", "diagnostic", "info"}:
        return TOKENS.info
    return TOKENS.border_strong
