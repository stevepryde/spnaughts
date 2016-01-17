# randombot.py
#
# This bot will win if it can and avoid an obvious loss, but other than that
# it just follows a pre-defined list of moves. Not very intelligent.
#
#

import random
from game.log import *
from robots.robot_base import Robot

class SIMPLEBOT(Robot):
  def setup(self):
    return

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

    # Otherwise pick the first move from a series of preferred moves.
    self.log_debug("Fall back to next move in preferred list")
    preferred_moves_str = '402681357'
    preferred_moves = list(preferred_moves_str)
    for move in preferred_moves:
      if (int(move) in moves):
        return int(move)

    print("MOVES contains: " + str(moves))
    # Shouldn't be here!
    raise Exception("SIMPLEBOT failed!")

    return random.choice(moves)

  def log_debug(self, message):
    log_debug("[SIMPLEBOT]: " + message)
    return
