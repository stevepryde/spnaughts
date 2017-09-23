"""Module for managing creation of bots."""


import importlib
import traceback

from lib.globals import get_config

# Bots may store data in BOT_TEMP_PATH/<botname>/.
# This directory will be created by this module if necessary, the first time
# it is requested by the bot.
BOT_TEMP_PATH = 'tempdata'


class BotManager:
    """Manage creation of bots."""

    def __init__(self, context):
        """
        Create new BotManager.

        :param context: The GameContext to use as the bots' parent context.
        """
        self.context = context
        return

    def create_bot(self, module_name):
        """Create new bot object."""
        config = get_config()
        full_module_path = "games.{0}.bots.{1}.{1}".format(config.game,
                                                           module_name)
        try:
            module = importlib.import_module(full_module_path)
        except ImportError as e:
            self.context.log.critical("Failed to import bot module '{}': {}".
                                      format(full_module_path, e))
            self.context.log.critical(traceback.format_exc())
            return

        # It is expected that the class name will be the same as the module
        # name, but all uppercase.
        classname = module_name.upper()
        class_type = getattr(module, classname)
        bot_obj = class_type(self.context)
        bot_obj.set_temp_path_base(BOT_TEMP_PATH)
        return bot_obj

    def create_bots(self):
        """Create multiple bots, as per specified config."""
        config = get_config()
        bots = []
        for bot_name in (config.bot1, config.bot2):
            bot_obj = self.create_bot(bot_name)
            if not bot_obj:
                self.context.log.critical(
                    "Error instantiating bot '{}'".format(bot_name))
                return

            bot_obj.name = bot_name
            bot_obj.create()
            bots.append(bot_obj)

        return bots
