"""Module for managing creation of bots."""

from typing import Any, Callable, Dict, List, Optional

import importlib
import inspect
import traceback

from lib.errors import BotCreateError
from lib.gameconfig import GameConfig
from lib.gamecontext import GameContext
from lib.gamefactory import GameFactory
from lib.gameplayer import GamePlayer
from lib.support.botdb import BotDB, ConnectionFailure

# Bots may store data in BOT_TEMP_PATH/<botname>/.
# This directory will be created by this module if necessary, the first time
# it is requested by the bot.
BOT_TEMP_PATH = "tempdata"


class BotFactory:
    """Manage creation of bots."""

    def __init__(self, context: GameContext, bot_config: Dict[str, Any]) -> None:
        """
        Create new BotFactory.

        :param context: The GameContext to use for logging.
        """
        self.context = context
        self.bot_config = bot_config
        self.bot_names = self.bot_config.get("bot_names", [])
        self.botdb = self.bot_config.get("botdb", False)
        self.bot_id = self.bot_config.get("bot_id")
        self.game = self.bot_config.get("game", "")
        return

    def _get_bot_class(self, module_name: str) -> Optional[Callable]:
        """Get the class name for the bot."""
        parts = module_name.split(".")
        game = ""
        module_basename = module_name
        if len(parts) > 1:
            game = parts[0]
            module_basename = parts[1]
            full_module_path = "games.{0}.bots.{1}.{1}".format(game, module_basename)
        else:
            full_module_path = "bots.{0}.{0}".format(module_name)

        try:
            module = importlib.import_module(full_module_path)
        except ImportError as e:
            raise BotCreateError(
                "Failed to import bot module '{}': {}".format(full_module_path, e)
            ) from e

        class_type = None
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                if name.lower() == module_basename.lower():
                    class_type = obj
                    break

        if not class_type:
            raise BotCreateError("Failed to find bot class matching: {}".format(module_basename))

        return class_type

    def create_bot(self, module_name: str) -> GamePlayer:
        """Create new bot object."""
        class_type = self._get_bot_class(module_name)
        assert class_type, "Invalid class"
        bot = self.create_bot_from_class(class_type)
        bot.name = module_name
        return bot

    def create_bot_from_class(self, class_type: Callable) -> GamePlayer:
        """Create new bot object from class."""
        bot_obj = class_type()
        return bot_obj

    def create_bots(self) -> List[GamePlayer]:
        """Create multiple bots, as per specified config."""
        gameclass = GameFactory(self.context).get_game_class(self.game)

        bots = []
        for bot_name in self.bot_names:
            bot_obj = self.create_bot(bot_name)
            if not bot_obj:
                raise BotCreateError("Error instantiating bot '{}'".format(bot_name))

            bot_obj.name = bot_name
            loaded = False
            if bot_obj.genetic and self.bot_id and self.botdb:
                try:
                    bot_data = BotDB().load_bot(self.bot_id)
                    if bot_data:
                        bot_obj.from_dict(bot_data.get("bot", {}))
                        self.context.log.info("Loaded bot: {} :: {}".format(bot_name, self.bot_id))
                        loaded = True
                    else:
                        self.context.log.warning("Bot '{}' not found".format(self.bot_id))
                except ConnectionFailure as e:
                    raise BotCreateError("Error connecting to MongoDB: {}".format(e)) from e

            if not loaded:
                bot_obj.create(game_info=gameclass.get_game_info())
            bots.append(bot_obj)
        return bots

    def clone_bots(self, existing_bots: List[GamePlayer]) -> List[GamePlayer]:
        """Clone the specified existing bots."""
        bots = []
        for i, bot_name in enumerate(self.bot_names):
            bot_obj = self.create_bot(bot_name)
            if not bot_obj:
                raise BotCreateError("Error instantiating bot '{}'".format(bot_name))

            bot_obj.name = bot_name
            bot_obj.from_dict(existing_bots[i].to_dict())
            bots.append(bot_obj)
        return bots
