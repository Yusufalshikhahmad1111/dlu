from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3


DB_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS exchanges (
    exchange_code TEXT PRIMARY KEY,
    lac TEXT NOT NULL,
    city_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'act'
);

CREATE TABLE IF NOT EXISTS dlus (
    dlu_id INTEGER PRIMARY KEY,
    exchange_code TEXT NOT NULL REFERENCES exchanges(exchange_code) ON DELETE CASCADE,
    dluc0_state TEXT NOT NULL DEFAULT 'act',
    dluc1_state TEXT NOT NULL DEFAULT 'standby',
    is_isolated INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS slots (
    dlu_id INTEGER NOT NULL REFERENCES dlus(dlu_id) ON DELETE CASCADE,
    shelf INTEGER NOT NULL CHECK (shelf BETWEEN 0 AND 7),
    module INTEGER NOT NULL CHECK (module BETWEEN 0 AND 15),
    card_type TEXT NOT NULL DEFAULT 'UNCONFIGURED',
    ost TEXT NOT NULL DEFAULT 'act',
    PRIMARY KEY (dlu_id, shelf, module)
);

CREATE TABLE IF NOT EXISTS card_types (
    card_type TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    port_count INTEGER NOT NULL CHECK (port_count >= 0)
);

CREATE TABLE IF NOT EXISTS subscribers (
    lac TEXT NOT NULL,
    dn TEXT NOT NULL,
    dlu_id INTEGER NOT NULL,
    shelf INTEGER NOT NULL,
    module INTEGER NOT NULL,
    port INTEGER NOT NULL CHECK (port >= 0),
    sub_type TEXT NOT NULL DEFAULT 'ms',
    dial_mode TEXT NOT NULL DEFAULT 'PB',
    line_state TEXT NOT NULL DEFAULT 'idle',
    cos_flags TEXT NOT NULL DEFAULT '',
    blk_reason TEXT,
    PRIMARY KEY (lac, dn),
    UNIQUE (dlu_id, shelf, module, port),
    FOREIGN KEY (dlu_id, shelf, module)
        REFERENCES slots(dlu_id, shelf, module) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cpt_routes (
    dest TEXT NOT NULL,
    code TEXT NOT NULL,
    sym TEXT NOT NULL DEFAULT 'NO',
    eval TEXT NOT NULL DEFAULT 'YES',
    name TEXT NOT NULL,
    route_type TEXT NOT NULL,
    PRIMARY KEY (dest, code)
);

CREATE TABLE IF NOT EXISTS alarms (
    alarm_id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_ref TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS command_files (
    file_name TEXT PRIMARY KEY,
    raw_commands TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Accepted',
    scheduled_at TEXT,
    executed_log TEXT
);

CREATE TABLE IF NOT EXISTS event_log (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    aggregate_type TEXT NOT NULL,
    aggregate_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


@dataclass(frozen=True)
class Slot:
    dlu_id: int
    shelf: int
    module: int
    card_type: str
    ost: str
    port_count: int


class Database:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.initialize()

    def initialize(self) -> None:
        self.conn.executescript(DB_SCHEMA)
        self.seed()
        self.conn.commit()

    def seed(self) -> None:
        self.conn.executemany(
            "INSERT OR IGNORE INTO card_types(card_type, display_name, port_count) VALUES (?, ?, ?)",
            [
                ("UNCONFIGURED", "Unconfigured", 0),
                ("SLMA8", "SLMA 8-port", 8),
                ("SLMA16", "SLMA 16-port", 16),
                ("CMRL", "SLMA CMRL", 6),
                ("SLMD", "SLMD", 16),
            ],
        )
        self.conn.execute(
            "INSERT OR IGNORE INTO exchanges(exchange_code,lac,city_name,status) VALUES ('ALE1','021','Aleppo','act')"
        )
        # The course/reference numbering uses DLU identifiers in multiples of 10.
        # We expose 10..250 as selectable DLU units; only explicitly backed demo
        # positions receive cards. The rest remain UNCONFIGURED.
        for dlu_id in range(10, 251, 10):
            self.conn.execute(
                "INSERT OR IGNORE INTO dlus(dlu_id,exchange_code,dluc0_state,dluc1_state) VALUES (?,?,?,?)",
                (dlu_id, "ALE1", "act", "standby"),
            )

        for dlu_id in range(10, 251, 10):
            for shelf in range(8):
                for module in range(16):
                    self.conn.execute(
                        "INSERT OR IGNORE INTO slots(dlu_id,shelf,module,card_type,ost) VALUES (?,?,?,?,?)",
                        (dlu_id, shelf, module, "UNCONFIGURED", "act"),
                    )

        # Only the cards required for the first academic demos are populated.
        # Unknown positions remain UNCONFIGURED instead of inventing hardware.
        self.conn.execute(
            "UPDATE slots SET card_type='SLMA8' WHERE dlu_id=50 AND shelf=1 AND module=5"
        )
        self.conn.execute(
            "UPDATE slots SET card_type='CMRL' WHERE dlu_id=10 AND shelf=1 AND module=7"
        )

        self.conn.execute(
            "INSERT OR IGNORE INTO cpt_routes(dest,code,eval,name,route_type) VALUES ('ALSTN','011','YES','DAMASCUS','NATIONAL')"
        )
        self.conn.execute(
            "INSERT OR IGNORE INTO cpt_routes(dest,code,eval,name,route_type) VALUES ('ALSTN','021','YES','ALEPPO','LOCAL')"
        )
        self.conn.execute(
            "INSERT OR IGNORE INTO cpt_routes(dest,code,eval,name,route_type) VALUES ('ALSTN','052','YES','HASAKAH','NATIONAL')"
        )
        self.conn.execute(
            "INSERT OR IGNORE INTO cpt_routes(dest,code,eval,name,route_type) VALUES ('ALSTI','00972','NO','BLACK LIST','INTERNATIONAL')"
        )
        self.conn.execute(
            "INSERT OR IGNORE INTO cpt_routes(dest,code,eval,name,route_type) VALUES ('EMERGENCY','110','YES','AMBULANCE','SERVICE')"
        )
        self.conn.execute(
            "INSERT OR IGNORE INTO cpt_routes(dest,code,eval,name,route_type) VALUES ('EMERGENCY','112','YES','POLICE','SERVICE')"
        )
        self.conn.execute(
            "INSERT OR IGNORE INTO cpt_routes(dest,code,eval,name,route_type) VALUES ('EMERGENCY','113','YES','FIRE','SERVICE')"
        )

    def get_dlu(self, dlu_id: int) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM dlus WHERE dlu_id=?", (dlu_id,)).fetchone()

    def list_dlus(self) -> list[sqlite3.Row]:
        return list(self.conn.execute("SELECT * FROM dlus ORDER BY dlu_id"))

    def get_slot(self, dlu_id: int, shelf: int, module: int) -> Slot | None:
        row = self.conn.execute(
            """
            SELECT s.*, c.port_count
            FROM slots s JOIN card_types c ON c.card_type=s.card_type
            WHERE s.dlu_id=? AND s.shelf=? AND s.module=?
            """,
            (dlu_id, shelf, module),
        ).fetchone()
        if not row:
            return None
        return Slot(
            row["dlu_id"],
            row["shelf"],
            row["module"],
            row["card_type"],
            row["ost"],
            row["port_count"],
        )

    def list_shelf(self, dlu_id: int, shelf: int) -> list[sqlite3.Row]:
        return list(
            self.conn.execute(
                """
                SELECT s.*, c.port_count, c.display_name
                FROM slots s JOIN card_types c ON c.card_type=s.card_type
                WHERE s.dlu_id=? AND s.shelf=? ORDER BY s.module
                """,
                (dlu_id, shelf),
            )
        )

    def list_dlu_slots(self, dlu_id: int) -> list[sqlite3.Row]:
        return list(
            self.conn.execute(
                """
                SELECT s.*, c.port_count, c.display_name
                FROM slots s JOIN card_types c ON c.card_type=s.card_type
                WHERE s.dlu_id=? ORDER BY s.shelf, s.module
                """,
                (dlu_id,),
            )
        )

    def list_subscribers_for_dlu(self, dlu_id: int) -> list[sqlite3.Row]:
        return list(
            self.conn.execute(
                "SELECT * FROM subscribers WHERE dlu_id=? ORDER BY shelf,module,port",
                (dlu_id,),
            )
        )

    def get_subscriber(self, dn: str, lac: str | None = None) -> sqlite3.Row | None:
        if lac:
            return self.conn.execute(
                "SELECT * FROM subscribers WHERE dn=? AND lac=?", (dn, lac)
            ).fetchone()
        return self.conn.execute(
            "SELECT * FROM subscribers WHERE dn=? ORDER BY lac LIMIT 1", (dn,)
        ).fetchone()

    def list_subscribers_range(self, start_dn: str, end_dn: str) -> list[sqlite3.Row]:
        return list(
            self.conn.execute(
                """
                SELECT * FROM subscribers
                WHERE CAST(dn AS INTEGER) BETWEEN CAST(? AS INTEGER) AND CAST(? AS INTEGER)
                ORDER BY CAST(dn AS INTEGER)
                """,
                (start_dn, end_dn),
            )
        )

    def event(
        self, event_type: str, aggregate_type: str, aggregate_id: str, payload_json: str
    ) -> None:
        self.conn.execute(
            "INSERT INTO event_log(event_type,aggregate_type,aggregate_id,payload_json) VALUES (?,?,?,?)",
            (event_type, aggregate_type, aggregate_id, payload_json),
        )

    def add_alarm(self, unit_ref: str, severity: str, message: str) -> None:
        self.conn.execute(
            "INSERT INTO alarms(unit_ref,severity,message,active) VALUES (?,?,?,1)",
            (unit_ref, severity, message),
        )

    def clear_active_alarms(self, unit_ref: str) -> None:
        self.conn.execute(
            "UPDATE alarms SET active=0 WHERE unit_ref=? AND active=1", (unit_ref,)
        )

    def reset_demo(self) -> None:
        """Reset only seeded/demo state, keeping the hardware dataset."""
        with self.conn:
            self.conn.execute("DELETE FROM subscribers")
            self.conn.execute("DELETE FROM alarms")
            self.conn.execute("DELETE FROM event_log")
            self.conn.execute("DELETE FROM command_files")
            self.conn.execute(
                "UPDATE dlus SET dluc0_state='act', dluc1_state='standby', is_isolated=0"
            )
            self.conn.execute(
                "UPDATE slots SET ost='act', card_type='UNCONFIGURED'"
            )
            self.conn.execute(
                "UPDATE slots SET card_type='SLMA8' "
                "WHERE dlu_id=50 AND shelf=1 AND module=5"
            )
            self.conn.execute(
                "UPDATE slots SET card_type='CMRL' "
                "WHERE dlu_id=10 AND shelf=1 AND module=7"
            )

    def close(self) -> None:
        self.conn.close()
