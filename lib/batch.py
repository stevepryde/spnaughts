"""Run a batch of games."""

from typing import Any, Deque, Dict, List

import collections
import copy
import random
import time

from lib.botfactory import BotFactory
from lib.gamebase import GameBase
from lib.gamecontext import GameContext
from lib.gamefactory import GameFactory
from lib.gameplayer import GamePlayer
from lib.gameresult import GameResult

P1_WINS = 1
P2_WINS = 2
DRAW = 3


class Batch(GameContext):
    """A Batch will run a batch of single games."""

    def __init__(self, bots: List[GamePlayer], batch_config: Dict[str, Any]) -> None:
        """
        Create a new Batch.

        :param bots: List of bots to run.
        :param batch_config: Dict containing batch config.
        """
        super().__init__()
        self.bots = bots

        # Don't use GameConfig here. Need to keep the data small so it can
        # be serialised efficiently.
        self.batch_config = batch_config
        self.game = self.batch_config.get("game", "")
        self.bot_config = self.batch_config.get("bot_config", {})
        self.batch_size = self.batch_config.get("batch_size", 1)
        self.stop_on_loss = self.batch_config.get("stop_on_loss", False)

        self.label = ""
        # info is used by genetic.batchworker.
        self.info = {}  # type: Dict[str, Any]

        self.overall_results = {P1_WINS: 0, P2_WINS: 0, DRAW: 0}
        self.num_games_played = 0
        self.total_score = {}  # type: Dict[str, float]
        self.wins = {}  # type: Dict[str, float]
        self.num_draws = 0
        self.identities = []  # type: List[str]
        return

    def run_batch(self) -> GameResult:
        """Run this batch and return the average scores."""
        self.start_batch()
        self.run_normal_batch()
        return self.process_batch_result()

    def start_batch(self) -> None:
        """Start this batch."""
        # Run a single batch.
        class_ = GameFactory(self).get_game_class(self.game)
        self.identities = list(class_.identities)
        for identity in self.identities:
            self.total_score[identity] = 0
            self.wins[identity] = 0

        self.num_games_played = 0
        self.num_draws = 0
        return

    def process_game_result(self, game_num: int, result: GameResult) -> None:
        """Process the result of a single game."""
        self.num_games_played += 1

        for identity in self.identities:
            self.total_score[identity] += result.get_score(identity)

        if result.is_tie():
            self.num_draws += 1
        else:
            self.wins[result.get_winner()] += 1
        return

    def process_batch_result(self) -> GameResult:
        """
        Process the results for this batch.

        :returns: List containing the average score for each bot.
        """
        # Print overall results.
        self.log.info("\nRESULTS:")
        self.log.info("Games Played: {}".format(self.num_games_played))
        self.log.info("")

        for i, bot in enumerate(self.bots):
            identity = self.identities[i]
            self.log.info("'{}' WINS: {}".format(bot.name, self.wins[identity]))
        self.log.info("DRAW/TIE: {}".format(self.num_draws))
        self.log.info("")

        # Get average scores.
        assert self.num_games_played > 0, "BUG: No games played!"

        batch_result = GameResult()
        batch_result.set_batch()
        self.log.info("\nAverage Scores:")
        for i, identity in enumerate(self.identities):
            self.bots[i].score = float(self.total_score[identity] / self.num_games_played)
            batch_result.set_score(identity, self.bots[i].score)
            self.log.info("{}: {}".format(self.bots[i].name, self.bots[i].score))
        return batch_result

    def run_normal_batch(self) -> None:
        """Run normal batch of games."""
        for game_num in range(1, self.batch_size + 1):
            self.log.info("\n********** Running game {} **********\n".format(game_num))

            game_obj = GameFactory(self).get_game_obj(self.game)

            bots = BotFactory(self, bot_config=self.bot_config).clone_bots(self.bots)
            game_obj.start(bots)
            result = game_obj.run()
            self.process_game_result(game_num, result)
        return
