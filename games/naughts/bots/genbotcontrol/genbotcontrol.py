"""
This bot is intended to mimic genbot1, but without any magic.

It uses random choices instead. It serves as a 'control'
subject to compare against genbot1.
"""


import random


from games.naughts.board import Board
from games.naughts.bots.naughtsbot import NaughtsBot


class GenBotControl(NaughtsBot):
    """
    Control bot for genbot1.

    If genbot1 does no better than this bot, then it is no better than random
    chance.
    """

    def __init__(self):
        """Create new GenBotControl."""
        super().__init__()
        self.genetic = True
        return

    def do_turn(self, current_board: Board):
        """Do one turn."""
        moves = current_board.get_possible_moves()

        # First, win the game if we can.
        straight_sequences = ["012", "345", "678", "036", "147", "258", "048", "246"]

        for seq in straight_sequences:
            (ours, theirs, blanks) = self.get_sequence_info(current_board, seq)
            if len(ours) == 2 and len(blanks) == 1:
                # Move into the blank for the win.
                return int(blanks[0])

        # Second, if we can't win, make sure the opponent can't win either.
        for seq in straight_sequences:
            (ours, theirs, blanks) = self.get_sequence_info(current_board, seq)
            if len(theirs) == 2 and len(blanks) == 1:
                # Move into the blank to block the win.
                return int(blanks[0])

        # If this is the first move...
        (ours, theirs, blanks) = self.get_sequence_info(current_board, "012345678")
        if not ours:
            # If we're the second player:
            if theirs:
                if 4 in moves:
                    return 4

                # Otherwise take the upper left.
                return 0

        # ENGAGE 'FAKE' BRAIN

        # THIS one is just a control, to see how well the real genbot works
        # compared to a fake one that just chooses a valid move at random.

        return random.choice(moves)
        # END OF 'FAKE' BRAIN ENGAGEMENT
