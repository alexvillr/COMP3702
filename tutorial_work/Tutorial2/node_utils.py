from typing import Set
from PuzzleNode import PuzzleNode
from typing import Set

def backtrack_actions(goal_node: PuzzleNode, visited_nodes: Set, print_progress: bool):
    print(f"Visited nodes: {len(visited_nodes)}")

    if goal_node is not None:
        seq = [goal_node]
        node = goal_node

        while node.parent:
            seq.append(node.parent)
            node = node.parent

        seq.reverse()
        print(f"Number of actions {len(seq)}")
        if print_progress:
            for s in seq:
                s.print()