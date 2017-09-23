"""Game Runner for a batch of games."""

import datetime
import os


from lib.batch import Batch
from lib.globals import log_info
from lib.runners.gamerunnerbase import GameRunnerBase


class BatchRunner(GameRunnerBase):
    """Batch game runner."""

    def run(self):
        """Run a batch of games."""
        # Set up log.
        bots = self.bot_manager.create_bots()
        batch = Batch(parent_context=self, bots=bots)
        batch.run_batch()
        return
