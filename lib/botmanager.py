"""Module for managing creation of bots."""

from typing import Callable, List, Optional

import importlib
import traceback

from lib.gamecontext import GameContext
from lib.gameplayer import GamePlayer
from lib.globals import get_config
from lib.support.botdb import BotDB

# Bots may store data in BOT_TEMP_PATH/<botname>/.
# This directory will be created by this module if necessary, the first time
# it is requested by the bot.
BOT_TEMP_PATH = "tempdata"


class BotManager:
    """Manage creation of bots."""

    def __init__(self, context: GameContext) -> None:
        """
        Create new BotManager.

        :param context: The GameContext to use as the bots' parent context.
        """
        self.context = context
        return

    def get_bot_class(self, module_name: str) -> Optional[Callable]:
        """Get the class name for the bot."""
        config = get_config()
        full_module_path = "games.{0}.bots.{1}.{1}".format(config.game, module_name)
        try:
            module = importlib.import_module(full_module_path)
        except ImportError as e:
            self.context.log.critical(
                "Failed to import bot module '{}': {}".format(full_module_path, e)
            )
            self.context.log.critical(traceback.format_exc())
            return None

        # It is expected that the class name will be the same as the module
        # name, but all uppercase.
        classname = module_name.upper()
        class_type = getattr(module, classname)
        return class_type

    def create_bot(self, module_name: str) -> GamePlayer:
        """Create new bot object."""
        class_type = self.get_bot_class(module_name)
        assert class_type, "Invalid class"
        return self.create_bot_from_class(class_type)

    def create_bot_from_class(self, class_type: Callable) -> GamePlayer:
        """Create new bot object from class."""
        bot_obj = class_type(self.context)
        bot_obj.set_temp_path_base(BOT_TEMP_PATH)
        return bot_obj

    def create_bots(self) -> List[GamePlayer]:
        """Create multiple bots, as per specified config."""
        config = get_config()
        bots = []
        for bot_name in (config.bot1, config.bot2):
            bot_obj = self.create_bot(bot_name)
            if not bot_obj:
                self.context.log.critical("Error instantiating bot '{}'".format(bot_name))
                return []

            bot_obj.name = bot_name

            loaded = False
            if bot_obj.genetic and config.bot_id:
                bot_data = BotDB().load_bot(config.bot_id)
                if bot_data:
                    bot_obj.from_dict(bot_data.get("bot", {}))
                    self.context.log.info("Loaded bot: {} :: {}".format(bot_name, config.bot_id))
                    loaded = True

            if not loaded:
                bot_obj.create()
            bots.append(bot_obj)

        return bots
