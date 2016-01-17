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
# singlegame.py
#
# This class is used to run a single game of naughts and crosses and return some
# information about the game.

from game.log import *
import game.board as board

class SINGLEGAME(object):
  def __init__(self):
    self.game_log_lines = []
    self.config = None
    return

  def get_game_log(self):
    return "\n".join(self.game_log_lines)

  def log_game(self, message):
    if (self.config and
        (('silent' not in self.config) or (not self.config['silent']))):
      print(message)

    self.game_log_lines.append(message)
    return

  def run(self, config, robots):
    self.config = config

    for robot in robots:
      robot.setup()

    game_board = board.BOARD()
    self.log_game("START GAME")

    current_robot_id = 0

    if (not config['silent']):
      game_board.show()

    num_turns = {'O':0,'X':0}

    while (not game_board.is_ended()):
      current_robot = robots[current_robot_id]
      name     = current_robot.get_name()
      identity = current_robot.get_identity()

      self.log_game("What is your move, '{}'?".format(name))

      move = current_robot.do_turn(game_board)
      move = int(move)

      self.log_game("'{}' chose move ({})".format(name, move))
      self.log_game("")

      if (move < 0 or move > 8):
        log_error("Robot '{}' performed a move out of range ({})".
                  format(name, move))

        return

      elif (game_board.getat(move) != ' '):
        log_error("Robot '{}' performed an illegal move ({})".
                  format(name, move))

        return

      game_board.setat(move, identity)

      num_turns[identity] += 1

      if (not config['silent']):
        game_board.show()

      if (current_robot_id == 0):
        current_robot_id = 1
      else:
        current_robot_id = 0

    result = game_board.get_game_state()

    if (result == 0):
      log_error("Game ended with invalid state of 0")
      return

    score_X = self.calculate_score(num_turns['X'], result == 1, result == 3)
    score_O = self.calculate_score(num_turns['O'], result == 2, result == 3)

    if (result == 1): # X wins
      self.log_game("Robot '{}' wins".format(robots[0].get_name()))
      robots[0].process_result('WIN', score_X)
      robots[1].process_result('LOSS', score_O)
    elif (result == 2): # O wins
      self.log_game("Robot '{}' wins".format(robots[1].get_name()))
      robots[0].process_result('LOSS', score_X)
      robots[1].process_result('WIN', score_O)
    elif (result == 3): # Tie
      self.log_game("It's a TIE")
      robots[0].process_result('TIE', score_X)
      robots[1].process_result('TIE', score_O)
    else:
      log_error("Game ended with invalid state ({})".format(result))
      return

    self.log_game("Scores: '{}':{:.2f} , '{}':{:.2f}".
                  format(robots[0].get_name(), score_X,
                         robots[1].get_name(), score_O))

    game_info = {'result':result,
                 'scores':{'X':score_X,'O':score_O}}
    return game_info

  def calculate_score(self, num_turns, is_win, is_draw):
    score = 10 - num_turns
    if (not is_win):
      if (is_draw):
        score = 0
      else:
        # Weight losses much more heavily than wins
        score = -score * 10

    return score
