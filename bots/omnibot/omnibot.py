"""
This is a special bot that simply returns all available moves.

It is intended to be combined with the magic batch runner to play through all
possible games against a bot.
"""

from typing import List


from lib.gameplayer import GamePlayer


class OmniBot(GamePlayer):
    """Do all possible moves."""

    def __init__(self) -> None:
        """Create new OmniBot object."""
        super().__init__()
        self.magic = True
        return

    def process_magic(self, inputs: List[float], available_moves: List[float]) -> List[float]:
        """Process one game turn."""
        return available_moves
