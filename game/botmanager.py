"""Module for managing creation of bots."""


import importlib
import traceback


from game.log import log_critical

# Path to bots.
BOT_BASE_PATH = 'bots'

# Bots may store data in BOT_TEMP_PATH/<botname>/.
# This directory will be created by this module if necessary, the first time
# it is requested by the bot.
BOT_TEMP_PATH = 'tempdata'


class BotManager(object):
    """Manage creation of bots"""

    def __init__(self):
        """Create new BotManager."""
        return

    def create_bot(self, module_name):
        """Create new bot object.

        Args:
            module_name: The name of the module to load.

        Returns:
            The bot object.

        """
        try:
            module = importlib.import_module("{0}.{1}.{1}".
                                             format(BOT_BASE_PATH, module_name))
        except ImportError as e:
            log_critical("Failed to import bot module '{0}.{1}.{1}': {2}".
                         format(BOT_BASE_PATH, module_name, e))
            log_critical(traceback.format_exc())
            return

        # It is expected that the class name will be the same as the module name,
        # but all uppercase.
        classname = module_name.upper()
        class_type = getattr(module, classname)
        bot_obj = class_type()
        bot_obj.set_temp_path_base(BOT_TEMP_PATH)

        return bot_obj

    def create_bots(self, config):
        """Create multiple bots, as per specified config."""

        bots = []
        for bot_name in (config['bot1'], config['bot2']):
            bot_obj = self.create_bot(bot_name)
            if (not bot_obj):
                log_critical("Error instantiating bot '{}'".format(bot_name))
                return

            bot_obj.name = bot_name
            bot_obj.create(config)
            bots.append(bot_obj)

        return bots
