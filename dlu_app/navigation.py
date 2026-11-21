from __future__ import annotations

from dataclasses import dataclass, field


LEARNING_AREAS = (
    "HARDWARE",
    "OMT / MML",
    "CALLS",
    "COMMANDS",
    "COMMS LAB",
    "SCENARIOS",
)


@dataclass
class StudentNavigationState:
    """Session-only student journey state; domain state stays in the DB/engines."""

    active_area: str = "HOME"
    current_context: str = "Learning Home"
    recent_activity: list[str] = field(
        default_factory=lambda: ["Opened DLU Lab · ready to learn"]
    )
    visited_areas: set[str] = field(default_factory=set)

    def visit(self, area: str, context: str | None = None) -> None:
        normalized = area.strip() or "HOME"
        self.active_area = normalized
        if context:
            self.current_context = context
        if normalized != "HOME":
            self.visited_areas.add(normalized)
        entry = context or normalized
        if self.recent_activity and self.recent_activity[0] == entry:
            return
        self.recent_activity.insert(0, entry)
        del self.recent_activity[8:]

    @property
    def progress_percent(self) -> int:
        return round((len(self.visited_areas) / len(LEARNING_AREAS)) * 100)

    @property
    def visited_count(self) -> int:
        return len(self.visited_areas)
