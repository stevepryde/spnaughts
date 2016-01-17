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
# human.py
#
# This bot accepts input via the keyboard for every move. This allows manual
# games with human vs another bot.
#
# Not practical in batch mode or genetic mode.
#

import random
from robots.robot_base import Robot

class HUMAN(Robot):

  def do_turn(self, current_board):
    moves = self.get_possible_moves(current_board)

    info_str = 'possible moves are [' + \
                 ','.join(map(lambda x: str(x), moves)) + \
                 ']: '

    # If there's only one choice, save ourselves some typing.
    if (len(moves) == 1):
      move = int(moves[0])
      print (info_str + "(Automatically choose {})".format(move))
      return move

    move = -1
    while (move not in moves):
      try:
        move = int(input(info_str))
      except ValueError:
        pass

    return int(move)
