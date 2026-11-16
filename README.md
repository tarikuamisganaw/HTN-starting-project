# Island supplies: an HTN planning starter project

Python 3.10+ and the standard library only. Run commands from this project directory. No installation, external services, or graphics are needed.

The simulator is complete. **The HTN planner is deliberately unfinished.** Remaining functionality includes compound tasks, alternative methods, recursive decomposition, preconditions and effects during planning, backtracking, and a decision trace.

## Run the starter

```sh
python3 --version
python3 -m htn_starter.demo
python3 -m unittest discover -s tests -v
python3 -m htn_starter.runner
python3 -m htn_starter.runner scenarios/03_new_raft.json
python3 -m htn_starter.runner --help
```

The demo manually executes a short action sequence and stops before completing the mission. It is not a planner. Tests should pass for the simulator and report five skipped planner tests. Both planner commands intentionally print `UNFINISHED` and exit with code **2** until the TODOs are implemented. This is the expected starter behavior. Once implemented, the runner exits 0 for a validated success or an expected failure, and 1 for invalid input, an invalid plan, or a result that disagrees with the scenario expectation.

## Already implemented

- `htn_starter/world.py`: immutable dataclass, state validation, readable display, mission check.
- `actions.py`: all eight actions and the `ACTIONS` registry.
- `scenarios.py` and `scenarios/`: strict JSON loader and seven public cases.
- `trace.py`: trace storage and formatting.
- `validation.py`: independent replay and final-goal checking.
- `demo.py`, `runner.py`, and `tests/test_simulator.py`: manual simulation, planner runner, and simulator tests.

## Complete world rules

Locations are `camp`, `riverbank`, and `island`. Camp and riverbank are directly connected. The riverbank and island can be crossed only using a usable bridge or a raft on your side. Materials are limited; there is no carrying limit and no replenishment.

State fields are `location`, inventory counts `wood` and `rope`, camp-store counts `store_wood` and `store_rope`, boolean `bridge_usable`, `raft_location` (`null`, `riverbank`, or `island` in JSON), and boolean `supplies_collected`. Counts must be nonnegative integers. The initial mission succeeds only when the character is at camp **and** supplies are collected.

| Action | Preconditions | Effects |
| --- | --- | --- |
| `gather_materials` | At camp; store contains wood or rope | Transfer all store materials to inventory; empty store |
| `move_to_riverbank` | At camp | Move to riverbank |
| `move_to_camp` | At riverbank | Move to camp |
| `repair_bridge` | At riverbank; bridge broken; at least 2 wood | Consume 2 wood; make bridge usable |
| `build_raft` | At riverbank; no raft anywhere; at least 1 wood and 1 rope | Consume 1 wood and 1 rope; put raft at riverbank |
| `cross_bridge` | At riverbank or island; bridge usable | Move to opposite side; consume nothing; raft stays where it is |
| `cross_raft` | At riverbank or island; raft on same side | Move character and raft to opposite side; consume nothing |
| `collect_supplies` | On island; at least 1 rope; supplies not collected | Mark supplies collected; keep the rope |

Every action checks all its preconditions before applying effects, returns a new `State` on success, and raises `ActionError` with a reason on failure. Input states never change, including after a failure. You may call `apply_action(state, name)` or a registry function. Unknown action names also raise `ActionError`. Invalid state construction raises `ValueError`.

## Remaining implementation and interfaces

1. **`htn_starter/domain.py`**: define the task hierarchy and methods. A task is a string. Primitive names are in `ACTIONS`; compound names are keys in `METHODS`. Each method accepts a simulated state and returns a list of subtasks or `None` if not applicable. An empty list is an applicable method that needs no work. Register alternative methods in preference order. Methods describe decomposition; the planner simulates primitive effects.
2. **`htn_starter/planner.py`**: implement `plan(state, tasks, trace) -> list[str] | None`. Return only primitive action names on success; return `None` on failure. `[]` is a successful empty plan. Use `result is None`, not truthiness, to detect failure. Do not mutate the input task list or starting state. Leave final execution to the runner's validator.
3. **Planner acceptance tests in `tests/`**: replace skipped placeholders with real assertions and remove skips. Add tests for alternative methods, later-task failure, empty tasks, unknown tasks, state preservation, and the chosen cycle/depth policy. Validate successful plans by replaying them. Do not equate a successful empty task list with achieving a mission goal.

