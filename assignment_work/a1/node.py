from state import *

class StateNode:
	def __init__(self, state: State, actions: tuple):
		self.state = state
		self.actions = actions

class StateNodeWithCost(StateNode):
	def __init__(self, state: State, actions: tuple, cost: int):
		super().__init__(state, actions)
		self.cost = cost

	def __lt__(self, other):
		if self.cost != other.cost:
			return self.cost < other.cost
		else:
			return self.actions[len(self.actions) - 1] < other.actions[len(other.actions) - 1]