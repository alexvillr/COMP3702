from constants import *

"""
state.py

This file contains a class representing a HexBot environment state. You should make use of this class in your solver.

COMP3702 2022 Assignment 1 Support Code

Last updated by njc 28/07/22
"""


class State:
    """
    Instance of a HexBot environment state.

    See constructor docstring for information on instance variables.

    You may use this class and its functions. You may add your own code to this class (e.g. get_successors function,
    get_heuristic function, etc), but should avoid removing or renaming existing variables and functions to ensure
    Tester functions correctly.
    """

    def __init__(self, environment, robot_posit, robot_orient, force_valid=True):
        """
        Construct a HexRobot environment state.

        :param environment: an Environment instance
        :param robot_posit: (row, col) tuple representing robot position
        :param robot_orient: element of ROBOT_ORIENTATIONS representing robot orientation
        :param force_valid: If true, raise exception if the created State violates validity constraints
        """
        if force_valid:
            r, c = robot_posit
            assert isinstance(r, int), '!!! tried to create State but robot_posit row is not an integer !!!'
            assert isinstance(c, int), '!!! tried to create State but robot_posit col is not an integer !!!'
            assert 0 <= r < environment.n_rows, '!!! tried to create State but robot_posit row is out of range !!!'
            assert 0 <= c < environment.n_cols, '!!! tried to create State but robot_posit col is out of range !!!'
            assert robot_orient in ROBOT_ORIENTATIONS, \
                '!!! tried to create State but robot_orient is not a valid orientation !!!'
        self.environment = environment
        self.robot_posit = robot_posit
        self.robot_orient = robot_orient
        self.force_valid = force_valid

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return (self.robot_posit == other.robot_posit and
                self.robot_orient == other.robot_orient)

    def __hash__(self):
        return hash((self.robot_posit, self.robot_orient))

    def deepcopy(self):
        return State(self.environment, self.robot_posit, self.robot_orient, force_valid=self.force_valid)



