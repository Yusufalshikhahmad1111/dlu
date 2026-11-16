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
                "Commands: DISP, STAT, TEST, CR, CAN, MOD, CONF, DIAG",
                {
                    "examples": [
                        "> stat dlu: dlu=50;",
                        "> disp dlumod: dlu=50, shelf=0, module=15;",
                        "> disp dlupport: eqn=50-0-15-0;",
                        "> statport: eqn=50-0-15-0;",
                        "> diag dlumod: dlu=10, shelf=1, module=7;",
                    ],
                },
            )

        # Accept spaced and compact command forms, e.g. CR SUB and CRSUB.
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
            # STATPORT: and similar single-token objects.
            compact = re.match(
                r"^(?P<verb>STATPORT|DISPDLUPORT|TESTDLULC)\s*:\s*(?P<params>.*)$",
                body,
                flags=re.I,
            )
            if not compact:
                return MmlResult(
                    False,
                    "MML-SYNTAX",
                    "Expected VERB OBJECT: param=value, ...;",
                )
            verb = compact.group("verb").upper()
            obj = ""
            params = self._params(compact.group("params"))
        else:
            verb = match.group("verb").upper()
            obj = (match.group("object") or "").upper()
            params = self._params(match.group("params"))

        try:
            if verb == "DISP" and obj == "SUB":
                return self._disp_sub(params)
            if verb == "DISP" and obj == "DLU":
                return self._disp_dlu(params)
            if verb == "DISP" and obj in {"DLUMOD", "MODULE"}:
                return self._disp_module(params)
            if verb == "DISP" and obj in {"DLUPORT", "PORT"}:
                return self._disp_port(params)
            if verb == "DISP" and obj == "SLOT":
                return self._disp_module(params)
            if verb == "DISP" and obj == "CPT":
                return self._disp_cpt(params)
            if verb == "DISP" and obj == "ALARMS":
                return self._disp_alarms(params)

            if verb == "STAT" and obj == "SUB":
                return self._stat_sub(params)
            if verb == "STAT" and obj == "DLU":
                return self._disp_dlu(params, title="DLU STATUS")
            if verb == "STAT" and obj in {"DLUMOD", "MODULE"}:
                return self._stat_module(params)
            if verb == "STAT" and obj == "PORT":
                return self._stat_port(params)
            if verb == "STATPORT":
                return self._stat_port(params)

            if verb == "TEST" and obj == "SUB":
                return self._test_sub(params)
            if verb == "TEST" and obj in {"DLULC", "DLU"}:
                return self._test_dluc(params)
            if verb == "TEST" and obj in {"DLUMOD", "MODULE"}:
                return self._diag_module(params, test_only=True)

            if verb == "CR" and obj == "SUB":
                return self._cr_sub(params)
            if verb == "CR" and obj == "DEST":
                return self._cr_dest(params)

            if verb == "CAN" and obj == "SUB":
                return self._can_sub(params)

            if verb == "MOD" and obj == "SUB":
                return self._mod_sub(params)

            if verb == "CONF" and obj == "DLU":
                return self._conf_dlu(params)
            if verb == "CONF" and obj in {"DLUMOD", "MODULE"}:
                return self._conf_module(params)

            if verb == "DIAG" and obj in {"DLU", "DLUC"}:
                return self._diag_dlu(params)
            if verb == "DIAG" and obj in {"DLUMOD", "MODULE"}:
                return self._diag_module(params)

            return MmlResult(
                False,
                "MML-UNKNOWN-COMMAND",
                f"Unsupported command: {verb} {obj}".strip(),
            )
        except sqlite3.IntegrityError as exc:
            self.db.conn.rollback()
            return MmlResult(False, "DB-CONSTRAINT", str(exc))
        except (TypeError, ValueError) as exc:
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
        if port < 0:
            raise ValueError("Port must be >= 0")
        return dlu, shelf, module, port

    def _module_params(self, params: dict[str, str]) -> tuple[int, int, int]:
        self._required(params, "dlu", "shelf", "module")
        dlu = int(params["dlu"])
        shelf = int(params["shelf"])
        module = int(params["module"])
        if not 0 <= shelf <= 7:
            raise ValueError("Shelf must be 0..7")
        if not 0 <= module <= 15:
            raise ValueError("Module must be 0..15")
        if self.db.get_dlu(dlu) is None:
            raise ValueError(f"DLU {dlu} not found")
        if self.db.get_slot(dlu, shelf, module) is None:
            raise ValueError("Module not found")
        return dlu, shelf, module

    def _slot_or_fail(self, eqn: str):
        dlu, shelf, module, port = self._eqn(eqn)
        slot = self.db.get_slot(dlu, shelf, module)
        if not slot:
            raise ValueError(f"EQN slot not found: {eqn}")
        if slot.card_type == "UNCONFIGURED":
            raise ValueError("The module is UNCONFIGURED")
        if port > slot.port_count - 1:
            raise ValueError(
                f"Port {port} is outside {slot.card_type} capacity "
                f"{slot.port_start if hasattr(slot, 'port_start') else 0}..{slot.port_count - 1}"
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
        return MmlResult(True, "OK", f"{len(rows)} subscriber record(s)", data)

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
        sides = [dict(row) for row in self.db.list_side_states(dlu_id)]
        data = {
            "title": title,
            "dlu": dlu_id,
            "exchange": dlu["exchange_code"],
            "dluc0": dlu["dluc0_state"],
            "dluc1": dlu["dluc1_state"],
            "sides": sides,
            "configured_modules": configured,
            "subscriber_count": len(subscribers),
            "shelves": 8,
            "modules_per_shelf": 16,
        }
        return MmlResult(True, "OK", f"DLU {dlu_id} operational", data)

    def _disp_module(self, params: dict[str, str]) -> MmlResult:
        dlu, shelf, module = self._module_params(params)
        slot = self.db.get_slot(dlu, shelf, module)
        rows = self.db.conn.execute(
            """
            SELECT * FROM subscribers
            WHERE dlu_id=? AND shelf=? AND module=?
            ORDER BY port
            """,
            (dlu, shelf, module),
        ).fetchall()
        return MmlResult(
            True,
            "OK",
            f"{slot.card_type} module {dlu}-{shelf}-{module}",
            {
                "dlu": dlu,
                "shelf": shelf,
                "module": module,
                "card_type": slot.card_type,
                "role": slot.role,
                "family": slot.family,
                "capacity": slot.port_count,
                "ost": slot.ost,
                "fault_state": slot.fault_state,
                "source_id": slot.source_id,
                "subscribers": [dict(row) for row in rows],
            },
        )

    def _disp_port(self, params: dict[str, str]) -> MmlResult:
        self._required(params, "eqn")
        dlu, shelf, module, port, slot = self._slot_or_fail(params["eqn"])
        sub = self.db.get_port_subscriber(dlu, shelf, module, port)
        return MmlResult(
            True,
            "OK",
            f"Port {params['eqn']}",
            {
                "eqn": params["eqn"],
                "dlu": dlu,
                "shelf": shelf,
                "module": module,
                "port": port,
                "card_type": slot.card_type,
                "card_ost": slot.ost,
                "fault_state": slot.fault_state,
                "subscriber": dict(sub) if sub else None,
            },
        )

    def _stat_sub(self, params: dict[str, str]) -> MmlResult:
        result = self._disp_sub(params)
        if not result.ok:
            return result
        for row in result.data or []:
            row["status"] = (
                f"{row['line_state']} / "
                f"{'BLOCKED' if row['blk_reason'] else 'NORMAL'}"
            )
        return MmlResult(True, "OK", "Subscriber status", result.data)

    def _stat_module(self, params: dict[str, str]) -> MmlResult:
        result = self._disp_module(params)
        if result.ok:
            result.message = "Module status"
        return result

    def _stat_port(self, params: dict[str, str]) -> MmlResult:
        result = self._disp_port(params)
        if result.ok:
            result.message = "Port status"
        return result

    def _test_sub(self, params: dict[str, str]) -> MmlResult:
        result = self._disp_sub(params)
        if not result.ok:
            return result
        tested = []
        for row in result.data or []:
            tested.append(
                {
                    "dn": row["dn"],
                    "eqn": row["eqn"],
                    "result": "PASS",
                    "line_state": row["line_state"],
                }
            )
        return MmlResult(True, "TEST-PASS", "Line test completed", tested)

    def _test_dluc(self, params: dict[str, str]) -> MmlResult:
        if "lc" in params and "-" in params["lc"]:
            dlu, side, _module, _port = self._eqn(params["lc"])
            side_id = side
        else:
            self._required(params, "dlu")
            dlu = int(params["dlu"])
            side_id = int(params.get("side", "0"))
        if self.db.get_dlu(dlu) is None:
            return MmlResult(False, "DLU-NOT-FOUND", f"DLU {dlu} not found")
        side = self.db.list_side_states(dlu)[side_id]
        return MmlResult(
            True,
            "TEST-PASS",
            f"DLUC{side_id} test completed",
            {
                "dlu": dlu,
                "side": side_id,
                "controller": side["controller"],
                "state": side["state"],
                "result": "PASS" if side["state"] != "mbl" else "MAINTENANCE",
            },
        )

    def _cr_sub(self, params: dict[str, str]) -> MmlResult:
        self._required(params, "dn", "eqn", "lac")
        dlu, shelf, module, port, slot = self._slot_or_fail(params["eqn"])
        dn = params["dn"]
        sub_type = params.get("type", params.get("class", "ms")).lower()

        card_ref = self.db.get_card_reference(slot.card_type)
        required_type = card_ref.subscriber_type if card_ref else None
        if required_type:
            accepted = {required_type}
            if required_type == "ms":
                accepted.add("main-station")
            if sub_type not in accepted:
                return MmlResult(
                    False,
                    "CARD-INCOMPATIBLE",
                    f"{slot.card_type} requires type={required_type}",
                )

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
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    params["lac"],
                    dn,
                    dlu,
                    shelf,
                    module,
                    port,
                    sub_type,
                    params.get("c/s", params.get("cs", "PB")),
                    "idle",
                    params.get("cos", ""),
                    None,
                ),
            )
            self.db.event(
                "SubscriberCreated",
                "subscriber",
                dn,
                json.dumps({"eqn": params["eqn"], "lac": params["lac"]}),
            )
        return MmlResult(
            True,
            "CREATED",
            f"Subscriber {dn} created at {params['eqn']}",
            {
                "dn": dn,
                "eqn": params["eqn"],
                "dlu": dlu,
                "shelf": shelf,
                "module": module,
                "port": port,
                "state": "idle",
            },
        )

    def _can_sub(self, params: dict[str, str]) -> MmlResult:
        self._required(params, "dn")
        row = self.db.get_subscriber(params["dn"], params.get("lac"))
        if not row:
            return MmlResult(False, "DN-NOT-FOUND", f"Subscriber {params['dn']} not found")

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
                "eqn": (
                    f"{row['dlu_id']}-{row['shelf']}-"
                    f"{row['module']}-{row['port']}"
                )
            },
        )

    def _mod_sub(self, params: dict[str, str]) -> MmlResult:
        self._required(params, "dn")
        row = self.db.get_subscriber(params["dn"], params.get("lac"))
        if not row:
            return MmlResult(False, "DN-NOT-FOUND", f"Subscriber {params['dn']} not found")

        updates: list[str] = []
        values: list[str | None] = []

        if "cos" in params:
            updates.append("cos_flags=?")
            values.append(params["cos"])
        if "ccos" in params:
            current = [x.strip() for x in row["cos_flags"].split("|") if x.strip()]
            remove = params["ccos"].lower()
            current = [x for x in current if x.lower() != remove]
            updates.append("cos_flags=?")
            values.append("|".join(current))
        if "blk" in params:
            updates.append("blk_reason=?")
            values.append(params["blk"])
            updates.append("line_state=?")
            values.append("blocked")
        if "cblk" in params:
            updates.append("blk_reason=?")
            values.append(None)
            if row["line_state"] == "blocked":
                updates.append("line_state=?")
                values.append("idle")
        if "optcl" in params:
            current = [x.strip() for x in row["cos_flags"].split("|") if x.strip()]
            if params["optcl"] not in current:
                current.append(params["optcl"])
            updates.append("cos_flags=?")
            values.append("|".join(current))
        if "line" in params:
            line = params["line"].lower()
            if line not in {"idle", "busy", "blocked"}:
                return MmlResult(False, "LINE-STATE", "line must be idle, busy or blocked")
            updates.append("line_state=?")
            values.append(line)

        if not updates:
            return MmlResult(
                False,
                "MML-PARAM",
                "Supported MOD SUB: cos, ccos, optcl, blk, cblk, line",
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
                json.dumps(params, ensure_ascii=False),
            )
        return MmlResult(True, "MODIFIED", f"Subscriber {row['dn']} modified")

    def _conf_dlu(self, params: dict[str, str]) -> MmlResult:
        self._required(params, "dlu", "ost")
        dlu = int(params["dlu"])
        if self.db.get_dlu(dlu) is None:
            return MmlResult(False, "DLU-NOT-FOUND", f"DLU {dlu} not found")

        if "dluc0" in params:
            side = 0
        elif "dluc1" in params:
            side = 1
        else:
            side = int(params.get("side", "0"))

        self.db.set_side_state(dlu, side, params["ost"])
        current = self.db.get_dlu(dlu)
        self.db.conn.commit()
        return MmlResult(
            True,
            "CONFIGURED",
            f"DLU {dlu} side {side} configuration updated",
            {
                "dluc0": current["dluc0_state"],
                "dluc1": current["dluc1_state"],
                "side": side,
                "ost": params["ost"].lower(),
            },
        )

    def _conf_module(self, params: dict[str, str]) -> MmlResult:
        dlu, shelf, module = self._module_params(params)
        ost = params.get("ost")
        if ost:
            slot = self.db.get_slot(dlu, shelf, module)
            if ost.lower() == "mbl":
                self.db.conn.execute(
                    """
                    UPDATE slots SET ost='mbl'
                    WHERE dlu_id=? AND shelf=? AND module=?
                    """,
                    (dlu,shelf,module),
                )
            elif ost.lower() == "act":
                if slot.fault_state == "fault":
                    return MmlResult(
                        False,
                        "STATE-GUARD",
                        "Cannot activate a module with a confirmed fault",
                    )
                self.db.conn.execute(
                    """
                    UPDATE slots SET ost='act'
                    WHERE dlu_id=? AND shelf=? AND module=?
                    """,
                    (dlu,shelf,module),
                )
            else:
                return MmlResult(False, "MML-PARAM", "ost must be mbl or act")

        self.db.conn.commit()
        return MmlResult(True, "CONFIGURED", "Module configuration updated", {
            "dlu":dlu, "shelf":shelf, "module":module,
            "ost":self.db.get_slot(dlu,shelf,module).ost
        })

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
            {"test_area": params.get("area", "all"), "result": "PASS"},
        )

    def _diag_module(
        self, params: dict[str, str], test_only: bool = False
    ) -> MmlResult:
        dlu, shelf, module = self._module_params(params)
        try:
            result = self.db.diagnose_module(dlu, shelf, module)
        except ValueError as exc:
            return MmlResult(False, "STATE-GUARD", str(exc))
        return MmlResult(
            result["result"] == "PASS",
            "DIAG-PASS" if result["result"] == "PASS" else "DIAG-FAULT",
            f"Module diagnostic {'completed' if not test_only else 'test completed'}",
            {
                "dlu": dlu,
                "shelf": shelf,
                "module": module,
                "card": result["card"],
                "result": result["result"],
            },
        )

    def _cr_dest(self, params: dict[str, str]) -> MmlResult:
        self._required(params, "dest", "code")
        name = params.get("name", params["dest"])
        route_type = params.get("route_type", "NATIONAL")
        with self.db.conn:
            self.db.conn.execute(
                """
                INSERT OR REPLACE INTO cpt_routes(
                    dest,code,eval,name,route_type
                ) VALUES (?,?,?,?,?)
                """,
                (
                    params["dest"],
                    params["code"],
                    params.get("eval", "YES"),
                    name,
                    route_type,
                ),
            )
        return MmlResult(
            True,
            "CREATED",
            f"Destination {name} created",
            {"dest": params["dest"], "code": params["code"]},
        )

    def _disp_cpt(self, params: dict[str, str]) -> MmlResult:
        rows = self.db.conn.execute(
            """
            SELECT * FROM cpt_routes
            WHERE (? IS NULL OR dest=?)
            AND (? IS NULL OR code=?)
            ORDER BY dest, code
            """,
            (
                params.get("dest"), params.get("dest"),
                params.get("code"), params.get("code"),
            ),
        ).fetchall()
        return MmlResult(True, "OK", f"{len(rows)} CPT route(s)", [dict(row) for row in rows])

    def _disp_alarms(self, params: dict[str, str]) -> MmlResult:
        rows = self.db.list_active_alarms()
        if params.get("type"):
            requested = params["type"].upper()
            rows = [row for row in rows if row["severity"] == requested]
        return MmlResult(True, "OK", f"{len(rows)} active alarm(s)", [dict(row) for row in rows])
