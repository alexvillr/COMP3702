from pickletools import UP_TO_NEWLINE
from tkinter import LEFT, RIGHT
from typing import Optional
from typing import Tuple

LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3

class PuzzleNode():
    def __init__(self, parent, action: Optional(int), current_state: Tuple[Tuple[int]]):
        self.parent = parent
        self.action = action
        self.current_state = current_state
        self.last_col = len(current_state) - 1
        self.last_row = len(current_state[0]) - 1

        self.blank_col, self.blank_row = self.find_blank()

    def find_blank(self) -> Tuple[int, int]:
        for index, row in enumerate(self.current_state):
            if -1 in row:
                return row.index(-1), index
    
    def actions(self) -> list:
        actions = list[int]()

        if self.blank_col > 0:
            actions.append(LEFT)
        if self.blank_col < self.last_col:
            actions.append(RIGHT)
        if self.blank_row > 0:
            actions.append(DOWN)
        if self.blank_row < self.last_row:
            actions.append(UP)
    
    def step(self, action: int):
        new_state = list(list(row) for row in self.current_state)
        if action == UP:
            new_state[self.blank_row][self.blank_col] = new_state[self.blank_row - 1][self.blank_col]
            new_state[self.blank_row - 1][self.blank_col] = -1
        elif action == DOWN:
            new_state[self.blank_row][self.blank_col] = new_state[self.blank_row + 1][self.blank_col]
            new_state[self.blank_row + 1][self.blank_col] = -1
        elif action == LEFT:
            new_state[self.blank_row][self.blank_col] = new_state[self.blank_row][self.blank_col - 1]
            new_state[self.blank_row][self.blank_col - 1] = -1
        elif action == RIGHT:
            new_state[self.blank_row][self.blank_col] = new_state[self.blank_row][self.blank_col + 1]
            new_state[self.blank_row][self.blank_col + 1] = -1

        return Tuple([Tuple(row) for row in new_state])

    def print(self):
        pass