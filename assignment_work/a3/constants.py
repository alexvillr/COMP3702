import string
"""
constants.py

This file contains constants used by the Environment and State classes.

COMP3702 2022 Assignment 1 Support Code

Last updated by njc 29/07/22
"""

# === Robot Orientations ===============================================================================================
# Possible orientations for the robot. '*' indicates the front side of the robot
#
#    UP          DOWN        UP_LEFT     UP_RIGHT     DOWN_LEFT   DOWN_RIGHT
#   ____         ____         ____         ____         ____         ____
#  /    \       /    \       /    \       /    \       /    \       /    \
# /  *   \     /  |   \     /  *   \     /   *  \     /   /  \     /  \   \
# \  |   /     \  *   /     \   \  /     \  /   /     \  *   /     \   *  /
#  \____/       \____/       \____/       \____/       \____/       \____/
#

ROBOT_UP = 'U.'
ROBOT_DOWN = 'D.'
ROBOT_UP_LEFT = 'UL'
ROBOT_UP_RIGHT = 'UR'
ROBOT_DOWN_LEFT = 'DL'
ROBOT_DOWN_RIGHT = 'DR'
ROBOT_ORIENTATIONS = [ROBOT_UP, ROBOT_DOWN, ROBOT_UP_LEFT, ROBOT_UP_RIGHT, ROBOT_DOWN_LEFT, ROBOT_DOWN_RIGHT]

# === Robot Actions ====================================================================================================
FORWARD = 0
REVERSE = 1
SPIN_LEFT = 2
SPIN_RIGHT = 3
ROBOT_ACTIONS = [FORWARD, REVERSE, SPIN_LEFT, SPIN_RIGHT]

# === Other Symbols ====================================================================================================
FREE_SPACE = '  '
TARGET = 'TT'
OBSTACLE = 'XX'
HAZARD = '!!'
ENVIRONMENT_SYMBOLS = [FREE_SPACE, TARGET, OBSTACLE, HAZARD]
IGNORED_SYMBOLS = [2 * c for c in string.ascii_lowercase]   # double lowercase letter is valid but ignored

ALL_VALID_SYMBOLS = ROBOT_ORIENTATIONS + ENVIRONMENT_SYMBOLS + IGNORED_SYMBOLS

# === Render Parameters ================================================================================================
RENDER_CELL_TOP_WIDTH = 7
RENDER_CELL_DEPTH = 4
RENDER_CELL_SIDE_WIDTH = RENDER_CELL_DEPTH // 2

