"""Immutable simulation state and mission predicates."""
from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    location: str = "camp"
    wood: int = 0
    rope: int = 0
    store_wood: int = 0
    store_rope: int = 0
    bridge_usable: bool = False
    raft_location: str | None = None
    supplies_collected: bool = False

    def __post_init__(self):
        if self.location not in ("camp", "riverbank", "island"):
            raise ValueError("location must be camp, riverbank, or island")
        if self.raft_location not in (None, "riverbank", "island"):
            raise ValueError("raft_location must be null, riverbank, or island")
        for name in ("wood", "rope", "store_wood", "store_rope"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        for name in ("bridge_usable", "supplies_collected"):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"{name} must be a boolean")


def mission_success(state: State) -> bool:
    return state.location == "camp" and state.supplies_collected


def display(state: State) -> str:
    return (f"Location: {state.location} | Inventory: {state.wood} wood, {state.rope} rope\n"
            f"Camp store: {state.store_wood} wood, {state.store_rope} rope | "
            f"Bridge: {'usable' if state.bridge_usable else 'broken'}\n"
            f"Raft: {state.raft_location or 'none'} | Supplies: "
            f"{'collected' if state.supplies_collected else 'not collected'}")
