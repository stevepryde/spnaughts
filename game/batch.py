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
# batch.py
#
# Run a batch of games.

import game.singlegame
from game.log import *

class BATCH(object):
  def __init__(self, config, robots):
    self.batch_log_lines = []
    self.batch_summary_lines = []
    self.config = config
    self.robots = robots
    self.label = ""
    self.batch_info = {}
    return

  def set_label(self, _label):
    self.label = _label
    return

  def set_batch_info(self, info):
    self.batch_info = info
    return

  def get_batch_info(self):
    return self.batch_info

  def get_batch_log(self):
    return "\n".join(self.batch_log_lines)

  def get_batch_summary(self):
    return "\n".join(self.batch_summary_lines)

  def log_batch(self, message):
    self.batch_log_lines.append(message)
    return

  def log_summary(self, message):
    self.batch_summary_lines.append(message)
    return

  def run_batch(self):
    config = self.config
    robots = self.robots

    # Run a single batch.
    robots[0].clear_score()
    robots[1].clear_score()

    # Setup robots.
    robots[0].set_identity('X')
    robots[1].set_identity('O')

    overall_results = {1:0,2:0,3:0}
    num_games_played = 0
    total_score = {'X':0,'O':0}
    for game_num in range(1, config['num_games'] + 1):
      self.log_batch("\n********** Running game {} **********\n".
                     format(game_num))

      game_obj = game.singlegame.SINGLEGAME()
      game_info = game_obj.run(config, robots)
      if (game_info == None):
        log_error("Game {} failed!".format(game_num))
        return

      game_log = game_obj.get_game_log()
      self.log_batch(game_log)
      result = game_info['result']

      num_games_played += 1
      total_score['X'] += game_info['scores']['X']
      total_score['O'] += game_info['scores']['O']

      if (result == 1):
        self.log_summary("Game {}: '{}' WINS".
                         format(game_num, robots[0].get_name()))
        if ('stoponloss' in config and config['stoponloss'] == 'O'):
          self.log_summary("Stopping because O lost a game and " +
                             "--stoponloss O was specified")
          return
      elif (result == 2):
        self.log_summary("Game {}: '{}' WINS".
                         format(game_num, robots[1].get_name()))
        if ('stoponloss' in config and config['stoponloss'] == 'X'):
          self.log_summary("Stopping because X lost a game and " +
                             "--stoponloss X was specified")
          return
      elif (result == 3):
        self.log_summary("Game {}: TIE".format(game_num))
      else:
        log_error("Invalid result received: '{}'".format(result))
        return

      if (result not in overall_results):
        log_error("No record of {} in overall_results".format(result))
        return
      else:
        overall_results[result] += 1

    # Print overall results.
    self.log_summary("\nRESULTS:")
    self.log_summary("'{}' WINS: {}".format(robots[0].get_name(), overall_results[1]))
    self.log_summary("'{}' WINS: {}".format(robots[1].get_name(), overall_results[2]))
    self.log_summary("DRAW/TIE: {}".format(overall_results[3]))

    # Get average scores.
    if (num_games_played > 0):
      avg_score_X = float(total_score['X'] / num_games_played)
      avg_score_O = float(total_score['O'] / num_games_played)

      robots[0].set_score(avg_score_X)
      robots[1].set_score(avg_score_O)

      self.log_batch("\nAverage Scores: '{}':{:.2f} , '{}':{:.2f}".
                     format(robots[0].get_name(), avg_score_X,
                            robots[1].get_name(), avg_score_O))

      self.log_summary("AVERAGE SCORES:\n'{}':{:.2f}\n'{}':{:.2f}".
                       format(robots[0].get_name(), avg_score_X,
                              robots[1].get_name(), avg_score_O))

    return [avg_score_X, avg_score_O]
