import unittest


class TestBFS(unittest.TestCase):
    def test_one_step(self):
        start = (
            (1, 2, 3),
            (4, 5, 6),
            (7, 8, -1)
        )

        goal = (
            (1, 2, 3),
            (4, 5, 6),
            (7, -1, 8)
        )

        states = BFS(start, goal)
        self.assertEqual(2, len(states))