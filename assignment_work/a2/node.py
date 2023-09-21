from state import *


class StateNode:
	def __init__(self, state: State):
		self.state = state


class StateNodeWithCost(StateNode):
	def __init__(self, state: State, cost: int):
		super().__init__(state)
		self.cost = cost

	def __lt__(self, other):
		if self.cost != other.cost:
			return self.cost < other.cost
