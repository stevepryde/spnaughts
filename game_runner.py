#!/usr/bin/env python

# Simple naughts and crosses game for developing AI robots.
#
# The robot must derive from robot_base.py
#

import sys
import time
import board
import copy
import argparse
import importlib
import traceback

from log import *

ROBOT_BASE_PATH = 'robots'
LOG_BASE_PATH   = 'logs'

def get_robot(robot_module):

  # Load test module.
  try:
    module = importlib.import_module("%s.%s.%s" %
                                     (ROBOT_BASE_PATH, robot_module,
                                      robot_module))
  except ImportError as e:
    log_critical("Failed to import robot module '%s.%s': %s" %
                 (ROBOT_BASE_PATH, robot_module, e))
    print(traceback.format_exc())
    return

  # It is expected that the class name will be the same as the module name,
  # but all uppercase.
  classname  = robot_module.upper()
  class_type = getattr(module, classname)
  robot_obj  = class_type()

  return robot_obj

def quit(message = 'Exiting...'):
  log_debug(message)
  sys.exit(1)

def run_one_game(robots):
  game = board.BOARD()
  log_info("START GAME")

  current_robot_id = 0

  game.show()

  while (not game.is_ended()):

    current_robot = robots[current_robot_id]
    name     = current_robot.get_name()
    identity = current_robot.get_identity()

    print ("What is your move, '{}'?".format(name))

    move = current_robot.do_turn(game)
    move = int(move)

    log_info("'{}' chose move ({})".format(name, move))
    print("")

    if (move < 0 or move > 8):
      log_error("Robot '{}' performed a move out of range ({})".
                format(name, move))

      quit()

    elif (game.getat(move) != ' '):
      log_error("Robot '{}' performed an illegal move ({})".
                format(name, move))

      quit()

    game.setat(move, identity)

    game.show()

    if (current_robot_id == 0):
      current_robot_id = 1
    else:
      current_robot_id = 0

  result = game.get_game_state()

  if (result == 0):
    log_error("Game ended with invalid state of 0")
    quit()
  elif (result == 1): # X wins
    log_info("Robot '{}' wins".format(robots[0].get_name()))
    robots[0].process_result('WIN')
    robots[1].process_result('LOSS')
  elif (result == 2): # O wins
    log_info("Robot '{}' wins".format(robots[1].get_name()))
    robots[0].process_result('LOSS')
    robots[1].process_result('WIN')
  elif (result == 3): # Tie
    log_info("It's a TIE")
    robots[0].process_result('TIE')
    robots[1].process_result('TIE')
  else:
    log_error("Game ended with invalid state ({})".format(result))
    quit()

  return



if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Game Runner')
  parser.add_argument('robot1', help='First robot, e.g. "human"')
  parser.add_argument('robot2', help='Second robot')
  args = parser.parse_args()

  if (not args.robot1 and not args.robot2):
    print("You need to specify two robots")
    sys.exit(1)

  # Init logging.
  init_default_logger(LOG_BASE_PATH)

  log_trace("Started")

  # Load robots.
  robots = []
  for robot_name in (args.robot1, args.robot2):
    robot_obj = get_robot(robot_name)
    if (not robot_obj):
      log_critical("Error instantiating robot '{}'".format(robot_name))
      quit()

    robot_obj.set_name(robot_name)
    robots.append(robot_obj)

  log_trace("Robots created")

  # Setup robots.
  robots[0].set_identity('X')
  robots[1].set_identity('O')

  for robot_obj in robots:
    robot_obj.setup()

  log_trace("Robot setup completed")

  try:
    run_one_game(robots)
  except KeyboardInterrupt:
    quit("Cancelled...")

  quit("Game completed.")

