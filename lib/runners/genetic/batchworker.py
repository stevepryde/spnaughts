"""Worker process for running batches from a queue."""

import multiprocessing
import time
from typing import Any, Dict, List

from lib.batch import Batch
from lib.botfactory import BotFactory
from lib.gamecontext import GameContext


class BatchWorker(multiprocessing.Process):
    """Worker class for a single 'thread'."""

    def __init__(
        self, input_batches: List[Batch], q_out: multiprocessing.Queue, score_threshold: float
    ) -> None:
        """
        Create new BatchWorker object.

        :param q_in: Queue of batches for input.
        :param q_out: Queue to output completed batches to.
        :param score_threshold: Maximum score to beat.
        """
        super().__init__()

        self.batches = input_batches
        self.outputs = []  # type: List[Batch]
        self.q_out = q_out
        self.score_threshold = score_threshold
        return

    def run(self) -> None:
        """Run batches."""
        try:
            for batch in self.batches:
                genetic_index = batch.info["index"]
                batch_result = batch.run_batch()

                genetic_identity = batch.identities[genetic_index]
                genetic_score = batch_result.get_score(genetic_identity)

                win = ""
                if genetic_score > self.score_threshold:
                    win = "*"

                print(
                    "Completed batch for sample {:5d} :: score = {:.3f} {}".format(
                        batch.info["sample"], genetic_score, win
                    )
                )

                self.q_out.put(
                    {
                        "bot_data": batch.bots[genetic_index].to_dict(),
                        "genetic_score": genetic_score,
                    }
                )

            self.q_out.put(None)
        except KeyboardInterrupt:
            print("Cancelled")
        return


class BatchWorkerIsolated(multiprocessing.Process):
    """Worker class for a single 'thread' - using isolated data."""

    def __init__(
        self,
        input_batch_data: List[Dict[str, Any]],
        q_out: multiprocessing.Queue,
        score_threshold: float,
    ) -> None:
        """
        Create new BatchWorker object.

        :param q_in: Queue of batches for input.
        :param q_out: Queue to output completed batches to.
        :param score_threshold: Maximum score to beat.
        """
        super().__init__()

        self.context = GameContext()

        self.input_data = input_batch_data
        self.q_out = q_out
        self.score_threshold = score_threshold
        return

    def run(self) -> None:
        """Run batches."""
        try:
            for batch_data in self.input_data:
                bots = []
                batch_config = batch_data.get("batch_config", {})
                bot_config = batch_config.get("bot_config", {})

                for bot_data in batch_data.get("bot_data", []):
                    bot = BotFactory(self.context, bot_config=bot_config).create_bot(
                        bot_data.get("name", "")
                    )
                    bot.from_dict(bot_data)
                    bots.append(bot)

                batch = Batch(bots, batch_config)

                genetic_index = batch_data.get("genetic_index", 0)
                batch_result = batch.run_batch()

                genetic_identity = batch.identities[genetic_index]
                genetic_score = batch_result.get_score(genetic_identity)

                win = ""
                if genetic_score > self.score_threshold:
                    win = "*"

                print(
                    "Completed batch for sample {:5d} :: score = {:.3f} {}".format(
                        batch_data.get("sample", 0), genetic_score, win
                    )
                )

                self.q_out.put(
                    {
                        "bot_data": batch.bots[genetic_index].to_dict(),
                        "genetic_score": genetic_score,
                    }
                )

            self.q_out.put(None)
        except KeyboardInterrupt:
            print("Cancelled")
        return
