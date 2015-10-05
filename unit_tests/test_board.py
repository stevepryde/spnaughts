#!/usr/bin/env python

import os,sys
# NOTE: This relies on this script being run from the same directory it is in.
sys.path.append(os.path.abspath('..'))
import board
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



