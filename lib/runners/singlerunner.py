"""Game runner for a single game."""


import random


from lib.runners.gamerunnerbase import GameRunnerBase
from lib.botfactory import BotFactory
from lib.gamefactory import GameFactory


class SingleRunner(GameRunnerBase):
    """Game Runner for a single game."""

    def run(self) -> None:
        """Run a single game."""
        bots = BotFactory(context=self, bot_config=self.config.get_bot_config()).create_bots()

        game_obj = GameFactory(self).get_game_obj(self.config.game)
        game_obj.set_initial_state()
        game_obj.start(bots)
        result = game_obj.run()
        self.log.info(str(result))
        return
