import heapq

from constants import *
from environment import *
from node import *
from state import State

"""
solution.py

This file is a template you should use to implement your solution.

You should implement 

COMP3702 2022 Assignment 1 Support Code

Last updated by njc 01/08/22
"""


class Solver:
    def __init__(self, environment, loop_counter):
        self.environment = environment
        self.loop_counter = loop_counter
        #
        # TODO: Define any class instance variables you require here.
        #

    def solve_ucs(self):
        """
        Find a path which solves the environment using Uniform Cost Search (UCS).
        :return: path (list of actions, where each action is an element of ROBOT_ACTIONS)
        """
        start = self.environment.get_init_state()
        visited: dict[State, int] = {start: 0}

        heap = [StateNodeWithCost(start, (), 0)]
        heapq.heapify(heap)

        nodes_expanded = 0

        while heap:
            self.loop_counter.inc()
            node = heapq.heappop(heap)

            if self.environment.is_solved(node.state):
                return node.actions
            for action in ROBOT_ACTIONS:

                valid, cost, new_state = self.environment.perform_action(
                    node.state, action
                )
                if valid:
                    new_cost = cost + node.cost

                    if (
                        new_state not in visited.keys()
                        or visited[new_state] > new_cost
                    ):
                        visited[new_state] = new_cost
                        heapq.heappush(
                            heap,
                            StateNodeWithCost(
                                new_state, node.actions + (action,), new_cost
                            ),
                        )

            nodes_expanded += 1

    def solve_a_star(self):
        """
        Find a path which solves the environment using A* search.
        :return: path (list of actions, where each action is an element of ROBOT_ACTIONS)
        """
        start = self.environment.get_init_state()
        visited: dict[State, int] = {start: 0}

        heap = [(start.heuristic(), StateNodeWithCost(start, (), 0))]
        heapq.heapify(heap)

        nodes_expanded = 0

        while heap:
            self.loop_counter.inc()
            _, node = heapq.heappop(heap)

            if self.environment.is_solved(node.state):
                return node.actions
            for action in ROBOT_ACTIONS:

                valid, cost, new_state = self.environment.perform_action(
                    node.state, action
                )
                if valid:
                    new_cost = cost + node.cost

                    if (
                        new_state not in visited.keys()
                        or visited[new_state] > new_cost
                    ):
                        visited[new_state] = new_cost
                        heapq.heappush(
                            heap,
                            (
                                new_cost + new_state.heuristic(),
                                StateNodeWithCost(
                                    new_state,
                                    node.actions + (action,),
                                    new_cost,
                                ),
                            ),
                        )

            nodes_expanded += 1
        return ()
