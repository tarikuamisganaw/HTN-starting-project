"""Replay a proposed plan independently, checking every precondition again."""
from typing import Callable
from .actions import ActionError, apply_action
from .world import State, mission_success


class PlanValidationError(ValueError):
    pass


def validate_plan(start: State, plan: list[str],
                  goal: Callable[[State], bool] = mission_success) -> State:
    if not isinstance(plan, list) or any(not isinstance(a, str) for a in plan):
        raise PlanValidationError("plan must be a list of primitive action names")
    current = start
    for step, action in enumerate(plan, 1):
        try:
            current = apply_action(current, action)
        except ActionError as exc:
            raise PlanValidationError(f"step {step}: {exc}") from exc
    if not goal(current):
        raise PlanValidationError("actions are valid, but the mission goal is not satisfied")
    return current
