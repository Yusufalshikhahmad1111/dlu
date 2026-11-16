from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import sqlite3
from typing import Any


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

CREATE TABLE IF NOT EXISTS dlu_sides (
    dlu_id INTEGER NOT NULL REFERENCES dlus(dlu_id) ON DELETE CASCADE,
    side INTEGER NOT NULL CHECK(side IN (0,1)),
    controller TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'standby',
    PRIMARY KEY(dlu_id, side)
);

CREATE TABLE IF NOT EXISTS hardware_sources (
    source_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL,
    page TEXT NOT NULL,
    note TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS card_types (
    card_type TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    family TEXT NOT NULL DEFAULT 'unknown',
    role TEXT NOT NULL DEFAULT '',
    port_count INTEGER NOT NULL CHECK(port_count >= 0),
    port_start INTEGER NOT NULL DEFAULT 0,
    port_end INTEGER NOT NULL DEFAULT -1,
    subscriber_type TEXT,
    source_id TEXT REFERENCES hardware_sources(source_id),
    verified INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS slots (
    dlu_id INTEGER NOT NULL REFERENCES dlus(dlu_id) ON DELETE CASCADE,
    shelf INTEGER NOT NULL CHECK (shelf BETWEEN 0 AND 7),
    module INTEGER NOT NULL CHECK (module BETWEEN 0 AND 15),
    card_type TEXT NOT NULL DEFAULT 'UNCONFIGURED' REFERENCES card_types(card_type),
    ost TEXT NOT NULL DEFAULT 'act',
    fault_state TEXT NOT NULL DEFAULT 'clear',
    PRIMARY KEY (dlu_id, shelf, module)
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

CREATE TABLE IF NOT EXISTS hardware_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dlu_id INTEGER NOT NULL,
    shelf INTEGER,
    module INTEGER,
    event_type TEXT NOT NULL,
    old_card TEXT,
    new_card TEXT,
    actor TEXT NOT NULL DEFAULT 'student',
    note TEXT,
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
    role: str
    family: str
    fault_state: str
    source_id: str | None


@dataclass(frozen=True)
class CardReference:
    code: str
    display_name: str
    family: str
    role: str
    port_count: int
    port_start: int
    port_end: int
    subscriber_type: str | None
    source_id: str | None
    source_title: str | None
    source_page: str | None
    source_note: str | None
    verified: bool


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
        self._migrate_legacy_columns()
        self.seed()
        self.conn.commit()

    def _migrate_legacy_columns(self) -> None:
        self._ensure_column("slots", "fault_state", "TEXT NOT NULL DEFAULT 'clear'")
        self._ensure_column("card_types", "family", "TEXT NOT NULL DEFAULT 'unknown'")
        self._ensure_column("card_types", "role", "TEXT NOT NULL DEFAULT ''")
        self._ensure_column("card_types", "port_start", "INTEGER NOT NULL DEFAULT 0")
        self._ensure_column("card_types", "port_end", "INTEGER NOT NULL DEFAULT -1")
        self._ensure_column("card_types", "subscriber_type", "TEXT")
        self._ensure_column("card_types", "source_id", "TEXT")
        self._ensure_column("card_types", "verified", "INTEGER NOT NULL DEFAULT 0")

    def _ensure_column(self, table: str, column: str, definition: str) -> None:
        columns = {
            row["name"]
            for row in self.conn.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if column not in columns:
            self.conn.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
            )

    @staticmethod
    def _seed_path() -> Path:
        return Path(__file__).resolve().parent.parent / "data" / "hardware_seed.json"

    def _load_seed(self) -> dict[str, Any]:
        path = self._seed_path()
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return {
            "version": 1,
            "sources": [],
            "models": [],
            "placements": [],
        }

    def seed(self) -> None:
        seed = self._load_seed()

        for source in seed.get("sources", []):
            self.conn.execute(
                """
                INSERT OR REPLACE INTO hardware_sources(
                    source_id,title,source_type,page,note
                ) VALUES (?,?,?,?,?)
                """,
                (
                    source["id"],
                    source["title"],
                    source["source_type"],
                    str(source["page"]),
                    source["note"],
                ),
            )

        models = seed.get("models", [])
        if not models:
            models = [
                {
                    "code": "UNCONFIGURED",
                    "name": "Unconfigured",
                    "family": "empty",
                    "role": "Empty slot",
                    "port_count": 0,
                    "port_start": 0,
                    "port_end": -1,
                    "subscriber_type": None,
                    "source_id": None,
                    "verified": True,
                }
            ]

        for model in models:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO card_types(
                    card_type,display_name,family,role,port_count,
                    port_start,port_end,subscriber_type,source_id,verified
                ) VALUES (?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    model["code"],
                    model["name"],
                    model.get("family", "unknown"),
                    model.get("role", ""),
                    model.get("port_count", 0),
                    model.get("port_start", 0),
                    model.get("port_end", -1),
                    model.get("subscriber_type"),
                    model.get("source_id"),
                    int(bool(model.get("verified"))),
                ),
            )

        self.conn.execute(
            "INSERT OR IGNORE INTO exchanges(exchange_code,lac,city_name,status) "
            "VALUES ('ALE1','021','Aleppo','act')"
        )

        # The course explicitly enumerates DLU identifiers 10..250.
        for dlu_id in range(10, 251, 10):
            self.conn.execute(
                """
                INSERT OR IGNORE INTO dlus(
                    dlu_id,exchange_code,dluc0_state,dluc1_state,is_isolated
                ) VALUES (?,?,?,?,0)
                """,
                (dlu_id, "ALE1", "act", "standby"),
            )
            self.conn.execute(
                """
                INSERT OR IGNORE INTO dlu_sides(dlu_id,side,controller,state)
                VALUES (?,?,?,?)
                """,
                (dlu_id, 0, "DLUC0", "act"),
            )
            self.conn.execute(
                """
                INSERT OR IGNORE INTO dlu_sides(dlu_id,side,controller,state)
                VALUES (?,?,?,?)
                """,
                (dlu_id, 1, "DLUC1", "standby"),
            )

        for dlu_id in range(10, 251, 10):
            for shelf in range(8):
                for module in range(16):
                    self.conn.execute(
                        """
                        INSERT OR IGNORE INTO slots(
                            dlu_id,shelf,module,card_type,ost,fault_state
                        ) VALUES (?,?,?,?,?,'clear')
                        """,
                        (dlu_id, shelf, module, "UNCONFIGURED", "act"),
                    )

        # Reset all seeded placements before applying the authoritative dataset.
        self.conn.execute(
            "UPDATE slots SET card_type='UNCONFIGURED', ost='act', fault_state='clear'"
        )
        for placement in seed.get("placements", []):
            self.conn.execute(
                """
                UPDATE slots
                SET card_type=?, ost='act', fault_state='clear'
                WHERE dlu_id=? AND shelf=? AND module=?
                """,
                (
                    placement["card"],
                    placement["dlu"],
                    placement["shelf"],
                    placement["module"],
                ),
            )

        routes = [
            ("ALSTN", "011", "YES", "DAMASCUS", "NATIONAL"),
            ("ALSTN", "014", "YES", "QUNETRA", "NATIONAL"),
            ("ALSTN", "021", "YES", "ALEPPO", "LOCAL"),
            ("ALSTN", "031", "YES", "HOMS", "NATIONAL"),
            ("ALSTN", "033", "YES", "HAMA", "NATIONAL"),
            ("ALSTN", "041", "YES", "LATTAKIA", "NATIONAL"),
            ("ALSTN", "043", "YES", "TARTOUS", "NATIONAL"),
            ("ALSTN", "051", "YES", "DEIR_EZZOR", "NATIONAL"),
            ("ALSTN", "052", "YES", "HASAKAH", "NATIONAL"),
            ("PLMN", "092", "NO", "BLOCKED_SYRIATEL", "MOBILE"),
            ("PLMN", "093", "YES", "SYRIATEL", "MOBILE"),
            ("PLMN", "094", "YES", "MTN", "MOBILE"),
            ("PLMN", "095", "YES", "MTN", "MOBILE"),
            ("PLMN", "096", "YES", "MTN", "MOBILE"),
            ("PLMN", "097", "NO", "BLOCKED_MTN", "MOBILE"),
            ("PLMN", "098", "YES", "SYRIATEL", "MOBILE"),
            ("PLMN", "099", "YES", "SYRIATEL", "MOBILE"),
            ("ALSTI", "00972", "NO", "BLACK LIST", "INTERNATIONAL"),
            ("ALSTI", "00961", "YES", "LEBANON", "INTERNATIONAL"),
            ("ALSTI", "00964", "YES", "IRAQ", "INTERNATIONAL"),
            ("EMERGENCY", "110", "YES", "AMBULANCE", "SERVICE"),
            ("EMERGENCY", "112", "NO", "POLICE", "SERVICE"),
            ("EMERGENCY", "113", "YES", "FIRE", "SERVICE"),
            ("SERVICE", "2014", "YES", "UNIVER", "SMART_NETWORK"),
        ]
        for row in routes:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO cpt_routes(
                    dest,code,eval,name,route_type
                ) VALUES (?,?,?,?,?)
                """,
                row,
            )

    def list_card_references(self) -> list[CardReference]:
        rows = self.conn.execute(
            """
            SELECT c.*, s.title AS source_title, s.page AS source_page,
                   s.note AS source_note
            FROM card_types c
            LEFT JOIN hardware_sources s ON s.source_id=c.source_id
            ORDER BY c.family, c.card_type
            """
        ).fetchall()
        return [
            CardReference(
                code=row["card_type"],
                display_name=row["display_name"],
                family=row["family"],
                role=row["role"],
                port_count=row["port_count"],
                port_start=row["port_start"],
                port_end=row["port_end"],
                subscriber_type=row["subscriber_type"],
                source_id=row["source_id"],
                source_title=row["source_title"],
                source_page=row["source_page"],
                source_note=row["source_note"],
                verified=bool(row["verified"]),
            )
            for row in rows
        ]

    def get_card_reference(self, card_type: str) -> CardReference | None:
        row = self.conn.execute(
            """
            SELECT c.*, s.title AS source_title, s.page AS source_page,
                   s.note AS source_note
            FROM card_types c
            LEFT JOIN hardware_sources s ON s.source_id=c.source_id
            WHERE c.card_type=?
            """,
            (card_type,),
        ).fetchone()
        if not row:
            return None
        return CardReference(
            code=row["card_type"],
            display_name=row["display_name"],
            family=row["family"],
            role=row["role"],
            port_count=row["port_count"],
            port_start=row["port_start"],
            port_end=row["port_end"],
            subscriber_type=row["subscriber_type"],
            source_id=row["source_id"],
            source_title=row["source_title"],
            source_page=row["source_page"],
            source_note=row["source_note"],
            verified=bool(row["verified"]),
        )

    def get_dlu(self, dlu_id: int) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM dlus WHERE dlu_id=?", (dlu_id,)
        ).fetchone()

    def list_dlus(self) -> list[sqlite3.Row]:
        return list(
            self.conn.execute("SELECT * FROM dlus ORDER BY dlu_id")
        )

    def get_slot(self, dlu_id: int, shelf: int, module: int) -> Slot | None:
        row = self.conn.execute(
            """
            SELECT s.*, c.port_count, c.role, c.family, c.source_id
            FROM slots s
            JOIN card_types c ON c.card_type=s.card_type
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
            row["role"],
            row["family"],
            row["fault_state"],
            row["source_id"],
        )

    def list_shelf(self, dlu_id: int, shelf: int) -> list[sqlite3.Row]:
        return list(
            self.conn.execute(
                """
                SELECT s.*, c.port_count, c.display_name, c.role, c.family,
                       c.verified, c.source_id
                FROM slots s
                JOIN card_types c ON c.card_type=s.card_type
                WHERE s.dlu_id=? AND s.shelf=? ORDER BY s.module
                """,
                (dlu_id, shelf),
            )
        )

    def list_dlu_slots(self, dlu_id: int) -> list[sqlite3.Row]:
        return list(
            self.conn.execute(
                """
                SELECT s.*, c.port_count, c.display_name, c.role, c.family,
                       c.verified, c.source_id
                FROM slots s
                JOIN card_types c ON c.card_type=s.card_type
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
                "SELECT * FROM subscribers WHERE dn=? AND lac=?",
                (dn, lac),
            ).fetchone()
        return self.conn.execute(
            "SELECT * FROM subscribers WHERE dn=? ORDER BY lac LIMIT 1",
            (dn,),
        ).fetchone()

    def get_port_subscriber(
        self, dlu_id: int, shelf: int, module: int, port: int
    ) -> sqlite3.Row | None:
        return self.conn.execute(
            """
            SELECT s.*
            FROM subscribers s
            WHERE s.dlu_id=? AND s.shelf=? AND s.module=? AND s.port=?
            """,
            (dlu_id, shelf, module, port),
        ).fetchone()

    def list_subscribers_range(
        self, start_dn: str, end_dn: str
    ) -> list[sqlite3.Row]:
        return list(
            self.conn.execute(
                """
                SELECT * FROM subscribers
                WHERE CAST(dn AS INTEGER) BETWEEN CAST(? AS INTEGER)
                  AND CAST(? AS INTEGER)
                ORDER BY CAST(dn AS INTEGER)
                """,
                (start_dn, end_dn),
            )
        )

    def list_side_states(self, dlu_id: int) -> list[sqlite3.Row]:
        return list(
            self.conn.execute(
                "SELECT * FROM dlu_sides WHERE dlu_id=? ORDER BY side",
                (dlu_id,),
            )
        )

    def event(
        self, event_type: str, aggregate_type: str, aggregate_id: str, payload_json: str
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO event_log(
                event_type,aggregate_type,aggregate_id,payload_json
            ) VALUES (?,?,?,?)
            """,
            (event_type, aggregate_type, aggregate_id, payload_json),
        )

    def add_alarm(self, unit_ref: str, severity: str, message: str) -> None:
        self.conn.execute(
            """
            INSERT INTO alarms(unit_ref,severity,message,active)
            VALUES (?,?,?,1)
            """,
            (unit_ref, severity, message),
        )

    def clear_active_alarms(self, unit_ref: str) -> None:
        self.conn.execute(
            "UPDATE alarms SET active=0 WHERE unit_ref=? AND active=1",
            (unit_ref,),
        )

    def list_active_alarms(self) -> list[sqlite3.Row]:
        return list(
            self.conn.execute(
                """
                SELECT * FROM alarms
                WHERE active=1
                ORDER BY
                    CASE severity
                        WHEN 'CRITICAL' THEN 1
                        WHEN 'MAJOR' THEN 2
                        ELSE 3
                    END,
                    alarm_id DESC
                """
            )
        )

    def set_side_state(self, dlu_id: int, side: int, state: str) -> None:
        normalized = state.lower()
        if normalized not in {"act", "standby", "mbl"}:
            raise ValueError("side state must be act, standby or mbl")

        partner = 1 - side
        with self.conn:
            self.conn.execute(
                "UPDATE dlu_sides SET state=? WHERE dlu_id=? AND side=?",
                (normalized, dlu_id, side),
            )
            if normalized == "act":
                self.conn.execute(
                    "UPDATE dlu_sides SET state='standby' "
                    "WHERE dlu_id=? AND side=?",
                    (dlu_id, partner),
                )
            elif normalized == "mbl":
                self.conn.execute(
                    "UPDATE dlu_sides SET state='act' "
                    "WHERE dlu_id=? AND side=? AND state!='mbl'",
                    (dlu_id, partner),
                )

            states = {
                row["side"]: row["state"]
                for row in self.list_side_states(dlu_id)
            }
            self.conn.execute(
                """
                UPDATE dlus
                SET dluc0_state=?, dluc1_state=?
                WHERE dlu_id=?
                """,
                (states[0], states[1], dlu_id),
            )
            self.event(
                "DluSideStateChanged",
                "dlu",
                str(dlu_id),
                json.dumps(states),
            )

    def inject_fault(self, dlu_id: int, shelf: int, module: int) -> None:
        slot = self.get_slot(dlu_id, shelf, module)
        if slot is None:
            raise ValueError("Module not found")
        if slot.card_type == "UNCONFIGURED":
            raise ValueError("Cannot inject a card fault into an UNCONFIGURED slot")
        with self.conn:
            self.conn.execute(
                """
                UPDATE slots SET fault_state='fault', ost='mbl'
                WHERE dlu_id=? AND shelf=? AND module=?
                """,
                (dlu_id, shelf, module),
            )
            self.conn.execute(
                "INSERT INTO alarms(unit_ref,severity,message,active) "
                "VALUES (?,?,?,1)",
                (
                    f"DLU {dlu_id}-{shelf}-{module}",
                    "MAJOR",
                    f"Hardware fault detected on {slot.card_type}",
                ),
            )
            self.conn.execute(
                """
                INSERT INTO hardware_events(
                    dlu_id,shelf,module,event_type,old_card,new_card,note
                ) VALUES (?,?,?,?,?,?,?)
                """,
                (
                    dlu_id,shelf,module,"FAULT_INJECTED",
                    slot.card_type,None,"Teaching fault injection",
                ),
            )

    def diagnose_module(self, dlu_id: int, shelf: int, module: int) -> dict[str, Any]:
        slot = self.get_slot(dlu_id, shelf, module)
        if slot is None:
            raise ValueError("Module not found")
        if slot.ost != "mbl":
            raise ValueError(
                "DIAG rejected: module must first be placed in ost=mbl"
            )
        result = "FAULT" if slot.fault_state == "fault" else "PASS"
        if result == "FAULT":
            self.add_alarm(
                f"DLU {dlu_id}-{shelf}-{module}",
                "CRITICAL",
                f"Diagnostic confirms fault on {slot.card_type}",
            )
        with self.conn:
            self.event(
                "ModuleDiagnosed",
                "module",
                f"{dlu_id}-{shelf}-{module}",
                json.dumps({"result": result}),
            )
        return {"result": result, "card": slot.card_type}

    def remove_card(self, dlu_id: int, shelf: int, module: int) -> str:
        slot = self.get_slot(dlu_id, shelf, module)
        if slot is None:
            raise ValueError("Module not found")
        if slot.ost != "mbl":
            raise ValueError("Card removal requires ost=mbl")
        if slot.fault_state != "fault":
            raise ValueError(
                "For the teaching replacement workflow, inject/confirm a fault first"
            )
        if self.conn.execute(
            """
            SELECT 1 FROM subscribers
            WHERE dlu_id=? AND shelf=? AND module=?
            """,
            (dlu_id, shelf, module),
        ).fetchone():
            raise ValueError("Cannot remove a card that still has subscriber ports assigned")

        with self.conn:
            self.conn.execute(
                """
                UPDATE slots
                SET card_type='UNCONFIGURED', fault_state='clear'
                WHERE dlu_id=? AND shelf=? AND module=?
                """,
                (dlu_id, shelf, module),
            )
            self.clear_active_alarms(f"DLU {dlu_id}-{shelf}-{module}")
            self.conn.execute(
                """
                INSERT INTO hardware_events(
                    dlu_id,shelf,module,event_type,old_card,new_card,note
                ) VALUES (?,?,?,?,?,?,?)
                """,
                (
                    dlu_id,shelf,module,"CARD_REMOVED",
                    slot.card_type,"UNCONFIGURED","Replacement workflow",
                ),
            )
        return slot.card_type

    def install_card(self, dlu_id: int, shelf: int, module: int, card_type: str) -> str:
        target = self.get_slot(dlu_id, shelf, module)
        ref = self.get_card_reference(card_type)
        if target is None:
            raise ValueError("Module not found")
        if ref is None or not ref.verified:
            raise ValueError("Card type is not in the verified hardware registry")
        if target.card_type != "UNCONFIGURED":
            raise ValueError(
                f"Slot already contains {target.card_type}; remove it first"
            )

        with self.conn:
            self.conn.execute(
                """
                UPDATE slots
                SET card_type=?, ost='mbl', fault_state='clear'
                WHERE dlu_id=? AND shelf=? AND module=?
                """,
                (card_type, dlu_id, shelf, module),
            )
            self.conn.execute(
                """
                INSERT INTO hardware_events(
                    dlu_id,shelf,module,event_type,old_card,new_card,note
                ) VALUES (?,?,?,?,?,?,?)
                """,
                (
                    dlu_id,shelf,module,"CARD_INSTALLED",
                    "UNCONFIGURED",card_type,"Replacement workflow",
                ),
            )
        return card_type

    def activate_card(self, dlu_id: int, shelf: int, module: int) -> str:
        slot = self.get_slot(dlu_id, shelf, module)
        if slot is None:
            raise ValueError("Module not found")
        if slot.card_type == "UNCONFIGURED":
            raise ValueError("Cannot activate an unconfigured module")
        if slot.fault_state == "fault":
            raise ValueError("Cannot activate a card with a confirmed fault")

        with self.conn:
            self.conn.execute(
                """
                UPDATE slots SET ost='act'
                WHERE dlu_id=? AND shelf=? AND module=?
                """,
                (dlu_id,shelf,module),
            )
            self.conn.execute(
                """
                INSERT INTO hardware_events(
                    dlu_id,shelf,module,event_type,old_card,new_card,note
                ) VALUES (?,?,?,?,?,?,?)
                """,
                (
                    dlu_id,shelf,module,"CARD_ACTIVATED",
                    slot.card_type,slot.card_type,"Replacement workflow",
                ),
            )
        return slot.card_type

    def reset_demo(self) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM subscribers")
            self.conn.execute("DELETE FROM alarms")
            self.conn.execute("DELETE FROM event_log")
            self.conn.execute("DELETE FROM command_files")
            self.conn.execute("DELETE FROM hardware_events")
            self.conn.execute(
                "UPDATE dlus SET dluc0_state='act', dluc1_state='standby', is_isolated=0"
            )
            self.conn.execute(
                "UPDATE dlu_sides SET state=CASE side WHEN 0 THEN 'act' ELSE 'standby' END"
            )
            self.conn.execute(
                "UPDATE slots SET ost='act', card_type='UNCONFIGURED', fault_state='clear'"
            )
            seed = self._load_seed()
            for placement in seed.get("placements", []):
                self.conn.execute(
                    """
                    UPDATE slots SET card_type=?, ost='act', fault_state='clear'
                    WHERE dlu_id=? AND shelf=? AND module=?
                    """,
                    (
                        placement["card"],
                        placement["dlu"],
                        placement["shelf"],
                        placement["module"],
                    ),
                )

    def close(self) -> None:
        self.conn.close()
