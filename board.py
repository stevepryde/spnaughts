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

    newdata = self.data[:pos] + turn

    if (pos < (len(self.data)-1)):
      newdata += self.data[pos+1:]

    if (len(newdata) != 9):
      raise Exception("Invalid length! newdata is '%s'" % newdata)

    self.data = newdata

    return

  def draw(self):

    i = 0
    for r in range(0,3):
      print(" %s | %s | %s " % (self.getat(i), self.getat(i+1), self.getat(i+2)))
      if (r < 2):
        print("-----------")

      i += 3

  def is_won(self):
    """
    Check if the current board has a win.
    Returns 0 for no win, 1 for X win, 2 for O win.
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

    return 0
