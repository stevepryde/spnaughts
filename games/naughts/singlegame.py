"""Module for running a single game of naughts and crosses."""


import copy
from typing import Any, Dict, List, Optional

from games.naughts import board
from games.naughts.bots.bot_base import NaughtsBot
from lib.gamebase import GameBase
from lib.gamecontext import GameContext
from lib.gameresult import GameResult, STATUS_LOSS, STATUS_TIE, STATUS_WIN


class SingleGame(GameBase):
    """Run a single game of naughts and crosses."""

    identities = ("X", "O")

    def __init__(self, parent_context: GameContext) -> None:
        """Create a new SingleGame object."""
        super().__init__(parent_context=parent_context)
        self.game_board = None  # type: Optional[board.Board]
        self.current_bot_id = 0
        return

    def is_ended(self) -> bool:
        """Return True if the game has ended, otherwise False."""
        assert self.game_board, "No game board!"
        return self.game_board.is_ended()

    def clone(self) -> "SingleGame":
        """Clone this instance of SingleGame."""
        assert self.parent_context, "Invalid parent context"
        cloned_game = SingleGame(self.parent_context)
        cloned_game.bots = copy.deepcopy(self.bots)
        cloned_game.game_board = copy.deepcopy(self.game_board)
        cloned_game.current_bot_id = self.current_bot_id
        cloned_game.num_turns = copy.deepcopy(self.num_turns)
        return cloned_game

    def start(self, bots: List[NaughtsBot]) -> None:
        """
        Start new game.

        :param bots: List of bots to run.
        """
        super().start(bots)
        self.game_board = board.Board()
        return

    def do_turn(self) -> List["SingleGame"]:
        """Process one game turn."""
        assert self.game_board, "No game board!"

        if not self.config.silent:
            self.game_board.show()

        current_bot = self.bots[self.current_bot_id]
        name = current_bot.name
        identity = current_bot.identity

        self.log.info("What is your move, '{}'?".format(name))

        # Allow for a bot to return multiple moves. This is useful for running
        # the 'omnibot' in order to train or measure other bots.
        moves = current_bot.do_turn(self.game_board.copy())

        # Update current_bot_id early, this way it will be copied to any
        # cloned games...
        if self.current_bot_id == 0:
            self.current_bot_id = 1
        else:
            self.current_bot_id = 0

        game_clones = []
        if isinstance(moves, list):
            for move in moves:
                # clone this game.
                cloned_game = self.clone()

                # apply move to clone.
                cloned_game.apply_move(int(move), name, identity)

                # append to game_clones
                game_clones.append(cloned_game)
        else:
            # Single move only.
            self.apply_move(int(moves), name, identity)

            # This will not affect the standard game runner.
            # The omnibot runner should use the returned list of games and
            # discard the one that was used to call do_turn().
            game_clones = [self]

        return game_clones

    def apply_move(self, move: int, name: str, identity: str) -> None:
        """
        Apply the specified move to the current game.

        :param move: The move to apply.
        :param name: The name of the bot.
        :param identity: The player identity ('X' or 'O')
        """
        assert self.game_board, "No game board!"

        self.log.info("'{}' chose move ({})".format(name, move))
        self.log.info("")

        if move < 0 or move > 8:
            self.log.error("Bot '{}' performed a move out of range ({})".format(name, move))
            return

        if self.game_board.getat(move) != " ":
            self.log.error("Bot '{}' performed an illegal move ({})".format(name, move))
            return

        self.game_board.setat(move, identity)
        self.num_turns[identity] += 1

        if not self.config.silent:
            self.game_board.show()
        return

    def get_result(self) -> Dict[str, Any]:
        """Get information about this game."""
        assert self.game_board, "No game board!"

        if len(self.bots) != 2:
            self.log.error("No bots have been set up - was this game started?")
            return {}

        outcome = self.game_board.get_game_state()

        if outcome == 0:
            self.log.error("Game ended with invalid state of 0 - was this " "game finished?")
            return {}

        result_X = GameResult()
        result_O = GameResult()

        if outcome == 1:
            self.log.info("Bot '{}' wins".format(self.bots[0].name))
            result_X.status = STATUS_WIN
            result_O.status = STATUS_LOSS
        elif outcome == 2:
            self.log.info("Bot '{}' wins".format(self.bots[1].name))
            result_X.status = STATUS_LOSS
            result_O.status = STATUS_WIN
        elif outcome == 3:
            self.log.info("It's a TIE")
            result_X.status = STATUS_TIE
            result_O.status = STATUS_TIE
        else:
            self.log.error("Game ended with invalid state ({})".format(outcome))
            return {}

        result_X.score = self.calculate_score(self.num_turns["X"], result_X.status)  # type: ignore
        result_O.score = self.calculate_score(self.num_turns["O"], result_O.status)  # type: ignore

        self.bots[0].score = result_X.score  # type: ignore
        self.bots[1].score = result_O.score  # type: ignore
        self.bots[0].process_game_result(result_X)
        self.bots[1].process_game_result(result_O)

        self.log.info(
            "Scores: '{}':{:.2f} , '{}':{:.2f}".format(
                self.bots[0].name, result_X.score, self.bots[1].name, result_O.score
            )
        )

        game_info = {"result": outcome, "scores": {"X": result_X.score, "O": result_O.score}}
        return game_info

    def calculate_score(self, num_turns: int, status: str) -> float:
        """
        Calculate the 'score' for this game.

        :param num_turns: The number of turns played.
        :param status: The status code (see GameResult).
        :returns: The game score, as float.
        """
        score = 10 - num_turns
        if status != STATUS_WIN:
            if status == STATUS_TIE:
                score = 0
            else:
                assert status == STATUS_LOSS, "Invalid status: {}".format(status)
                # Weight losses much more heavily than wins
                score = -score * 10
        return score
