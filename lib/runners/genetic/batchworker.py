"""Worker process for running batches from a queue."""

import multiprocessing


class BatchWorker(multiprocessing.Process):
    """Worker class for a single 'thread'."""

    def __init__(self, batch_queue, score_threshold):
        """
        Create new BatchWorker object.

        :param batch_queue: collections.deque() object containing batches to
            run.
        :param score_threshold: Maximum score to beat.
        """
        super().__init__()

        self.batch_queue = batch_queue
        self.manager = multiprocessing.Manager()
        self.scores = self.manager.dict()
        self.score_threshold = score_threshold
        return

    def run(self):
        """Run batches until the queue is empty."""
        try:
            while True:
                batch = self.batch_queue.get()

                # The game runner signals the end of the queue by enqueuing
                # 'None'.
                if batch is None:
                    break

                info = batch.batch_info
                batch_scores = batch.run_batch()
                if batch_scores is not None:
                    self.scores[info['sample']] = batch_scores

                win = ""
                score = batch_scores[info['index']]
                if score > self.score_threshold:
                    win = "*"

                print("Completed batch for sample {:5d} :: score = {:.3f} {}".
                      format(info['sample'], score, win))

                self.batch_queue.task_done()
        except KeyboardInterrupt:
            print("Cancelled")
        return
