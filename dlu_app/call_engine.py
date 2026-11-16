from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
import uuid

from .db import Database


CALL_SCHEMA = """
CREATE TABLE IF NOT EXISTS call_resources (
    resource_id TEXT PRIMARY KEY,
    resource_type TEXT NOT NULL,
    capacity INTEGER NOT NULL CHECK(capacity >= 0),
    used INTEGER NOT NULL DEFAULT 0 CHECK(used >= 0),
    CHECK(used <= capacity)
);

CREATE TABLE IF NOT EXISTS call_sessions (
    call_id TEXT PRIMARY KEY,
    caller_dn TEXT NOT NULL,
    caller_lac TEXT NOT NULL,
    called_number TEXT NOT NULL,
    called_dn TEXT,
    call_type TEXT NOT NULL,
    state TEXT NOT NULL,
    failure_reason TEXT,
    cpt_dest TEXT,
    cpt_code TEXT,
    cpt_eval TEXT,
    route_name TEXT,
    created_at TEXT NOT NULL,
    connected_at TEXT,
    released_at TEXT
);

CREATE TABLE IF NOT EXISTS call_legs (
    call_id TEXT NOT NULL REFERENCES call_sessions(call_id) ON DELETE CASCADE,
    sequence_no INTEGER NOT NULL,
    node_type TEXT NOT NULL,
    node_id TEXT NOT NULL,
    from_node TEXT,
    to_node TEXT,
    state TEXT NOT NULL,
    resource_id TEXT,
    PRIMARY KEY(call_id, sequence_no)
);

CREATE TABLE IF NOT EXISTS call_resource_leases (
    call_id TEXT NOT NULL REFERENCES call_sessions(call_id) ON DELETE CASCADE,
    resource_id TEXT NOT NULL REFERENCES call_resources(resource_id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    PRIMARY KEY(call_id, resource_id)
);
"""


@dataclass(frozen=True)
class CptMatch:
    dest: str
    code: str
    sym: str
    eval: str
    name: str
    route_type: str
    match_kind: str
    score: int


@dataclass(frozen=True)
class NumberAnalysis:
    original: str
    normalized: str
    number_type: str
    target_lac: str | None
    target_dn: str | None
    cpt: CptMatch | None


@dataclass(frozen=True)
class CallNode:
    node_type: str
    node_id: str
    label: str


@dataclass(frozen=True)
class CallEdge:
    source: str
    target: str
    state: str
    resource_id: str | None


@dataclass(frozen=True)
class CallPath:
    call_type: str
    nodes: tuple[CallNode, ...]
    edges: tuple[CallEdge, ...]

    def labels(self) -> list[str]:
        return [node.label for node in self.nodes]


@dataclass(frozen=True)
class CallResult:
    ok: bool
    code: str
    message: str
    call_id: str | None = None
    path: CallPath | None = None
    analysis: NumberAnalysis | None = None
    data: dict | None = None


