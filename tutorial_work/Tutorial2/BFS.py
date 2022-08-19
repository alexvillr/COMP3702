from queue import Queue
import time
from typing import Tuple
from PuzzleNode import PuzzleNode


def BFS(init_state: Tuple[Tuple[int]], goal_state: Tuple[Tuple[int]]):
    t0 = time.time()
    visited = set[Tuple]()

    q = Queue[PuzzleNode]
    q.put(PuzzleNode(None, None, init_state))

    while not q.empty():
        node = q.get()

        if node.current_state == goal_state:
            print("We reached the goal!")
            break

        for action in node.actions():
            new_state = node.step(action)
            if new_state not in visited:
                visited.add(new_state)
                q.put(PuzzleNode(node, action, new_state))
        
        if q.empty():
            node = None
        
        t_dfs = (time.time() - t0) / 1
        print(f'Finished in {t_dfs}')