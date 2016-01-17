# singlerunner.py
#
# Handle running of a single game.

import datetime
from game.gamerunnerbase import GAMERUNNERBASE
from game.log import *
import game.singlegame

class SINGLERUNNER(GAMERUNNERBASE):
  def run(self, config, robots):
    config['silent'] = False

    # Run a single batch.
    robots[0].clear_score()
    robots[1].clear_score()

    # Setup robots.
    robots[0].set_identity('X')
    robots[1].set_identity('O')

    # Set up log.
    log_base_dir = config['log_base_dir']

    robot_name0   = robots[0].name
    robot_name1   = robots[1].name

    ts            = str(datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S%f'))
    game_log_path = os.path.join(log_base_dir, "single_game_" + robot_name0 +
                                 "_" + robot_name1 + "_" + ts + ".log")

    game_obj = game.singlegame.SINGLEGAME()
    game_info = game_obj.run(config, robots)
    if (game_info == None):
      return

    # Since 'silent' is always False for this runner, the game log will already
    # have been output, so just write the game log to a new file.

    try:
      game_log_file = open(game_log_path, 'wb')
      game_log_file.write(bytes(game_obj.get_game_log(), 'UTF8'))
      game_log_file.close()

    except Exception as e:
      log_error("Error writing game log file '{}': {}".
                format(game_log_path, str(e)))

    return

