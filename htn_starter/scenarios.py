"""Load JSON scenarios; metadata is never supplied to the planner."""
from dataclasses import dataclass, fields
import json
from pathlib import Path
from .world import State


@dataclass(frozen=True)
class Scenario:
    name: str
    expected_solvable: bool
    state: State


def load_scenario(path: str | Path) -> Scenario:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"name", "expected_solvable", "state"}:
        raise ValueError("scenario needs exactly name, expected_solvable, and state")
    if not isinstance(data["name"], str) or not data["name"].strip():
        raise ValueError("name must be a nonempty string")
    if type(data["expected_solvable"]) is not bool:
        raise ValueError("expected_solvable must be a boolean")
    raw = data["state"]
    if not isinstance(raw, dict) or set(raw) != {f.name for f in fields(State)}:
        raise ValueError("state must contain exactly all documented state fields")
    return Scenario(data["name"], data["expected_solvable"], State(**raw))
