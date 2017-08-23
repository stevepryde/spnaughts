"""
This bot just executes moves at random. It is a useful baseline.

It is also very useful for training and testing AI bots.
"""


import random


from games.naughts.bots.bot_base import Bot


class RANDOMBOT(Bot):
    """Do random move from possible moves only."""

    def do_turn(self, game_obj):
        """Choose random move from all possible moves."""
        moves = self.get_possible_moves(game_obj)
        return random.choice(moves)
