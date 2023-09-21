import os
import platform
import random
from constants import *
from state import State

"""
environment.py

This file contains a class representing a HexBot environment and supporting helper methods. You should make use of this
class in your RL agent.

You should not modify this class.

COMP3702 2022 Assignment 3 Support Code

Last updated by njc 12/10/22
"""

DISABLE_COLOUR = False      # Set to True to disable colour coding (useful if colours are not displaying correctly)


class Environment:
    """
    Instance of a HexBot environment.

    The hex grid is indexed top to bottom, left to right (i.e. the top left corner has coordinates (0, 0) and the bottom
    right corner has coordinates (n_rows-1, n_cols-1)). Even numbered columns (starting from zero) are in the top half
    of the row, odd numbered columns are in the bottom half of the row.

    e.g.
        row 0, col 0            row 0, col 2                ...
                    row 0, col 1            row 0, col 3
        row 1, col 0            row 1, col 2                ...
                    row 1, col 1            row 1, col 3
            ...         ...         ...         ...
    """

    def __init__(self, filename, force_valid=True):
        """
        Process the given input file and create a new game environment instance based on the input file.

        :param filename: name of input file
        :param force_valid: When creating states, raise exception if the created State violates validity constraints
        """
        if platform.system() == 'Windows':
            os.system('color')  # enable coloured terminal output

        self.force_valid = force_valid
        f = open(filename, 'r')

        # environment dimensions
        self.n_rows = None
        self.n_cols = None

        # seed (for T model, R model, and episode random outcomes)
        self.seed = None

        # RL agent parameters
        self.agent_type = None
        self.gamma = None
        self.alpha = None

        # solver requirements
        self.training_reward_tgt = None
        self.evaluation_reward_tgt = None
        self.training_time_tgt = None

        # hex grid data
        self.obstacle_map = None
        self.hazard_map = None
        self.target_list = []

        self.robot_init_posit = None
        self.robot_init_orient = None

        # ========== read input file data ==========
        line_num = 0
        row = None
        for line in f:
            line_num += 1

            # skip annotations in input file
            if line.strip()[0] == '#':
                continue

            # read meta data
            #   environment dimensions
            if self.n_rows is None or self.n_cols is None:
                try:
                    self.n_rows, self.n_cols = tuple([int(x) for x in line.strip().split(',')])
                    self.obstacle_map = [[0 for _ in range(self.n_cols)] for __ in range(self.n_rows)]
                    self.hazard_map = [[0 for _ in range(self.n_cols)] for __ in range(self.n_rows)]
                except ValueError:
                    assert False, f'!!! Invalid input file - n_rows and n_cols (line {line_num}) !!!'

            #   environment seed
            elif self.seed is None:
                try:
                    self.seed = int(line.strip())
                except ValueError:
                    assert False, f'!!! Invalid input file - environment seed (line {line_num}) !!!'

            #   RL agent parameters
            elif self.agent_type is None:
                st = line.strip()
                assert st == 'q-learn' or st == 'sarsa', \
                    f'!!! Invalid input file - unrecognised agent type (line {line_num}) !!!'
                self.agent_type = st
            elif self.gamma is None:
                try:
                    self.gamma = float(line.strip())
                except ValueError:
                    assert False, f'!!! Invalid input file - gamma/discount factor (line {line_num}) !!!'
            elif self.alpha is None:
                try:
                    self.alpha = float(line.strip())
                except ValueError:
                    assert False, f'!!! Invalid input file - alpha/learning rate (line {line_num}) !!!'

            #   RL agent requirements
            elif self.training_reward_tgt is None:
                try:
                    self.training_reward_tgt = float(line.strip())
                except ValueError:
                    assert False, f'!!! Invalid input file - training reward target (line {line_num}) !!!'
            elif self.evaluation_reward_tgt is None:
                try:
                    self.evaluation_reward_tgt = float(line.strip())
                except ValueError:
                    assert False, f'!!! Invalid input file - evaluation reward target (line {line_num}) !!!'
            elif self.training_time_tgt is None:
                try:
                    self.training_time_tgt = float(line.strip())
                except ValueError:
                    assert False, f'!!! Invalid input file - training time target (line {line_num}) !!!'

            # read hex grid data
            if line[0] in ['/', '\\']:
                # handle start of new row
                if line[0] == '/':
                    if row is None:
                        row = 0
                    else:
                        row += 1
                    col_offset = 0
                    len_offset = 1 if self.n_cols % 2 == 1 else 0
                else:
                    col_offset = 1
                    len_offset = 0

                # split line into symbols and strip formatting characters
                symbols = [s.replace('\\', '').replace('/', '').replace('_', '') for s in line.strip().split('\\__/')]
                symbols = [s for s in symbols if len(s) > 0]    # remove empty symbols
                if len(symbols) != ((self.n_cols // 2) + len_offset):
                    assert False, f'!!! Invalid input file - incorrect hex grid row length (line {line_num}) !!!'

                # process the symbol in each cell of the row
                for col, sym in enumerate(symbols):
                    assert sym in ALL_VALID_SYMBOLS, \
                        f'!!! Invalid input file - unrecognised hex grid symbol (line {line_num}) !!!'
                    if sym == OBSTACLE:
                        self.obstacle_map[row][(2 * col) + col_offset] = 1
                    elif sym == HAZARD:
                        self.hazard_map[row][(2 * col) + col_offset] = 1
                    elif sym == TARGET:
                        self.target_list.append((row, (2 * col) + col_offset))
                    elif sym in ROBOT_ORIENTATIONS:
                        assert self.robot_init_posit is None and self.robot_init_orient is None, \
                            f'!!! Invalid input file - more than one initial robot position (line {line_num}) !!!'
                        self.robot_init_posit = (row, (2 * col) + col_offset)
                        self.robot_init_orient = sym

        assert row == self.n_rows - 1, '!!! Invalid input file - incorrect number of rows !!!'
        assert self.robot_init_posit is not None and self.robot_init_orient is not None,\
            '!!! Invalid input file - no initial robot position !!!'

        # ========== generate random t_model, r_model ==========
        random.seed(self.seed)

        # transition model
        self.__double_move_probs = {a: random.uniform(0.05, 0.6) for a in ROBOT_ACTIONS}
        self.__drift_cw_probs = {a: random.uniform(0.02, 0.3) for a in ROBOT_ACTIONS}
        self.__drift_ccw_probs = {a: random.uniform(0.02, 0.3) for a in ROBOT_ACTIONS}

        # penalties
        self.__collision_penalty = random.uniform(0.1, 5.0)
        self.__hazard_penalty = random.uniform(1.0, 20.0)

        # action costs
        self.__action_costs = {a: random.uniform(0.1, 3.0) for a in ROBOT_ACTIONS}

        # ========== keep track of total reward experienced ==========
        self.__reward_total = 0

    def get_init_state(self):
        """
        Get a state representation instance for the initial state.

        :return: initial state
        """
        return State(self, self.robot_init_posit, self.robot_init_orient)

    def __apply_action_noise(self, action):
        """
        Convert an action performed by the robot to a series of movements (representing action effect uncertainty).

        Not: Drift CW and Drift CCW are mutually exclusive, but each can occur together with Double Move
        :param action: action performed by robot
        :return: List of movements
        """
        movements = []
        # chance to drift CW or CCW (apply before selected action)
        r = random.random()
        if r < self.__drift_cw_probs[action]:
            movements.append(SPIN_RIGHT)
        elif r < self.__drift_ccw_probs[action] + self.__drift_cw_probs[action]:
            movements.append(SPIN_LEFT)

        # selected action
        movements.append(action)

        # chance for movement to be doubled
        if random.random() < self.__double_move_probs[action]:
            movements.append(action)

        return movements

    def __apply_dynamics(self, state, movement):
        """
        Perform the given action on the given state, and return the reward/cost received and the resulting new state.
        :param state:
        :param movement:
        :return: (reward/cost [float], next_state [instance of State])
        """
        if movement == SPIN_LEFT or movement == SPIN_RIGHT:
            # no collision possible for spin actions
            cost = self.__action_costs[movement]
            if movement == SPIN_LEFT:
                new_orient = {ROBOT_UP: ROBOT_UP_LEFT,
                              ROBOT_UP_LEFT: ROBOT_DOWN_LEFT,
                              ROBOT_DOWN_LEFT: ROBOT_DOWN,
                              ROBOT_DOWN: ROBOT_DOWN_RIGHT,
                              ROBOT_DOWN_RIGHT: ROBOT_UP_RIGHT,
                              ROBOT_UP_RIGHT: ROBOT_UP}[state.robot_orient]
            else:
                new_orient = {ROBOT_UP: ROBOT_UP_RIGHT,
                              ROBOT_UP_RIGHT: ROBOT_DOWN_RIGHT,
                              ROBOT_DOWN_RIGHT: ROBOT_DOWN,
                              ROBOT_DOWN: ROBOT_DOWN_LEFT,
                              ROBOT_DOWN_LEFT: ROBOT_UP_LEFT,
                              ROBOT_UP_LEFT: ROBOT_UP}[state.robot_orient]
            new_state = State(self, state.robot_posit, new_orient)
            return -1 * cost, new_state
        else:
            forward_direction = state.robot_orient
            # get coordinates of position forward of the robot
            forward_robot_posit = get_adjacent_cell_coords(state.robot_posit, forward_direction)
            if movement == FORWARD:
                new_robot_posit = forward_robot_posit
            else:
                move_direction = {ROBOT_UP: ROBOT_DOWN,
                                  ROBOT_DOWN: ROBOT_UP,
                                  ROBOT_UP_LEFT: ROBOT_DOWN_RIGHT,
                                  ROBOT_UP_RIGHT: ROBOT_DOWN_LEFT,
                                  ROBOT_DOWN_LEFT: ROBOT_UP_RIGHT,
                                  ROBOT_DOWN_RIGHT: ROBOT_UP_LEFT}[state.robot_orient]
                new_robot_posit = get_adjacent_cell_coords(state.robot_posit, move_direction)

            # test for out of bounds
            nr, nc = new_robot_posit
            if (not 0 <= nr < self.n_rows) or (not 0 <= nc < self.n_cols):
                return -1 * self.__collision_penalty, state

            # test for robot collision with obstacle
            if self.obstacle_map[nr][nc]:
                return -1 * self.__collision_penalty, state

            # test for robot collision with hazard
            if self.hazard_map[nr][nc]:
                return -1 * self.__hazard_penalty, state

            # this action does not collide and does not push or pull any widgets
            cost = self.__action_costs[movement]
            new_state = State(self, new_robot_posit, state.robot_orient)
            return -1 * cost, new_state

    def perform_action(self, state, action, seed=None):
        """
        Perform the given action on the given state, and return whether the action was successful (i.e. valid and
        collision free), the cost of performing the action, and the resulting new state.
        :param state: 
        :param action:
        :param seed:
        :return: (cost [float], next_state [instance of State])
        """
        # sample a movement outcome
        if seed is not None:
            random.seed(seed)
        movements = self.__apply_action_noise(action)

        # apply dynamics based on the sampled movements
        new_state = state
        min_reward = 0
        for m in movements:
            reward, new_state = self.__apply_dynamics(new_state, m)
            # use the minimum reward over all movements
            if reward < min_reward:
                min_reward = reward

        # keep track of total reward
        self.__reward_total += min_reward

        return min_reward, new_state

    def is_solved(self, state):
        """
        Check if the environment has been solved (i.e. the robot is at a target)
        :param state: current state
        :return: True if solved, False otherwise
        """
        return state.robot_posit in self.target_list

    def get_total_reward(self):
        """
        Get the total reward experienced so far (read only, writing this variable is not allowed)
        :return: total reward
        """
        return self.__reward_total

    def render(self, state):
        """
        Render the environment's current state to terminal
        :param state: current state
        """
        class Colours:
            prefix = "\033["
            reset = f"{prefix}0m"

            black = f"{prefix}30m"
            red = f"{prefix}31m"        # robot colour
            green = f"{prefix}32m"      # target colour
            yellow = f"{prefix}33m"     # w colour
            blue = f"{prefix}34m"
            magenta = f"{prefix}35m"    # w colour
            cyan = f"{prefix}36m"       # w colour
            white = f"{prefix}37m"

            robot_colour = red
            tgt_colour = green
            hazard_colour = blue

        buffer = [[' ' for _ in range((self.n_cols * RENDER_CELL_TOP_WIDTH) +
                                      ((self.n_cols + 1) * RENDER_CELL_SIDE_WIDTH))]
                  for __ in range((self.n_rows * RENDER_CELL_DEPTH) + RENDER_CELL_SIDE_WIDTH + 1)]

        # draw hex grid lines
        for i in range(self.n_rows):
            for j in range(0, self.n_cols, 2):
                # draw 2 complete hex cells each loop iteration
                #  __
                # /1 \__
                # \__/2 \
                #    \__/

                for k in range(RENDER_CELL_TOP_WIDTH):
                    # draw top half-row upper boundary '_'
                    y = i * RENDER_CELL_DEPTH
                    x = (j * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH) + k
                    buffer[y][x] = '_'

                    # draw top half-row lower boundary '_'
                    y = (i + 1) * RENDER_CELL_DEPTH
                    x = (j * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH) + k
                    buffer[y][x] = '_'

                    if j < self.n_cols - 1:
                        # draw bottom half-row upper boundary '_'
                        y = (i * RENDER_CELL_DEPTH) + RENDER_CELL_SIDE_WIDTH
                        x = ((j + 1) * RENDER_CELL_TOP_WIDTH) + ((j + 2) * RENDER_CELL_SIDE_WIDTH) + k
                        buffer[y][x] = '_'

                        # draw bottom half-row lower boundary '_'
                        y = ((i + 1) * RENDER_CELL_DEPTH) + RENDER_CELL_SIDE_WIDTH
                        x = ((j + 1) * RENDER_CELL_TOP_WIDTH) + ((j + 2) * RENDER_CELL_SIDE_WIDTH) + k
                        buffer[y][x] = '_'

                for k in range(RENDER_CELL_SIDE_WIDTH):
                    # draw top half-row up-left boundary '/'
                    y = (i * RENDER_CELL_DEPTH) + RENDER_CELL_SIDE_WIDTH - k
                    x = (j * RENDER_CELL_TOP_WIDTH) + (j * RENDER_CELL_SIDE_WIDTH) + k
                    buffer[y][x] = '/'

                    # draw top half-row up-right boundary '\'
                    y = (i * RENDER_CELL_DEPTH) + RENDER_CELL_SIDE_WIDTH - k
                    x = ((j + 1) * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH) - k + 1
                    buffer[y][x] = '\\'

                    # draw top half-row down-left boundary '\'
                    y = ((i + 1) * RENDER_CELL_DEPTH) - k
                    x = (j * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH) - k - 1
                    buffer[y][x] = '\\'

                    # draw top half-row down-right boundary '/'
                    y = ((i + 1) * RENDER_CELL_DEPTH) - k
                    x = ((j + 1) * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH) + k
                    buffer[y][x] = '/'

                    if j < self.n_cols - 1:
                        # draw bottom half-row up-right boundary '\'
                        y = ((i + 1) * RENDER_CELL_DEPTH) - k
                        x = ((j + 2) * RENDER_CELL_TOP_WIDTH) + ((j + 3) * RENDER_CELL_SIDE_WIDTH) - k - 1
                        buffer[y][x] = '\\'

                        # draw bottom half-row down-left boundary '\'
                        y = ((i + 1) * RENDER_CELL_DEPTH) + RENDER_CELL_SIDE_WIDTH - k
                        x = ((j + 1) * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH) - k + 1
                        buffer[y][x] = '\\'

                        # draw bottom half-row down-right boundary '/'
                        y = ((i + 1) * RENDER_CELL_DEPTH) + RENDER_CELL_SIDE_WIDTH - k
                        x = ((j + 2) * RENDER_CELL_TOP_WIDTH) + ((j + 2) * RENDER_CELL_SIDE_WIDTH) + k
                        buffer[y][x] = '/'

        # draw obstacles
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if self.obstacle_map[i][j]:
                    # draw an obstacle here
                    y = i * RENDER_CELL_DEPTH + (RENDER_CELL_SIDE_WIDTH if j % 2 == 1 else 0) + 1
                    x = (j * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH)

                    # 1st obstacle row
                    for x_offset in range(RENDER_CELL_TOP_WIDTH):
                        buffer[y][x + x_offset] = 'X'
                    # 2nd obstacle row
                    for x_offset in range(-1, RENDER_CELL_TOP_WIDTH + 1):
                        buffer[y + 1][x + x_offset] = 'X'
                    # 3rd obstacle row
                    for x_offset in range(-1, RENDER_CELL_TOP_WIDTH + 1):
                        buffer[y + 2][x + x_offset] = 'X'
                    # 4th obstacle row (overwrites bottom border)
                    for x_offset in range(RENDER_CELL_TOP_WIDTH):
                        buffer[y + 3][x + x_offset] = 'X'

        # draw hazards
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if self.hazard_map[i][j]:
                    # draw an obstacle here
                    y = i * RENDER_CELL_DEPTH + (RENDER_CELL_SIDE_WIDTH if j % 2 == 1 else 0) + 1
                    x = (j * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH)

                    # 1st obstacle row
                    for x_offset in range(RENDER_CELL_TOP_WIDTH):
                        buffer[y][x + x_offset] = '!'
                    # 2nd obstacle row
                    for x_offset in range(-1, RENDER_CELL_TOP_WIDTH + 1):
                        buffer[y + 1][x + x_offset] = '!'
                    # 3rd obstacle row
                    for x_offset in range(-1, RENDER_CELL_TOP_WIDTH + 1):
                        buffer[y + 2][x + x_offset] = '!'
                    # 4th obstacle row (overwrites bottom border)
                    for x_offset in range(RENDER_CELL_TOP_WIDTH):
                        buffer[y + 3][x + x_offset] = '!'

        # draw targets
        for tgt in self.target_list:
            ti, tj = tgt
            # draw in bottom half of cell, horizontally centered
            y = ti * RENDER_CELL_DEPTH + (RENDER_CELL_SIDE_WIDTH if tj % 2 == 1 else 0) + RENDER_CELL_SIDE_WIDTH + 1
            x = (tj * RENDER_CELL_TOP_WIDTH) + ((tj + 1) * RENDER_CELL_SIDE_WIDTH) + (RENDER_CELL_TOP_WIDTH // 2)
            # buffer[y][x] = 'T'
            buffer[y][x - 1] = 't'
            buffer[y][x] = 'g'
            buffer[y][x + 1] = 't'

        # draw robot
        ri, rj = state.robot_posit
        # reference coord in top half of cell, horizontally centred (change draw position based on orientation)
        y = ri * RENDER_CELL_DEPTH + (RENDER_CELL_SIDE_WIDTH if rj % 2 == 1 else 0) + RENDER_CELL_SIDE_WIDTH
        x = (rj * RENDER_CELL_TOP_WIDTH) + ((rj + 1) * RENDER_CELL_SIDE_WIDTH) + (RENDER_CELL_TOP_WIDTH // 2)
        # handle each orientation separately
        if state.robot_orient == ROBOT_UP:
            buffer[y + 1][x] = 'R'
            buffer[y - 1][x] = '*'
        elif state.robot_orient == ROBOT_DOWN:
            buffer[y - 1][x] = 'R'
            buffer[y + 1][x] = '*'
        elif state.robot_orient == ROBOT_UP_LEFT:
            buffer[y + 1][x + 1] = 'R'
            buffer[y][x - 2] = '*'
        elif state.robot_orient == ROBOT_UP_RIGHT:
            buffer[y + 1][x - 1] = 'R'
            buffer[y][x + 2] = '*'
        elif state.robot_orient == ROBOT_DOWN_LEFT:
            buffer[y][x + 1] = 'R'
            buffer[y + 1][x - 2] = '*'
        else:   # state.robot_orient == ROBOT_DOWN_RIGHT
            buffer[y][x - 1] = 'R'
            buffer[y + 1][x + 2] = '*'

        # print render buffer to screen
        for row in buffer:
            line = ''
            for i, char in enumerate(row):
                if char in ['t', 'g']:
                    # target
                    if not DISABLE_COLOUR:
                        line += Colours.tgt_colour
                if char == 'R' or char == '*':
                    # part of robot
                    if not DISABLE_COLOUR:
                        line += Colours.robot_colour
                if char == '!':
                    # hazard
                    if not DISABLE_COLOUR:
                        line += Colours.hazard_colour

                line += char

                if char in ['t', 'g']:
                    # end of target
                    if not DISABLE_COLOUR:
                        line += Colours.reset
                if char == 'R' or char == '*':
                    # end of part of robot
                    if not DISABLE_COLOUR:
                        line += Colours.reset
                if char == '!':
                    # end of hazard
                    if not DISABLE_COLOUR:
                        line += Colours.reset
            print(line)
        print('\n')


def get_adjacent_cell_coords(posit, direction):
    """
    Return the coordinates of the cell adjacent to the given position in the given direction.
    orientation.
    :param posit: position
    :param direction: direction (element of ROBOT_ORIENTATIONS)
    :return: (row, col) of adjacent cell
    """
    r, c = posit
    if direction == ROBOT_UP:
        return r - 1, c
    elif direction == ROBOT_DOWN:
        return r + 1, c
    elif direction == ROBOT_UP_LEFT:
        if c % 2 == 0:
            return r - 1, c - 1
        else:
            return r, c - 1
    elif direction == ROBOT_UP_RIGHT:
        if c % 2 == 0:
            return r - 1, c + 1
        else:
            return r, c + 1
    elif direction == ROBOT_DOWN_LEFT:
        if c % 2 == 0:
            return r, c - 1
        else:
            return r + 1, c - 1
    else:   # direction == ROBOT_DOWN_RIGHT
        if c % 2 == 0:
            return r, c + 1
        else:
            return r + 1, c + 1











