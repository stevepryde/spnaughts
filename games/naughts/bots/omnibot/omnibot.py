"""
This bot is a special bot that will return a list of all available moves.

This is designed to be used with --batch 0 to use the magic batch runner.
Basically, after each turn, the current game will be cloned, once for each
returned move. Each of those cloned games will be added to a queue. The
magic batch runner pops the first item off the left side of the queue and
processes the next turn. See the magic batch runner in game/batch.py for
more details.
"""


from games.naughts.bots.bot_base import NaughtsBot


class OMNIBOT(NaughtsBot):
    """
    Special bot that returns all available moves.

    This way cloned games can be spawned for each one.
    Consider this the British Museum algorithm.
    """

    def do_turn(self, game_obj):
        """Do one turn."""
        return self.get_possible_moves(game_obj)
