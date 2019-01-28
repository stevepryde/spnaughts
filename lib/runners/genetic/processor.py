"""Process batches for all samples."""

import multiprocessing
import time
from typing import Any, Dict, Iterable, Iterator, List

from lib.batch import Batch
from lib.gamecontext import GameContext
from lib.gameplayer import GamePlayer
from lib.runners.genetic.batchworker import BatchWorker
from lib.globals import timer


class Processor:
    """Batch processor."""

    def __init__(
        self,
        context: GameContext,
        bot: GamePlayer,
        genetic_index: int,
        batch_config: Dict[str, Any],
    ):
        """Create a new Processor object."""
        self.context = context
        self.bot = bot
        self.batch_config = batch_config
        self.genetic_index = genetic_index
        return

    def run(
        self, samples: Iterable[GamePlayer], generation_index: int, score_threshold: float
    ) -> Iterator[Batch]:
        """
        Process the specified samples.

        This is also a generator, allowing for the processed batches to be
        collected as we go.
        """
        for index, sample in enumerate(samples):
            if self.genetic_index == 0:
                bot_list = [sample, self.bot]
            else:
                bot_list = [self.bot, sample]

            batch = Batch(bots=bot_list, batch_config=self.batch_config)
            batch.label = "Gen {} - Sample {}".format(generation_index, index)
            batch.info = {
                "generation": generation_index,
                "sample": index,
                "index": self.genetic_index,
            }

            batch_result = batch.run_batch()

            genetic_identity = batch.identities[self.genetic_index]
            genetic_score = batch_result.get_score(genetic_identity)
            batch.info["genetic_score"] = genetic_score
            batch.bots[self.genetic_index].score = genetic_score
            batch.info["bot_data"] = batch.bots[self.genetic_index].to_dict()

            win = ""
            if genetic_score > score_threshold:
                win = "*"

            print(
                "Completed batch for sample {:5d} :: score = {:.3f} {}".format(
                    batch.info["sample"], genetic_score, win
                )
            )

            yield batch
        return


class ProcessorMP(Processor):
    """Multi-process processor."""

    def __init__(
        self,
        context: GameContext,
        bot: GamePlayer,
        genetic_index: int,
        batch_config: Dict[str, Any],
    ) -> None:
        """Create ProcessorMP object."""
        super().__init__(context, bot, genetic_index, batch_config)

        self.num_workers = multiprocessing.cpu_count() - 2
        if self.num_workers < 1:
            self.num_workers = 1

        self.context.log.info("Using {} threads...".format(self.num_workers))
        return

    def run(
        self, samples: Iterable[GamePlayer], generation_index: int, score_threshold: float
    ) -> Iterator[Batch]:
        """
        Process the specified samples.

        This is also a generator, allowing for the processed batches to be
        collected as we go.
        """

        # Set up the batch queue and worker threads.
        workers = []
        worker_inputs = {}  # type: Dict[int, List[Batch]]
        q_out = multiprocessing.Queue()  # type: multiprocessing.Queue[Batch]

        for i in range(self.num_workers):
            worker_inputs[i] = []

        with timer("Generate batches"):
            for index, sample in enumerate(samples):
                if self.genetic_index == 0:
                    bot_list = [sample, self.bot]
                else:
                    bot_list = [self.bot, sample]

                batch = Batch(bots=bot_list, batch_config=self.batch_config)
                batch.label = "Gen {} - Sample {}".format(generation_index, index)
                batch.info = {
                    "generation": generation_index,
                    "sample": index,
                    "index": self.genetic_index,
                }

                qindex = index % self.num_workers
                worker_inputs[qindex].append(batch)

        with timer("Start workers"):
            for qid in range(self.num_workers):
                worker = BatchWorker(worker_inputs[qid], q_out, score_threshold)
                worker.start()
                workers.append(worker)

        with timer("Wait for workers"):
            workers_finished = 0
            while workers_finished < len(workers):
                batch = q_out.get()
                if batch is None:
                    workers_finished += 1
                    continue

                yield batch

        with timer("Join workers"):
            for worker in workers:
                worker.join()
        return

