"""Module for managing creation of bots."""


import importlib
import traceback


from lib.log import log_critical

# Bots may store data in BOT_TEMP_PATH/<botname>/.
# This directory will be created by this module if necessary, the first time
# it is requested by the bot.
BOT_TEMP_PATH = 'tempdata'


class BotManager(object):
    """Manage creation of bots."""

    def __init__(self, config):
        """Create new BotManager."""
        self.config = config
        return

    def create_bot(self, module_name):
        """Create new bot object."""
        full_module_path = "games.{0}.bots.{1}.{1}".format(self.config.game,
                                                           module_name)
        try:
            module = importlib.import_module(full_module_path)
        except ImportError as e:
            log_critical("Failed to import bot module '{}': {}".
                         format(full_module_path, e))
            log_critical(traceback.format_exc())
            return

        # It is expected that the class name will be the same as the module
        # name, but all uppercase.
        classname = module_name.upper()
        class_type = getattr(module, classname)
        bot_obj = class_type(self.config)
        bot_obj.set_temp_path_base(BOT_TEMP_PATH)
        return bot_obj

    def create_bots(self):
        """Create multiple bots, as per specified config."""
        bots = []
        for bot_name in (self.config.bot1, self.config.bot2):
            bot_obj = self.create_bot(bot_name)
            if not bot_obj:
                log_critical("Error instantiating bot '{}'".format(bot_name))
                return

            bot_obj.name = bot_name
            bot_obj.create()
            bots.append(bot_obj)

        return bots
