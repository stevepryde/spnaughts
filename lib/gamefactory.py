"""Module for managing creation of games."""

from typing import Callable, List, Optional, Type

import importlib
import traceback

from lib.errors import GameCreateError
from lib.gamebase import GameBase
from lib.gamecontext import GameContext
from lib.gameplayer import GamePlayer


class GameFactory:
    """Manage creation of games."""

    def __init__(self, context: GameContext) -> None:
        """
        Create new GameFactory.

        :param context: The GameContext to use for logging.
        """
        self.context = context
        return

    def get_game_class(self, game: str) -> Type[GameBase]:
        """Get the class for the SingleGame object for the game type."""
        module_name = "games.{}.singlegame".format(game)
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            raise GameCreateError(
                "Failed to import game module '{}': {}".format(module_name, e)
            ) from e

        class_ = getattr(module, "SingleGame")
        return class_

    def get_game_obj(self, game: str) -> GameBase:
        """Get a new instance of the SingleGame object for the game type."""
        class_ = self.get_game_class(game)
        return class_()
