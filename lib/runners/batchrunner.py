"""Game Runner for a batch of games."""

from lib.batch import Batch
from lib.runners.gamerunnerbase import GameRunnerBase


class BatchRunner(GameRunnerBase):
    """Batch game runner."""

    def __init__(self):
        """Create a new BatchRunner object."""
        super().__init__()
        self.enable_console_logging()
        return

    def run(self):
        """Run a batch of games."""
        # Set up log.
        bots = self.bot_manager.create_bots()
        batch = Batch(parent_context=self, bots=bots)
        batch.run_batch()
        return
