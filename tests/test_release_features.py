from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3

import pytest

from dlu_app import __version__
from dlu_app.backup_restore import BackupError, DatabaseBackupManager
from dlu_app.db import Database
from dlu_app.mml import MmlEngine


def make_db():
    tmp = TemporaryDirectory()
    db = Database(Path(tmp.name) / "dlu_lab.sqlite3")
    return tmp, db


def test_release_version_is_stable():
    assert __version__ == "2.0.0"


def test_project_version_matches_runtime_version():
    pyproject = Path(__file__).parents[1] / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    assert 'version = "2.0.0"' in text


def test_database_backup_round_trip_and_integrity_validation():
    tmp, db = make_db()
    try:
        mml = MmlEngine(db)
        created = mml.execute(
            "> cr sub: dlu=50, type=ms, eqn=50-0-15-0, lac=021, dn=2299000;"
        )
        assert created.ok

        backup_path = Path(tmp.name) / "release-backup.sqlite3"
        info = DatabaseBackupManager.create_backup(db.path, backup_path)
        assert info.integrity == "ok"
        assert info.size_bytes > 0
        assert DatabaseBackupManager.validate_backup(backup_path).integrity == "ok"

        db.reset_demo()
        assert db.get_subscriber("2299000", "021") is None

        DatabaseBackupManager.prepare_restore(db.path, backup_path)
        db.close()
        restored = DatabaseBackupManager.apply_pending_restore(
            Path(tmp.name) / "dlu_lab.sqlite3"
        )
        assert restored is not None

        reopened = Database(restored)
        try:
            assert reopened.get_subscriber("2299000", "021") is not None
        finally:
            reopened.close()
    finally:
        try:
            db.close()
        except sqlite3.ProgrammingError:
            pass
        tmp.cleanup()


def test_corrupt_backup_is_rejected():
    tmp, db = make_db()
    try:
        corrupt = Path(tmp.name) / "corrupt.sqlite3"
        corrupt.write_bytes(b"not a sqlite database")
        with pytest.raises(BackupError):
            DatabaseBackupManager.validate_backup(corrupt)
    finally:
        db.close()
        tmp.cleanup()


def test_pending_restore_path_is_deterministic():
    path = Path("demo") / "dlu_lab.sqlite3"
    assert str(DatabaseBackupManager.pending_restore_path(path)).endswith(
        "dlu_lab.sqlite3.restore.pending"
    )


def test_pyproject_contains_release_deployment_intent():
    pyproject = Path(__file__).parents[1] / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    assert "[tool.pyside6.deploy]" in text
    assert 'mode = "onefile"' in text
    assert "include-data-dir=data=data" in text
