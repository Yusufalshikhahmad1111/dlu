from pathlib import Path
from tempfile import TemporaryDirectory

from dlu_app.db import Database
from dlu_app.mml import MmlEngine


def make_engine():
    tmp = TemporaryDirectory()
    db = Database(Path(tmp.name) / "test.sqlite3")
    return tmp, db, MmlEngine(db)


def test_source_backed_card_registry():
    tmp, db, _mml = make_engine()
    try:
        refs = {ref.code: ref for ref in db.list_card_references()}
        assert refs["SLMA8"].port_count == 8
        assert refs["SLMA16"].port_count == 16
        assert refs["SLMA64"].port_count == 64
        assert refs["CMRL"].port_count == 6
        assert refs["SLMA8"].verified
        assert refs["CMRL"].source_page == "60"
    finally:
        db.close()
        tmp.cleanup()


def test_course_supported_seed_placements():
    tmp, db, _mml = make_engine()
    try:
        slma = db.get_slot(50, 0, 15)
        cmrl = db.get_slot(10, 1, 7)
        assert slma is not None
        assert slma.card_type == "SLMA8"
        assert slma.port_count == 8
        assert cmrl is not None
        assert cmrl.card_type == "CMRL"
        assert cmrl.port_count == 6
    finally:
        db.close()
        tmp.cleanup()


def test_extended_mml_inspection_focus_data():
    tmp, db, mml = make_engine()
    try:
        result = mml.execute("> disp dlupport: eqn=50-0-15-0;")
        assert result.ok
        assert result.data["eqn"] == "50-0-15-0"
        assert result.data["card_type"] == "SLMA8"

        result = mml.execute("> stat dlu: dlu=50;")
        assert result.ok
        assert result.data["shelves"] == 8
        assert result.data["modules_per_shelf"] == 16
    finally:
        db.close()
        tmp.cleanup()


def test_maintenance_replacement_workflow():
    tmp, db, mml = make_engine()
    try:
        db.inject_fault(50, 0, 15)
        slot = db.get_slot(50, 0, 15)
        assert slot.fault_state == "fault"
        assert slot.ost == "mbl"

        diag = mml.execute(
            "> diag dlumod: dlu=50, shelf=0, module=15;"
        )
        assert not diag.ok
        assert diag.code == "DIAG-FAULT"

        removed = db.remove_card(50, 0, 15)
        assert removed == "SLMA8"
        assert db.get_slot(50, 0, 15).card_type == "UNCONFIGURED"

        installed = db.install_card(50, 0, 15, "SLMA8")
        assert installed == "SLMA8"
        assert db.get_slot(50, 0, 15).ost == "mbl"

        db.activate_card(50, 0, 15)
        final_slot = db.get_slot(50, 0, 15)
        assert final_slot.ost == "act"
        assert final_slot.fault_state == "clear"
    finally:
        db.close()
        tmp.cleanup()


def test_cmrl_guard_and_range():
    tmp, db, mml = make_engine()
    try:
        for port in range(6):
            result = mml.execute(
                f"> cr sub: dlu=10, type=cmrl, "
                f"eqn=10-1-7-{port}, lac=021, dn={2250500 + port};"
            )
            assert result.ok

        bad = mml.execute(
            "> cr sub: dlu=10, type=cmrl, eqn=10-1-7-6, "
            "lac=021, dn=2250506;"
        )
        assert not bad.ok
        assert bad.code == "MML-VALIDATION"
    finally:
        db.close()
        tmp.cleanup()


def test_compact_mml_aliases_and_port_focus():
    tmp, db, mml = make_engine()
    try:
        result = mml.execute("> dispdlupport: eqn=50-0-15-0;")
        assert result.ok
        assert result.data["card_type"] == "SLMA8"

        result = mml.execute("> STATPORT: eqn=50-0-15-0;")
        assert result.ok
        assert result.data["eqn"] == "50-0-15-0"
    finally:
        db.close()
        tmp.cleanup()
