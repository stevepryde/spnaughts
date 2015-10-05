# randombot.py
#
# This bot just executes moves at random. It is a useful baseline.
#

from robots.robot_base import Robot
import random

class HUMAN(Robot):

  def do_turn(self, current_board):
    moves = self.get_possible_moves(current_board)

    move = -1
    while (move not in moves):
      try:
        move = input('possible moves are [' +
                     ','.join(map(lambda x: str(x), moves)) +
                     ']:')

        move = int(move)

      except ValueError:
        pass

    return int(move)
