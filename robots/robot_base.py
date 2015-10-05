# robot_base.py
#
# This is the base class for AI naughts and crosses robots.
#
# All robots must implement do_turn().
#
# Robots can optionally implement setup() and process_result().

class Robot(object):
  def __init__(self):
    self.identity = '' # This will be set to X or O.
    self.name     = '' # This will be set by the game runner.
    return

  def get_identity(self):
    return self.identity

  def get_their_identity(self):
    if (self.identity == 'X'):
      return 'O'

    return 'X'

  def set_identity(self, _identity):
    self.identity = _identity
    return

  def get_name(self):
    return "{} ({})".format(self.name, self.identity)

  def set_name(self, _name):
    self.name = _name
    return

  def setup(self):
    return

  def do_turn(self, current_board):
    """
    Must return the position 0-9 for this turn.
    """
    return 0

  def process_result(self, result):
    """
    result determines the outcome of the game.
    result is a string which can be 'TIE', 'WIN' or 'LOSS'.
    """
    return

  ###########################################
  #
  # HELPER METHODS
  # These are methods that are probably generally useful to several bots
  #
  ###########################################

  def get_possible_moves(self, current_board):
    possible = []
    for pos in range(9):
      if (current_board.getat(pos) == ' '):
        possible.append(pos)

    return possible

  def get_sequence_info(self, current_board, sequence):
    """
    Return info about the given sequence, in the form of 3 lists.
    The first list will be all positions matching my own identity.
    The second list will be all positions matching the other identity.
    The third list will be all blank positions.
    """

    ours   = []
    theirs = []
    blanks = []

    for n in range(len(sequence)):
      c = int(sequence[n])
      val = current_board.getat(c)
      if (val == self.get_identity()):
        ours.append(c)
      elif (val == ' '):
        blanks.append(c)
      else:
        theirs.append(c)

    return (ours, theirs, blanks)

  def get_unrotated_move(self, move, rotations):
    """
    Return the correct, unrotated move that corresponds to the move we would
    make on a board rotated the specified number of times.
    For example, if rotations is 1, and I want to get the corrected move for
    move 0, this would return 6. If rotations is 2, and I want the corrected
    move for 1, this would return 7.
    """

    rotations = int(rotations) % 4

    # Don't do anything if we don't have to.
    if (rotations == 0):
      return move

    transform_map = '630741852'
    for rot_number in range(rotations):
      move = int(transform_map[move])

    return move


