from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Callable

from .call_engine import CallEngine, CallResult
from .db import Database
from .mml import MmlEngine, MmlResult


@dataclass(frozen=True)
class ScenarioDefinition:
    scenario_id: str
    title: str
    summary: str
    objective: str


@dataclass
class ScenarioStepResult:
    label: str
    kind: str
    expected: str
    ok: bool
    code: str
    actual: str
    command: str | None = None
    data: Any = None


@dataclass
class ScenarioResult:
    scenario_id: str
    title: str
    passed: bool
    affected_eqns: list[str]
    expected_result: str
    actual_result: str
    steps: list[ScenarioStepResult] = field(default_factory=list)


class TeachingScenarioRunner:
    """Deterministic teaching scenarios backed by the existing simulator engines.

    The runner intentionally reuses MML, DB, Call Engine and Command Files instead
    of duplicating business rules. Scenarios therefore exercise the same paths a
    student uses in the main application.
    """

    DEMO_DNS = ("2233500", "2233501")
    ALEPPO_DNS = tuple(str(2233510 + index) for index in range(8))
    CMRL_DNS = tuple(str(2233520 + index) for index in range(6))
    OVERNIGHT_FILE = "stage6-overnight-demo"

    _DEFINITIONS = (
        ScenarioDefinition(
            "aleppo-8-line",
            "Aleppo 8-Line Expansion",
            "Build eight subscriber lines on the source-backed SLMA8.",
            "Verify the eight physical ports map to eight valid subscriber records.",
        ),
        ScenarioDefinition(
            "cmrl-capacity",
            "CMRL Capacity Limit",
            "Fill the verified six-port CMRL and prove port 6 is rejected.",
            "Verify capacity is enforced by the hardware card definition.",
        ),
        ScenarioDefinition(
            "dlu-maintenance",
            "DLU / Card Maintenance",
            "Inject, diagnose, remove, replace and activate a real configured card.",
            "Verify the documented maintenance sequence clears the fault and restores service.",
        ),
        ScenarioDefinition(
            "billing-block",
            "Billing Block",
            "Apply an account-suspension block, inspect it, then clear it.",
            "Verify blk=accsusp changes the subscriber to BLOCKED and cblk restores service.",
        ),
        ScenarioDefinition(
            "international-blacklist",
            "International Blacklist",
            "Attempt a blacklisted international destination.",
            "Verify EVAL=NO stops the call before PDC reservation and exposes the blocked path.",
        ),
        ScenarioDefinition(
            "overnight-command-file",
            "Command File Overnight Run",
            "Schedule a command file before midnight and execute it after rollover.",
            "Verify virtual-clock rollover executes the file exactly once.",
        ),
    )

    def __init__(self, db: Database, mml: MmlEngine):
        self.db = db
        self.mml = mml
        self.call_engine = CallEngine(db)

    @classmethod
    def catalog(cls) -> tuple[ScenarioDefinition, ...]:
        return cls._DEFINITIONS

    def run(self, scenario_id: str) -> ScenarioResult:
        handlers: dict[str, Callable[[], ScenarioResult]] = {
            "aleppo-8-line": self._aleppo_8_line,
            "cmrl-capacity": self._cmrl_capacity,
            "dlu-maintenance": self._dlu_maintenance,
            "billing-block": self._billing_block,
            "international-blacklist": self._international_blacklist,
            "overnight-command-file": self._overnight_command_file,
        }
        handler = handlers.get(scenario_id)
        if not handler:
            raise ValueError(f"Unknown teaching scenario: {scenario_id}")
        return handler()

    @staticmethod
    def _step_from_mml(
        label: str,
        result: MmlResult,
        command: str,
        *,
        expected_ok: bool = True,
        expected_code: str | None = None,
        expected_text: str | None = None,
    ) -> ScenarioStepResult:
        code_ok = expected_code is None or result.code == expected_code
        text_ok = expected_text is None or expected_text in result.message
        passed = result.ok == expected_ok and code_ok and text_ok
        actual = f"[{result.code}] {result.message}"
        return ScenarioStepResult(
            label=label,
            kind="MML",
            expected=(
                (expected_code + " · ") if expected_code else ""
            ) + ("OK" if expected_ok else "EXPECTED FAILURE"),
            ok=passed,
            code=result.code,
            actual=actual,
            command=command,
            data=result.data,
        )

    @staticmethod
    def _step_action(
        label: str,
        ok: bool,
        expected: str,
        actual: str,
        *,
        code: str = "ACTION",
        data: Any = None,
    ) -> ScenarioStepResult:
        return ScenarioStepResult(
            label=label,
            kind="ACTION",
            expected=expected,
            ok=ok,
            code=code,
            actual=actual,
            data=data,
        )

    @staticmethod
    def _definition(scenario_id: str) -> ScenarioDefinition:
        for item in TeachingScenarioRunner._DEFINITIONS:
            if item.scenario_id == scenario_id:
                return item
        raise ValueError(scenario_id)

    @staticmethod
    def _result(
        definition: ScenarioDefinition,
        passed: bool,
        eqns: list[str],
        expected: str,
        actual: str,
        steps: list[ScenarioStepResult],
    ) -> ScenarioResult:
        return ScenarioResult(
            definition.scenario_id,
            definition.title,
            passed,
            eqns,
            expected,
            actual,
            steps,
        )

    def _aleppo_8_line(self) -> ScenarioResult:
        definition = self._definition("aleppo-8-line")
        dlu, shelf, module = 50, 0, 15
        eqns = [f"{dlu}-{shelf}-{module}-{port}" for port in range(8)]
        steps: list[ScenarioStepResult] = []

        slot = self.db.get_slot(dlu, shelf, module)
        preflight_ok = bool(slot and slot.card_type == "SLMA8" and slot.fault_state == "clear")
        steps.append(
            self._step_action(
                "Source-backed SLMA8 preflight",
                preflight_ok,
                "SLMA8 at 50-0-15 and clear",
                (
                    f"{slot.card_type if slot else 'MISSING'} / "
                    f"{slot.fault_state if slot else 'MISSING'}"
                ),
                code="PREFLIGHT",
            )
        )
        if not preflight_ok:
            return self._result(
                definition,
                False,
                eqns,
                "Eight lines created on the verified SLMA8.",
                "Preflight failed; use Reset Demo or restore the source-backed card.",
                steps,
            )

        for index, port in enumerate(range(8)):
            dn = self.ALEPPO_DNS[index]
            command = (
                f"> cr sub: dlu=50, type=ms, eqn=50-0-15-{port}, "
                f"lac=021, dn={dn};"
            )
            result = self.mml.execute(command)
            steps.append(
                self._step_from_mml(
                    f"Create line {port}",
                    result,
                    command,
                    expected_code="CREATED",
                )
            )

        inspect = self.mml.execute("> disp dlumod: dlu=50, shelf=0, module=15;")
        steps.append(
            self._step_from_mml(
                "Verify module subscriber inventory",
                inspect,
                "> disp dlumod: dlu=50, shelf=0, module=15;",
                expected_code="OK",
            )
        )
        subscribers = []
        if inspect.ok and isinstance(inspect.data, dict):
            subscribers = inspect.data.get("subscribers", [])
        exact_dns = {str(row.get("dn")) for row in subscribers}
        passed = (
            all(step.ok for step in steps)
            and len(subscribers) == 8
            and exact_dns == set(self.ALEPPO_DNS)
        )
        actual = (
            f"{len(subscribers)}/8 subscriber records present on "
            "DLU 50 / Shelf 0 / Module 15"
        )
        return self._result(
            definition,
            passed,
            eqns,
            "8/8 ports 0..7 created as valid Aleppo subscribers.",
            actual,
            steps,
        )

    def _cmrl_capacity(self) -> ScenarioResult:
        definition = self._definition("cmrl-capacity")
        eqns = [f"10-1-7-{port}" for port in range(7)]
        steps: list[ScenarioStepResult] = []
        slot = self.db.get_slot(10, 1, 7)
        preflight_ok = bool(slot and slot.card_type == "CMRL" and slot.port_count == 6)
        steps.append(
            self._step_action(
                "Verified CMRL preflight",
                preflight_ok,
                "CMRL with exactly 6 ports at 10-1-7",
                (
                    f"{slot.card_type if slot else 'MISSING'} / "
                    f"{slot.port_count if slot else 'MISSING'}P"
                ),
                code="PREFLIGHT",
            )
        )
        if not preflight_ok:
            return self._result(
                definition,
                False,
                eqns,
                "Ports 0..5 accepted and port 6 rejected.",
                "Preflight failed; expected the course-backed CMRL placement.",
                steps,
            )

        for index, port in enumerate(range(6)):
            dn = self.CMRL_DNS[index]
            command = (
                f"> cr sub: dlu=10, type=cmrl, eqn=10-1-7-{port}, "
                f"lac=021, dn={dn};"
            )
            result = self.mml.execute(command)
            steps.append(
                self._step_from_mml(
                    f"Create CMRL port {port}",
                    result,
                    command,
                    expected_code="CREATED",
                )
            )

        rejected_command = (
            "> cr sub: dlu=10, type=cmrl, eqn=10-1-7-6, "
            "lac=021, dn=2233526;"
        )
        rejected = self.mml.execute(rejected_command)
        steps.append(
            self._step_from_mml(
                "Reject port 6",
                rejected,
                rejected_command,
                expected_ok=False,
                expected_code="MML-VALIDATION",
            )
        )

        inspect = self.mml.execute("> disp dlumod: dlu=10, shelf=1, module=7;")
        steps.append(
            self._step_from_mml(
                "Verify six-port inventory",
                inspect,
                "> disp dlumod: dlu=10, shelf=1, module=7;",
                expected_code="OK",
            )
        )
        subscribers = inspect.data.get("subscribers", []) if inspect.ok and isinstance(inspect.data, dict) else []
        passed = all(step.ok for step in steps) and len(subscribers) == 6
        actual = (
            f"{len(subscribers)}/6 CMRL ports accepted; port 6 rejected by capacity guard"
        )
        return self._result(
            definition,
            passed,
            eqns,
            "CMRL accepts ports 0..5 and rejects port 6.",
            actual,
            steps,
        )

    def _maintenance_slot(self):
        for row in self.db.list_dlu_slots(10) + self.db.list_dlu_slots(20) + self.db.list_dlu_slots(30):
            if row["card_type"] == "UNCONFIGURED":
                continue
            count = self.db.conn.execute(
                """
                SELECT COUNT(*) AS n FROM subscribers
                WHERE dlu_id=? AND shelf=? AND module=?
                """,
                (row["dlu_id"], row["shelf"], row["module"]),
            ).fetchone()["n"]
            if count == 0 and row["fault_state"] == "clear":
                return row
        # Fall back to any configured, unused module across the source-backed fleet.
        for dlu_id_row in self.db.list_dlus():
            for row in self.db.list_dlu_slots(int(dlu_id_row["dlu_id"])):
                if row["card_type"] == "UNCONFIGURED" or row["fault_state"] != "clear":
                    continue
                count = self.db.conn.execute(
                    """
                    SELECT COUNT(*) AS n FROM subscribers
                    WHERE dlu_id=? AND shelf=? AND module=?
                    """,
                    (row["dlu_id"], row["shelf"], row["module"]),
                ).fetchone()["n"]
                if count == 0:
                    return row
        return None

    def _dlu_maintenance(self) -> ScenarioResult:
        definition = self._definition("dlu-maintenance")
        steps: list[ScenarioStepResult] = []
        row = self._maintenance_slot()
        if row is None:
            steps.append(
                self._step_action(
                    "Find unused configured card",
                    False,
                    "At least one configured card with no subscriber ports",
                    "No eligible configured card found",
                    code="PREFLIGHT",
                )
            )
            return self._result(
                definition,
                False,
                [],
                "Fault → MBL → DIAG → REMOVE → INSTALL → ACTIVATE → VERIFY.",
                "No eligible maintenance card is currently unused.",
                steps,
            )

        dlu, shelf, module = row["dlu_id"], row["shelf"], row["module"]
        card_type = row["card_type"]
        eqn = f"{dlu}-{shelf}-{module}-ALL"
        steps.append(
            self._step_action(
                "Select configured card",
                True,
                "Configured verified card with no subscriber assignment",
                f"{card_type} at {dlu}-{shelf}-{module}",
                code="PREFLIGHT",
            )
        )

        try:
            self.db.inject_fault(dlu, shelf, module)
            steps.append(
                self._step_action(
                    "Inject fault",
                    True,
                    "fault + MBL",
                    f"{card_type} marked fault / MBL",
                    code="FAULT-INJECTED",
                )
            )
        except ValueError as exc:
            steps.append(
                self._step_action(
                    "Inject fault",
                    False,
                    "fault + MBL",
                    str(exc),
                    code="FAULT-INJECT",
                )
            )
            return self._result(
                definition, False, [eqn], "Maintenance workflow completes.", str(exc), steps
            )

        diag_command = f"> diag dlumod: dlu={dlu}, shelf={shelf}, module={module};"
        diag = self.mml.execute(diag_command)
        steps.append(
            self._step_from_mml(
                "Diagnose fault",
                diag,
                diag_command,
                expected_ok=False,
                expected_code="DIAG-FAULT",
            )
        )

        try:
            removed = self.db.remove_card(dlu, shelf, module)
            steps.append(
                self._step_action(
                    "Remove faulty card",
                    removed == card_type,
                    f"Remove {card_type}",
                    f"Removed {removed}",
                    code="CARD-REMOVED",
                )
            )
            installed = self.db.install_card(dlu, shelf, module, card_type)
            steps.append(
                self._step_action(
                    "Install replacement",
                    installed == card_type,
                    f"Install {card_type}",
                    f"Installed {installed} in MBL",
                    code="CARD-INSTALLED",
                )
            )
            activated = self.db.activate_card(dlu, shelf, module)
            steps.append(
                self._step_action(
                    "Activate replacement",
                    activated == card_type,
                    f"Activate {card_type}",
                    f"Activated {activated}",
                    code="CARD-ACTIVATED",
                )
            )
        except ValueError as exc:
            steps.append(
                self._step_action(
                    "Replacement workflow",
                    False,
                    "Remove → Install → Activate",
                    str(exc),
                    code="MAINTENANCE-FAIL",
                )
            )
            return self._result(
                definition, False, [eqn],
                "Fault → MBL → DIAG → REMOVE → INSTALL → ACTIVATE → VERIFY.",
                str(exc),
                steps,
            )

        verify_command = f"> stat dlumod: dlu={dlu}, shelf={shelf}, module={module};"
        verify = self.mml.execute(verify_command)
        steps.append(
            self._step_from_mml(
                "Verify final module state",
                verify,
                verify_command,
                expected_code="OK",
            )
        )
        final = self.db.get_slot(dlu, shelf, module)
        passed = (
            all(step.ok for step in steps)
            and final is not None
            and final.card_type == card_type
            and final.ost == "act"
            and final.fault_state == "clear"
        )
        actual = (
            f"{card_type} {dlu}-{shelf}-{module}: "
            f"OST={final.ost if final else 'MISSING'}, "
            f"FAULT={final.fault_state if final else 'MISSING'}"
        )
        return self._result(
            definition,
            passed,
            [eqn],
            "Replacement card ends ACT with cleared fault state.",
            actual,
            steps,
        )

    def _prepare_demo_line(self, steps: list[ScenarioStepResult]) -> tuple[str, str] | None:
        try:
            caller, called = self.call_engine.prepare_demo_subscribers()
        except ValueError as exc:
            steps.append(
                self._step_action(
                    "Prepare demo subscriber",
                    False,
                    "Demo subscriber 2233500 available at 50-0-15-0",
                    str(exc),
                    code="PREFLIGHT",
                )
            )
            return None
        normalize = self.mml.execute(f"> mod sub: dn={caller}, cblk=y, line=idle;")
        steps.append(
            self._step_from_mml(
                "Normalize demo line",
                normalize,
                f"> mod sub: dn={caller}, cblk=y, line=idle;",
                expected_code="MODIFIED",
            )
        )
        if not normalize.ok:
            return None
        return caller, called

    def _billing_block(self) -> ScenarioResult:
        definition = self._definition("billing-block")
        steps: list[ScenarioStepResult] = []
        pair = self._prepare_demo_line(steps)
        eqn = "50-0-15-0"
        if pair is None:
            return self._result(
                definition,
                False,
                [eqn],
                "Account suspension blocks then clears the subscriber line.",
                "Demo subscriber preparation failed.",
                steps,
            )
        caller, _called = pair

        before = self.mml.execute(f"> stat sub: dn={caller};")
        steps.append(
            self._step_from_mml(
                "Inspect normal subscriber",
                before,
                f"> stat sub: dn={caller};",
                expected_code="OK",
            )
        )
        block_command = f"> mod sub: dn={caller}, blk=accsusp;"
        blocked = self.mml.execute(block_command)
        steps.append(
            self._step_from_mml(
                "Apply billing block",
                blocked,
                block_command,
                expected_code="MODIFIED",
            )
        )
        inspect = self.mml.execute(f"> stat sub: dn={caller};")
        steps.append(
            self._step_from_mml(
                "Verify BLOCKED / accsusp",
                inspect,
                f"> stat sub: dn={caller};",
                expected_code="OK",
            )
        )
        clear_command = f"> mod sub: dn={caller}, cblk=y;"
        cleared = self.mml.execute(clear_command)
        steps.append(
            self._step_from_mml(
                "Clear billing block",
                cleared,
                clear_command,
                expected_code="MODIFIED",
            )
        )
        final = self.mml.execute(f"> stat sub: dn={caller};")
        steps.append(
            self._step_from_mml(
                "Verify service restored",
                final,
                f"> stat sub: dn={caller};",
                expected_code="OK",
            )
        )

        row = self.db.get_subscriber(caller, "021")
        blocked_result = (
            inspect.ok
            and isinstance(inspect.data, list)
            and bool(inspect.data)
            and inspect.data[0]["line_state"] == "blocked"
            and inspect.data[0]["blk_reason"] == "accsusp"
        )
        restored_result = (
            row is not None
            and row["line_state"] == "idle"
            and not row["blk_reason"]
        )
        passed = all(step.ok for step in steps) and blocked_result and restored_result
        actual = (
            f"blocked={blocked_result} · restored={restored_result} · "
            f"final_state={row['line_state'] if row else 'MISSING'}"
        )
        return self._result(
            definition,
            passed,
            [eqn],
            "blk=accsusp produces BLOCKED; cblk restores IDLE/NORMAL.",
            actual,
            steps,
        )

    def _international_blacklist(self) -> ScenarioResult:
        definition = self._definition("international-blacklist")
        steps: list[ScenarioStepResult] = []
        pair = self._prepare_demo_line(steps)
        eqn = "50-0-15-0"
        if pair is None:
            return self._result(
                definition,
                False,
                [eqn],
                "00972 is blocked before PDC reservation.",
                "Demo subscriber preparation failed.",
                steps,
            )
        caller, _called = pair

        test_command = f"> test call: caller={caller}, number=00972;"
        test_result = self.mml.execute(test_command)
        steps.append(
            self._step_from_mml(
                "Resolve blacklisted destination",
                test_result,
                test_command,
                expected_code="TEST-PASS",
            )
        )

        call: CallResult = self.call_engine.start_call(caller, "00972")
        path = call.path.labels() if call.path else []
        steps.append(
            self._step_action(
                "Attempt blacklisted call",
                (
                    not call.ok
                    and call.code == "CALL-BLOCKED"
                    and path == ["DLU 50", "CPT / BLOCKED"]
                ),
                "CALL-BLOCKED with DLU 50 → CPT / BLOCKED",
                f"{call.code} · path={path}",
                code=call.code,
                data=call.analysis,
            )
        )
        used, capacity = self.call_engine.resource_usage()
        subscriber = self.db.get_subscriber(caller, "021")
        resource_guard = used == 0
        state_guard = subscriber is not None and subscriber["line_state"] == "idle"
        steps.append(
            self._step_action(
                "Verify resource guard",
                resource_guard and state_guard,
                "PDC 0/120 and caller IDLE",
                f"PDC {used}/{capacity} · state={subscriber['line_state'] if subscriber else 'MISSING'}",
                code="POSTCHECK",
            )
        )
        passed = all(step.ok for step in steps)
        actual = (
            f"{call.code}; path={path}; PDC={used}/{capacity}; "
            f"caller_state={subscriber['line_state'] if subscriber else 'MISSING'}"
        )
        return self._result(
            definition,
            passed,
            [eqn, "00972"],
            "EVAL=NO blocks 00972 before any voice resource is reserved.",
            actual,
            steps,
        )

    def _overnight_command_file(self) -> ScenarioResult:
        definition = self._definition("overnight-command-file")
        steps: list[ScenarioStepResult] = []
        pair = self._prepare_demo_line(steps)
        eqn = "50-0-15-0"
        if pair is None:
            return self._result(
                definition,
                False,
                [eqn],
                "Scheduled command file crosses midnight and executes once.",
                "Demo subscriber preparation failed.",
                steps,
            )
        caller, _called = pair

        raw = (
            f"> {self.OVERNIGHT_FILE};\n"
            f"> mod sub: dn={caller}, blk=accsusp;\n"
            f"> disp sub: dn={caller};\n"
            "> endfile;"
        )
        try:
            file = self.mml.command_files.save(self.OVERNIGHT_FILE, raw)
            steps.append(
                self._step_action(
                    "Accept overnight command file",
                    file.status == "Accepted",
                    "Accepted",
                    f"{file.file_name} · {file.status}",
                    code="CMD-FILE-ACCEPTED",
                )
            )
            self.mml.command_files.clock.set("23:55")
            scheduled = self.mml.command_files.schedule(
                self.OVERNIGHT_FILE, "00:05"
            )
            steps.append(
                self._step_action(
                    "Schedule for 00:05",
                    scheduled.scheduled_at == "00:05",
                    "Accepted @ 00:05",
                    f"{scheduled.status} @ {scheduled.scheduled_at}",
                    code="CMD-FILE-SCHEDULED",
                )
            )
            results = self.mml.command_files.advance(10)
            executed_once = (
                len(results) == 1
                and results[0].status == "Executed"
                and self.mml.command_files.clock.current == "00:05"
            )
            steps.append(
                self._step_action(
                    "Cross midnight and execute",
                    executed_once,
                    "One Executed run at virtual 00:05",
                    (
                        f"clock={self.mml.command_files.clock.current} · "
                        f"runs={len(results)}"
                    ),
                    code=results[0].message if results else "NO-RUN",
                )
            )
            duplicate = self.mml.command_files.advance(5)
            no_duplicate = len(duplicate) == 0
            steps.append(
                self._step_action(
                    "No duplicate scheduled run",
                    no_duplicate,
                    "0 additional executions",
                    f"additional_runs={len(duplicate)}",
                    code="DUPLICATE-GUARD",
                )
            )
        except ValueError as exc:
            steps.append(
                self._step_action(
                    "Command-file execution",
                    False,
                    "Accepted → Scheduled → Executed",
                    str(exc),
                    code="CMD-FILE-FAIL",
                )
            )

        row = self.mml.command_files.get(self.OVERNIGHT_FILE)
        subscriber = self.db.get_subscriber(caller, "021")
        final_state_ok = (
            subscriber is not None
            and subscriber["line_state"] == "blocked"
            and subscriber["blk_reason"] == "accsusp"
        )
        file_ok = bool(row and row.status == "Executed" and row.scheduled_at is None)
        steps.append(
            self._step_action(
                "Verify final scheduled-file state",
                final_state_ok and file_ok,
                "File Executed; scheduled_at cleared; subscriber BLOCKED/accsusp",
                (
                    f"file={row.status if row else 'MISSING'}; "
                    f"scheduled_at={row.scheduled_at if row else 'MISSING'}; "
                    f"subscriber={subscriber['line_state'] if subscriber else 'MISSING'}"
                ),
                code="POSTCHECK",
            )
        )
        passed = all(step.ok for step in steps)
        actual = (
            f"clock={self.mml.command_files.clock.current}; "
            f"file={row.status if row else 'MISSING'}; "
            f"scheduled_at={row.scheduled_at if row else 'MISSING'}; "
            f"subscriber={subscriber['line_state'] if subscriber else 'MISSING'}"
        )
        return self._result(
            definition,
            passed,
            [eqn, "00:05"],
            "Overnight schedule executes exactly once across midnight.",
            actual,
            steps,
        )


def scenario_result_to_dict(result: ScenarioResult) -> dict[str, Any]:
    return {
        "scenario_id": result.scenario_id,
        "title": result.title,
        "passed": result.passed,
        "affected_eqns": result.affected_eqns,
        "expected_result": result.expected_result,
        "actual_result": result.actual_result,
        "steps": [
            {
                "label": step.label,
                "kind": step.kind,
                "expected": step.expected,
                "ok": step.ok,
                "code": step.code,
                "actual": step.actual,
                "command": step.command,
                "data": step.data,
            }
            for step in result.steps
        ],
    }
