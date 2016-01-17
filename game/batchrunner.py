################################################################################
# SP Naughts - Simple naughts and crosses game including a collection of AI bots
# Copyright (C) 2015, 2016 Steve Pryde
#
# This file is part of SP Naughts.
#
# SP Naughts is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SP Naughts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SP Naughts.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
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
