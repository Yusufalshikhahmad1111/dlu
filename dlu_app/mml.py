from __future__ import annotations

from dataclasses import dataclass
import json
import re
import sqlite3

from .db import Database


@dataclass
class MmlResult:
    ok: bool
    code: str
    message: str
    data: list[dict] | dict | None = None
    state_changes: list[str] | None = None
    alarms: list[str] | None = None


class MmlEngine:
    def __init__(self, db: Database):
        self.db = db

    def execute(self, raw: str) -> MmlResult:
        text = raw.strip()
        if not text:
            return MmlResult(False, "MML-SYNTAX", "Empty command")
        if not text.startswith(">"):
            return MmlResult(False, "MML-SYNTAX", "Command must start with '>'")
        if not text.endswith(";"):
            return MmlResult(False, "MML-SYNTAX", "Command must end with ';'")

        body = re.sub(r"\s+", " ", text[1:-1].strip())
        if body.upper() in {"HELP", "H"}:
            return MmlResult(
                True,
                "OK",
                "Supported commands: DISP, STAT, TEST, CR, CAN, MOD, CONF, DIAG",
            )

        # Normalize compact forms such as CRSUB: and DISPSUB:.
        body = re.sub(
            r"^(CR|CAN|MOD|DISP|STAT|TEST|CONF|DIAG)\s*([A-Z]+)\s*:",
            lambda m: f"{m.group(1)} {m.group(2)}:",
            body,
            flags=re.I,
        )
        match = re.match(
            r"^(?P<verb>[A-Za-z]+)(?:\s+(?P<object>[A-Za-z]+))?\s*:\s*(?P<params>.*)$",
            body,
        )
        if not match:
            return MmlResult(
                False,
                "MML-SYNTAX",
                "Expected VERB OBJECT: param=value, ...;",
            )

        verb = match.group("verb").upper()
        obj = (match.group("object") or "").upper()
        params = self._params(match.group("params"))

        try:
            if verb == "DISP" and obj == "SUB":
                return self._disp_sub(params)
            if verb == "DISP" and obj == "DLU":
                return self._disp_dlu(params)
            if verb == "DISP" and obj == "SLOT":
                return self._disp_slot(params)
            if verb == "STAT" and obj == "SUB":
                return self._stat_sub(params)
            if verb == "STAT" and obj == "DLU":
                return self._disp_dlu(params, title="DLU STATUS")
            if verb == "TEST" and obj == "SUB":
                return self._test_sub(params)
            if verb == "CR" and obj == "SUB":
                return self._cr_sub(params)
            if verb == "CAN" and obj == "SUB":
                return self._can_sub(params)
            if verb == "MOD" and obj == "SUB":
                return self._mod_sub(params)
            if verb == "CONF" and obj == "DLU":
                return self._conf_dlu(params)
            if verb == "DIAG" and obj == "DLU":
                return self._diag_dlu(params)
            return MmlResult(
                False,
                "MML-UNKNOWN-COMMAND",
                f"Unsupported command: {verb} {obj}".strip(),
            )
        except sqlite3.IntegrityError as exc:
            self.db.conn.rollback()
            return MmlResult(False, "DB-CONSTRAINT", str(exc))
        except ValueError as exc:
            self.db.conn.rollback()
            return MmlResult(False, "MML-VALIDATION", str(exc))

    @staticmethod
    def _params(text: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for piece in text.split(","):
            piece = piece.strip()
            if not piece or "=" not in piece:
                continue
            key, value = piece.split("=", 1)
            result[key.strip().lower()] = value.strip()
        return result

    @staticmethod
    def _required(params: dict[str, str], *keys: str) -> None:
        for key in keys:
            if not params.get(key):
                raise ValueError(f"Missing parameter: {key}")

    @staticmethod
    def _eqn(value: str) -> tuple[int, int, int, int]:
        match = re.fullmatch(r"(\d+)-(\d+)-(\d+)-(\d+)", value.strip())
        if not match:
            raise ValueError("EQN must be DLU-SHELF-MODULE-PORT")
        dlu, shelf, module, port = map(int, match.groups())
        if not 0 <= shelf <= 7:
            raise ValueError("Shelf must be 0..7")
        if not 0 <= module <= 15:
            raise ValueError("Module must be 0..15")
        return dlu, shelf, module, port

    def _slot_or_fail(self, eqn: str):
        dlu, shelf, module, port = self._eqn(eqn)
        slot = self.db.get_slot(dlu, shelf, module)
        if not slot:
            raise ValueError(f"EQN slot not found: {eqn}")
        if slot.card_type == "UNCONFIGURED":
            raise ValueError("The module is UNCONFIGURED")
        if port < 0 or port >= slot.port_count:
            max_port = max(slot.port_count - 1, -1)
            raise ValueError(
                f"Port {port} is outside {slot.card_type} capacity 0..{max_port}"
            )
        return dlu, shelf, module, port, slot

    def _disp_sub(self, params: dict[str, str]) -> MmlResult:
        self._required(params, "dn")
        raw_dn = params["dn"]
        if "&&" in raw_dn:
            start, end = [item.strip() for item in raw_dn.split("&&", 1)]
            rows = self.db.list_subscribers_range(start, end)
        else:
            row = self.db.get_subscriber(raw_dn, params.get("lac"))
            rows = [row] if row else []

        if not rows:
            return MmlResult(False, "DN-NOT-FOUND", f"Subscriber {raw_dn} not found")

        data = []
        for row in rows:
            item = dict(row)
            item["eqn"] = (
                f"{row['dlu_id']}-{row['shelf']}-{row['module']}-{row['port']}"
            )
            data.append(item)
        return MmlResult(
            True,
            "OK",
            f"{len(rows)} subscriber record(s)",
            data,
        )

    def _disp_dlu(
        self, params: dict[str, str], title: str = "DLU DISPLAY"
    ) -> MmlResult:
        self._required(params, "dlu")
        dlu_id = int(params["dlu"])
        dlu = self.db.get_dlu(dlu_id)
        if not dlu:
            return MmlResult(False, "DLU-NOT-FOUND", f"DLU {dlu_id} not found")

        slots = self.db.list_dlu_slots(dlu_id)
        configured = sum(
            1 for slot in slots if slot["card_type"] != "UNCONFIGURED"
        )
        subscribers = self.db.list_subscribers_for_dlu(dlu_id)
        data = {
            "title": title,
            "dlu": dlu_id,
            "exchange": dlu["exchange_code"],
            "dluc0": dlu["dluc0_state"],
            "dluc1": dlu["dluc1_state"],
            "configured_modules": configured,
            "subscriber_count": len(subscribers),
            "shelves": 8,
            "modules_per_shelf": 16,
        }
        return MmlResult(
            True,
            "OK",
            f"DLU {dlu_id} operational",
            data,
        )

    def _disp_slot(self, params: dict[str, str]) -> MmlResult:
        self._required(params, "dlu", "shelf", "module")
        slot = self.db.get_slot(
            int(params["dlu"]),
            int(params["shelf"]),
            int(params["module"]),
        )
        if not slot:
            return MmlResult(False, "SLOT-NOT-FOUND", "Slot not found")

        rows = self.db.conn.execute(
            """
            SELECT * FROM subscribers
            WHERE dlu_id=? AND shelf=? AND module=?
            ORDER BY port
            """,
            (slot.dlu_id, slot.shelf, slot.module),
        ).fetchall()
        return MmlResult(
            True,
            "OK",
            f"{slot.card_type} with {slot.port_count} port(s)",
            {
                "slot": slot.__dict__,
                "subscribers": [dict(row) for row in rows],
            },
        )

    def _stat_sub(self, params: dict[str, str]) -> MmlResult:
        result = self._disp_sub(params)
        if not result.ok:
            return result
        rows = result.data or []
        for row in rows:
            row["status"] = (
                f"{row['line_state']} / "
                f"{'BLOCKED' if row['blk_reason'] else 'NORMAL'}"
            )
        return MmlResult(True, "OK", "Subscriber status", rows)

    def _test_sub(self, params: dict[str, str]) -> MmlResult:
        result = self._disp_sub(params)
        if not result.ok:
            return result
        rows = result.data or []
        tested = []
        for row in rows:
            tested.append(
                {
                    "dn": row["dn"],
                    "eqn": row["eqn"],
                    "result": "PASS",
                    "line_state": row["line_state"],
                }
            )
        return MmlResult(True, "TEST-PASS", "Line test completed", tested)

    def _cr_sub(self, params: dict[str, str]) -> MmlResult:
        self._required(params, "dn", "eqn", "lac")
        dlu, shelf, module, port, _ = self._slot_or_fail(params["eqn"])
        dn = params["dn"]

        if self.db.get_subscriber(dn, params["lac"]):
            return MmlResult(False, "DN-EXISTS", f"DN {dn} already exists")

        occupied = self.db.conn.execute(
            """
            SELECT 1 FROM subscribers
            WHERE dlu_id=? AND shelf=? AND module=? AND port=?
            """,
            (dlu, shelf, module, port),
        ).fetchone()
        if occupied:
            return MmlResult(
                False,
                "PORT-OCCUPIED",
                f"Port {params['eqn']} is already occupied",
            )

        with self.db.conn:
            self.db.conn.execute(
                """
                INSERT INTO subscribers(
                    lac,dn,dlu_id,shelf,module,port,
                    sub_type,dial_mode,line_state,cos_flags,blk_reason
                )
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    params["lac"],
                    dn,
                    dlu,
                    shelf,
                    module,
                    port,
                    params.get("class", "ms"),
                    params.get("c/s", "PB"),
                    "idle",
                    params.get("cos", ""),
                    None,
                ),
            )
            self.db.event(
                "SubscriberCreated",
                "subscriber",
                dn,
                json.dumps(
                    {"eqn": params["eqn"], "lac": params["lac"]}
                ),
            )
        return MmlResult(
            True,
            "CREATED",
            f"Subscriber {dn} created at {params['eqn']}",
            {"dn": dn, "eqn": params["eqn"], "state": "idle"},
        )

    def _can_sub(self, params: dict[str, str]) -> MmlResult:
        self._required(params, "dn")
        row = self.db.get_subscriber(params["dn"], params.get("lac"))
        if not row:
            return MmlResult(
                False,
                "DN-NOT-FOUND",
                f"Subscriber {params['dn']} not found",
            )

        with self.db.conn:
            self.db.conn.execute(
                "DELETE FROM subscribers WHERE lac=? AND dn=?",
                (row["lac"], row["dn"]),
            )
            self.db.event(
                "SubscriberCancelled",
                "subscriber",
                row["dn"],
                json.dumps(
                    {
                        "eqn": (
                            f"{row['dlu_id']}-{row['shelf']}-"
                            f"{row['module']}-{row['port']}"
                        )
                    }
                ),
            )
        return MmlResult(
            True,
            "CANCELLED",
            f"Subscriber {row['dn']} cancelled",
            {
                "released_eqn": (
                    f"{row['dlu_id']}-{row['shelf']}-"
                    f"{row['module']}-{row['port']}"
                )
            },
        )

    def _mod_sub(self, params: dict[str, str]) -> MmlResult:
        self._required(params, "dn")
        row = self.db.get_subscriber(params["dn"], params.get("lac"))
        if not row:
            return MmlResult(
                False,
                "DN-NOT-FOUND",
                f"Subscriber {params['dn']} not found",
            )

        allowed = {"cos", "blk", "line"}
        updates: list[str] = []
        values: list[str | None] = []

        if "cos" in params:
            updates.append("cos_flags=?")
            values.append(params["cos"])
        if "blk" in params:
            updates.append("blk_reason=?")
            values.append(params["blk"])
        if "line" in params:
            line = params["line"].lower()
            if line not in {"idle", "busy", "blocked"}:
                return MmlResult(
                    False,
                    "LINE-STATE",
                    "line must be idle, busy or blocked",
                )
            updates.append("line_state=?")
            values.append(line)

        extra = {
            key for key in params if key not in {"dn", "lac"}
        }
        if not updates or any(key not in allowed for key in extra):
            return MmlResult(
                False,
                "MML-PARAM",
                "Supported MOD SUB parameters: cos, blk, line",
            )

        values.extend([row["lac"], row["dn"]])
        with self.db.conn:
            self.db.conn.execute(
                f"UPDATE subscribers SET {', '.join(updates)} "
                "WHERE lac=? AND dn=?",
                values,
            )
            self.db.event(
                "SubscriberModified",
                "subscriber",
                row["dn"],
                json.dumps(
                    {
                        key: value
                        for key, value in params.items()
                        if key not in {"dn", "lac"}
                    }
                ),
            )
        return MmlResult(
            True,
            "MODIFIED",
            f"Subscriber {row['dn']} modified",
        )

    def _conf_dlu(self, params: dict[str, str]) -> MmlResult:
        self._required(params, "dlu")
        dlu_id = int(params["dlu"])
        dlu = self.db.get_dlu(dlu_id)
        if not dlu:
            return MmlResult(False, "DLU-NOT-FOUND", f"DLU {dlu_id} not found")

        requested = params.get("dluc0")
        ost = params.get("ost")
        if not requested or not ost:
            return MmlResult(
                False,
                "MML-PARAM",
                "CONF DLU needs dluc0=y|n and ost=mbl|act",
            )

        with self.db.conn:
            if requested.lower() in {"y", "yes"}:
                if ost.lower() == "mbl":
                    self.db.conn.execute(
                        "UPDATE dlus SET dluc0_state='mbl', dluc1_state='act' "
                        "WHERE dlu_id=?",
                        (dlu_id,),
                    )
                    self.db.clear_active_alarms(f"DLU {dlu_id}")
                else:
                    self.db.conn.execute(
                        "UPDATE dlus SET dluc0_state='act' WHERE dlu_id=?",
                        (dlu_id,),
                    )
                self.db.event(
                    "DluStateChanged",
                    "dlu",
                    str(dlu_id),
                    json.dumps({"dluc0": ost.lower()}),
                )

        current = self.db.get_dlu(dlu_id)
        return MmlResult(
            True,
            "CONFIGURED",
            f"DLU {dlu_id} configuration updated",
            {
                "dluc0": current["dluc0_state"],
                "dluc1": current["dluc1_state"],
            },
        )

    def _diag_dlu(self, params: dict[str, str]) -> MmlResult:
        self._required(params, "dlu")
        dlu_id = int(params["dlu"])
        dlu = self.db.get_dlu(dlu_id)
        if not dlu:
            return MmlResult(False, "DLU-NOT-FOUND", f"DLU {dlu_id} not found")

        if dlu["dluc0_state"] != "mbl" and dlu["dluc1_state"] != "mbl":
            return MmlResult(
                False,
                "STATE-GUARD",
                "DIAG rejected: DLU must first be placed in ost=mbl",
            )

        return MmlResult(
            True,
            "DIAG-PASS",
            f"DLU {dlu_id} diagnostic completed",
            {"test_area": "all", "result": "PASS"},
        )
