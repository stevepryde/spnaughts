# batchrunner.py
#
# Game runner for running a single batch.

from game.gamerunnerbase import GAMERUNNERBASE
import game.batch
from game.log import *

class BATCHRUNNER(GAMERUNNERBASE):
  def run(self, config, robots):
    # Set up log.
    log_base_dir = config['log_base_dir']

    robot_name0   = robots[0].name
    robot_name1   = robots[1].name

    ts            = str(datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S%f'))
    game_log_path = os.path.join(log_base_dir, "single_batch_" + robot_name0 +
                                 "_" + robot_name1 + "_" + ts + ".log")

    batch = game.batch.BATCH(config, robots)
    batch.run_batch()

    summary = batch.get_batch_summary()
    print(summary)

    # Write batch log to a file.
    try:
      game_log_file = open(game_log_path, 'wb')
      game_log_file.write(bytes(summary, 'UTF8'))
      game_log_file.write(bytes("\n\nFULL LOG:\n", 'UTF8'))
      game_log_file.write(bytes(batch.get_batch_log(), 'UTF8'))
      game_log_file.close()

    except Exception as e:
      log_error("Error writing game log file '{}': {}".
                format(game_log_path, str(e)))

    return
