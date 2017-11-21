"""
Maintain list of top bots ever produced by genetic algorithm.
"""

import copy
import json
import os


from lib.globals import log_error, log_warning


class TopBots:
    """Maintain top bots list."""

    def __init__(self, path):
        self.path = path
        self.topbots = []
        self.num_saved = 10
        return

    def load(self, botname):
        self.topbots = []
        fn = os.path.join(self.path, botname.lower())

        if (not os.path.exists(fn)):
            # No file for this bot.
            log_warning("No existing file for bot '{}'".format(botname))
            return

        with open(fn, 'rt') as f:
            try:
                self.topbots = json.load(f)
            except json.JSONDecodeError:
                log_error("Error decoding JSON for bot '{}'".format(botname))
        return

    def save(self, botname):
        fn = os.path.join(self.path, botname.lower())
        with open(fn, 'wt') as f:
            json.dump(self.topbots, f)
        return

    def check(self, botname, bot):
        """
        Check if the specified bot should go in the top 10.
        """

        self.load(botname)

        data_copy = copy.deepcopy(bot.to_dict())
        self.topbots.append(data_copy)
        self.sort_and_cull()

        if (data_copy in self.topbots):
            # This recipe made the cut.
            # Write file out to disk.
            self.save(botname)
            return True

        return False

    def sort_and_cull(self):
        sorted_bots = sorted(self.topbots, key=lambda x: x.get('score'),
                             reverse=True)
        self.topbots = sorted_bots[:self.num_saved]
        return

    def get_top_bot_data(self, botname):
        self.load(botname)
        self.sort_and_cull()
        return self.topbots
