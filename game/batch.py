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

import collections
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

    # Init details used during the running of the batch:
    self.start_batch()

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

  def write_to_file(self, filename):
    summary    = self.get_batch_summary()
    log_output = self.get_batch_log()

    try:
      batch_log_file = open(filename, 'wb')
      batch_log_file.write(bytes(summary, 'UTF8'))
      batch_log_file.write(bytes("\n\nFULL LOG:\n", 'UTF8'))
      batch_log_file.write(bytes(log_output, 'UTF8'))
      batch_log_file.close()

    except Exception as e:
      log_error("Error writing batch log file '{}': {}".
                format(filename, str(e)))

    return

  def run_batch(self):

    self.start_batch()

    # Run the batch, either using the normal batch runner or the 'magic' one,
    # depending on the 'num_games' setting.
    if (self.config['num_games'] == 0):
      self.run_magic_batch()
    else:
      self.run_normal_batch()

    average_scores = self.process_batch_result()

    return average_scores

  def start_batch(self):
    # Run a single batch.
    self.robots[0].clear_score()
    self.robots[1].clear_score()

    # Setup robots.
    self.robots[0].set_identity('X')
    self.robots[1].set_identity('O')

    self.overall_results = {1:0,2:0,3:0}
    self.num_games_played = 0
    self.total_score = {'X':0,'O':0}

    return

  def process_game_result(self, game_num, game_info):
    result = game_info['result']

    self.num_games_played += 1
    self.total_score['X'] += game_info['scores']['X']
    self.total_score['O'] += game_info['scores']['O']

    if (result == 1):
      self.log_summary("Game {}: '{}' WINS".
                       format(game_num, self.robots[0].get_name()))
      if ('stoponloss' in self.config and self.config['stoponloss'] == 'O'):
        self.log_summary("Stopping because O lost a game and " +
                           "--stoponloss O was specified")
        return
    elif (result == 2):
      self.log_summary("Game {}: '{}' WINS".
                       format(game_num, self.robots[1].get_name()))
      if ('stoponloss' in self.config and self.config['stoponloss'] == 'X'):
        self.log_summary("Stopping because X lost a game and " +
                           "--stoponloss X was specified")
        return
    elif (result == 3):
      self.log_summary("Game {}: TIE".format(game_num))
    else:
      log_error("Invalid result received: '{}'".format(result))
      return

    if (result not in self.overall_results):
      log_error("No record of {} in overall_results".format(result))
      return
    else:
      self.overall_results[result] += 1

    return

  def process_batch_result(self):

    # Print overall results.
    self.log_summary("\nRESULTS:")
    self.log_summary("Games Played: {}".format(self.num_games_played))
    self.log_summary("")
    self.log_summary("'{}' WINS: {}".format(self.robots[0].get_name(),
                     self.overall_results[1]))
    self.log_summary("'{}' WINS: {}".format(self.robots[1].get_name(),
                     self.overall_results[2]))
    self.log_summary("DRAW/TIE: {}".format(self.overall_results[3]))
    self.log_summary("")

    # Get average scores.
    if (self.num_games_played > 0):
      avg_score_X = float(self.total_score['X'] / self.num_games_played)
      avg_score_O = float(self.total_score['O'] / self.num_games_played)

      self.robots[0].set_score(avg_score_X)
      self.robots[1].set_score(avg_score_O)

      self.log_batch("\nAverage Scores: '{}':{:.2f} , '{}':{:.2f}".
                     format(self.robots[0].get_name(), avg_score_X,
                            self.robots[1].get_name(), avg_score_O))

      self.log_summary("AVERAGE SCORES:\n'{}':{:.2f}\n'{}':{:.2f}".
                       format(self.robots[0].get_name(), avg_score_X,
                              self.robots[1].get_name(), avg_score_O))

    return [avg_score_X, avg_score_O]

  def run_normal_batch(self):
    """
    This is the normal batch runner that just runs a batch of n games.
    """

    for game_num in range(1, self.config['num_games'] + 1):
      self.log_batch("\n********** Running game {} **********\n".
                     format(game_num))

      game_obj  = game.singlegame.SINGLEGAME()
      game_info = game_obj.run(self.config, self.robots)
      if (game_info == None):
        log_error("Game {} failed!".format(game_num))
        return

      game_log = game_obj.get_game_log()
      self.log_batch(game_log)

      self.process_game_result(game_num, game_info)

    return

  def run_magic_batch(self):
    """
    This is a pseudo-batch that actually runs every possible combination of
    moves against the target bot.
    """

    game_num = 0
    game_obj_initial = game.singlegame.SINGLEGAME()
    game_obj_initial.start(self.config, self.robots)

    game_queue = collections.deque()
    game_queue.append(game_obj_initial)

    try:
      while(True):
        game_obj  = game_queue.popleft()
        new_games = game_obj.do_turn()

        if (len(new_games) == 0):
          log_error("No cloned games returned from do_turn() when running " +
                      "magic batch")
          break

        for new_game_obj in new_games:
          if (new_game_obj.is_ended()):
            # A game has finished, so process the result...
            game_num += 1
            game_info = new_game_obj.get_game_info()
            if (game_info == None):
              log_error("Game {} failed!".format(game_num))
              return

            game_log = new_game_obj.get_game_log()
            self.log_batch(game_log)

            self.process_game_result(game_num, game_info)
          else:
            # This game has not yet finished, so add it to the end of the queue.
            game_queue.append(new_game_obj)
    except IndexError:
      # All games should have been run to completion.
      pass

    return

