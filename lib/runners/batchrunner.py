"""Game Runner for a batch of games."""

from lib.batch import Batch
from lib.botfactory import BotFactory
from lib.runners.gamerunnerbase import GameRunnerBase


class BatchRunner(GameRunnerBase):
    """Batch game runner."""

    def run(self) -> None:
        """Run a batch of games."""
        # Set up log.
        bots = BotFactory(context=self, bot_config=self.config.get_bot_config()).create_bots()

        batch = Batch(bots=bots, batch_config=self.config.get_batch_config())
        batch.log.log_to_console()
        batch.run_batch()
        return
