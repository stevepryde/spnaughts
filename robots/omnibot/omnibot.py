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
# omnibot.py
#
# This bot is a special bot that will return a list of all available moves.
#
# This is designed to be used with --batch 0 to use the magic batch runner.
# Basically, after each turn, the current game will be cloned, once for each
# returned move. Each of those cloned games will be added to a queue. The
# magic batch runner pops the first item off the left side of the queue and
# processes the next turn. See the magic batch runner in game/batch.py for
# more details.
#
#

from game.log import *
from robots.robot_base import Robot

class OMNIBOT(Robot):
  def setup(self):
    return

  def do_turn(self, current_board):
    moves = self.get_possible_moves(current_board)

    return moves

  def log_debug(self, message):
    log_debug("[OMNIBOT]: " + message)
    return
