from collections import deque


def BFS(problem, goal):
    '''
    Solves 8-game with BFS
    Parameters:
        problem(String): the intitial state of the 8-game
        goal(String): the goal state of the 8-game
    returns:
        'Failure' if there is no possible way to reach the goal state from the initial state
        node, a pair value with the final state and the amount 
    '''
    node = (problem, 0)
    if (node[0] == goal):
        return node
    frontier = deque()
    frontier.append(node)
    explored = set()
    while (not frontier.empty()):
        node = frontier.popleft()
        explored.add(node)


