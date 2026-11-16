"""CLI for the unfinished student planner and independent plan validation."""
import argparse
from pathlib import Path
from .planner import plan
from .scenarios import load_scenario
from .trace import Trace
from .validation import PlanValidationError, validate_plan
from .world import display

DEFAULT = Path(__file__).resolve().parent.parent / "scenarios/02_bridge_repair.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", nargs="?", type=Path, default=DEFAULT)
    args = parser.parse_args()
    try:
        scenario = load_scenario(args.scenario)
    except (OSError, ValueError, TypeError) as exc:
        print(f"Scenario error: {exc}")
        return 1
    print(f"Scenario: {scenario.name} (expected solvable: {scenario.expected_solvable})")
    print(display(scenario.state))
    trace = Trace()
    try:
        result = plan(scenario.state, ["retrieve_supplies"], trace)
    except NotImplementedError as exc:
        print(f"\nUNFINISHED — {exc}")
        print("Simulator is ready. Passing simulator tests does not complete the assignment.")
        return 2
    finally:
        print(f"\nPlanning trace:\n{trace.render()}")
    if result is None:
        print("Planner reported failure (None).")
        return 1 if scenario.expected_solvable else 0
    try:
        final = validate_plan(scenario.state, result)
    except PlanValidationError as exc:
        print(f"Invalid plan: {exc}")
        return 1
    print(f"Validated plan: {result}\n{display(final)}")
    if not scenario.expected_solvable:
        print("Unexpected success: inspect the scenario's expected result.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
