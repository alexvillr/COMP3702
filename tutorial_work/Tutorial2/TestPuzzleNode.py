import unittest

from PuzzleNode import PuzzleNode
from PuzzleNode import LEFT, RIGHT, UP, DOWN


class TestPuzzleNode(unittest.TestCase):
    def setUp(self) -> None:
        self.bottom_right = PuzzleNode(
            None,
            None,
            (
            (1, 2, 3),
            (4, 5, 6),
            (7, 8, -1)
            )
        )

        self.center = PuzzleNode(
            None,
            None,
            (
                (1, 2, 3),
                (4, -1, 5),
                (6, 7, 8)
            )
        )


    def test_find_blank(self):
        node = self.bottom_right

        self.assertEqual((2, 2), node.find_blank())
    
    def test_actions_for_center(self):
        self.assertEqual([LEFT, RIGHT, UP, DOWN], self.center.actions())

    def test_step_up(self):
        new_state = self.bottom_right.step(UP)

        self.assertEqual(
            ((1, 2, 3),
            (4, 5, -1),
            (7, 8, 6)),
            new_state
        )

    def test_step_down(self):
        #TODO
        pass

    def test_step_left(self):
        #TODO
        pass
    
    def test_step_right(self):
        #TODO
        pass