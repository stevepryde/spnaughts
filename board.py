# board.py

##
# BOARD
# -----
#
# The BOARD is a representation of a naughts and crosses board.
#
# It consists of 9 characters,
# 3 lots of 3, reading left to right, top to bottom.
# - = blank space. X and O are represented by exactly those letters
# (uppercase).
#

class BOARD(object):
  def __init__(self):
    self.data = '---------'
    return

  def copy(self):
    """
    Return a copy of this instance.
    """
    b = BOARD()
    b.data = self.data
    return b

  def getat(self,pos):
    # Position corresponds to the 0-based position within 'data' to put the
    # new entry.
    #
    # i.e.
    #
    #  0 | 1 | 2
    # -----------
    #  3 | 4 | 5
    # -----------
    #  6 | 7 | 8

    c = self.data[pos]
    if (c == '-'):
      c = ' '

    return c

  def setat(self,pos,turn):
    # Position corresponds to the 0-based position within 'data' to put the
    # new entry.
    #
    # i.e.
    #
    #  0 | 1 | 2
    # -----------
    #  3 | 4 | 5
    # -----------
    #  6 | 7 | 8
    #
    # turn is either 'X' or 'O'

    c = self.getat(pos)
    if (c != ' '):
      raise Exception("Invalid position! Already set!")

    # Can't modify strings, so use a list instead.
    newdata = list(self.data)
    newdata[pos] = turn

    newdata_str = ''.join(newdata)

    if (len(newdata_str) != 9):
      raise Exception("Invalid length! newdata is '{}'".format(newdata_str))

    self.data = newdata_str

    return

  def show(self):

    prefix = '  '

    i = 0
    for r in range(0,3):
      print(prefix + " {} | {} | {} ".
            format(self.getat(i), self.getat(i+1), self.getat(i+2)))

      if (r < 2):
        print(prefix + "-----------")

      i += 3

    print("")

    return

  def get_game_state(self):
    """
    Check if the current board has a win.
    Returns 0 for no win, 1 for X win, 2 for O win, 3 for draw/tie.
    """
    sequences = ['012',
                 '345',
                 '678',
                 '036',
                 '147',
                 '258',
                 '048',
                 '246'
                 ]

    for seq in sequences:
      val = ''
      for n in range(len(seq)):
        c = seq[n]
        val += self.getat(int(c))

      if (val == 'XXX'):
        return 1
      elif (val == 'OOO'):
        return 2

    is_draw = True
    for pos in range(9):
      val = self.getat(pos)
      if (val != 'X' and val != 'O'):
        is_draw = False

    if (is_draw):
      return 3

    return 0

  def is_ended(self):
    return self.get_game_state() != 0

  ##########################################################
  # HELPER METHODS for use in robots.
  ##########################################################

  def getat_multi(self, pos_str):
    """
    Return a string containing just the contents at the specified positions.
    For example, if I pass in '012', it will return a string identifying the
    contents of the top row.
    """

    contents = ''
    for n in range(len(pos_str)):
      contents += self.getat(int(pos_str[n]))

    return contents

  def get_rotated_board(self, rotations):
    """
    Return a copy of the board, rotated 90/180/270 degrees clockwise.
    The number of rotations is 1 for 90 degrees, 2 for 180 degrees, and 3 for
    270 degrees.
    """

    rotations = int(rotations) % 4

    board_copy    = self.copy()
    transform_map = '630741852'

    # Minor optimisation. Don't do anything if we don't have to.
    if (rotations == 0):
      return board_copy

    for rot_number in range(rotations):
      orig_data = board_copy.data

      new_data = list(orig_data)
      for pos in range(len(transform_map)):
        new_data[pos] = orig_data[int(transform_map[pos])]

      board_copy.data = ''.join(new_data)

    return board_copy

  def get_first_empty_space(self, moves):
    move_list = list(moves)

    for move in move_list:
      if (self.getat(int(move)) == ' '):
        return int(move)

    return -1



