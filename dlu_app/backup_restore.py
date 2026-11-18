from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import shutil
import sqlite3
import tempfile

@dataclass(frozen=True)
class BackupInfo:
    path: Path
    size_bytes: int
    integrity: str
    created_at: str

class BackupError(RuntimeError):
    """Raised when a database backup/restore operation is unsafe or invalid."""

class DatabaseBackupManager:
    """Safe SQLite backup/restore lifecycle for the DLU Lab desktop app."""

    REQUIRED_TABLES = {
        "exchanges", "dlus", "dlu_sides", "hardware_sources",
        "card_types", "slots", "subscribers", "cpt_routes",
        "alarms", "command_files", "event_log", "hardware_events",
    }

    @staticmethod
    def default_backup_dir(db_path: str | Path) -> Path:
        return Path(db_path).resolve().parent / "backups"

    @classmethod
    def create_backup(cls, db_path: str | Path, target_path: str | Path | None = None) -> BackupInfo:
        source = Path(db_path).resolve()
        if not source.exists():
            raise BackupError(f"Database not found: {source}")
        target = (
            Path(target_path).expanduser().resolve()
            if target_path is not None
            else cls.default_backup_dir(source) / f"dlu_lab_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f"{target.stem}_", suffix=".tmp", dir=target.parent)
        os.close(fd)
        temp_path = Path(temp_name)
        try:
            source_conn = sqlite3.connect(source)
            destination_conn = sqlite3.connect(temp_path)
            try:
                source_conn.backup(destination_conn)
                destination_conn.commit()
            finally:
                destination_conn.close()
                source_conn.close()
            cls.validate_backup(temp_path)
            os.replace(temp_path, target)
            info = cls.validate_backup(target)
            cls._write_metadata(target, info)
            return info
        except Exception as exc:
            temp_path.unlink(missing_ok=True)
            if isinstance(exc, BackupError):
                raise
            raise BackupError(f"Could not create backup: {exc}") from exc

    @classmethod
    def validate_backup(cls, backup_path: str | Path) -> BackupInfo:
        path = Path(backup_path).expanduser().resolve()
        if not path.exists() or not path.is_file():
            raise BackupError(f"Backup file not found: {path}")
        try:
            conn = sqlite3.connect(path)
            try:
                row = conn.execute("PRAGMA integrity_check").fetchone()
                integrity = str(row[0] if row else "")
                if integrity.lower() != "ok":
                    raise BackupError(f"SQLite integrity check failed: {integrity or 'unknown'}")
                tables = {
                    str(row[0])
                    for row in conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                    ).fetchall()
                }
                missing = cls.REQUIRED_TABLES - tables
                if missing:
                    raise BackupError(
                        "Backup is missing required tables: " + ", ".join(sorted(missing))
                    )
            finally:
                conn.close()
        except sqlite3.DatabaseError as exc:
            raise BackupError(f"Invalid SQLite database: {exc}") from exc
        return BackupInfo(
            path=path,
            size_bytes=path.stat().st_size,
            integrity="ok",
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def prepare_restore(cls, db_path: str | Path, backup_path: str | Path) -> Path:
        target_db = Path(db_path).resolve()
        backup = cls.validate_backup(backup_path)
        pending = cls.pending_restore_path(target_db)
        pending.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f"{target_db.stem}_restore_", suffix=".tmp", dir=pending.parent)
        os.close(fd)
        temp_path = Path(temp_name)
        try:
            shutil.copy2(backup.path, temp_path)
            cls.validate_backup(temp_path)
            os.replace(temp_path, pending)
            return pending
        except Exception as exc:
            temp_path.unlink(missing_ok=True)
            pending.unlink(missing_ok=True)
            if isinstance(exc, BackupError):
                raise
            raise BackupError(f"Could not stage restore: {exc}") from exc

    @classmethod
    def apply_pending_restore(cls, db_path: str | Path) -> Path | None:
        target_db = Path(db_path).resolve()
        pending = cls.pending_restore_path(target_db)
        if not pending.exists():
            return None
        cls.validate_backup(pending)
        rollback_dir = cls.default_backup_dir(target_db)
        rollback_dir.mkdir(parents=True, exist_ok=True)
        rollback = rollback_dir / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"
        if target_db.exists():
            cls.create_backup(target_db, rollback)
        os.replace(pending, target_db)
        return target_db

    @staticmethod
    def pending_restore_path(db_path: str | Path) -> Path:
        path = Path(db_path).resolve()
        return path.with_suffix(path.suffix + ".restore.pending")

    @staticmethod
    def _write_metadata(path: Path, info: BackupInfo) -> None:
        metadata = {
            "application": "DLU Lab",
            "database": path.name,
            "backup": str(path),
            "size_bytes": info.size_bytes,
            "integrity": info.integrity,
            "created_at": info.created_at,
        }
        path.with_suffix(path.suffix + ".json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
