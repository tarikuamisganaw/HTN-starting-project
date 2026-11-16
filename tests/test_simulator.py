import json
from dataclasses import asdict, replace
from pathlib import Path
import tempfile
import unittest

from htn_starter.actions import ACTIONS, ActionError, apply_action
from htn_starter.scenarios import load_scenario
from htn_starter.trace import Trace
from htn_starter.validation import PlanValidationError, validate_plan
from htn_starter.world import State, mission_success


class SimulatorTests(unittest.TestCase):
    def test_valid_actions_and_unchanged_inputs(self):
        bank = State(location='riverbank', wood=3, rope=2)
        cases = [
            ('gather_materials', State(wood=1, rope=1, store_wood=2, store_rope=3),
             State(wood=3, rope=4)),
            ('move_to_riverbank', State(), State(location='riverbank')),
            ('move_to_camp', bank, replace(bank, location='camp')),
            ('repair_bridge', bank, replace(bank, wood=1, bridge_usable=True)),
            ('build_raft', bank, replace(bank, wood=2, rope=1, raft_location='riverbank')),
            ('cross_bridge', replace(bank, bridge_usable=True),
             replace(bank, bridge_usable=True, location='island')),
            ('cross_raft', replace(bank, raft_location='riverbank'),
             replace(bank, location='island', raft_location='island')),
            ('collect_supplies', replace(bank, location='island'),
             replace(bank, location='island', supplies_collected=True)),
        ]
        self.assertEqual({a for a, _, _ in cases}, set(ACTIONS))
        for action, start, expected in cases:
            with self.subTest(action=action):
                snapshot = asdict(start)
                result = apply_action(start, action)
                self.assertEqual(result, expected)
                self.assertIsNot(result, start)
                self.assertEqual(asdict(start), snapshot)

    def test_every_precondition_and_failure_preserves_input(self):
        bank = State(location='riverbank', wood=2, rope=1)
        island = replace(bank, location='island')
        cases = {
            'gather_materials': [replace(bank, store_wood=1), State()],
            'move_to_riverbank': [bank, island],
            'move_to_camp': [State(), island],
            'repair_bridge': [replace(bank, location='camp'),
                              replace(bank, bridge_usable=True), replace(bank, wood=1)],
            'build_raft': [replace(bank, location='camp'),
                           replace(bank, raft_location='island'),
                           replace(bank, wood=0), replace(bank, rope=0)],
            'cross_bridge': [State(bridge_usable=True), bank],
            'cross_raft': [State(), bank, replace(bank, raft_location='island')],
            'collect_supplies': [bank, replace(island, rope=0),
                                 replace(island, supplies_collected=True)],
            'unknown': [State()],
        }
        for action, states in cases.items():
            for start in states:
                with self.subTest(action=action, state=start):
                    snapshot = asdict(start)
                    with self.assertRaisesRegex(ActionError, '.+'):
                        apply_action(start, action)
                    self.assertEqual(asdict(start), snapshot)

    def test_store_one_material_and_empty_after_transfer(self):
        for changes in ({'store_wood': 2}, {'store_rope': 3}):
            state = apply_action(State(**changes), 'gather_materials')
            self.assertEqual(state.store_wood + state.store_rope, 0)
            self.assertEqual(state.wood + state.rope, sum(changes.values()))
            with self.assertRaises(ActionError):
                apply_action(state, 'gather_materials')

    def test_crossings_both_directions(self):
        for action, changes in [('cross_bridge', {'bridge_usable': True}),
                                ('cross_raft', {'raft_location': 'riverbank'})]:
            original = State(location='riverbank', wood=1, rope=2, **changes)
            island = apply_action(original, action)
            self.assertEqual(island.location, 'island')
            if action == 'cross_raft':
                self.assertEqual(island.raft_location, 'island')
            self.assertEqual(apply_action(island, action), original)

    def test_rope_trap_is_a_simulation_failure(self):
        # A partial, deliberately failing branch; not a solution to the mission.
        start = State(wood=2, rope=1)
        state = start
        for action in ('move_to_riverbank', 'build_raft', 'cross_raft'):
            state = apply_action(state, action)
        with self.assertRaisesRegex(ActionError, 'rope'):
            apply_action(state, 'collect_supplies')
        self.assertEqual(start, State(wood=2, rope=1))

    def test_state_rejects_invalid_values(self):
        for field in ('wood', 'rope', 'store_wood', 'store_rope'):
            for value in (-1, 1.5, True, '2'):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    State(**{field: value})
        for changes in ({'location': 'sea'}, {'raft_location': 'camp'},
                        {'bridge_usable': 1}, {'supplies_collected': 'yes'}):
            with self.assertRaises(ValueError):
                State(**changes)

    def test_mission_requires_both_conditions(self):
        for location in ('camp', 'riverbank', 'island'):
            for collected in (False, True):
                self.assertEqual(mission_success(State(location=location, supplies_collected=collected)),
                                 location == 'camp' and collected)

    def test_validator_replays_and_checks_goal(self):
        start = State(location='riverbank', supplies_collected=True)
        final = validate_plan(start, ['move_to_camp'])
        self.assertTrue(mission_success(final))
        self.assertEqual(start.location, 'riverbank')
        self.assertEqual(validate_plan(final, []), final)
        for bad in ([], ['move_to_camp', 'move_to_camp'], ['missing'], None, 'move_to_camp', [1]):
            with self.subTest(plan=bad), self.assertRaises(PlanValidationError):
                validate_plan(start, bad)
        with self.assertRaisesRegex(PlanValidationError, 'step 2'):
            validate_plan(State(), ['move_to_riverbank', 'collect_supplies'])

    def test_public_scenarios(self):
        paths = sorted((Path(__file__).resolve().parents[1] / 'scenarios').glob('*.json'))
        self.assertEqual(len(paths), 7)
        scenarios = [load_scenario(p) for p in paths]
        self.assertEqual([s.expected_solvable for s in scenarios], [True, True, True, False, True, False, True])
        self.assertTrue(all(s.state.location == 'camp' and not s.state.supplies_collected for s in scenarios))

    def test_loader_rejects_bad_schema(self):
        good = dict(name='test', expected_solvable=True, state=asdict(State()))
        malformed = [{}, good | {'extra': 1}, good | {'expected_solvable': 'yes'},
                     good | {'state': {}}, good | {'state': asdict(State()) | {'wood': -1}}]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'test.json'
            for data in malformed:
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    load_scenario(path)

    def test_trace_events(self):
        trace = Trace()
        for event in ('expand', 'method', 'condition_failed', 'backtrack', 'plan'):
            trace.record(event, 'example', depth=1)
        self.assertEqual(len(trace.lines), 5)
        self.assertIn('  [backtrack] example', trace.render())
        with self.assertRaises(ValueError):
            trace.record('typo', '')
