"""This bot just executes the first possible move every time."""

import random
from typing import List

from lib.gameplayer import GamePlayer


class FirstBot(GamePlayer):
    """Do the first possible move every time."""

    def process(self, inputs: List[float], available_moves: List[float]) -> float:
        """Process one game turn."""
        return available_moves[0]
