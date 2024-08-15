import heapq

import numpy as np
from constants import *
from environment import *
from node import StateNodeWithCost
from state import State

"""
solution.py

This file is a template you should use to implement your solution.

You should implement each section below which contains a TODO comment.

COMP3702 2022 Assignment 2 Support Code

Last updated by njc 08/09/22
"""


class Solver:
    def __init__(self, environment: Environment):
        self.rewards = None
        self.environment = environment
        self.states = None
        self.last_policy = None
        self.t_model = None
        self.r_model = None
        self.exit_states = None
        self.max_diff = None
        self.epsilon = self.environment.epsilon
        self.policy = dict()
        self.state_values = dict()
        #
        # TODO: Define any class instance variables you require (e.g. dictionary mapping state to VI value) here.
        #

    # === Value Iteration ==============================================================================================

    def vi_initialise(self):
        """
        Initialise any variables required before the start of Value Iteration.
        """
        #
        # TODO: Implement any initialisation for Value Iteration (e.g. building a list of states) here. You should not
        #  perform value iteration in this method.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        self.state_values = self.get_states()
        self.policy = {state: FORWARD for state in self.state_values.keys()}

    def vi_is_converged(self):
        """
        Check if Value Iteration has reached convergence.
        :return: True if converged, False otherwise
        """
        #
        # TODO: Implement code to check if Value Iteration has reached convergence here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        if self.max_diff is None:
            return False
        return self.max_diff < self.epsilon

    def vi_iteration(self):
        """
        Perform a single iteration of Value Iteration (i.e. loop over the state space once).
        """
        #
        # TODO: Implement code to perform a single iteration of Value Iteration here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        self.policy = dict()
        current_max_diff = 0.0
        for state in self.state_values.keys():
            if self.environment.is_solved(state):
                state_value = 0.0
            else:
                action_values = dict()
                for action in ROBOT_ACTIONS:
                    action_value = 0
                    for stoch_actions, probability in self.stoch_actions(
                        action
                    ).items():
                        stoch_action_rewards = dict()
                        for stoch_action in stoch_actions:
                            (reward, next_state) = self.environment.apply_dynamics(
                                state, stoch_action
                            )
                            stoch_action_rewards[stoch_action] = reward
                        reward = min(stoch_action_rewards.values())
                        action_value += probability * (
                            reward
                            + self.environment.gamma
                            * self.state_values[next_state]
                        )
                    action_values[action] = action_value
                state_value = max(action_values.values())
                self.policy[state] = dict_argmax(action_values)
            if abs(state_value - self.state_values[state]) > current_max_diff:
                current_max_diff = abs(state_value - self.state_values[state])
            self.state_values[state] = state_value
            self.max_diff = current_max_diff
            self.vi_is_converged()

    def vi_plan_offline(self):
        """
        Plan using Value Iteration.
        """
        # !!! In order to ensure compatibility with tester, you should not modify this method !!!
        self.vi_initialise()
        while not self.vi_is_converged():
            self.vi_iteration()

    def vi_get_state_value(self, state: State):
        """
        Retrieve V(s) for the given state.
        :param state: the current state
        :return: V(s)
        """
        #
        # TODO: Implement code to return the value V(s) for the given state (based on your stored VI values) here. If a
        #  value for V(s) has not yet been computed, this function should return 0.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        return self.state_values[state]

    def vi_select_action(self, state: State):
        """
        Retrieve the optimal action for the given state (based on values computed by Value Iteration).
        :param state: the current state
        :return: optimal action for the given state (element of ROBOT_ACTIONS)
        """
        #
        # TODO: Implement code to return the optimal action for the given state (based on your stored VI values) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        return self.policy[state]

    # === Policy Iteration =============================================================================================

    def pi_initialise(self):
        """
        Initialise any variables required before the start of Policy Iteration.
        """
        #
        # TODO: Implement any initialisation for Policy Iteration (e.g. building a list of states) here. You should not
        #  perform policy iteration in this method. You should assume an initial policy of always move FORWARDS.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        (
            self.state_values,
            self.exit_states,
            self.rewards,
        ) = self.get_states_and_exit_states()
        self.states = list(self.state_values.keys())
        self.policy = {state: FORWARD for state in self.state_values.keys()}
        self.last_policy = {
            state: REVERSE for state in self.state_values.keys()
        }
        t_model = np.zeros(
            [
                len(self.state_values.keys()),
                len(ROBOT_ACTIONS),
                len(self.state_values.keys()),
            ]
        )
        for state_index, state in enumerate(self.state_values.keys()):
            for action_index, action in enumerate(ROBOT_ACTIONS):
                if state in self.exit_states:
                    for exit_state in self.exit_states:
                        t_model[state_index][action_index][
                            self.states.index(exit_state)
                        ] = 0.0
                else:
                    for stoch_action, probability in self.stoch_actions(
                        action
                    ).items():
                        for current_action in stoch_action:
                            cost, next_state = self.environment.apply_dynamics(
                                state, current_action
                            )
                            next_state_index = self.states.index(next_state)
                            t_model[state_index][action_index][
                                next_state_index
                            ] += probability
        self.t_model = t_model

        # r model (lin alg)
        r_model = np.zeros([len(self.state_values)])
        for state_index, state in enumerate(self.states):
            r_model[state_index] = self.state_values[state]
        self.r_model = r_model

        # lin alg policy
        self.la_policy = np.zeros([len(self.states)], dtype=np.int64) + FORWARD

    def pi_is_converged(self):
        """
        Check if Policy Iteration has reached convergence.
        :return: True if converged, False otherwise
        """
        #
        # TODO: Implement code to check if Policy Iteration has reached convergence here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        self.last_policy = self.policy.copy()
        new_policy = dict()

        for state in self.states:
            # Keep track of maximum value
            action_values = dict()
            for action in ROBOT_ACTIONS:
                total = 0
                for stoch_action, p in self.stoch_actions(action).items():
                    # Apply action
                    for current_action in stoch_action:
                        _, next_state = self.environment.apply_dynamics(
                            state, current_action
                        )
                        total += p * (
                            self.rewards[(state, current_action)]
                            + (
                                self.environment.gamma
                                * self.state_values[next_state]
                            )
                        )
                action_values[action] = total
            # Update policy
            new_policy[state] = dict_argmax(action_values)
        self.policy = new_policy

        return all(
            self.last_policy[state] == self.policy[state]
            for state in self.state_values.keys()
        )

    def pi_iteration(self):
        """
        Perform a single iteration of Policy Iteration (i.e. perform one step of policy evaluation and one step of
        policy improvement).
        """
        #
        # TODO: Implement code to perform a single iteration of Policy Iteration (evaluation + improvement) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        state_numbers = np.array(
            range(len(self.states))
        )  # indices of every state
        t_pi = self.t_model[state_numbers, self.la_policy]
        values = np.linalg.solve(
            np.identity(len(self.states)) - (self.environment.gamma * t_pi),
            self.r_model,
        )
        self.state_values = {
            state: values[index] for index, state in enumerate(self.states)
        }

    def pi_plan_offline(self):
        """
        Plan using Policy Iteration.
        """
        # !!! In order to ensure compatibility with tester, you should not modify this method !!!
        self.pi_initialise()
        while not self.pi_is_converged():
            self.pi_iteration()

    def pi_select_action(self, state: State):
        """
        Retrieve the optimal action for the given state (based on values computed by Value Iteration).
        :param state: the current state
        :return: optimal action for the given state (element of ROBOT_ACTIONS)
        """
        #
        # TODO: Implement code to return the optimal action for the given state (based on your stored PI policy) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        return self.policy[state]

    # === Helper Methods ===============================================================================================
    #
    #
    # TODO: Add any additional methods here
    #
    #
    def stoch_actions(self, action):
        forward_probs = {
            (FORWARD, FORWARD): 0.25,
            (SPIN_LEFT, FORWARD): 0.0375,
            (SPIN_RIGHT, FORWARD): 0.0375,
            (SPIN_LEFT, FORWARD, FORWARD): 0.0125,
            (SPIN_RIGHT, FORWARD, FORWARD): 0.0125,
            (FORWARD,): 0.65,
        }
        reverse_probs = {
            (REVERSE, REVERSE): 0.05,
            (SPIN_LEFT, REVERSE): 0.02375,
            (SPIN_RIGHT, REVERSE): 0.02375,
            (SPIN_LEFT, REVERSE, REVERSE): 0.00125,
            (SPIN_RIGHT, REVERSE, REVERSE): 0.00125,
            (REVERSE,): 0.9,
        }
        ccw_probs = {(SPIN_LEFT,): 1}
        cw_probs = {(SPIN_RIGHT,): 1}
        if action == FORWARD:
            return forward_probs
        elif action == REVERSE:
            return reverse_probs
        elif action == SPIN_LEFT:
            return ccw_probs
        elif action == SPIN_RIGHT:
            return cw_probs
        else:
            raise ValueError('Not a proper action')

    def get_states(self):
        """
        Apply BFS to the environment until we have a list of all states
        :return:List(State) list of all possible states in the environment
        """
        start = self.environment.get_init_state()
        states: dict[State, float] = {start: 0}

        heap = [StateNodeWithCost(start, 0)]
        heapq.heapify(heap)

        while heap:
            node = heapq.heappop(heap)
            action_values = dict()
            for action in ROBOT_ACTIONS:
                action_value = 0
                for stoch_actions, probability in self.stoch_actions(
                    action
                ).items():
                    stoch_action_rewards = dict()
                    for stoch_action in stoch_actions:
                        reward, next_state = self.environment.apply_dynamics(
                            node.state, stoch_action
                        )
                        stoch_action_rewards[stoch_action] = reward
                    reward = min(stoch_action_rewards.values())
                    action_value += probability * reward
                action_values[action] = action_value

                new_cost = max(action_values.values())

                if self.environment.is_solved(next_state):
                    states[node.state] = 0.0

                if (
                    next_state not in states.keys()
                    or states[next_state] < new_cost
                ):
                    states[next_state] = new_cost
                    heapq.heappush(
                        heap, StateNodeWithCost(next_state, new_cost)
                    )

        return states

    def get_states_and_exit_states(self):
        """
        Apply BFS to the environment until we have a list of all states
        :return:List(State) list of all possible states in the environment
        """
        start = self.environment.get_init_state()
        states: dict[State, float] = {start: 0}
        rewards = dict()
        exit_states = []

        heap = [StateNodeWithCost(start, 0)]
        heapq.heapify(heap)

        while heap:
            node = heapq.heappop(heap)
            action_values = dict()
            for action in ROBOT_ACTIONS:
                action_value = 0
                for stoch_actions, probability in self.stoch_actions(
                    action
                ).items():
                    stoch_action_rewards = dict()
                    for stoch_action in stoch_actions:
                        reward, next_state = self.environment.apply_dynamics(
                            node.state, stoch_action
                        )
                        stoch_action_rewards[stoch_action] = reward
                    reward = min(stoch_action_rewards.values())
                    action_value += probability * reward
                action_values[action] = action_value
                rewards[(node.state, action)] = action_value
                new_cost = max(action_values.values())

                if self.environment.is_solved(next_state):
                    states[node.state] = 0.0
                    exit_states.append(node.state)

                if (
                    next_state not in states.keys()
                    or states[next_state] < new_cost
                ):
                    states[next_state] = new_cost
                    heapq.heappush(
                        heap, StateNodeWithCost(next_state, new_cost)
                    )

        return states, exit_states, rewards


def dict_argmax(dictionary):
    max_value = max(dictionary.values())
    for key, value in dictionary.items():
        if value == max_value:
            return key
