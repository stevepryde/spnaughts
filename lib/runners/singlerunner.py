"""Game runner for a single game."""


import random


from lib.runners.gamerunnerbase import GameRunnerBase


class SingleRunner(GameRunnerBase):
    """Game Runner for a single game."""

    def __init__(self):
        """Create a new SingleRunner object."""
        super().__init__()
        self.enable_console_logging()
        return

    def run(self):
        """Run a single game."""
        bots = self.bot_manager.create_bots()
        class_ = self.config.get_game_class()
        for index, identity in enumerate(class_.identities):
            bots[index].clear_score()
            bots[index].identity = identity

        # random.seed(1)
        game_obj = self.config.get_game_obj(self)
        game_obj.enable_file_logging()
        game_obj.run(bots)
        return
