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
# genbot_control.py
#
# This robot is intended to mimic genbot1, but without any of the genetic
# algorithm magic. It uses random choices instead. It serves as a 'control'
# subject to compare against genbot1.

import os, random
from game.log import *
from robots.genetic_robot_base import GeneticRobot

class GENBOTCONTROL(GeneticRobot):
  def create(self, config):
    return

  def get_recipe(self):
    return "BLAH"

  def create_from_recipe(self, recipe):
    return

  def mutate_recipe(self, recipe):
    return recipe

  def do_turn(self, current_board):
    moves = self.get_possible_moves(current_board)

    # First, win the game if we can.
    straight_sequences = ['012',
                          '345',
                          '678',
                          '036',
                          '147',
                          '258',
                          '048',
                          '246']

    for seq in straight_sequences:
      (ours, theirs, blanks) = self.get_sequence_info(current_board, seq)
      if (len(ours) == 2 and len(blanks) == 1):
        # Move into the blank for the win.
        return int(blanks[0])

    # Second, if we can't win, make sure the opponent can't win either.
    for seq in straight_sequences:
      (ours, theirs, blanks) = self.get_sequence_info(current_board, seq)
      if (len(theirs) == 2 and len(blanks) == 1):
        # Move into the blank to block the win.
        return int(blanks[0])

    # If this is the first move...
    (ours, theirs, blanks) = self.get_sequence_info(current_board, '012345678')
    if (len(ours) == 0):
      # If we're the second player:
      if (len(theirs) > 0):
        if (4 in moves):
          return 4

        # Otherwise take the upper left.
        return 0

    # ENGAGE 'FAKE' BRAIN

    # THIS one is just a control, to see how well the real genbot works compared
    # to a fake one that just chooses a valid move at random.

    return random.choice(moves)

    # END OF 'FAKE' BRAIN ENGAGEMENT

  def log_debug(self, message):
    log_debug("[GENBOTCONTROL]: " + message)
    return
