"""TODO: design compound tasks and ordered alternative methods.

A task is a string: either an ACTIONS name or a METHODS key.
A method takes a simulated State and returns a list of subtasks if applicable,
or None if inapplicable. [] means applicable with nothing left to do.
Methods must not execute actions, mutate state, or perform search.
Name each method clearly so the planner can report method.__name__ in its trace.

Suggested compounds: retrieve_supplies, reach_island, prepare_resources,
return_to_camp. The main task should reach the island, collect, then return.
Design the alternatives yourself from README's world rules. For the
backtracking demonstration, order the new-raft strategy before bridge repair.
Account for existing infrastructure, resources in the store, and the return.
"""
from typing import Callable
from .world import State

Method = Callable[[State], list[str] | None]

# TODO: write your method functions and register them in preference order.
METHODS: dict[str, list[Method]] = {
    "retrieve_supplies": [],
    "reach_island": [],
    "prepare_resources": [],
    "return_to_camp": [],
}
