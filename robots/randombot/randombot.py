# randombot.py
#
# This bot just executes moves at random. It is a useful baseline.
#

import random
from robots.robot_base import Robot

class RANDOMBOT(Robot):

  def do_turn(self, current_board):
    moves = self.get_possible_moves(current_board)

    return random.choice(moves)