Suggested compound tasks are `retrieve_supplies`, `reach_island`, `prepare_resources`, and `return_to_camp`. The main task should eventually reach the island, collect supplies, and return to camp. Strategies should follow the rules above; no completed methods or search implementation are provided.

Use `trace.record(event, detail, depth=0)` for `expand`, `method`, `condition_failed`, `backtrack`, and `plan`. Include task names, method names, failed reasons, and the final plan or failure. For example, `trace.record("expand", "retrieve_supplies", depth=0)`. The runner prints `trace.render()`. Explain both local failures and decisions revisited because a later task failed.

### Required backtracking demonstration

Use scenario 02: camp, broken bridge, no raft, two wood and one rope in inventory, empty store, no supplies collected. **Try the new-raft strategy before bridge repair.** Building a raft is initially legal but consumes the only rope. Collection then fails. The planner must revisit the earlier choice during planning and discover bridge repair, which preserves rope. Backtracking only when the method's initial conditions fail is insufficient. The failed branch must not consume resources in other branches or in the real starting state.

### Public scenarios

All begin at camp without collected supplies. The store is empty and no raft exists except where stated.

| File in `scenarios/` | Initial resources and infrastructure | Expected |
| --- | --- | --- |
| `01_working_bridge.json` | Usable bridge; 0 wood, 1 rope | Solvable |
| `02_bridge_repair.json` | Broken bridge; 2 wood, 1 rope | Solvable via repair |
| `03_new_raft.json` | Broken bridge; 1 wood, 2 rope | Solvable via raft |
| `04_insufficient_rope.json` | Broken bridge; 1 wood, 1 rope | Impossible |
| `05_camp_store.json` | Broken bridge; inventory 0 wood, 1 rope; store 2 wood | Solvable |
| `06_no_rope.json` | Usable bridge; no materials anywhere | Impossible |
| `07_existing_raft.json` | Broken bridge; raft at riverbank; 0 wood, 1 rope | Solvable |

To add a scenario, copy a JSON file, choose a descriptive filename and `name`, set `expected_solvable`, and edit all nine state fields. Keep exactly the three top-level keys shown in existing files. Run the runner with the new file path as its argument. The expected flag is evaluation metadata, never planner input. If you add files, update the simulator test that checks the seven-case public inventory, or keep custom cases in a separate directory.

## Three-day implementation schedule

- **Day 1:** run the demo and tests; learn the rules; draw the task hierarchy; define methods and their order.
- **Day 2:** implement recursive planning and backtracking; trace the rope trap; verify simulated states stay independent.
- **Day 3:** test all scenarios; implement the greedy comparison and small extension; prepare the demonstration.

After HTN works, implement a greedy version using the **same method order** that never revisits an earlier method choice. The greedy implementation is also left unfinished. Compare outcomes and traces, especially scenario 02. Explain why local feasibility does not guarantee mission success; do not silently change strategy order to improve the greedy result.

Add a second mission, **`repair_bridge_and_return`**, using the existing actions and planner. Its goal is a usable bridge and a character at camp; collecting supplies is not required. Add or reuse domain methods, create tests, and pass a goal predicate to `validate_plan(start, plan, goal=...)`. The runner can also expose the new mission. Do not change the planning algorithm to support the mission. Consider an already usable bridge, available store materials, and insufficient wood.

Completion deliverables include the task hierarchy and methods, completed planner, planning traces (including backtracking and failure), test results, greedy comparison, second mission, and a five-minute explanation covering planning versus execution, `[]` versus `None`, and recovery from a later failure.

Evaluation criteria: **60%** correctness on common scenarios, **25%** understanding and explanation, **15%** a small live modification. A live modification can adjust a method, resource condition, or mission, with an explanation of the effect.
