"""Worker process for running batches from a queue."""

import multiprocessing
import time
from typing import List

from lib.batch import Batch


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
                avg_scores = batch.run_batch()
                genetic_score = avg_scores[genetic_index]

                batch.info["avg_scores"] = avg_scores
                batch.info["genetic_score"] = genetic_score
                batch.bots[genetic_index].score = genetic_score
                batch.info["bot_data"] = batch.bots[genetic_index].to_dict()

                win = ""
                if genetic_score > self.score_threshold:
                    win = "*"

                print(
                    "Completed batch for sample {:5d} :: score = {:.3f} {}".format(
                        batch.info["sample"], genetic_score, win
                    )
                )

                self.q_out.put(batch)

            self.q_out.put(None)
        except KeyboardInterrupt:
            print("Cancelled")
        return