class CallRepository:
    def __init__(self, db: Database):
        self.db = db
        self.ensure_schema()
        self.ensure_resources()

    def ensure_schema(self) -> None:
        self.db.conn.executescript(CALL_SCHEMA)
        self.db.conn.commit()

    def ensure_resources(self) -> None:
        self.db.conn.execute(
            """
            INSERT OR IGNORE INTO call_resources(resource_id,resource_type,capacity,used)
            VALUES ('PDC-VOICE','PDC',120,0)
            """
        )
        self.db.conn.commit()

    def cpt_rows(self) -> list[dict]:
        return [
            dict(row)
            for row in self.db.conn.execute(
                "SELECT dest,code,sym,eval,name,route_type FROM cpt_routes"
            ).fetchall()
        ]

    def match_cpt(self, number: str) -> CptMatch | None:
        normalized = normalize_number(number)
        matches: list[CptMatch] = []
        for row in self.cpt_rows():
            code = str(row["code"]).strip()
            if not code:
                continue
            if "&&" in code:
                parts = [part.strip() for part in code.split("&&", 1)]
                if len(parts) != 2 or not all(part.isdigit() for part in parts):
                    continue
                lo, hi = (int(parts[0]), int(parts[1]))
                width = max(len(parts[0]), len(parts[1]))
                prefix = normalized[:width]
                if not prefix.isdigit():
                    continue
                value = int(prefix)
                if lo <= value <= hi:
                    matches.append(
                        CptMatch(
                            row["dest"], code, row["sym"], row["eval"], row["name"],
                            row["route_type"], "range", len(code),
                        )
                    )
                continue
            if normalized == code:
                kind = "exact"
            elif normalized.startswith(code):
                kind = "prefix"
            else:
                continue
            matches.append(
                CptMatch(
                    row["dest"], code, row["sym"], row["eval"], row["name"],
                    row["route_type"], kind, len(code),
                )
            )
        if not matches:
            return None
        matches.sort(key=lambda item: (item.score, item.match_kind == "exact"), reverse=True)
        return matches[0]

    def create_call(
        self,
        call_id: str,
        caller_dn: str,
        caller_lac: str,
        called_number: str,
        called_dn: str | None,
        call_type: str,
        state: str,
        failure_reason: str | None,
        cpt: CptMatch | None,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.db.conn.execute(
            """
            INSERT INTO call_sessions(
                call_id,caller_dn,caller_lac,called_number,called_dn,
                call_type,state,failure_reason,cpt_dest,cpt_code,cpt_eval,
                route_name,created_at,connected_at,released_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,NULL)
            """,
            (
                call_id, caller_dn, caller_lac, called_number, called_dn,
                call_type, state, failure_reason,
                cpt.dest if cpt else None,
                cpt.code if cpt else None,
                cpt.eval if cpt else None,
                cpt.name if cpt else None,
                now,
                now if state == "CONNECTED" else None,
            ),
        )

    def add_legs(self, call_id: str, path: CallPath) -> None:
        for idx, node in enumerate(path.nodes):
            source = path.nodes[idx - 1].node_id if idx else None
            edge_resource = None
            if idx > 0:
                edge_resource = next(
                    (
                        edge.resource_id
                        for edge in path.edges
                        if edge.source == source and edge.target == node.node_id
                    ),
                    None,
                )
            self.db.conn.execute(
                """
                INSERT INTO call_legs(
                    call_id,sequence_no,node_type,node_id,from_node,to_node,state,resource_id
                ) VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    call_id, idx, node.node_type, node.node_id,
                    source, node.node_id,
                    "ACTIVE" if idx > 0 else "IDLE",
                    edge_resource,
                ),
            )

    def reserve(self, call_id: str, resource_id: str, quantity: int = 1) -> None:
        row = self.db.conn.execute(
            "SELECT capacity,used FROM call_resources WHERE resource_id=?",
            (resource_id,),
        ).fetchone()
        if not row:
            raise ValueError(f"Resource {resource_id} not found")
        if row["used"] + quantity > row["capacity"]:
            raise RuntimeError("CALL-RESOURCE-BUSY")
        self.db.conn.execute(
            "UPDATE call_resources SET used=used+? WHERE resource_id=?",
            (quantity, resource_id),
        )
        self.db.conn.execute(
            """
            INSERT INTO call_resource_leases(call_id,resource_id,quantity)
            VALUES (?,?,?)
            """,
            (call_id, resource_id, quantity),
        )

    def release_all(self, call_id: str) -> None:
        leases = self.db.conn.execute(
            "SELECT resource_id,quantity FROM call_resource_leases WHERE call_id=?",
            (call_id,),
        ).fetchall()
        for lease in leases:
            self.db.conn.execute(
                "UPDATE call_resources SET used=MAX(0,used-?) WHERE resource_id=?",
                (lease["quantity"], lease["resource_id"]),
            )
        self.db.conn.execute(
            "DELETE FROM call_resource_leases WHERE call_id=?", (call_id,)
        )

    def resource_usage(self, resource_id: str = "PDC-VOICE") -> tuple[int, int]:
        row = self.db.conn.execute(
            "SELECT used,capacity FROM call_resources WHERE resource_id=?",
            (resource_id,),
        ).fetchone()
        if not row:
            return 0, 0
        return int(row["used"]), int(row["capacity"])

    def get_call(self, call_id: str) -> dict | None:
        row = self.db.conn.execute(
            "SELECT * FROM call_sessions WHERE call_id=?", (call_id,)
        ).fetchone()
        return dict(row) if row else None

    def legs(self, call_id: str) -> list[dict]:
        return [
            dict(row)
            for row in self.db.conn.execute(
                "SELECT * FROM call_legs WHERE call_id=? ORDER BY sequence_no",
                (call_id,),
            ).fetchall()
        ]

    def reset_demo(self) -> None:
        with self.db.conn:
            self.db.conn.execute("DELETE FROM call_resource_leases")
            self.db.conn.execute("DELETE FROM call_legs")
            self.db.conn.execute("DELETE FROM call_sessions")
            self.db.conn.execute("UPDATE call_resources SET used=0")

    def update_call_state(self, call_id: str, state: str, reason: str | None = None) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.db.conn.execute(
            """
            UPDATE call_sessions
            SET state=?, failure_reason=?,
                connected_at=CASE WHEN ?='CONNECTED' THEN ? ELSE connected_at END,
                released_at=CASE WHEN ?='RELEASED' THEN ? ELSE released_at END
            WHERE call_id=?
            """,
            (state, reason, state, now, state, now, call_id),
        )


class CallEngine:
    def __init__(self, db: Database):
        self.db = db
        self.repo = CallRepository(db)

    def analyze(self, caller_dn: str, dialed_number: str) -> NumberAnalysis:
        caller = self.db.get_subscriber(caller_dn)
        if not caller:
            raise ValueError("CALL-NOT-FOUND")
        normalized = normalize_number(dialed_number)
        if not normalized or not normalized.isdigit():
            raise ValueError("CALL-INVALID-NUMBER")

        cpt = self.repo.match_cpt(normalized)
        target_lac = None
        target_dn = None
        number_type = "UNKNOWN"

        exact_local = self.db.get_subscriber(normalized, caller["lac"])
        if exact_local:
            target_lac = exact_local["lac"]
            target_dn = exact_local["dn"]
            number_type = "LOCAL"
        elif cpt:
            route_type = cpt.route_type.upper()
            if cpt.dest == "ALSTN":
                target_lac = cpt.code
                candidate = normalized[len(cpt.code):]
                target_dn = candidate or normalized
                number_type = "LOCAL" if target_lac == caller["lac"] else "NATIONAL"
            elif cpt.dest == "ALSTI":
                number_type = "INTERNATIONAL"
            elif cpt.dest in {"SERVICE", "EMERGENCY"}:
                number_type = "SERVICE"
            else:
                number_type = route_type
        else:
            number_type = "UNKNOWN"

        return NumberAnalysis(
            original=dialed_number,
            normalized=normalized,
            number_type=number_type,
            target_lac=target_lac,
            target_dn=target_dn,
            cpt=cpt,
        )

    @staticmethod
    def _remote_dlu(target_lac: str | None) -> str:
        return f"DLU-LAC{target_lac}" if target_lac else "REMOTE-DLU"

    def build_path(
        self,
        caller: dict,
        analysis: NumberAnalysis,
        target: dict | None = None,
        state: str = "ACTIVE",
    ) -> CallPath:
        caller_node = CallNode("DLU", f"DLU-{caller['dlu_id']}", f"DLU {caller['dlu_id']}")
        if analysis.number_type == "LOCAL":
            target_dlu = target["dlu_id"] if target else caller["dlu_id"]
            nodes = (
                caller_node,
                CallNode("SN", "SN", "SN"),
                CallNode("DLU", f"DLU-{target_dlu}", f"DLU {target_dlu}"),
            )
        elif analysis.number_type == "NATIONAL":
            nodes = (
                caller_node,
                CallNode("LTG", f"LTG-{caller['dlu_id']}", "LTG"),
                CallNode("SN", "SN", "SN"),
                CallNode("LTG", f"LTG-{analysis.target_lac or 'REMOTE'}", "LTG"),
                CallNode("DLU", self._remote_dlu(analysis.target_lac), self._remote_dlu(analysis.target_lac)),
            )
        elif analysis.number_type == "INTERNATIONAL":
            nodes = (
                caller_node,
                CallNode("LTG", f"LTG-{caller['dlu_id']}", "LTG"),
                CallNode("SN", "SN", "SN"),
                CallNode("GATEWAY", "ALSTI", "International Gateway"),
            )
        elif analysis.number_type == "SERVICE":
            nodes = (
                caller_node,
                CallNode("SN", "SN", "SN"),
                CallNode("SERVICE", analysis.normalized, f"SERVICE {analysis.normalized}"),
            )
        elif analysis.cpt and analysis.cpt.eval.upper() == "NO":
            nodes = (caller_node, CallNode("CPT", "CPT", "CPT / BLOCKED"))
        else:
            nodes = (caller_node, CallNode("CPT", "CPT", "CPT / NO ROUTE"))

        edges = tuple(
            CallEdge(
                source=nodes[idx].node_id,
                target=nodes[idx + 1].node_id,
                state=state,
                resource_id=(
                    "PDC-VOICE"
                    if analysis.number_type in {"NATIONAL", "INTERNATIONAL"} and idx >= 1
                    else None
                ),
            )
            for idx in range(len(nodes) - 1)
        )
        return CallPath(analysis.number_type, nodes, edges)

    def _fail(
        self,
        caller: dict,
        analysis: NumberAnalysis,
        code: str,
        message: str,
        reason: str,
    ) -> CallResult:
        call_id = f"CALL-{uuid.uuid4().hex[:10].upper()}"
        path = self.build_path(caller, analysis, state="BLOCKED")
        with self.db.conn:
            self.repo.create_call(
                call_id,
                caller["dn"],
                caller["lac"],
                analysis.normalized,
                analysis.target_dn,
                analysis.number_type,
                "FAILED",
                reason,
                analysis.cpt,
            )
            self.repo.add_legs(call_id, path)
            self.db.event(
                "CallFailed",
                "call",
                call_id,
                json.dumps({"code": code, "reason": reason}),
            )
        return CallResult(False, code, message, call_id, path, analysis, {"reason": reason})

    def start_call(self, caller_dn: str, dialed_number: str) -> CallResult:
        caller = self.db.get_subscriber(caller_dn)
        if not caller:
            return CallResult(False, "CALL-NOT-FOUND", f"Caller {caller_dn} not found")
        if caller["blk_reason"] or caller["line_state"] == "blocked":
            return CallResult(False, "CALL-BLOCKED", f"Caller {caller_dn} is blocked")
        if caller["line_state"] == "busy":
            return CallResult(False, "CALL-PORT-BUSY", f"Caller {caller_dn} is already busy")

        try:
            analysis = self.analyze(caller_dn, dialed_number)
        except ValueError as exc:
            return CallResult(False, str(exc), str(exc))

        if analysis.cpt and analysis.cpt.eval.upper() == "NO":
            return self._fail(
                caller, analysis, "CALL-BLOCKED",
                f"{analysis.cpt.name} · EVAL=NO", analysis.cpt.name,
            )

        target = None
        if analysis.number_type == "LOCAL":
            target = self.db.get_subscriber(
                analysis.target_dn or analysis.normalized, caller["lac"]
            )
            if not target:
                return self._fail(
                    caller, analysis, "CALL-NOT-FOUND",
                    "Called local subscriber not found", "target-not-found",
                )
            if target["dn"] == caller["dn"]:
                return self._fail(
                    caller, analysis, "CALL-SAME-SUBSCRIBER",
                    "Caller and called subscriber are identical", "same-subscriber",
                )
            if target["blk_reason"] or target["line_state"] == "blocked":
                return self._fail(
                    caller, analysis, "CALL-BLOCKED",
                    f"Called subscriber {target['dn']} is blocked", "called-blocked",
                )
            if target["line_state"] == "busy":
                return self._fail(
                    caller, analysis, "CALL-PORT-BUSY",
                    f"Called subscriber {target['dn']} is busy", "called-busy",
                )

        if analysis.number_type == "UNKNOWN":
            return self._fail(
                caller, analysis, "CALL-NO-ROUTE",
                "Number analysis produced no route", "no-route",
            )

        path = self.build_path(caller, analysis, target=target)
        call_id = f"CALL-{uuid.uuid4().hex[:10].upper()}"

        with self.db.conn:
            self.repo.create_call(
                call_id,
                caller["dn"],
                caller["lac"],
                analysis.normalized,
                target["dn"] if target else analysis.target_dn,
                analysis.number_type,
                "SETUP",
                None,
                analysis.cpt,
            )

            if analysis.number_type in {"NATIONAL", "INTERNATIONAL"}:
                try:
                    self.repo.reserve(call_id, "PDC-VOICE", 1)
                except RuntimeError:
                    self.repo.update_call_state(call_id, "FAILED", "PDC capacity exhausted")
                    self.repo.add_legs(call_id, path)
                    self.db.event(
                        "CallFailed",
                        "call",
                        call_id,
                        json.dumps({"code": "CALL-RESOURCE-BUSY"}),
                    )
                    return CallResult(
                        False,
                        "CALL-RESOURCE-BUSY",
                        "No PDC voice channel is available",
                        call_id,
                        path,
                        analysis,
                    )

            self.db.conn.execute(
                "UPDATE subscribers SET line_state='busy' WHERE lac=? AND dn=?",
                (caller["lac"], caller["dn"]),
            )
            if target:
                self.db.conn.execute(
                    "UPDATE subscribers SET line_state='busy' WHERE lac=? AND dn=?",
                    (target["lac"], target["dn"]),
                )

            self.repo.update_call_state(call_id, "CONNECTED")
            self.repo.add_legs(call_id, path)
            self.db.event(
                "CallConnected",
                "call",
                call_id,
                json.dumps(
                    {
                        "caller": caller["dn"],
                        "called": target["dn"] if target else analysis.target_dn,
                        "type": analysis.number_type,
                        "cpt": analysis.cpt.code if analysis.cpt else None,
                    }
                ),
            )

        return CallResult(
            True,
            "CALL-CONNECTED",
            f"{analysis.number_type} call connected",
            call_id,
            path,
            analysis,
            {
                "caller_dn": caller["dn"],
                "called_dn": target["dn"] if target else analysis.target_dn,
                "cpt": {
                    "dest": analysis.cpt.dest if analysis.cpt else None,
                    "code": analysis.cpt.code if analysis.cpt else None,
                    "eval": analysis.cpt.eval if analysis.cpt else None,
                    "name": analysis.cpt.name if analysis.cpt else None,
                },
            },
        )

    def release_call(self, call_id: str) -> CallResult:
        call = self.repo.get_call(call_id)
        if not call:
            return CallResult(False, "CALL-NOT-FOUND", f"Call {call_id} not found")
        if call["state"] == "RELEASED":
            return CallResult(True, "CALL-ALREADY-RELEASED", "Call already released", call_id)

        with self.db.conn:
            for dn, lac in (
                (call["caller_dn"], call["caller_lac"]),
                (call["called_dn"], None),
            ):
                if not dn:
                    continue
                row = self.db.get_subscriber(dn, lac)
                if row and row["line_state"] == "busy":
                    self.db.conn.execute(
                        "UPDATE subscribers SET line_state='idle' WHERE lac=? AND dn=?",
                        (row["lac"], row["dn"]),
                    )
            self.repo.release_all(call_id)
            self.repo.update_call_state(call_id, "RELEASED")
            self.db.conn.execute(
                "UPDATE call_legs SET state='RELEASED' WHERE call_id=?",
                (call_id,),
            )
            self.db.event(
                "CallReleased",
                "call",
                call_id,
                json.dumps({"caller": call["caller_dn"], "called": call["called_dn"]}),
            )

        path = self.path_for(call_id)
        return CallResult(True, "CALL-RELEASED", f"Call {call_id} released", call_id, path)

    def path_for(self, call_id: str) -> CallPath | None:
        call = self.repo.get_call(call_id)
        if not call:
            return None
        legs = self.repo.legs(call_id)
        if not legs:
            return None
        nodes = tuple(
            CallNode(leg["node_type"], leg["node_id"], leg["node_id"])
            for leg in legs
        )
        edges = tuple(
            CallEdge(
                legs[idx]["node_id"],
                legs[idx + 1]["node_id"],
                legs[idx + 1]["state"],
                legs[idx + 1]["resource_id"],
            )
            for idx in range(len(legs) - 1)
        )
        return CallPath(call["call_type"], nodes, edges)

    def resource_usage(self) -> tuple[int, int]:
        return self.repo.resource_usage()

    def active_call_count(self) -> int:
        row = self.db.conn.execute(
            "SELECT COUNT(*) AS n FROM call_sessions WHERE state='CONNECTED'"
        ).fetchone()
        return int(row["n"])

    def prepare_demo_subscribers(self) -> tuple[str, str]:
        slot = self.db.get_slot(50, 0, 15)
        if not slot or slot.card_type != "SLMA8":
            raise ValueError("Source-backed SLMA8 demo slot 50-0-15 is unavailable")
        created: list[str] = []
        for port, dn in ((0, "2233500"), (1, "2233501")):
            existing = self.db.get_port_subscriber(50, 0, 15, port)
            if existing:
                if existing["dn"] == dn:
                    created.append(dn)
                    continue
                raise ValueError(
                    f"Demo port 50-0-15-{port} is already used by {existing['dn']}"
                )
            with self.db.conn:
                self.db.conn.execute(
                    """
                    INSERT INTO subscribers(
                        lac,dn,dlu_id,shelf,module,port,sub_type,dial_mode,
                        line_state,cos_flags,blk_reason
                    ) VALUES ('021',?,?,?,?,?,'ms','PB','idle','',NULL)
                    """,
                    (dn, 50, 0, 15, port),
                )
                self.db.event(
                    "DemoSubscriberPrepared",
                    "subscriber",
                    dn,
                    json.dumps({"eqn": f"50-0-15-{port}", "stage": "3"}),
                )
            created.append(dn)
        return created[0], created[1]


def normalize_number(number: str) -> str:
    value = re.sub(r"[\\s().-]", "", str(number or ""))
    if value.startswith("+"):
        value = value[1:]
    return value
