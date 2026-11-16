from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import TYPE_CHECKING

from .db import Database

if TYPE_CHECKING:
    from .mml import MmlEngine


COMMAND_FILE_STATES = {"Accepted", "Started", "Finished", "Executed", "Failed"}
TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


@dataclass(frozen=True)
class CommandFileCommand:
    line_no: int
    raw: str


@dataclass(frozen=True)
class CommandFile:
    file_name: str
    raw_commands: str
    status: str
    scheduled_at: str | None
    executed_log: list[dict]


@dataclass(frozen=True)
class CommandFileRun:
    ok: bool
    code: str
    message: str
    file_name: str
    status: str
    executed: int = 0
    failed: int = 0
    log: list[dict] | None = None


class VirtualClock:
    def __init__(self, start: str = "00:00"):
        self._validate(start)
        self.minutes = self._to_minutes(start)

    @staticmethod
    def _validate(value: str) -> None:
        if not TIME_RE.fullmatch(str(value).strip()):
            raise ValueError("Virtual time must use HH:MM")

    @staticmethod
    def _to_minutes(value: str) -> int:
        hours, minutes = map(int, str(value).strip().split(":"))
        return hours * 60 + minutes

    @staticmethod
    def _format(minutes: int) -> str:
        minutes %= 24 * 60
        return f"{minutes // 60:02d}:{minutes % 60:02d}"

    @property
    def current(self) -> str:
        return self._format(self.minutes)

    def set(self, value: str) -> str:
        self._validate(value)
        self.minutes = self._to_minutes(value)
        return self.current

    def advance(self, minutes: int) -> str:
        if minutes < 0:
            raise ValueError("Virtual clock cannot move backward")
        self.minutes = (self.minutes + int(minutes)) % (24 * 60)
        return self.current


