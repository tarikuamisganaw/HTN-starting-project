"""TODO: recursive HTN planning with backtracking.

plan(state, tasks, trace) returns primitive action names, or None on failure.
[] is a successful empty plan, so never use `if not result` to detect failure.
Use ACTIONS/apply_action for simulation and METHODS for decomposition.
Planning must not call the final plan validator or alter the starting state.

Implement base cases, primitive simulation, ordered method selection,
recursive decomposition, and backtracking. A later task failure must allow
an earlier method choice to be revisited. Define how unknown tasks and cycles
are handled; document any search-depth limit. Emit all five Trace event types.
Do not use expected_solvable metadata or hard-coded scenario solutions.
"""
from .world import State
from .trace import Trace


def plan(state: State, tasks: list[str], trace: Trace) -> list[str] | None:
    raise NotImplementedError(
        "TODO: implement methods in htn_starter/domain.py and "
        "recursive planning/backtracking in htn_starter/planner.py"
    )
