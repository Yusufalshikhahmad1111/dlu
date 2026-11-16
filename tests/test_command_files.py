from pathlib import Path
from tempfile import TemporaryDirectory

from dlu_app.command_files import CommandFileEngine, VirtualClock
from dlu_app.db import Database
from dlu_app.mml import MmlEngine


def make_engine():
    tmp = TemporaryDirectory()
    db = Database(Path(tmp.name) / "test.sqlite3")
    mml = MmlEngine(db)
    return tmp, db, mml, mml.command_files


def test_virtual_clock_and_parser():
    clock = VirtualClock("01:30")
    assert clock.current == "01:30"
    assert clock.advance(45) == "02:15"
    assert clock.set("23:00") == "23:00"

    tmp, db, _mml, engine = make_engine()
    try:
        commands = engine.parse(
            "demo",
            "> demo;
> stat dlu: dlu=50;
> endfile;",
        )
        assert len(commands) == 1
        assert commands[0].line_no == 2
    finally:
        db.close()
        tmp.cleanup()


def test_accept_execute_and_persist_log():
    tmp, db, mml, engine = make_engine()
    try:
        caller, _called = mml.call_engine.prepare_demo_subscribers()
        assert caller == "2233500"

        file = engine.save(
            "block-demo",
            "> block-demo;
"
            f"> mod sub: dn={caller}, blk=accsusp;
"
            f"> disp sub: dn={caller};
"
            "> endfile;",
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
        assert len(persisted.executed_log) == 2
        assert persisted.executed_log[0]["ok"] is True
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
    finally:
        db.close()
        tmp.cleanup()


def test_failed_file_stops_at_first_failed_command():
    tmp, db, mml, engine = make_engine()
    try:
        caller, _called = mml.call_engine.prepare_demo_subscribers()
        engine.save(
            "failed-demo",
            f"> disp sub: dn={caller};
"
            "> stat sub: dn=9999999;
"
            f"> disp sub: dn={caller};",
        )
        result = engine.execute("failed-demo")
        assert not result.ok
        assert result.status == "Failed"
        assert result.executed == 1
        assert result.failed == 1
        persisted = engine.get("failed-demo")
        assert persisted.status == "Failed"
        assert len(persisted.executed_log) == 2
    finally:
        db.close()
        tmp.cleanup()


def test_mml_execmdfile_schedules_file():
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
    finally:
        db.close()
        tmp.cleanup()
