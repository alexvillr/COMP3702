import sys
import time
import math
import numpy as np
from constants import *
from environment import *
from state import State
"""
solution.py

This file is a template you should use to implement your solution.

You should implement code for each of the TODO sections below.

COMP3702 2022 Assignment 3 Support Code

Last updated by njc 12/10/22
"""


class RLAgent:

    #
    # TODO: (optional) Define any constants you require here.
    #

    def __init__(self, environment: Environment):
        self.environment = environment
        self.actions = ROBOT_ACTIONS
        self.epsilon_start = 0.5
        self.epsilon_final = 0.1
        self.epsilon_decay = 10000
        self.epsilon = 0.2
        self.alpha = self.environment.alpha
        self.gamma = self.environment.gamma
        self.q_values = {}
        random.seed(self.environment.seed)
        

    # === Q-learning ===================================================================================================

    def q_learn_train(self):
        """
        Train this RL agent via Q-Learning.
        """
        frame_idx = 0
        rewards = []
        episode_no = 0
        max_r100 = -math.inf
        total_reward = 0

        while True:
            state = self.environment.get_init_state()

            episode_reward = 0
            done = False
            episode_start = frame_idx
            reward = 0

            while not done:
                # self.epsilon = self.epsilon_final + (self.epsilon_start - self.epsilon_final) * math.exp(-1.0 * frame_idx / self.epsilon_decay)
                if (random.uniform(0, 1) < self.epsilon):
                    # explore - i.e. choose a random action
                    action = random.choice(self.actions)
                else:
                    best_q = -math.inf
                    best_a = None
                    for a in self.actions:
                        if ((state, a) in self.q_values.keys()) and (self.q_values[(state, a)] > best_q):
                            best_a = a
                            best_q = self.q_values[(state, a)]
                    if best_a is None:
                        action = random.choice(self.actions)
                    else: 
                        action = best_a
                        
                # ensure cell exists
                if (state, action) not in self.q_values.keys():
                    self.q_values[(state, action)] = 0

                reward, next_state = self.environment.perform_action(state, action)
                done = self.environment.is_solved(next_state)
                frame_idx += 1
                episode_reward += reward

                # ===== update value table =====
                # Q_new(s,a) <-- Q_old(s,a) + alpha * (TD_error)
                # Q_new(s,a) <-- Q_old(s,a) + alpha * (TD_target - Q_old(s, a))
                # Q_new(s,a) <-- Q_old(s,a) + alpha * (R + gamma * max_a(Q(s',a) - Q_old(s, a))
                # target = r + gamma * max_{a' in A} Q(s', a')
                Q_old = self.q_values[(state, action)]
                if done:
                    Q_next_state_max = 0
                else:
                    best_q = -math.inf
                    best_a = None
                    for a in self.actions:
                        if ((next_state, a) in self.q_values.keys()) and (self.q_values[(next_state, a)] > best_q):
                            best_a = a
                            best_q = self.q_values[(next_state, a)]
                    if best_a is None:
                        action = random.choice(self.actions)
                    else: 
                        action = best_a
                    # ensure cell exists
                    if (next_state, action) not in self.q_values.keys():
                        self.q_values[(next_state, action)] = 0
                    
                    Q_next_state_max = self.q_values[(next_state, action)]

                Q_new = Q_old + self.alpha * (reward + self.gamma * Q_next_state_max - Q_old)

                self.q_values[(state, action)] = Q_new

                state = next_state
                total_reward += reward
                
                if (frame_idx - episode_start) > 100:
                    done = True

            rewards.append(reward)
            r100 = np.mean(rewards[-100:])
            if r100 > max_r100:
                max_r100 = r100
            print(f"Frame: {frame_idx}, Episode {episode_no}, steps taken {frame_idx - episode_start}, reward: {episode_reward}, R100: {r100}, max R100: {max_r100}, epsilon: {self.epsilon}")

            if r100 >= (self.environment.evaluation_reward_tgt * 0.01):
                print(f"Solved after {frame_idx} frames with R100 of {r100}")
                break

            if frame_idx > 1000000 or total_reward <= self.environment.training_reward_tgt: # max frames
                print(f"Ran out of time after {frame_idx} frames")
                break
            episode_no += 1

        print(f"Steps taken {frame_idx}")


    def q_learn_select_action(self, state: State):
        """
        Select an action to perform based on the values learned from training via Q-learning.
        :param state: the current state
        :return: approximately optimal action for the given state
        """
        best_q = -math.inf
        best_a = None
        for a in self.actions:
            if ((state, a) in self.q_values.keys() and
                    self.q_values[(state, a)] > best_q):
                best_q = self.q_values[(state, a)]
                best_a = a

        if best_a is None:
            return random.choice(self.actions)
        else:
            return best_a

    # === SARSA ========================================================================================================

    def sarsa_train(self):
        """
        Train this RL agent via SARSA.
        """
        frame_idx = 0
        rewards = []
        episode_no = 0
        max_r100 = -math.inf
        total_reward = 0
        self.epsilon = 0.1

        while True:
            state = self.environment.get_init_state()
            action = self.choose_action(state, self.epsilon)

            episode_reward = 0
            done = False
            episode_start = frame_idx
            reward = 0

            while not done:
                # self.epsilon = self.epsilon_final + (self.epsilon_start - self.epsilon_final) * math.exp(-1.0 * frame_idx / self.epsilon_decay)

                reward, next_state = self.environment.perform_action(state, action)
                done = self.environment.is_solved(next_state)
                frame_idx += 1
                episode_reward += reward

                # ===== update value table =====
                # Q_new(s,a) <-- Q_old(s,a) + alpha * (TD_error)
                # Q_new(s,a) <-- Q_old(s,a) + alpha * (TD_target - Q_old(s, a))
                # Q_new(s,a) <-- Q_old(s,a) + alpha * (R + gamma*Q(s',a') - Q_old(s, a))
                # S' == next_state, a' == next_action
                next_action = self.choose_action(next_state, self.epsilon)
                if (state, action) not in self.q_values.keys():
                    self.q_values[(state, action)] = 0
                Q_old = self.q_values[(state, action)]
                if (next_state, next_action) not in self.q_values.keys():
                    self.q_values[(next_state, next_action)] = 0
                Q_next_old = self.q_values[(next_state, next_action)]

                Q_new = Q_old + self.alpha * (reward + self.gamma * Q_next_old - Q_old)

                self.q_values[(state, action)] = Q_new

                state = next_state
                action = next_action
                
                total_reward += reward
                
                if ((frame_idx - episode_start) > 500) or episode_reward * 3 <= self.environment.evaluation_reward_tgt:
                    done = True

            rewards.append(reward)
            r100 = np.mean(rewards[-200:])
            if r100 > max_r100:
                max_r100 = r100
            print(f"Frame: {frame_idx}, Episode {episode_no}, steps taken {frame_idx - episode_start}, reward: {episode_reward}, R100: {r100}, max R100: {max_r100}, epsilon: {self.epsilon}")

            if r100 <= self.environment.evaluation_reward_tgt:
                print(f"Solved after {frame_idx} frames with R100 of {r100}")
                break

            if frame_idx > 100000000000 or total_reward <= self.environment.training_reward_tgt: # max iters
                print(f"Ran out of time after {frame_idx} frames")
                break
            episode_no += 1

        print(f"Steps taken {frame_idx}")
        print(self.q_values)

    def sarsa_select_action(self, state: State):
        """
        Select an action to perform based on the values learned from training via SARSA.
        :param state: the current state
        :return: approximately optimal action for the given state
        """
        best_q = -math.inf
        best_a = None
        for a in self.actions:
            if ((state, a) in self.q_values.keys()) and (self.q_values[(state, a)] > best_q):
                best_q = self.q_values[(state, a)]
                best_a = a

        if best_a is None:
            return random.choice(self.actions)
        else:
            return best_a

    # === Helper Methods ===============================================================================================
    def choose_action(self, state: int, epsilon: float):
        if random.uniform(0, 1) < self.epsilon:
            # explore - i.e. choose a random action
            return random.choice(self.actions)
        else:
            best_q = -math.inf
            best_a = None
            for a in self.actions:
                if ((state, a) in self.q_values.keys()) and (self.q_values[(state, a)] > best_q):
                    best_q = self.q_values[(state, a)]
                    best_a = a

            if best_a is None:
                return random.choice(self.actions)
            else:
                return best_a
    
    
    """
    def ql_train_once(self):
        # ===== select an action to perform (epsilon greedy exploration) =====
        best_q = -math.inf
        best_a = None
        for a in self.actions:
            if ((self.persistent_state, a) in self.q_values.keys()) and (self.q_values[(self.persistent_state, a)] > best_q):
                best_q = self.q_values[(self.persistent_state, a)]
                best_a = a

        # epsilon chance to choose random action
        random.seed(self.environment.seed)
        if (best_a is None) or (random.random() < self.epsilon):
            action = random.choice(self.actions)
        else:
            action = best_a

        # ===== simulate result of action =====
        reward, next_state = self.environment.perform_action(self.persistent_state, action)
        
        self.states.add(next_state)

        # ===== update value table =====
        # Q(s,a) <-- Q(s,a) + alpha * (temporal difference)
        # Q(s,a) <-- Q(s,a) + alpha * (target - Q(s, a))
        # target = r + gamma * max_{a' in A} Q(s', a')
        # compute target
        best_q1 = -math.inf
        best_a1 = None
        for a1 in self.actions:
            if ((next_state, a1) in self.q_values.keys()) and (self.q_values[(next_state, a1)] > best_q1):
                best_q1 = self.q_values[(next_state, a1)]
                best_a1 = a1
        if best_a1 is None or self.environment.is_solved(next_state):
            best_q1 = 0
        target = reward + (self.environment.gamma * best_q1)
        if (self.persistent_state, action) in self.q_values:
            old_q = self.q_values[(self.persistent_state, action)]
        else:
            old_q = 0
        new_q = old_q + (self.alpha * (target - old_q))
        self.q_values[(self.persistent_state, action)] = new_q

        # move to next state
        self.persistent_state = next_state
        
        return reward, action, self.environment.is_solved(next_state)
    """