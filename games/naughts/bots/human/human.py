"""
This bot accepts input via the keyboard for every move.

This allows manual games with human vs another bot.
Not practical in batch mode or genetic mode.
"""

from typing import Any

from games.naughts.board import Board
from games.naughts.bots.naughtsbot import NaughtsBot


class HUMAN(NaughtsBot):
    """Bot that gets input from the user."""

    def do_turn(self, current_board: Board):
        """Do one turn."""
        moves = current_board.get_possible_moves()
        current_board.show()

        info_str = "possible moves are [{}]".format(",".join([str(x) for x in moves]))

        # If there's only one choice, save ourselves some typing.
        if len(moves) == 1:
            print("{} (Automatically choose {})".format(info_str, moves[0]))
            return moves[0]

        move = -1
        while move not in moves:
            try:
                move = int(input(info_str))
            except ValueError:
                pass

        return int(move)

    def show_result(self, data: Any) -> None:
        """Allow bot to see final result."""
        if isinstance(data, Board):
            print("\nGame over:")
            data.show()
        return
