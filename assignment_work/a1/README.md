# Assignment 1 Support Code

This is the support code for COMP3702 2022 Assignment 1 (HexBot).

The following files are provided:

**environment.py**

This file contains a class representing a HexBot environment and supporting helper methods. You should make use of this
class in your solver.

This file contains a number of functions which will be useful in developing your solver:

~~~~~
__init__(filename)
~~~~~

Constructs a new instance based on the given input filename.

~~~~~
get_init_state()
~~~~~

Returns a State object (see below) representing the initial state of the level.

~~~~~
perform_action(state, action)
~~~~~

Simulates the outcome of performing the given 'action' starting from the given 'state', where 'action' is an element of
GameEnv.ACTIONS and 'state' is a State object. Returns a tuple of whether the action was successful (i.e. valid and
collision free), the cost of performing the action, and the resulting new state

~~~~~
is_solved(state)
~~~~~

Checks whether the given 'state' (a State object) is solved (i.e. all targets are covered by a widget). Returns
True (solved) or False (not solved).

~~~~~
render(state)
~~~~~

Prints a graphical representation of the given 'state' (a State object) to the terminal.

**state.py**

This file contains a class representing a HexBot environment state. You should make use of this class and its functions
in your solver. You may add your own code to this class (e.g. get_successors function, get_heuristic function, etc), but
should avoid removing or renaming existing variables and functions to ensure Tester functions correctly.

~~~~~
__init__(self, environment, robot_posit, robot_orient, widget_centres, widget_orients, force_valid=True)
~~~~~

Constructs a HexRobot environment state. Refer to the docstring for this method for information on the arguments taken
by this method.

**constants.py**

This file contains constants used by the Environment and State classes. It may be helpful to import this file into
your solver.

**play.py**

Running this file launches an interactive environment simulation. Becoming familiar with the environment mechanics may
be helpful in designing your solution.

The script takes 1 argument, input_filename, which must be a valid testcase file (e.g. one of the provided files in the
testcases directory). e.g.

~~~~~
python play.py testcases/example.txt
~~~~~

When prompted for an action, press W to move the robot forward, S to move the robot in reverse, A to turn the robot
left (counterclockwise) and D to turn the robot right (clockwise). Use Q to exit the simulation, and R to reset the
environment to the initial configuration.

**solution.py**

This file is a template you should use to implement your solution.

You should implement the `solve_ucs()` and `solve_a_star()` functions as well as any initialisation or helper functions
you require.

You can test your solution by running `tester.py`.

**tester.py**

Use this script to evaluate your solution. This script calls your implementations of `solve_ucs()` and `solve_a_star()`
in `solution.py`. Use command line arguments to select whether to evaluate UCS, A*, or both methods, and the numbers of
the testcases you wish to evaluate on.

Usage:

~~~~~
$ python tester.pyc [search_type] [testcases] [-v (optional)]
    search_type = 'ucs', 'a_star' or 'both'
    testcases = a comma separated list of numbers (e.g. '1,3,4')
    if -v is specified, the solver's trajectory will be visualised
~~~~~

**testcases**

A directory containing input files which can be used to evaluate your solution.

The format of a testcase file is:

~~~~~
num_rows, num_cols
cost_tgt
time_tgt UCS, time_tgt A*
nodes_expanded_tgt UCS, nodes_expanded_tgt A*
hex grid data (row 1)
...
hex grid data (row num_rows)
~~~~~

Testcase files can contain comments, starting with '#', which are ignored by the input file parser.
