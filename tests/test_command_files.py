from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from dlu_app.command_files import CommandFileEngine, VirtualClock
from dlu_app.db import Database
from dlu_app.mml import MmlEngine


def make_engine():
    tmp = TemporaryDirectory()
    db = Database(Path(tmp.name) / "test.sqlite3")
    mml = MmlEngine(db)
    return tmp, db, mml, mml.command_files


def test_virtual_clock_and_parser_preserves_source_lines():
    clock = VirtualClock("01:30")
    assert clock.current == "01:30"
    assert clock.advance(45) == "02:15"
    assert clock.set("23:00") == "23:00"
    with pytest.raises(ValueError, match="cannot move backward"):
        clock.advance(-1)

    tmp, db, _mml, engine = make_engine()
    try:
        commands = engine.parse(
            "demo",
            """> demo;
> stat dlu: dlu=50;
> endfile;
""",
        )
        assert len(commands) == 1
        assert commands[0].line_no == 2
        assert commands[0].raw == "> stat dlu: dlu=50;"
    finally:
        db.close()
        tmp.cleanup()


def test_parser_validation_and_nested_exec_rejection():
    tmp, db, _mml, engine = make_engine()
    try:
        with pytest.raises(ValueError, match=r"Line 2:"):
            engine.parse(
                "bad",
                """> bad;
not-an-mml-command
""",
            )
        with pytest.raises(ValueError, match=r"Line 2: nested EXECMDFILE"):
            engine.parse(
                "nested",
                """> nested;
> execmdfile: file=other;
""",
            )
        with pytest.raises(ValueError, match="contains no executable commands"):
            engine.parse(
                "empty",
                """> empty;
> endfile;""",
            )
    finally:
        db.close()
        tmp.cleanup()


def test_accept_execute_and_persist_log():
    tmp, db, mml, engine = make_engine()
    try:
        caller, _called = mml.call_engine.prepare_demo_subscribers()
        file = engine.save(
            "block-demo",
            f"""> block-demo;
> mod sub: dn={caller}, blk=accsusp;
> disp sub: dn={caller};
> endfile;
""",
        )
        assert file.status == "Accepted"

        result = engine.execute("block-demo")
        assert result.ok
        assert result.status == "Executed"
        assert result.executed == 2
        assert result.failed == 0

        persisted = engine.get("block-demo")
        assert persisted is not None
        assert persisted.status == "Executed"
        assert persisted.scheduled_at is None
        assert len(persisted.executed_log) == 2
        assert persisted.executed_log[0]["ok"] is True
        assert persisted.executed_log[0]["line"] == 2

        events = [
            row["event_type"]
            for row in db.conn.execute(
                "SELECT event_type FROM event_log WHERE aggregate_type='command_file' "
                "AND aggregate_id=? ORDER BY event_id",
                ("block-demo",),
            ).fetchall()
        ]
        assert events[-3:] == [
            "CommandFileStarted",
            "CommandFileFinished",
            "CommandFileExecuted",
        ]
    finally:
        db.close()
        tmp.cleanup()


def test_schedule_and_virtual_clock_execution():
    tmp, db, mml, engine = make_engine()
    try:
        caller, _called = mml.call_engine.prepare_demo_subscribers()
        engine.save(
            "scheduled-demo",
            f"> disp sub: dn={caller};",
        )
        file = engine.schedule("scheduled-demo", "02:00")
        assert file.status == "Accepted"
        assert file.scheduled_at == "02:00"

        assert engine.advance(60) == []
        assert engine.get("scheduled-demo").status == "Accepted"

        results = engine.advance(60)
        assert len(results) == 1
        assert results[0].status == "Executed"
        assert engine.clock.current == "02:00"
        assert engine.get("scheduled-demo").scheduled_at is None
        assert engine.advance(60) == []
    finally:
        db.close()
        tmp.cleanup()


def test_schedule_crosses_midnight():
    tmp, db, mml, engine = make_engine()
    try:
        caller, _called = mml.call_engine.prepare_demo_subscribers()
        engine.save(
            "midnight-demo",
            f"> disp sub: dn={caller};",
        )
        engine.clock.set("23:50")
        engine.schedule("midnight-demo", "00:05")

        assert engine.advance(10) == []
        assert engine.clock.current == "00:00"
        assert engine.get("midnight-demo").status == "Accepted"

        results = engine.advance(10)
        assert len(results) == 1
        assert results[0].status == "Executed"
        assert engine.clock.current == "00:10"
    finally:
        db.close()
        tmp.cleanup()


def test_schedule_validates_time():
    tmp, db, _mml, engine = make_engine()
    try:
        engine.save("time-demo", "> help;")
        for value in ("24:00", "12:60", "abc", "2:00"):
            with pytest.raises(ValueError):
                engine.schedule("time-demo", value)
    finally:
        db.close()
        tmp.cleanup()


def test_failed_file_stops_at_first_failed_command():
    tmp, db, mml, engine = make_engine()
    try:
        caller, _called = mml.call_engine.prepare_demo_subscribers()
        engine.save(
            "failed-demo",
            f"""> failed-demo;
> disp sub: dn={caller};
> stat sub: dn=9999999;
> disp sub: dn={caller};
> endfile;
""",
        )
        result = engine.execute("failed-demo")
        assert not result.ok
        assert result.status == "Failed"
        assert result.executed == 1
        assert result.failed == 1
        persisted = engine.get("failed-demo")
        assert persisted is not None
        assert persisted.status == "Failed"
        assert persisted.scheduled_at is None
        assert len(persisted.executed_log) == 2
        assert persisted.executed_log[-1]["code"] == "DN-NOT-FOUND"

        events = [
            row["event_type"]
            for row in db.conn.execute(
                "SELECT event_type FROM event_log WHERE aggregate_type='command_file' "
                "AND aggregate_id=? ORDER BY event_id",
                ("failed-demo",),
            ).fetchall()
        ]
        assert events[-3:] == [
            "CommandFileStarted",
            "CommandFileFinished",
            "CommandFileFailed",
        ]
    finally:
        db.close()
        tmp.cleanup()


def test_mml_execmdfile_schedules_and_executes_same_file():
    tmp, db, mml, engine = make_engine()
    try:
        caller, _called = mml.call_engine.prepare_demo_subscribers()
        engine.save(
            "mml-demo",
            f"> disp sub: dn={caller};",
        )

        result = mml.execute("> execmdfile: file=mml-demo, time=02:30;")
        assert result.ok
        assert result.code == "CMD-FILE-ACCEPTED"
        assert result.data["scheduled_at"] == "02:30"

        immediate = mml.execute("> execmdfile: file=mml-demo;")
        assert immediate.ok
        assert immediate.code == "CMD-FILE-EXECUTED"
        assert immediate.data["status"] == "Executed"
        assert engine.get("mml-demo").scheduled_at is None
    finally:
        db.close()
        tmp.cleanup()
