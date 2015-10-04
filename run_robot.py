#!/usr/bin/env python

# Simple naughts and crosses game for developing AI robots.
#
# The robot must derive from robot_base.py
#

from robot1 import Robot1
import sys
import time
import board
import copy


if __name__ == '__main__':
  try:
    r = Robot1()
    r.setup()

    game = board.BOARD()
    print("START GAME...\n")
    print("User goes first. User is X.\n")

    game.draw()

    turn = 'X'

    won = 0

    # There will be 9 turns in total. User starts.
    for n in range(0,9):
      if (turn == 'X'):
        print("\n")
        is_valid_move = False
        while (not is_valid_move):
          is_valid_move = True
          move = input('What is your move (0-8)?')
          if (len(move) == 0):
            is_valid_move = False
          elif (int(move) < 0 or int(move) > 8):
            print("Out of range. Try again...")
            is_valid_move = False
          elif (game.getat(int(move)) != ' '):
            print("Invalid position (already occupied). Try again...")
            is_valid_move = False

        print("MOVE was '%s'" % move)
        game.setat(int(move),'X')
        print
      elif (turn == 'O'):
        print("Robot Turn:")
        answer = r.do_turn(game.copy())
        if (answer != None):
          if (game.getat(int(answer)) != ' '):
            print("\nINVALID MOVE: %d" % int(answer))
            sys.exit(0)

          game.setat(int(answer), 'O')
          print("\n")
          print("ROBOT MOVE WAS: %d" % int(answer))
        else:
          print("Timed out waiting for ROBOT ANSWER :(")
          break

      game.draw()

      win = game.is_won()
      if (win == 1):
        print("YOU WIN!")
        won = 1
        break
      elif (win == 2):
        print("ROBOT WINS!")
        won = 2
        break

      if (turn == 'X'):
        turn = 'O'
      else:
        turn = 'X'

    if (won == 0):
      print("TIE!")

    r.process_result(won)

  except KeyboardInterrupt:
    print("Stopping...")
