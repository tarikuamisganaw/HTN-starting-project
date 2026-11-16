"""Manual simulation only: this script contains no HTN planner."""
from .actions import ActionError, apply_action
from .world import State, display


def main() -> None:
    state = State(store_wood=1, store_rope=2)
    print("Manual action demo (not a complete mission or an HTN solution).")
    print(display(state))
    print("First try an invalid action at camp:")
    original = state
    try:
        apply_action(state, "repair_bridge")
    except ActionError as exc:
        print(f"Rejected: {exc}")
    assert state == original
    for action in ("gather_materials", "move_to_riverbank", "build_raft", "cross_raft"):
        previous = state
        state = apply_action(state, action)
        assert state is not previous
        print(f"\nAfter {action}:\n{display(state)}")
    print("\nThe raft moved with us. One rope remains; this demo stops before collection.")
    print("Each successful action returned a new state; earlier states are unchanged.")


if __name__ == "__main__":
    main()
