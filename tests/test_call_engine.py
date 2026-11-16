from pathlib import Path
from tempfile import TemporaryDirectory

from dlu_app.call_engine import CallEngine
from dlu_app.db import Database


def make_engine():
    tmp = TemporaryDirectory()
    db = Database(Path(tmp.name) / "test.sqlite3")
    engine = CallEngine(db)
    return tmp, db, engine


def test_prepare_demo_and_local_call_path():
    tmp, db, engine = make_engine()
    try:
        caller, called = engine.prepare_demo_subscribers()
        result = engine.start_call(caller, called)
        assert result.ok
        assert result.code == "CALL-CONNECTED"
        assert result.analysis.number_type == "LOCAL"
        assert result.path.labels() == ["DLU 50", "SN", "DLU 50"]
        assert db.get_subscriber(caller)["line_state"] == "busy"
        assert db.get_subscriber(called)["line_state"] == "busy"

        released = engine.release_call(result.call_id)
        assert released.ok
        assert db.get_subscriber(caller)["line_state"] == "idle"
        assert db.get_subscriber(called)["line_state"] == "idle"
        assert engine.resource_usage() == (0, 120)
    finally:
        db.close()
        tmp.cleanup()


def test_national_call_uses_pdc_and_route():
    tmp, db, engine = make_engine()
    try:
        caller, _called = engine.prepare_demo_subscribers()
        result = engine.start_call(caller, "0522233500")
        assert result.ok
        assert result.analysis.number_type == "NATIONAL"
        assert result.path.labels() == [
            "DLU 50", "LTG", "SN", "LTG", "DLU-LAC052"
        ]
        assert engine.resource_usage() == (1, 120)
        engine.release_call(result.call_id)
        assert engine.resource_usage() == (0, 120)
    finally:
        db.close()
        tmp.cleanup()


def test_black_list_blocks_without_resource_reservation():
    tmp, db, engine = make_engine()
    try:
        caller, _called = engine.prepare_demo_subscribers()
        result = engine.start_call(caller, "00972")
        assert not result.ok
        assert result.code == "CALL-BLOCKED"
        assert result.analysis.cpt.name == "BLACK LIST"
        assert engine.resource_usage() == (0, 120)
        assert db.get_subscriber(caller)["line_state"] == "idle"
    finally:
        db.close()
        tmp.cleanup()


def test_international_call_path():
    tmp, db, engine = make_engine()
    try:
        caller, _called = engine.prepare_demo_subscribers()
        result = engine.start_call(caller, "00964")
        assert result.ok
        assert result.analysis.number_type == "INTERNATIONAL"
        assert result.path.labels() == [
            "DLU 50", "LTG", "SN", "International Gateway"
        ]
        assert engine.resource_usage() == (1, 120)
    finally:
        db.close()
        tmp.cleanup()


def test_busy_guard_and_release():
    tmp, db, engine = make_engine()
    try:
        caller, called = engine.prepare_demo_subscribers()
        first = engine.start_call(caller, called)
        second = engine.start_call(caller, called)
        assert first.ok
        assert not second.ok
        assert second.code == "CALL-PORT-BUSY"
        engine.release_call(first.call_id)
    finally:
        db.close()
        tmp.cleanup()


def test_cpt_longest_specific_match():
    tmp, db, engine = make_engine()
    try:
        match = engine.repo.match_cpt("009720")
        assert match is not None
        assert match.code == "00972"
        assert match.name == "BLACK LIST"
    finally:
        db.close()
        tmp.cleanup()


def test_pdc_exhaustion_does_not_create_connected_call():
    tmp, db, engine = make_engine()
    try:
        caller, _called = engine.prepare_demo_subscribers()
        with db.conn:
            engine.repo.reserve("CALL-RESERVE", "PDC-VOICE", 120)
        result = engine.start_call(caller, "0522233500")
        assert not result.ok
        assert result.code == "CALL-RESOURCE-BUSY"
        assert engine.resource_usage() == (120, 120)
    finally:
        with db.conn:
            engine.repo.release_all("CALL-RESERVE")
        db.close()
        tmp.cleanup()


def test_omt_call_analysis_and_status():
    tmp, db, engine = make_engine()
    try:
        caller, called = engine.prepare_demo_subscribers()
        from dlu_app.mml import MmlEngine
        mml = MmlEngine(db)

        analysis = mml.execute(
            f"> test call: caller={caller}, number={called};"
        )
        assert analysis.ok
        assert analysis.code == "TEST-PASS"
        assert analysis.data["type"] == "LOCAL"

        started = engine.start_call(caller, called)
        shown = mml.execute(
            f"> stat call: call={started.call_id};"
        )
        assert shown.ok
        assert shown.data["call"]["state"] == "CONNECTED"
        assert shown.data["path"] == ["DLU 50", "SN", "DLU 50"]
    finally:
        db.close()
        tmp.cleanup()
