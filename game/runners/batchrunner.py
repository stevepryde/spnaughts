"""Game Runner for a batch of games."""

import datetime
import os

from game.runners.gamerunnerbase import GameRunnerBase
from game.batch import Batch


class BatchRunner(GameRunnerBase):
    """Batch game runner."""

    def run(self, config, bots):
        """Run a batch of games."""
        # Set up log.
        log_base_dir = config['log_base_dir']

        bot_name0 = bots[0].name
        bot_name1 = bots[1].name

        ts = str(datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S%f'))
        log_filename = os.path.join(log_base_dir, "single_batch_{}_{}_{}.log".
                                    format(bot_name0, bot_name1, ts))

        batch = Batch(config, bots)
        batch.run_batch()

        summary = batch.batch_summary
        print(summary)

        batch.write_to_file(log_filename)
        return
