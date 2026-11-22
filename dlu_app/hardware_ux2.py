from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .design_tokens import get_tokens, normalize_mode


class HardwareInspectorPanel(QFrame):
    """Read-only hardware context inspector backed by the existing Database API."""

    def __init__(
        self,
        db: Any,
        on_open: Callable[[str, Any], None] | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.db = db
        self.on_open = on_open
        self.mode = "morning"
        self.current_kind = "exchange"
        self.current_data: Any = None
        self.setObjectName("HardwareInspector")
        self.setMinimumWidth(290)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("HARDWARE INSPECTOR")
        title.setObjectName("SectionTitle")
        header.addWidget(title, 1)
        self.mode_hint = QLabel("HOVER / SELECT")
        self.mode_hint.setObjectName("Legend")
        header.addWidget(self.mode_hint, 0, Qt.AlignRight)
        root.addLayout(header)

        self.object_type = QLabel("EXCHANGE")
        self.object_type.setObjectName("Eyebrow")
        root.addWidget(self.object_type)

        self.object_title = QLabel("ALE1 · TRAINING EXCHANGE")
        self.object_title.setObjectName("InspectorTitle")
        self.object_title.setWordWrap(True)
        root.addWidget(self.object_title)

        self.path_label = QLabel("Exchange → ALE1")
        self.path_label.setObjectName("InspectorPath")
        self.path_label.setWordWrap(True)
        root.addWidget(self.path_label)

        self.state_chip = QLabel("[ READY ]")
        self.state_chip.setObjectName("InspectorState")
        self.state_chip.setAlignment(Qt.AlignCenter)
        root.addWidget(self.state_chip)

        self.note = QLabel("")
        self.note.setWordWrap(True)
        self.note.setObjectName("InspectorNote")
        root.addWidget(self.note)

        facts = QFrame()
        facts.setObjectName("InspectorFacts")
        grid = QGridLayout(facts)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(7)

        self.fact_labels: dict[str, QLabel] = {}
        fields = (
            ("EQN", "—"),
            ("CAPACITY", "—"),
            ("ROLE", "—"),
            ("FAMILY", "—"),
            ("CONTROLLER", "—"),
            ("SUBSCRIBER", "—"),
        )
        for row, (key, value) in enumerate(fields):
            k = QLabel(key)
            k.setObjectName("InspectorKey")
            v = QLabel(value)
            v.setObjectName("InspectorValue")
            v.setTextInteractionFlags(Qt.TextSelectableByMouse)
            v.setWordWrap(True)
            grid.addWidget(k, row, 0)
            grid.addWidget(v, row, 1)
            self.fact_labels[key] = v
        root.addWidget(facts)

        self.open_button = QPushButton("OPEN SELECTED")
        self.open_button.setObjectName("InspectorOpen")
        self.open_button.setEnabled(False)
        self.open_button.clicked.connect(self._open_selected)
        root.addWidget(self.open_button)

        self.hierarchy_hint = QLabel(
            "Exchange → DLU → Side/Controller → Shelf → Module → Port → Subscriber"
        )
        self.hierarchy_hint.setWordWrap(True)
        self.hierarchy_hint.setObjectName("Legend")
        root.addWidget(self.hierarchy_hint)

        root.addStretch(1)
        self.set_mode("morning")
        self.inspect("exchange", None, source="selection")

    def set_mode(self, mode: str) -> None:
        self.mode = normalize_mode(mode)
        tokens = get_tokens(self.mode)
        self.setStyleSheet(
            f"""
            QFrame#HardwareInspector {{
                background: {tokens.surface};
                border: 1px solid {tokens.border};
                border-radius: {tokens.radius_lg}px;
            }}
            QLabel#Eyebrow {{
                color: {tokens.text_muted};
                font-size: 8pt;
                font-weight: 900;
                letter-spacing: 1px;
            }}
            QLabel#InspectorTitle {{
                color: {tokens.text_primary};
                font-size: 15pt;
                font-weight: 900;
            }}
            QLabel#InspectorPath {{
                color: {tokens.text_secondary};
                padding-bottom: 3px;
            }}
            QLabel#InspectorState {{
                color: {tokens.text_primary};
                background: {tokens.surface_elevated};
                border: 1px solid {tokens.border_strong};
                border-radius: {tokens.radius_sm}px;
                padding: 6px 8px;
                font-weight: 900;
            }}
            QLabel#InspectorNote {{
                color: {tokens.text_secondary};
                background: {tokens.surface_elevated};
                border: 1px solid {tokens.border};
                border-radius: {tokens.radius_sm}px;
                padding: 8px;
            }}
            QFrame#InspectorFacts {{
                background: {tokens.card};
                border: 1px solid {tokens.border};
                border-radius: {tokens.radius_md}px;
            }}
            QLabel#InspectorKey {{
                color: {tokens.text_muted};
                font-size: 8pt;
                font-weight: 900;
            }}
            QLabel#InspectorValue {{
                color: {tokens.text_primary};
                font-size: 9pt;
                font-weight: 700;
            }}
            QPushButton#InspectorOpen {{
                background: {tokens.primary};
                color: {tokens.white};
                border-color: {tokens.primary};
                font-weight: 900;
            }}
            QPushButton#InspectorOpen:hover {{
                background: {tokens.success};
                border-color: {tokens.success};
            }}
            """
        )

    def _set_fact(self, key: str, value: Any) -> None:
        label = self.fact_labels.get(key)
        if label is not None:
            label.setText("—" if value in (None, "") else str(value))

    def _state_style(self, state: str) -> str:
        tokens = get_tokens(self.mode)
        value = (state or "").strip().lower()
        if value in {"active", "act", "idle", "ready"}:
            return f"color:{tokens.success};background:{tokens.surface_elevated};border-color:{tokens.success};"
        if value in {"mbl", "blocked", "warning"}:
            return f"color:{tokens.warning};background:{tokens.surface_elevated};border-color:{tokens.warning};"
        if value in {"fault", "busy", "critical", "fail"}:
            return f"color:{tokens.danger};background:{tokens.surface_elevated};border-color:{tokens.danger};"
        if value in {"test", "diagnostic"}:
            return f"color:{tokens.info};background:{tokens.surface_elevated};border-color:{tokens.info};"
        return f"color:{tokens.text_primary};background:{tokens.surface_elevated};border-color:{tokens.border_strong};"

    def _set_state(self, text: str, semantic: str) -> None:
        self.state_chip.setText(f"[ {text.upper()} ]")
        self.state_chip.setStyleSheet(
            f"""
            QLabel#InspectorState {{
                {self._state_style(semantic)}
                border-width: 1px;
                border-style: solid;
                border-radius: 6px;
                padding: 6px 8px;
                font-weight: 900;
            }}
            """
        )

    def inspect(self, kind: str, data: Any, source: str = "selection") -> None:
        self.current_kind = kind
        self.current_data = data
        self.mode_hint.setText("HOVER" if source == "hover" else "SELECTED")
        self._set_fact("EQN", None)
        self._set_fact("CAPACITY", None)
        self._set_fact("ROLE", None)
        self._set_fact("FAMILY", None)
        self._set_fact("CONTROLLER", None)
        self._set_fact("SUBSCRIBER", None)
        self.open_button.setEnabled(False)

        if kind == "exchange":
            self.object_type.setText("EXCHANGE")
            self.object_title.setText("ALE1 · TRAINING EXCHANGE")
            self.path_label.setText("Exchange → ALE1")
            self._set_state("READY", "ready")
            self._set_fact("CAPACITY", "25 DLU entries")
            self._set_fact("ROLE", "Training exchange")
            self.note.setText(
                "Top-level context. The simulator keeps hardware facts source-backed; "
                "this panel only summarizes the existing database state."
            )
            return

        if kind == "dlu":
            dlu_id = int(data)
            row = self.db.get_dlu(dlu_id)
            if row is None:
                return
            sides = self.db.list_side_states(dlu_id)
            active = any((s["state"] or "").lower() == "act" for s in sides)
            self.object_type.setText("DLU")
            self.object_title.setText(f"DLU {dlu_id} · DIGITAL LINE UNIT")
            self.path_label.setText(f"Exchange → ALE1 → DLU {dlu_id}")
            self._set_state("ACTIVE" if active else "DEGRADED", "active" if active else "warning")
            self._set_fact("CAPACITY", "8 shelves · 16 module positions / shelf")
            self._set_fact("ROLE", "DLU chassis")
            self._set_fact(
                "CONTROLLER",
                f"DLUC0 {row['dluc0_state'].upper()} · DLUC1 {row['dluc1_state'].upper()}",
            )
            self.note.setText(
                "Side/controller redundancy is shown as context. Shelf addressing is "
                "kept independent so the UI never invents a physical side placement."
            )
            self.open_button.setEnabled(True)
            return

        if kind == "side":
            dlu_id, side = data
            rows = {int(s["side"]): s for s in self.db.list_side_states(int(dlu_id))}
            row = rows.get(int(side))
            if row is None:
                return
            self.object_type.setText("SIDE / CONTROLLER")
            self.object_title.setText(f"DLU {dlu_id} · SIDE {side}")
            self.path_label.setText(f"Exchange → ALE1 → DLU {dlu_id} → Side {side}")
            state = (row["state"] or "standby").upper()
            self._set_state(state, row["state"])
            self._set_fact("CONTROLLER", row["controller"])
            self._set_fact("ROLE", "Controller side")
            self.note.setText(
                "Controller side is a logical redundancy context. It is not mapped to a "
                "specific shelf unless the source data says so."
            )
            self.open_button.setEnabled(False)
            return

        if kind == "shelf":
            dlu_id, shelf = data
            rows = self.db.list_shelf(int(dlu_id), int(shelf))
            configured = sum(1 for r in rows if r["card_type"] != "UNCONFIGURED")
            faults = sum(1 for r in rows if r["fault_state"] == "fault")
            semantic = "fault" if faults else "active" if configured else "ready"
            self.object_type.setText("SHELF")
            self.object_title.setText(f"DLU {dlu_id} · SHELF {shelf}")
            self.path_label.setText(f"Exchange → ALE1 → DLU {dlu_id} → Shelf {shelf}")
            self._set_state("FAULT" if faults else "CONFIGURED" if configured else "EMPTY", semantic)
            self._set_fact("CAPACITY", f"{configured}/16 modules configured")
            self._set_fact("ROLE", "Equipment bay")
            self.note.setText(
                "Shelf contains module positions 0..15. Empty positions remain visible "
                "because the simulator does not infer unsupported placements."
            )
            self.open_button.setEnabled(True)
            return

        if kind == "module":
            dlu_id, shelf, module = map(int, data)
            slot = self.db.get_slot(dlu_id, shelf, module)
            if slot is None:
                return
            configured = slot.card_type != "UNCONFIGURED"
            fault = slot.fault_state == "fault"
            ost = (slot.ost or "").lower()
            semantic = "fault" if fault else ost or "ready"
            self.object_type.setText("MODULE / CARD")
            self.object_title.setText(f"Module {module} · {slot.card_type}")
            self.path_label.setText(
                f"Exchange → ALE1 → DLU {dlu_id} → Shelf {shelf} → Module {module}"
            )
            label = "FAULT" if fault else ost.upper() if ost else "EMPTY"
            self._set_state(label, semantic)
            self._set_fact("EQN", f"{dlu_id}-{shelf}-{module}")
            self._set_fact("CAPACITY", f"{slot.port_count} ports")
            self._set_fact("ROLE", slot.role or "Unconfigured")
            self._set_fact("FAMILY", slot.family or "—")
            self.note.setText(
                f"Verified card: {slot.card_type != 'UNCONFIGURED'} · "
                f"Fault state: {slot.fault_state or 'normal'}"
            )
            self.open_button.setEnabled(True)
            return

        if kind == "port":
            dlu_id, shelf, module, port = map(int, data)
            slot = self.db.get_slot(dlu_id, shelf, module)
            sub = self.db.get_port_subscriber(dlu_id, shelf, module, port)
            if slot is None:
                return
            self.object_type.setText("PORT")
            self.object_title.setText(f"Port {port} · EQN {dlu_id}-{shelf}-{module}-{port}")
            self.path_label.setText(
                f"Exchange → ALE1 → DLU {dlu_id} → Shelf {shelf} → "
                f"Module {module} → Port {port}"
            )
            line_state = (sub["line_state"] if sub else "unassigned") or "unassigned"
            semantic = "blocked" if sub and sub["blk_reason"] else line_state
            self._set_state(
                "BLOCKED" if sub and sub["blk_reason"] else line_state,
                semantic,
            )
            self._set_fact("EQN", f"{dlu_id}-{shelf}-{module}-{port}")
            self._set_fact("CAPACITY", "1 subscriber line")
            self._set_fact("ROLE", slot.role or slot.card_type)
            self._set_fact("FAMILY", slot.family or "—")
            self._set_fact("SUBSCRIBER", sub["dn"] if sub else "UNASSIGNED")
            self.note.setText(
                f"Line state: {line_state.upper()} · "
                f"Block: {sub['blk_reason'] if sub and sub['blk_reason'] else 'NONE'}"
            )
            self.open_button.setEnabled(True)
            return

        if kind == "subscriber":
            dlu_id, shelf, module, port = map(int, data)
            sub = self.db.get_port_subscriber(dlu_id, shelf, module, port)
            self.inspect("port", data, source=source)
            if sub:
                self.object_type.setText("SUBSCRIBER")
                self.object_title.setText(f"Subscriber DN {sub['dn']}")
                self.path_label.setText(
                    f"Exchange → ALE1 → DLU {dlu_id} → Shelf {shelf} → "
                    f"Module {module} → Port {port} → Subscriber"
                )
                self._set_fact("SUBSCRIBER", sub["dn"])
                self._set_fact("EQN", f"{dlu_id}-{shelf}-{module}-{port}")
                self._set_fact("ROLE", sub["sub_type"])
                self.note.setText(
                    f"LAC {sub['lac']} · Line {sub['line_state']} · "
                    f"Block {sub['blk_reason'] or 'NONE'}"
                )
            return

    def _open_selected(self) -> None:
        if self.on_open is not None:
            self.on_open(self.current_kind, self.current_data)


