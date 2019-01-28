"""
This bot just executes moves at random. It is a useful baseline.

It is also very useful for training and testing AI bots.
"""


import random
from typing import List


from lib.gameplayer import GamePlayer


class RandomBot(GamePlayer):
    """Do random move from possible moves only."""

    def process(self, inputs: List[float], available_moves: List[float]) -> float:
        """Process one game turn."""
        return random.choice(available_moves)

