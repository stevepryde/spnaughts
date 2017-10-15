"""Base class for a generic game runner."""

from lib.botmanager import BotManager
from lib.gamecontext import GameContext
from lib.globals import get_config


class GameRunnerBase(GameContext):
    """Game Runner object."""

    def __init__(self):
        """Create new GameRunnerBase object."""
        config = get_config()
        classname = self.__class__.__name__.lower()
        prefix = "{}_{}_{}_".format(classname, config.bot1, config.bot2)
        super().__init__(parent_context=None, subdir_prefix=prefix)
        self.enable_file_logging()
        self.log.set_as_default()
        self.bot_manager = BotManager(self)
        return

    def run(self):
        """Run one or more games using this Game Runner."""
        return
