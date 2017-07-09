"""Game runner for a single game."""


import datetime
import os


from game.log import log_error
from game.runners.gamerunnerbase import GameRunnerBase
from game.singlegame import SingleGame


class SingleRunner(GameRunnerBase):
    """Game Runner for a single game."""

    def run(self, config, bots):
        """Run a single game."""
        # Run a single batch.
        for index, identity in enumerate(['X', 'O']):
            bots[index].clear_score()
            bots[index].identity = identity

        # Set up log.
        log_base_dir = config['log_base_dir']

        bot_name0 = bots[0].name
        bot_name1 = bots[1].name

        ts = str(datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S%f'))
        game_log_path = os.path.join(log_base_dir, "single_game_{}_{}_{}.log".
                                     format(bot_name0, bot_name1, ts))

        game_obj = SingleGame()
        game_info = game_obj.run(config, bots)
        if game_info is None:
            return

        # Since 'silent' is always False for this runner, the game log will
        # already have been output, so just write the game log to a new file.
        try:
            with open(game_log_path, 'wt') as game_log_file:
                game_log_file.write(game_obj.game_log)
        except IOError as e:
            log_error("Error writing game log file '{}': {}".
                      format(game_log_path, str(e)))
        return
