"""Process batches for all samples."""

import multiprocessing
import time

from lib.batch import Batch
from lib.runners.genetic.batchworker import BatchWorker


class Processor:
    """Batch processor."""

    def __init__(self, context, bot, genetic_index):
        """Create a new Processor object."""
        self.context = context
        self.bot = bot
        self.genetic_index = genetic_index
        return

    def run(self, samples, generation_index, score_threshold):
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

            batch = Batch(parent_context=self.context, bots=bot_list)
            batch.label = "Gen {} - Sample {}".format(generation_index, index)
            batch.info = {
                'generation': generation_index,
                'sample': index,
                'index': self.genetic_index
            }

            avg_scores = batch.run_batch()

            genetic_score = avg_scores[self.genetic_index]
            batch.info['avg_scores'] = avg_scores
            batch.info['genetic_score'] = genetic_score
            batch.bots[self.genetic_index].score = genetic_score
            batch.info['bot_data'] = batch.bots[self.genetic_index].to_dict()

            win = ""
            if genetic_score > score_threshold:
                win = "*"

            print("Completed batch for sample {:5d} :: score = {:.3f} {}".
                  format(batch.info['sample'], genetic_score, win))

            yield batch
        return


class ProcessorMP(Processor):
    """Multi-process processor."""

    def __init__(self, context, bot, genetic_index):
        """Create ProcessorMP object."""
        super().__init__(context, bot, genetic_index)

        self.num_workers = multiprocessing.cpu_count() - 2
        if self.num_workers < 1:
            self.num_workers = 1

        self.context.log.info("Using {} threads...".format(self.num_workers))
        return

    def run(self, samples, generation_index, score_threshold):
        """
        Process the specified samples.

        This is also a generator, allowing for the processed batches to be
        collected as we go.
        """

        # Set up the batch queue and worker threads.
        q_in = multiprocessing.Queue()
        q_out = multiprocessing.Queue()
        workers = []

        # Start the workers before populating the queue.
        # This way they can get busy using other cores while we're
        # adding stuff to the queue.
        for _ in range(self.num_workers):
            worker = BatchWorker(q_in, q_out, score_threshold)
            worker.start()
            workers.append(worker)

        for index, sample in enumerate(samples):
            if self.genetic_index == 0:
                bot_list = [sample, self.bot]
            else:
                bot_list = [self.bot, sample]

            batch = Batch(parent_context=self.context, bots=bot_list)
            batch.label = "Gen {} - Sample {}".format(generation_index, index)
            batch.info = {
                'generation': generation_index,
                'sample': index,
                'index': self.genetic_index
            }
            q_in.put(batch)

        # Tell the workers to stop.
        for _ in range(len(workers)):
            q_in.put(None)

        workers_finished = 0
        while True:
            batch = q_out.get()
            if batch is None:
                workers_finished += 1
                if workers_finished >= len(workers):
                    break
                continue

            yield batch

        # Queue should now be empty.
        assert q_out.empty(), "Out queue is not empty!"

        for worker in workers:
            worker.join()

        return
