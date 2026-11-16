"""Small trace API; the student decides when to emit each event."""
from dataclasses import dataclass, field

EVENTS = {"expand", "method", "condition_failed", "backtrack", "plan"}


@dataclass
class Trace:
    lines: list[str] = field(default_factory=list)

    def record(self, event: str, detail: str, depth: int = 0) -> None:
        if event not in EVENTS:
            raise ValueError(f"unknown trace event: {event}")
        if type(depth) is not int or depth < 0:
            raise ValueError("depth must be a nonnegative integer")
        self.lines.append(f"{'  ' * depth}[{event}] {detail}")

    def render(self) -> str:
        return "\n".join(self.lines) or "(no trace events yet)"
