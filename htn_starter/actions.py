"""Actions return a fresh State, or raise ActionError without changing input."""
from dataclasses import replace
from typing import Callable
from .world import State


class ActionError(ValueError):
    """A primitive action's preconditions are not satisfied."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ActionError(reason)


def gather_materials(s: State) -> State:
    require(s.location == "camp", "must be at camp")
    require(s.store_wood + s.store_rope > 0, "camp store is empty")
    return replace(s, wood=s.wood + s.store_wood, rope=s.rope + s.store_rope,
                   store_wood=0, store_rope=0)


def move_to_riverbank(s: State) -> State:
    require(s.location == "camp", "must be at camp")
    return replace(s, location="riverbank")


def move_to_camp(s: State) -> State:
    require(s.location == "riverbank", "must be at riverbank")
    return replace(s, location="camp")


def repair_bridge(s: State) -> State:
    require(s.location == "riverbank", "must be at riverbank")
    require(not s.bridge_usable, "bridge is already usable")
    require(s.wood >= 2, "need at least two wood")
    return replace(s, wood=s.wood - 2, bridge_usable=True)


def build_raft(s: State) -> State:
    require(s.location == "riverbank", "must be at riverbank")
    require(s.raft_location is None, "a raft already exists")
    require(s.wood >= 1, "need at least one wood")
    require(s.rope >= 1, "need at least one rope")
    return replace(s, wood=s.wood - 1, rope=s.rope - 1, raft_location="riverbank")


def cross_bridge(s: State) -> State:
    require(s.location in ("riverbank", "island"), "must be at riverbank or island")
    require(s.bridge_usable, "bridge is broken")
    return replace(s, location="island" if s.location == "riverbank" else "riverbank")


def cross_raft(s: State) -> State:
    require(s.location in ("riverbank", "island"), "must be at riverbank or island")
    require(s.raft_location == s.location, "raft must be on the same side")
    opposite = "island" if s.location == "riverbank" else "riverbank"
    return replace(s, location=opposite, raft_location=opposite)


def collect_supplies(s: State) -> State:
    require(s.location == "island", "must be on the island")
    require(s.rope >= 1, "need at least one rope to collect supplies")
    require(not s.supplies_collected, "supplies already collected")
    return replace(s, supplies_collected=True)


ACTIONS: dict[str, Callable[[State], State]] = {
    fn.__name__: fn for fn in (gather_materials, move_to_riverbank, move_to_camp,
                              repair_bridge, build_raft, cross_bridge, cross_raft,
                              collect_supplies)
}


def apply_action(state: State, name: str) -> State:
    if not isinstance(name, str) or name not in ACTIONS:
        raise ActionError(f"unknown action: {name!r}")
    try:
        return ACTIONS[name](state)
    except ActionError as exc:
        raise ActionError(f"{name}: {exc}") from exc
