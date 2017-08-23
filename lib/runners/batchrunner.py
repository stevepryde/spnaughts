"""Game Runner for a batch of games."""

import datetime
import os


from lib.batch import Batch
from lib.log import log_info
from lib.runners.gamerunnerbase import GameRunnerBase


class BatchRunner(GameRunnerBase):
    """Batch game runner."""

    def run(self):
        """Run a batch of games."""
        # Set up log.
        bots = self.bot_manager.create_bots()

        bot_name0 = bots[0].name
        bot_name1 = bots[1].name

        ts = str(datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S%f'))
        log_filename = os.path.join(self.config.log_base_dir,
                                    "single_batch_{}_{}_{}.log".
                                    format(bot_name0, bot_name1, ts))

        batch = Batch(self.config, bots)
        batch.run_batch()

        summary = batch.batch_summary
        log_info(summary)

        batch.write_to_file(log_filename)
        return
