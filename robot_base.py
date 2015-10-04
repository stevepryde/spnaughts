# robot_base.py
#
# This is the base class for AI naughts and crosses robots.
#
# All robots must implement do_turn().
#
# Robots can optionally implement setup() and process_result().

class Robot(object):
  def __init__(self):
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
    0 means draw.
    1 means player won.
    2 means robot won.
    """
    return
