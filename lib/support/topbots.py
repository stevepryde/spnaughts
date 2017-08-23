"""
Maintain list of top bots ever produced by genetic algorithm.
"""

import os


class TopBots:
    """Maintain top bots list."""

    def __init__(self, path):
        self.path = path

        # keys = botname, values = dict of scores keyed by recipe.
        self.topbots = {}
        self.num_saved = 10
        return

    def load(self, botname):
        key = botname.lower()
        fn = os.path.join(self.path, key)

        if (not os.path.exists(fn)):
            # No file for this bot.
            self.topbots[key] = {}
            return

        with open(fn, 'rt') as f:
            lines = f.read().split('\n')

        topdict = {}
        for line in lines:
            if (not line.strip()):
                continue

            parts = line.split('=', 1)
            try:
                topdict[parts[1].strip()] = float(parts[0])
            except TypeError:
                pass

        self.topbots[key] = topdict
        return

    def save(self, botname):
        key = botname.lower()
        recipes = self.topbots.get(key)
        if (not recipes or not isinstance(recipes, dict)):
            return

        sorted_keys = sorted(recipes, key=recipes.__getitem__, reverse=True)

        fn = os.path.join(self.path, key)
        with open(fn, 'wt') as f:
            for dkey in sorted_keys:
                f.write("{:.3f}={}\n".format(recipes[dkey], dkey))

        return

    def check(self, botname, recipe, score):
        """
        Check if the specified recipe should go in the top 10.
        """

        self.load(botname)

        # Easy way to do this is simply to add it to the dictionary, and then
        # sort the dictionary again and cull to top 10.
        key = botname.lower()
        botdict = self.topbots.get(key)
        if (not botdict):
            botdict = {}
            self.topbots[key] = botdict

        vals = botdict.values()
        if (vals):
            if (score <= min(vals) and len(botdict) >= self.num_saved):
                return False

        # Add this one to the dict.
        botdict[recipe] = score

        # Now sort and cull - this may drop a random one off the end.
        self.sort_and_cull(botname)

        if (recipe in self.topbots[key]):
            # This recipe made the cut.
            # Write file out to disk.
            self.save(botname)
            return True

        return False

    def sort_and_cull(self, botname):
        key = botname.lower()
        botdict = self.topbots.get(key)
        if (not botdict):
            return

        sorted_keys = sorted(botdict, key=botdict.__getitem__, reverse=True)

        newdict = {}
        for dkey in sorted_keys[:self.num_saved]:
            newdict[dkey] = botdict[dkey]

        self.topbots[key] = newdict
        return

    def get_top_recipe_list(self, botname):
        self.load(botname)

        key = botname.lower()
        botdict = self.topbots.get(key)
        if (not botdict):
            return []

        sorted_keys = sorted(botdict, key=botdict.__getitem__, reverse=True)
        return sorted_keys
