# randombot.py
#
# This bot just executes moves at random. It is a useful baseline.
#

from robots.robot_base import Robot
import random

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
