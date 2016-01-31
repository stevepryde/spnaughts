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
    self.robots = []
    self.game_board = None
    self.current_robot_id = 0
    self.num_turns = {'O':0,'X':0}
    return

  def get_game_log(self):
    return "\n".join(self.game_log_lines)

  def log_game(self, message):
    if (self.config and
        (('silent' not in self.config) or (not self.config['silent']))):
      print(message)

    self.game_log_lines.append(message)
    return

  def clone(self):
    cloned_game = SINGLEGAME()
    cloned_game.game_log_lines   = list(self.game_log_lines)
    cloned_game.config           = self.config
    cloned_game.robots           = list(self.robots)
    cloned_game.game_board       = self.game_board.copy()
    cloned_game.current_robot_id = self.current_robot_id
    cloned_game.num_turns        = dict(self.num_turns)
    return cloned_game

  def start(self, config, robots):
    self.config = config
    self.robots = []

    for robot in robots:
      robot.setup()
      self.robots.append(robot)

    self.game_board = board.BOARD()
    self.log_game("START GAME")

    self.current_robot_id = 0

    self.num_turns = {'O':0,'X':0}

    return

  def do_turn(self):
    if (not self.config['silent']):
      self.game_board.show()

    current_robot = self.robots[self.current_robot_id]
    name     = current_robot.get_name()
    identity = current_robot.get_identity()

    self.log_game("What is your move, '{}'?".format(name))

    # Allow for a bot to return multiple moves. This is useful for running
    # the 'omnibot' in order to train or measure other bots.
    moves = current_robot.do_turn(self.game_board)

    # Update current_robot_id early, this way it will be copied to any
    # cloned games...
    if (self.current_robot_id == 0):
      self.current_robot_id = 1
    else:
      self.current_robot_id = 0

    game_clones = []
    if (type(moves) is list):
      for move in moves:
        # clone this game.
        cloned_game = self.clone()

        # apply move to clone.
        cloned_game.apply_move(int(move), name, identity)

        # append to game_clones
        game_clones.append(cloned_game)
    else:
      # type(moves) is not list
      self.apply_move(int(moves), name, identity)

      # This will not affect the standard game runner.
      # The omnibot runner should use the returned list of games and discard
      # the one that was used to call do_turn().
      game_clones = [self]

    return game_clones

  def apply_move(self, move, name, identity):
    self.log_game("'{}' chose move ({})".format(name, move))
    self.log_game("")

    if (move < 0 or move > 8):
      log_error("Robot '{}' performed a move out of range ({})".
                format(name, move))

      return

    elif (self.game_board.getat(move) != ' '):
      log_error("Robot '{}' performed an illegal move ({})".
                format(name, move))

      return

    self.game_board.setat(move, identity)

    self.num_turns[identity] += 1

    if (not self.config['silent']):
      self.game_board.show()

    return

  def is_ended(self):
    return self.game_board.is_ended()

  def run(self, config, robots):
    self.start(config, robots)

    while (not self.is_ended()):
      self.do_turn()

    game_info = self.get_game_info()
    return game_info

  def get_game_info(self):
    if (len(self.robots) != 2):
      log_error("No robots have been set up - was this game started?")
      return

    result = self.game_board.get_game_state()

    if (result == 0):
      log_error("Game ended with invalid state of 0 - was this game finished?")
      return

    score_X = self.calculate_score(self.num_turns['X'], result == 1, result == 3)
    score_O = self.calculate_score(self.num_turns['O'], result == 2, result == 3)

    if (result == 1): # X wins
      self.log_game("Robot '{}' wins".format(self.robots[0].get_name()))
      self.robots[0].process_result('WIN', score_X)
      self.robots[1].process_result('LOSS', score_O)
    elif (result == 2): # O wins
      self.log_game("Robot '{}' wins".format(self.robots[1].get_name()))
      self.robots[0].process_result('LOSS', score_X)
      self.robots[1].process_result('WIN', score_O)
    elif (result == 3): # Tie
      self.log_game("It's a TIE")
      self.robots[0].process_result('TIE', score_X)
      self.robots[1].process_result('TIE', score_O)
    else:
      log_error("Game ended with invalid state ({})".format(result))
      return

    self.log_game("Scores: '{}':{:.2f} , '{}':{:.2f}".
                  format(self.robots[0].get_name(), score_X,
                         self.robots[1].get_name(), score_O))

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
