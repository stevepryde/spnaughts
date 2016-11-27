"""This bot just executes moves at random. It is a useful baseline.
It is also very useful for training and testing AI bots.
"""


import random


from bots.bot_base import Bot


class RANDOMBOT(Bot):
    """Do random move from possible moves only."""

    def do_turn(self, current_board):
        """Choose random move from all possible moves."""
        moves = self.get_possible_moves(current_board)
        return random.choice(moves)
