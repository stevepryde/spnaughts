"""Worker process for running batches from a queue."""

import multiprocessing
import os


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
                sample = info['sample']
                gen = info['generation']
                log_path = info['log_path']
                bot_index = info['index']

                batch_scores = batch.run_batch()
                if batch_scores is not None:
                    self.scores[sample] = batch_scores

                if batch.config.log_games:
                    # Write batch log to a file.
                    gen_path = os.path.join(log_path, "Gen{}".format(gen))
                    sample_log_path = os.path.join(gen_path,
                                                   "sample_{}_batch_log.log".
                                                   format(sample))

                    try:
                        os.makedirs(gen_path, exist_ok=True)
                        batch.write_to_file(sample_log_path)
                    except OSError as e:
                        print("Error creating batch log path '{}': {}".
                              format(gen_path, str(e)))

                win = ""
                score = batch_scores[bot_index]
                if score > self.score_threshold:
                    win = "*"

                print("Completed batch for sample {:5d} :: score = {:.3f} {}".
                      format(sample, score, win))

                self.batch_queue.task_done()
        except KeyboardInterrupt:
            print("Cancelled")
        return
