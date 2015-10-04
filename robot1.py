# robot1.py
#
# First prototype:
# The idea is to create a robot that works from memory and figures out the
# best move over time, constantly improving gameplay.
#
#
# Memory:
# For each turn, we note the current board, the move we took, and the final
# outcome of the game.
#
# If we haven't played this board before, play a random pos.
# If we have played this board before, score up the previous attempts and then
# try the best scored position, or random if there are more than 1.
#
# RESULTS:
# Ok, so there's a big weakness in the blunt win/lose ranking.
# It seems that because I can easily beat the robot, it never really learns
# anything. A win is a win is a win, meaning that even if the robot chooses the
# correct spot one move, if it ultimately loses the game it assumes that spot
# was no good. I need to find a way to improve this.
#
#
#
#
#

from robot_base import Robot
import operator
import random

MEMFILE = 'robotmem.dat'

class Robot1(Robot):
  def setup(self):
    # The history is where we keep track of each turn for THIS GAME ONLY.
    # When we process the result, we simply trace this history and update the
    # result, then write to disk.
    self.history = []

    # The memory is stored on disk, and is a record of all previous games.
    # It is a dict, keyed by board (the raw data representation of a board).
    # The value is another dict where the keys are the positions we've tried,
    # and the values their associated score. Higher is better.
    self.memory = {}
    try:
      f = open(MEMFILE, 'rt')
      for line in f:
        fields = line.rstrip().split(':')
        if (len(fields) == 3):
          data = str(fields[0])
          move = int(fields[1])
          score = int(fields[2])

          if (data not in self.memory):
            self.memory[data] = {}

          self.memory[data][move] = score

      f.close()

    except IOError as e:
      print("Error reading memory file from disk: %s" % str(e))

    return

  def get_moves(self, current_board):
    possible = {}
    for pos in range(0,9):
      if (current_board.getat(pos) == ' '):
        possible[pos] = 0

    if (current_board.data in self.memory):
      remembered = self.memory[current_board.data]
      for key,value in remembered.items():
        possible[int(key)] = value

    # Get the move(s) with the highest value.
    max_value = max(possible.values())
    bestmoves = []
    for move in possible.keys():
      if (possible[move] == max_value):
        bestmoves.append(int(move))

    return bestmoves

  def do_turn(self, current_board):
    moves = self.get_moves(current_board)
    move = 0
    if (len(moves) < 1):
      raise Exception("No possible moves!")
    elif (len(moves) == 1):
      # Only one move.
      move = moves[0]
    else:
      # Choose at random.
      move = random.choice(moves)

    self.history.append({'board':current_board,
                         'move':move})

    return move

  def process_result(self, result):
    delta = 0
    if (result == 1):
      # robot lost.
      delta = -1
    elif (result == 2):
      # robot won.
      delta = 1

    if (delta != 0):
      # Retrace the history and write the results into 'memory'.
      for hist in self.history:
        move = int(hist['move'])
        data = hist['board'].data

        if (data not in self.memory):
          self.memory[data] = {}

        if (move not in self.memory[data]):
          self.memory[data][move] = 0

        self.memory[data][move] += delta

    # Then write the 'memory' to disk.
    try:
      f = open(MEMFILE, 'wt')

      for data in self.memory:
        mem = self.memory[data]
        for key,value in mem.items():
          f.write("%s:%d:%d\n" % (data, int(key), int(value)))

      f.close()

    except IOError as e:
      print("Error writing memory file to disk: %s" % str(e))

    return
