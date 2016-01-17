# goodbot.py
#
# This is based on perfectbot, but crippled a little to make it slightly imperfect.
#
#

from robots.robot_base import Robot
import random
from log import *

class GOODBOT(Robot):
  def setup(self):
    self.defensive = False
    self.scenario = 0 # The 2WW scenario we are trying for.
    self.scenario_rotation = -1
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
        # Don't try anything funky to win.
        self.defensive = True

        if (4 in moves):
          return 4

        # Otherwise take the upper left.
        return 0

      # We're starting. Try for a 2WW below.
      self.defensive = False

    their_identity = self.get_their_identity()

    # Offensive: Try to set up a 2-way win.
    if (not self.defensive):
      # Not in defensive mode. I have a limited time to set up a 2WW scenario.
      self.log_debug("I am in offensive mode")

      if (self.scenario == 0):
        # Choose a 2WW scenario at random.
        self.scenario = random.randint(1, 3)
        self.scenario_rotation = random.randint(0, 3)

      # Try to set up the scenario in all 4 rotations, but prioritise the
      # current scenario rotation.
      # Also try all scenarios, but prioritise the current one.
      rotations = [self.scenario_rotation]
      # for n in range(4):
      #   if (n not in rotations):
      #     rotations.append(n)

      scenarios = [self.scenario]
      # TODO: I think it is probably dangerous to continue with a failed
      #       offensive scenario. Perhaps it should try the initial scenario,
      #       and if that fails, revert to defensive mode, and only after that
      #       should it attempt another offensive scenario.
      #
      # for n in range(1,4):
      #   if (n not in scenarios):
      #     scenarios.append(n)

      self.log_debug("Trying scenario {} in rotation {}".
                     format(self.scenario,self.scenario_rotation))

      for scen in scenarios:
        for rotation in rotations:
          b = current_board.get_rotated_board(rotation)

          if (scen == 1):
            # Scenario 1:
            # X_
            # _O
            # *_X
            if (their_identity in list(b.getat_multi('03678'))):
              # They've blocked us.
              continue

            if (b.getat_multi('37') != '  '):
              # Something's gone wrong with our plan.
              continue

            move = b.get_first_empty_space('086')
            if (move >= 0):
              # Update the scenario rotation just in case it's not the original
              # one.
              self.scenario = scen
              self.scenario_rotation = rotation

              return self.get_unrotated_move(move, rotation)

          elif (scen == 2):
            # Scenario 2:
            # X_*
            #  OX
            #   _
            if (their_identity in list(b.getat_multi('01258'))):
              # They've blocked us.
              continue

            if (b.getat_multi('18') != '  '):
              # Something's gone wrong with our plan.
              continue

            move = b.get_first_empty_space('052')
            if (move >= 0):
              self.scenario = scen
              self.scenario_rotation = rotation
              return self.get_unrotated_move(move, rotation)

          elif (scen == 3):
            # Scenario 3 is just scenario 2 mirrored:
            # X
            # _O
            # *X_
            if (their_identity in list(b.getat_multi('03678'))):
              # They've blocked us.
              continue

            if (b.getat_multi('38') != '  '):
              # Something's gone wrong with our plan.
              continue

            move = b.get_first_empty_space('076')
            if (move >= 0):
              self.scenario = scen
              self.scenario_rotation = rotation
              return self.get_unrotated_move(move, rotation)

      # If we fall through to here, it means we've tried all offensive moves
      # and scanned all possible scenarios but none are left available to us.

    self.defensive = True
    self.log_debug("I am in defensive mode")
    # Defensive: Avoid 2-way wins.
    for rotation in range(4):
      b = current_board.get_rotated_board(rotation)

      # Scenario 1:
      # X_
      # _O
      # *_X
      if (b.getat_multi('03678') == "{0}   {0}".format(their_identity)):
        self.log_debug("Prevent 2WW scenario 1")
        return self.get_unrotated_move(3, rotation)

      # Scenario 2:
      # X_*
      #  OX
      #   _
      if (b.getat_multi('01258') == "{0}  {0} ".format(their_identity)):
        self.log_debug("Prevent 2WW scenario 2")
        return self.get_unrotated_move(2, rotation)

      # Scenario 2 in mirrored form:
      # X
      # _O
      # *X_
      # if (b.getat_multi('03678') == "{0}  {0} ".format(their_identity)):
      #   self.log_debug("Prevent mirrored 2WW scenario 2")
      #   return self.get_unrotated_move(6, rotation)

      # Scenario 3:
      # NOTE: This scenario actually leaves the opponent vulnerable but we don't
      #       currently exploit this. Ironically I think if we try to exploit it
      #       we are left vulnerable instead.
      # Start with 1, then play 5, then 2.
      #
      # _X*
      #  OX
      #   _
      # if (b.getat_multi('01258') == " {0} {0} ".format(their_identity)):
      #   self.log_debug("Prevent 2WW scenario 3")
      #   return self.get_unrotated_move(2, rotation)

      # Scenario 4:
      #
      # X _
      # _X
      # * O
      # if (b.getat_multi('02346') == "{0}  {0} ".format(their_identity)):
      #   self.log_debug("Prevent 2WW scenario 4")
      #   # This scenario can go two ways, so cover both.
      #   move = b.get_first_empty_space('62')
      #   return self.get_unrotated_move(move, rotation)

      # Scenario 4 mirrored:
      #
      # X_*
      #  X
      # _ O
      # if (b.getat_multi('01246') == "{0}  {0} ".format(their_identity)):
      #   self.log_debug("Prevent mirrored 2WW scenario 4")
      #   move = b.get_first_empty_space('26')
      #   return self.get_unrotated_move(move, rotation)

      # TODO: DID I MISS ANY? It should be impossible to win here.


    # Otherwise pick the first move from a series of preferred moves.
    self.log_debug("Fall back to next move in preferred list")
    preferred_moves_str = '402681357'
    preferred_moves = list(preferred_moves_str)
    for move in preferred_moves:
      if (int(move) in moves):
        return int(move)

    print("MOVES contains: " + str(moves))
    # Shouldn't be here!
    raise Exception("GOODBOT failed!")

    return random.choice(moves)

  def log_debug(self, message):
    log_debug("[GOODBOT]: " + message)
    return
