"""
Base class for AI Connect 4 bots.

All bots must implement do_turn().
"""


import os
from typing import Any, List, Optional, Tuple, TYPE_CHECKING

from games.connect4.world import World
from lib.gameplayer import GamePlayer
from lib.globals import log_debug, log_trace

if TYPE_CHECKING:
    from games.connect4.singlegame import SingleGame


class Connect4Bot(GamePlayer):
    """Base class for all Connect 4 bots."""

    @property
    def other_identity(self) -> str:
        """Get the identity character for the other bot."""
        if self.identity == "X":
            return "O"
        return "X"

    def process(self, inputs: List[float], available_moves: List[float]) -> Any:
        """Process one game turn."""
        assert len(inputs) == 98, "BUG: Invalid number of inputs for Connect 4 game: {}".format(
            len(inputs)
        )

        world = World()
        dinputs = list(inputs)
        for row in range(7):
            for col in range(7):
                x = dinputs.pop(0)
                if x > 0.0:
                    world.setat_raw(col, row, self.identity)

        for row in range(7):
            for col in range(7):
                x = dinputs.pop(0)
                if x > 0.0:
                    world.setat_raw(col, row, self.other_identity)
        return float(self.do_turn(world))

    def do_turn(self, current_world: World) -> int:
        """Do one turn. Override in subclass."""
        return 0

    def show_result(self, data: Any) -> None:
        """Allow bot to see final result."""
        return
