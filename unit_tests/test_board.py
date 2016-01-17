#!/usr/bin/env python
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

import os,sys
# NOTE: This relies on this script being run from the same directory it is in.
sys.path.append(os.path.abspath('..'))
import game.board as board
from robots.robot_base import Robot

def is_val(a, b, message):
  if (a != b):
    print("Failed test: {}".format(message))
    sys.exit(1)

  print("PASS: {}".format(message))
  return

if __name__ == '__main__':
  b = board.BOARD()

  b.data = 'X--OO-OXX'

  multi = b.getat_multi('012')
  is_val(multi, 'X  ', "getat_multi() with 012")

  multi = b.getat_multi('1234')
  is_val(multi, '  OO', "getat_multi() with 1234")

  multi = b.getat_multi('58712')
  is_val(multi, ' XX  ', "getat_multi() with 58712")

  # Test rotated boards
  rot1 = b.get_rotated_board(1)
  is_val(rot1.data, 'OOXXO-X--', "get_rotated_board() with 1 rotation")

  rot2 = b.get_rotated_board(2)
  is_val(rot2.data, 'XXO-OO--X', "get_rotated_board() with 2 rotations")

  rot3 = b.get_rotated_board(3)
  is_val(rot3.data, '--X-OXXOO', "get_rotated_board() with 3 rotations")

  # Also test robot base methods that interact with boards.
  base_robot = Robot()
  is_val(base_robot.get_unrotated_move(1, 3), 5, "get_unrotated_move(1) with 3 rotations")
  is_val(base_robot.get_unrotated_move(1, 2), 7, "get_unrotated_move(1) with 2 rotations")
  is_val(base_robot.get_unrotated_move(1, 1), 3, "get_unrotated_move(1) with 1 rotation")
