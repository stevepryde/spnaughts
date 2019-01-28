"""Base class for a generic game runner."""

import os

from lib.gameconfig import GameConfig
from lib.gamecontext import GameContext
from lib.support.pathmaker import get_unique_dir


class GameRunnerBase(GameContext):
    """Game Runner object."""

    def __init__(self, config: GameConfig) -> None:
        """Create new GameRunnerBase object."""
        super().__init__()
        self.config = config
        classname = self.__class__.__name__.lower()
        prefix = "{}_{}_{}_".format(classname, self.config.bot1, self.config.bot2)
        self.path = get_unique_dir(base_path=config.log_base_dir, prefix=prefix)
        self.log.log_to_console()
        self.log.log_to_file(filename=os.path.join(self.path, "game.log"))
        self.log.set_as_default()
        return

    def run(self) -> None:
        """Run one or more games using this Game Runner."""
        return
