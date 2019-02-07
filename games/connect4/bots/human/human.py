"""
This bot accepts input via the keyboard for every move.

This allows manual games with human vs another bot.
Not practical in batch mode or genetic mode.
"""

from typing import Any

from games.connect4.world import World
from games.connect4.bots.connect4bot import Connect4Bot


class Human(Connect4Bot):
    """Bot that gets input from the user."""

    def do_turn(self, current_world: World):
        """Do one turn."""
        moves = current_world.get_possible_moves()
        current_world.show()

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
        if isinstance(data, World):
            print("\nGame over:")
            data.show()
        return
