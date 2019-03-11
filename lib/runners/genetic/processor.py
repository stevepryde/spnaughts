"""Process batches for all samples."""

import multiprocessing
import time
from typing import Any, Dict, Iterable, Iterator, List, Optional

from lib.batch import Batch
from lib.gamecontext import GameContext
from lib.gameplayer import GamePlayer
from lib.runners.genetic.batchworker import BatchWorker, BatchWorkerIsolated
from .rabbit import RabbitManager


class Processor:
    """Batch processor."""

    def __init__(
        self,
        context: GameContext,
        other_bot: GamePlayer,
        genetic_index: int,
        batch_config: Dict[str, Any],
        rabbit: Optional[RabbitManager] = None,
    ):
        """Create a new Processor object."""
        self.context = context
        self.other_bot = other_bot
        self.batch_config = batch_config
        self.genetic_index = genetic_index
        self.rabbit = rabbit
        return

    def run(
        self, samples: Iterable[GamePlayer], generation_index: int, score_threshold: float
    ) -> Iterator[Dict[str, Any]]:
        """
        Process the specified samples.

        This is also a generator, allowing for the processed batches to be
        collected as we go.
        """
        for index, sample in enumerate(samples):
            if self.genetic_index == 0:
                bot_list = [sample, self.other_bot]
            else:
                bot_list = [self.other_bot, sample]

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

            yield {
                "bot_data": batch.bots[self.genetic_index].to_dict(),
                "genetic_score": genetic_score,
                "sample": index,
            }
        return


class ProcessorMP(Processor):
    """Multi-process processor."""

    def __init__(
        self,
        context: GameContext,
        other_bot: GamePlayer,
        genetic_index: int,
        batch_config: Dict[str, Any],
    ) -> None:
        """Create ProcessorMP object."""
        super().__init__(context, other_bot, genetic_index, batch_config)

        self.num_workers = multiprocessing.cpu_count() - 2
        if self.num_workers < 1:
            self.num_workers = 1

        self.context.log.info("Using {} threads...".format(self.num_workers))
        return

    def run(
        self, samples: Iterable[GamePlayer], generation_index: int, score_threshold: float
    ) -> Iterator[Dict[str, Any]]:
        """
        Process the specified samples.

        This is also a generator, allowing for the processed batches to be
        collected as we go.
        """

        # Set up the batch queue and worker threads.
        workers = []
        worker_inputs = {}  # type: Dict[int, List[Batch]]
        q_out = multiprocessing.Queue()  # type: multiprocessing.Queue[Dict[str, Any]]

        for i in range(self.num_workers):
            worker_inputs[i] = []

        for index, sample in enumerate(samples):
            if self.genetic_index == 0:
                bot_list = [sample, self.other_bot]
            else:
                bot_list = [self.other_bot, sample]

            qindex = index % self.num_workers

            batch = Batch(bots=bot_list, batch_config=self.batch_config)
            batch.label = "Gen {} - Sample {}".format(generation_index, index)
            batch.info = {
                "generation": generation_index,
                "sample": index,
                "index": self.genetic_index,
            }

            qindex = index % self.num_workers
            worker_inputs[qindex].append(batch)

        for qid in range(self.num_workers):
            worker = BatchWorker(worker_inputs[qid], q_out, score_threshold)
            worker.start()
            workers.append(worker)

        workers_finished = 0
        while workers_finished < len(workers):
            batch_result = q_out.get()
            if batch_result is None:
                workers_finished += 1
                continue

            yield batch_result

        for worker in workers:
            worker.join()
        return


class ProcessorRabbit(Processor):
    """
    RabbitMQ batch distributor.

    This one places batches onto the queue and waits for their responses.
    """

    def run(
        self, samples: Iterable[GamePlayer], generation_index: int, score_threshold: float
    ) -> Iterator[Dict[str, Any]]:
        """
        Process the specified samples by farming them out to rabbitmq.

        This is also a generator, allowing for the processed batches to be
        collected as we go.
        """
        assert self.rabbit, "RabbitManager not set!"

        game_id = self.batch_config.get("game_id", "test")
        qid = "{}-{}".format(game_id, generation_index)
        self.rabbit.create_output_queue(qid=qid)

        count = 0
        for index, sample in enumerate(samples):
            if self.genetic_index == 0:
                bot_list = [sample, self.other_bot]
            else:
                bot_list = [self.other_bot, sample]

            self.rabbit.put_on_batch_queue(
                {
                    "qid": qid,
                    "bot_data": [x.to_dict() for x in bot_list],
                    "genetic_index": self.genetic_index,
                    "batch_config": self.batch_config,
                    "score_threshold": score_threshold,
                    "sample": index,
                }
            )
            count += 1

        for _ in range(count):
            result = None
            # How long should 1 result take?
            timeout = time.monotonic() + 60
            while time.monotonic() < timeout:
                result = self.rabbit.get_from_output_queue(qid=qid)
                if not result:
                    time.sleep(0.5)
                    continue
                break

            if not result:
                raise TimeoutError("Timed out waiting for batch results")

            tag, body = result
            yield body
            self.rabbit.done_message(tag)
        return

