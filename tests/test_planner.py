"""TODO: remove skips as you implement these acceptance tests.
Passing simulator tests does not verify HTN planning.
"""
import unittest


class PlannerTests(unittest.TestCase):
    @unittest.skip('TODO: implement planner and test all seven public scenarios')
    def test_public_scenarios(self):
        self.fail('Call plan; compare None explicitly; replay successes with validate_plan')

    @unittest.skip('TODO: implement and test backtracking, with new raft tried first')
    def test_backtracking_trace(self):
        self.fail('Assert failed collection, backtracking, bridge alternative, and valid final plan')

    @unittest.skip('TODO: test planner base cases, state preservation, and failure')
    def test_planner_contract(self):
        self.fail('Test empty tasks -> [], impossible tasks -> None, and unchanged input')

    @unittest.skip('TODO: implement greedy comparison using the same method order')
    def test_greedy_comparison(self):
        self.fail('Compare greedy and HTN on the rope trap; explain different results')

    @unittest.skip('TODO: add repair_bridge_and_return without changing search')
    def test_second_mission(self):
        self.fail('Add methods and use validate_plan with a new goal predicate')
