# genbot_control.py
#
#
import os
from robots.robot_base import Robot
import random
from log import *
from robots.genbot1 import nodes

class GENBOTCONTROL(Robot):
  def create(self):

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

    # ENGAGE 'FAKE' BRAIN

    # THIS one is just a control, to see how well the real genbot works compared
    # to a fake one that just chooses a valid move at random.

    return random.choice(moves)

    # END OF 'FAKE' BRAIN ENGAGEMENT

  def log_debug(self, message):
    log_debug("[GENBOTCONTROL]: " + message)
    return
