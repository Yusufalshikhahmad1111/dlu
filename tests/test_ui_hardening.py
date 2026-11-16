from pathlib import Path

from dlu_app.db import Slot
from dlu_app.theme import THEMES
from dlu_app.ui import DluSimulatorWindow
from dlu_app.ui_utils import make_font


def test_theme_palettes_have_identical_complete_tokens():
    assert set(THEMES) == {"ivory", "silver"}
    fields = set(THEMES["ivory"].__dataclass_fields__)
    assert fields == set(THEMES["silver"].__dataclass_fields__)
    for palette in THEMES.values():
        for field in fields:
            value = getattr(palette, field)
            assert isinstance(value, str)
            assert value


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
        assert "#" not in text, f"hardcoded color found in {path}"
