# randombot.py
#
# This bot just executes moves at random. It is a useful baseline.
#

from robots.robot_base import Robot
import random

class RANDOMBOT(Robot):

  def do_turn(self, current_board):
    moves = self.get_possible_moves(current_board)

    return random.choice(moves)
