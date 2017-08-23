"""
This bot accepts input via the keyboard for every move.

This allows manual games with human vs another bot.
Not practical in batch mode or genetic mode.
"""


from games.naughts.bots.bot_base import Bot


class HUMAN(Bot):
    """Bot that gets input from the user."""

    def do_turn(self, game_obj):
        """Do one turn."""
        moves = self.get_possible_moves(game_obj)
        moves = [str(x) for x in moves]

        info_str = 'possible moves are [{}]'.format(','.join(moves))

        # If there's only one choice, save ourselves some typing.
        if len(moves) == 1:
            move = int(moves[0])
            print("{} (Automatically choose {})".format(info_str, move))
            return move

        move = -1
        while move not in moves:
            try:
                move = str(int(input(info_str)))
            except ValueError:
                pass

        return int(move)
