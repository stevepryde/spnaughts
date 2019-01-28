"""
Base class for AI naughts and crosses bots.

All bots must implement do_turn().
Bots can optionally implement setup() and process_game_result().
Genetic bots can also optionally implement process_batch_result().
"""


import os
from typing import Any, List, Optional, Tuple, TYPE_CHECKING

from games.naughts.board import Board
from lib.gameplayer import GamePlayer
from lib.globals import log_debug, log_trace

if TYPE_CHECKING:
    from games.naughts.singlegame import SingleGame


class NaughtsBot(GamePlayer):
    """Base class for all naughts bots."""

    @property
    def other_identity(self) -> str:
        """Get the identity character for the other bot."""
        if self.identity == "X":
            return "O"
        return "X"

    def process(self, inputs: List[float], available_moves: List[float]) -> Any:
        """Process one game turn."""
        assert len(inputs) == 9, "BUG: Invalid number of inputs for naughts game: {}".format(
            len(inputs)
        )

        board = Board()
        for pos, x in enumerate(inputs):
            value = " "
            if x > 0.0:
                value = self.identity
            elif x < 0.0:
                value = self.other_identity
            board.setat(pos, value)
        return float(self.do_turn(board))

    def do_turn(self, current_board: Board) -> int:
        """Do one turn. Override in subclass."""
        return 0

    ##########################################################################
    # HELPER METHODS
    # These are methods that are probably generally useful to several bots.
    ##########################################################################

    def get_sequence_info(
        self, board: Board, sequence: str
    ) -> Tuple[List[int], List[int], List[int]]:
        """
        Return info about the given sequence, in the form of 3 lists.

        :param board: The board to query.
        :param sequence: The sequence to get information for.

        :returns: Tuple containing 3 lists.
            The first list will be all positions matching my own identity.
            The second list will be all positions matching the other identity.
            The third list will be all blank positions.
        """
        ours = []
        theirs = []
        blanks = []

        seq_list = [int(x) for x in list(sequence)]

        for c in seq_list:
            val = board.getat(c)
            if val == self.identity:
                ours.append(c)
            elif val == " ":
                blanks.append(c)
            else:
                theirs.append(c)

        return (ours, theirs, blanks)

    def get_unrotated_move(self, move: int, rotations: int) -> int:
        """
        Return the correct, unrotated move.

        The returned move corresponds to the move we would make on a board
        rotated the specified number of times.
        For example, if rotations is 1, and I want to get the corrected move
        for move 0, this would return 6. If rotations is 2, and I want the
        corrected move for 1, this would return 7.

        :param move: The move to make.
        :param rotations: The number of 90 degree rotations, in a clockwise
            direction.
        :returns: The move, rotated anti-clockwise by the number of specified
            rotations.
        """
        rotations = int(rotations) % 4

        # Don't do anything if we don't have to.
        if rotations == 0:
            return int(move)

        transform_map = [6, 3, 0, 7, 4, 1, 8, 5, 2]
        for _ in range(rotations):
            move = transform_map[int(move)]

        return move
