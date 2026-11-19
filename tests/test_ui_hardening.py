from pathlib import Path
import re

from dlu_app.db import Slot
from dlu_app.design_tokens import TOKENS, semantic_color
from dlu_app.theme import THEMES
from dlu_app.ui import DluSimulatorWindow
from dlu_app.ui_utils import make_font


def test_theme_palettes_have_complete_stage8_tokens():
    assert set(THEMES) == {"control_room", "ivory", "silver"}
    fields = set(THEMES["control_room"].__dataclass_fields__)
    assert fields == set(THEMES["ivory"].__dataclass_fields__)
    assert fields == set(THEMES["silver"].__dataclass_fields__)
    assert THEMES["control_room"] == THEMES["ivory"] == THEMES["silver"]
    for palette in THEMES.values():
        for field in fields:
            value = getattr(palette, field)
            assert isinstance(value, str)
            assert value


def test_stage8_semantic_colors_use_the_design_system():
    assert semantic_color("ACTIVE") == TOKENS.success
    assert semantic_color("MBL") == TOKENS.warning
    assert semantic_color("FAULT") == TOKENS.danger
    assert semantic_color("TEST") == TOKENS.info


def test_shared_font_helper_never_returns_invalid_size():
    assert make_font(-1).pointSize() >= 8
    assert make_font(None).pointSize() >= 8
    assert make_font("bad").pointSize() >= 8
    assert make_font(10, bold=True).pointSize() == 10


def test_slot_mapping_accepts_dataclass_and_dict():
    slot = Slot(
        50, 0, 15, "SLMA8", "act", 8,
        "Subscriber line module", "SLM", "clear", "PEU-CO-60"
    )
    mapped = DluSimulatorWindow._slot_mapping(slot)
    assert mapped["card_type"] == "SLMA8"
    assert mapped["port_count"] == 8
    assert mapped["dlu_id"] == 50

    as_dict = {"card_type": "CMRL", "port_count": 6, "dlu_id": 10}
    assert DluSimulatorWindow._slot_mapping(as_dict) is as_dict


def test_ui_source_does_not_duplicate_theme_hex_values():
    for path in ("dlu_app/ui.py", "dlu_app/call_ui.py"):
        text = Path(path).read_text(encoding="utf-8")
        assert not re.search(r"#[0-9a-fA-F]{6}", text), f"hardcoded color found in {path}"


def _relative_luminance(value: str) -> float:
    value = value.lstrip("#")
    channels = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [
        channel / 12.92 if channel <= 0.03928
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return (
        0.2126 * linear[0]
        + 0.7152 * linear[1]
        + 0.0722 * linear[2]
    )


def _contrast(foreground: str, background: str) -> float:
    light = max(_relative_luminance(foreground), _relative_luminance(background))
    dark = min(_relative_luminance(foreground), _relative_luminance(background))
    return (light + 0.05) / (dark + 0.05)


def test_stage8_text_and_primary_states_meet_contrast_target():
    for foreground in (
        TOKENS.text_primary,
        TOKENS.text_secondary,
        TOKENS.text_muted,
        TOKENS.primary,
        TOKENS.success,
        TOKENS.warning,
        TOKENS.danger,
        TOKENS.info,
    ):
        assert _contrast(foreground, TOKENS.bg) >= 4.5
        assert _contrast(foreground, TOKENS.surface) >= 4.5
