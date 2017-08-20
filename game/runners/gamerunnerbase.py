"""Base class for a generic game runner."""

from game.botmanager import BotManager


class GameRunnerBase:
    """Game Runner object."""

    def __init__(self, config):
        """Create new GameRunnerBase object."""
        self.config = config
        self.bot_manager = BotManager(self.config)
        return

    def run(self):
        """Run one or more games using this Game Runner."""
        return
