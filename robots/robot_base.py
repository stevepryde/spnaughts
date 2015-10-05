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

