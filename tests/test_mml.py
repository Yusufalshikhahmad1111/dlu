from pathlib import Path
from tempfile import TemporaryDirectory

from dlu_app.db import Database
from dlu_app.mml import MmlEngine


def make_engine():
    tmp = TemporaryDirectory()
    db = Database(Path(tmp.name) / "test.sqlite3")
    return tmp, db, MmlEngine(db)


def test_create_display_cancel():
    tmp, db, mml = make_engine()
    try:
        result = mml.execute(
            "> cr sub: dn=2233500, eqn=50-1-5-0, "
            "lac=021, class=ms, c/s=PB;"
        )
        assert result.ok
        assert result.code == "CREATED"

        result = mml.execute("> disp sub: dn=2233500;")
        assert result.ok
        assert result.data[0]["eqn"] == "50-1-5-0"

        result = mml.execute(
            "> can sub: lac=021, dn=2233500;"
        )
        assert result.ok
        assert result.code == "CANCELLED"
    finally:
        db.close()
        tmp.cleanup()


def test_cmrl_port_guard():
    tmp, db, mml = make_engine()
    try:
        ok = mml.execute(
            "> cr sub: dn=2250500, eqn=10-1-7-0, "
            "lac=021, class=cmrl, c/s=PB;"
        )
        assert ok.ok

        bad = mml.execute(
            "> cr sub: dn=2250506, eqn=10-1-7-6, "
            "lac=021, class=cmrl, c/s=PB;"
        )
        assert not bad.ok
        assert bad.code == "MML-VALIDATION"
    finally:
        db.close()
        tmp.cleanup()


def test_diag_guard():
    tmp, db, mml = make_engine()
    try:
        bad = mml.execute("> diag dlu: dlu=10;")
        assert not bad.ok
        assert bad.code == "STATE-GUARD"

        cfg = mml.execute(
            "> conf dlu: dlu=10, dluc0=y, ost=mbl;"
        )
        assert cfg.ok

        good = mml.execute("> diag dlu: dlu=10;")
        assert good.ok
        assert good.code == "DIAG-PASS"
    finally:
        db.close()
        tmp.cleanup()