class CommandFileEngine:
    def __init__(self, db: Database, mml: MmlEngine | None = None):
        self.db = db
        self.mml = mml
        self.clock = VirtualClock()

    def set_mml(self, mml: MmlEngine) -> None:
        self.mml = mml

    @staticmethod
    def _normalize_name(name: str) -> str:
        value = str(name or "").strip()
        value = re.sub(r"[^A-Za-z0-9_.-]+", "-", value)
        value = value.strip("-")
        if not value:
            raise ValueError("Command file name is required")
        return value

    def parse(self, file_name: str, raw_commands: str) -> list[CommandFileCommand]:
        name = self._normalize_name(file_name)
        text = str(raw_commands or "").replace("\r\n", "\n").replace("\r", "\n")
        if not text.strip():
            raise ValueError("Command file is empty")

        indexed_lines = [
            (line_no, line.strip())
            for line_no, line in enumerate(text.split("\n"), start=1)
            if line.strip()
        ]
        if not indexed_lines:
            raise ValueError("Command file is empty")

        first_no, first_line = indexed_lines[0]
        if first_line.startswith(">") and first_line.endswith(";"):
            first_body = first_line[1:-1].strip()
            if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", first_body):
                indexed_lines = indexed_lines[1:]

        if indexed_lines:
            last_no, last_line = indexed_lines[-1]
            if last_line.upper() in {"> END FILE;", "> ENDFILE;"}:
                indexed_lines = indexed_lines[:-1]

        if not indexed_lines:
            raise ValueError(f"Command file {name} contains no executable commands")

        commands: list[CommandFileCommand] = []
        for line_no, line in indexed_lines:
            if not line.startswith(">") or not line.endswith(";"):
                raise ValueError(
                    f"Line {line_no}: command files require commands starting with '>' and ending with ';'"
                )
            body = line[1:-1].strip()
            if not body:
                raise ValueError(f"Line {line_no}: empty command")
            if re.match(r"(?i)^execmdfile\s*:", body):
                raise ValueError(f"Line {line_no}: nested EXECMDFILE is not allowed")
            commands.append(CommandFileCommand(line_no, line))
        return commands

    def _row(self, file_name: str) -> dict | None:
        row = self.db.conn.execute(
            "SELECT file_name,raw_commands,status,scheduled_at,executed_log "
            "FROM command_files WHERE file_name=?",
            (self._normalize_name(file_name),),
        ).fetchone()
        if not row:
            return None
        return dict(row)

    @staticmethod
    def _decode_log(value: str | None) -> list[dict]:
        if not value:
            return []
        try:
            decoded = json.loads(value)
            return decoded if isinstance(decoded, list) else []
        except json.JSONDecodeError:
            return []

    def get(self, file_name: str) -> CommandFile | None:
        row = self._row(file_name)
        if not row:
            return None
        return CommandFile(
            row["file_name"],
            row["raw_commands"],
            row["status"],
            row["scheduled_at"],
            self._decode_log(row["executed_log"]),
        )

    def list_files(self) -> list[CommandFile]:
        rows = self.db.conn.execute(
            """
            SELECT file_name,raw_commands,status,scheduled_at,executed_log
            FROM command_files
            ORDER BY file_name
            """
        ).fetchall()
        return [
            CommandFile(
                row["file_name"],
                row["raw_commands"],
                row["status"],
                row["scheduled_at"],
                self._decode_log(row["executed_log"]),
            )
            for row in rows
        ]

    def save(self, file_name: str, raw_commands: str) -> CommandFile:
        name = self._normalize_name(file_name)
        self.parse(name, raw_commands)
        with self.db.conn:
            self.db.conn.execute(
                """
                INSERT INTO command_files(file_name,raw_commands,status,scheduled_at,executed_log)
                VALUES (?,?,?,?,?)
                ON CONFLICT(file_name) DO UPDATE SET
                    raw_commands=excluded.raw_commands,
                    status='Accepted',
                    scheduled_at=NULL,
                    executed_log=NULL
                """,
                (name, raw_commands.strip(), "Accepted", None, None),
            )
            self.db.event(
                "CommandFileAccepted",
                "command_file",
                name,
                json.dumps({"status": "Accepted"}),
            )
        result = self.get(name)
        assert result is not None
        return result

    def schedule(self, file_name: str, scheduled_at: str) -> CommandFile:
        self._validate_schedule(scheduled_at)
        name = self._normalize_name(file_name)
        file = self.get(name)
        if not file:
            raise ValueError(f"Command file {name} not found")
        if file.status in {"Started", "Finished"}:
            raise ValueError(f"Cannot schedule command file in state {file.status}")
        with self.db.conn:
            self.db.conn.execute(
                """
                UPDATE command_files
                SET status='Accepted', scheduled_at=?, executed_log=NULL
                WHERE file_name=?
                """,
                (scheduled_at.strip(), name),
            )
            self.db.event(
                "CommandFileScheduled",
                "command_file",
                name,
                json.dumps({"scheduled_at": scheduled_at.strip()}),
            )
        result = self.get(name)
        assert result is not None
        return result

    @staticmethod
    def _validate_schedule(value: str) -> None:
        VirtualClock._validate(value)

    @staticmethod
    def VirtualTime_validate(value: str) -> None:
        VirtualClock._validate(value)

    def execute(self, file_name: str) -> CommandFileRun:
        name = self._normalize_name(file_name)
        file = self.get(name)
        if not file:
            return CommandFileRun(
                False,
                "CMD-FILE-NOT-FOUND",
                f"Command file {name} not found",
                name,
                "Failed",
            )
        try:
            commands = self.parse(name, file.raw_commands)
        except ValueError as exc:
            return self._fail(name, str(exc))

        if self.mml is None:
            return self._fail(name, "MML engine is not attached")

        with self.db.conn:
            self.db.conn.execute(
                "UPDATE command_files SET status='Started', executed_log=NULL WHERE file_name=?",
                (name,),
            )
            self.db.event(
                "CommandFileStarted",
                "command_file",
                name,
                json.dumps({"status": "Started", "clock": self.clock.current}),
            )

        log: list[dict] = []
        failed = 0
        for command in commands:
            result = self.mml.execute(command.raw)
            entry = {
                "line": command.line_no,
                "command": command.raw,
                "ok": result.ok,
                "code": result.code,
                "message": result.message,
                "state_changes": result.state_changes or [],
            }
            log.append(entry)
            if not result.ok:
                failed += 1
                break

        with self.db.conn:
            self.db.conn.execute(
                """
                UPDATE command_files
                SET status='Finished', executed_log=?, scheduled_at=NULL
                WHERE file_name=?
                """,
                (json.dumps(log, ensure_ascii=False), name),
            )
            self.db.event(
                "CommandFileFinished",
                "command_file",
                name,
                json.dumps({"commands": len(log), "failed": failed}),
            )
            final_status = "Failed" if failed else "Executed"
            self.db.conn.execute(
                "UPDATE command_files SET status=? WHERE file_name=?",
                (final_status, name),
            )
            self.db.event(
                "CommandFileExecuted" if not failed else "CommandFileFailed",
                "command_file",
                name,
                json.dumps({"status": final_status, "clock": self.clock.current}),
            )

        return CommandFileRun(
            not failed,
            "CMD-FILE-EXECUTED" if not failed else "CMD-FILE-FAILED",
            f"{len(log) - failed}/{len(commands)} command(s) executed",
            name,
            final_status,
            executed=len(log) - failed,
            failed=failed,
            log=log,
        )

    def _fail(self, name: str, reason: str) -> CommandFileRun:
        with self.db.conn:
            self.db.conn.execute(
                """
                UPDATE command_files
                SET status='Failed', scheduled_at=NULL, executed_log=?
                WHERE file_name=?
                """,
                (
                    json.dumps(
                        [{"ok": False, "code": "CMD-FILE-ERROR", "message": reason}],
                        ensure_ascii=False,
                    ),
                    name,
                ),
            )
            self.db.event(
                "CommandFileFailed",
                "command_file",
                name,
                json.dumps({"status": "Failed", "reason": reason}),
            )
        return CommandFileRun(
            False,
            "CMD-FILE-ERROR",
            reason,
            name,
            "Failed",
            0,
            1,
        )

    def due_files(self, previous_minutes: int | None = None) -> list[CommandFile]:
        current_minutes = self.clock.minutes
        due: list[CommandFile] = []
        for file in self.list_files():
            if not file.scheduled_at or file.status != "Accepted":
                continue
            scheduled = VirtualClock._to_minutes(file.scheduled_at)
            if previous_minutes is None:
                is_due = scheduled <= current_minutes
            elif previous_minutes == current_minutes:
                is_due = False
            elif previous_minutes < current_minutes:
                is_due = previous_minutes < scheduled <= current_minutes
            else:
                is_due = scheduled > previous_minutes or scheduled <= current_minutes
            if is_due:
                due.append(file)
        return due

    def advance(self, minutes: int) -> list[CommandFileRun]:
        previous_minutes = self.clock.minutes
        self.clock.advance(minutes)
        results: list[CommandFileRun] = []
        for file in self.due_files(previous_minutes):
            results.append(self.execute(file.file_name))
        return results

    def reset_clock(self) -> str:
        return self.clock.set("00:00")

    def reset(self) -> None:
        with self.db.conn:
            self.db.conn.execute("DELETE FROM command_files")
            self.db.event(
                "CommandFilesReset",
                "command_file",
                "all",
                json.dumps({"clock": self.clock.current}),
            )
        self.reset_clock()
