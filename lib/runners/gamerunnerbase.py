"""Base class for a generic game runner."""

from lib.botmanager import BotManager
from lib.gamecontext import GameContext
from lib.globals import get_config


class GameRunnerBase(GameContext):
    """Game Runner object."""

    def __init__(self) -> None:
        """Create new GameRunnerBase object."""
        super().__init__(parent_context=None)
        classname = self.__class__.__name__.lower()
        prefix = "{}_{}_{}_".format(classname, self.config.bot1, self.config.bot2)
        self.enable_file_logging(subdir_prefix=prefix)
        self.log.set_as_default()
        self.bot_manager = BotManager(self)
        return

    def run(self) -> None:
        """Run one or more games using this Game Runner."""
        return
