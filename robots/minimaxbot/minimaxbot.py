# minimaxbot.py
#
# This bot will win if it can and avoid an obvious loss.
# Otherwise it uses the minimax (actually, A-B) algorithm to determine next move.
#
# This is the optimal solution to the game. It will always pick an optimal game
# plan, which results in not just a guaranteed win or tie, but also the most
# wins against randombot compared to other bots that likewise cannot lose.
#

import random
from game.log import *
from robots.robot_base import Robot

class MINIMAXBOT(Robot):
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

      # For the first move, just pick from a random set - otherwise A-B takes
      # too long.
      choices = [0, 2, 4, 6, 8]
      return random.choice(choices)

    # Get the (first) move with the best score...
    best_score = None
    choices = []
    for move in moves:
      temp_board = current_board.copy()
      temp_board.setat(int(move), self.get_identity())
      score = self.alphabeta(temp_board, self.get_opponent(), -999, 999)

      if (best_score == None or score > best_score):
        best_score = score
        choices = [int(move)]
      elif(score == best_score):
        choices.append(int(move))

    return random.choice(choices)

  def log_debug(self, message):
    log_debug("[MINIMAXBOT]: " + message)
    return

  def get_score(self, test_board):
    """
    Returns 1 for a win, -1 for a loss, or 0 for a tie.
    """

    winner = test_board.get_winner()
    if (winner):
      if (winner == self.get_identity()):
        return 1
      else:
        return -1

    return 0

  def alphabeta(self, node_board, turn, alpha, beta, depth = 0):
    # NOTE: depth is provided only for debugging purposes.

    moves = self.get_possible_moves(node_board)
    if (len(moves) == 0 or node_board.is_ended()):
      return self.get_score(node_board)

    if (turn == self.get_identity()):
      v = -999
      for move in moves:
        test_board = node_board.copy()
        test_board.setat(int(move), turn)
        v = max(v, self.alphabeta(test_board, self.get_opponent(turn), alpha, beta, depth + 1))
        alpha = max(alpha, v)
        if (beta <= alpha):
          break

      return v

    v = 999
    for move in moves:
      test_board = node_board.copy()
      test_board.setat(int(move), turn)
      v = min(v, self.alphabeta(test_board, self.get_opponent(turn), alpha, beta, depth + 1))
      beta = min(beta, v)
      if (beta <= alpha):
        break

    return v
