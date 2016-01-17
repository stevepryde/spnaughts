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
import random

from log import *

# Path to robots.
ROBOT_BASE_PATH = 'robots'

# All system logs go here.
LOG_BASE_PATH   = 'logs'

# Robots may store data in ROBOT_TEMP_PATH/<robotname>/.
# This directory will be created by this module if necessary, the first time
# it is requested by the robot.
ROBOT_TEMP_PATH = 'tempdata'

def get_robot(robot_module):

  # Load test module.
  try:
    module = importlib.import_module("%s.%s.%s" %
                                     (ROBOT_BASE_PATH, robot_module,
                                      robot_module))
  except ImportError as e:
    log_critical("Failed to import robot module '%s.%s': %s" %
                 (ROBOT_BASE_PATH, robot_module, e))
    log_critical(traceback.format_exc())
    return

  # It is expected that the class name will be the same as the module name,
  # but all uppercase.
  classname  = robot_module.upper()
  class_type = getattr(module, classname)
  robot_obj  = class_type()
  robot_obj.set_temp_path_base(ROBOT_TEMP_PATH)

  return robot_obj

def quit(message = 'Exiting...'):
  log_debug(message)
  sys.exit(1)

def run_one_game(config, robots):
  for robot in robots:
    robot.setup()

  game = board.BOARD()
  log_info("START GAME")

  current_robot_id = 0

  if (not config['batch_mode']):
    game.show()

  num_turns = {'O':0,'X':0}

  while (not game.is_ended()):

    current_robot = robots[current_robot_id]
    name     = current_robot.get_name()
    identity = current_robot.get_identity()

    if (not config['batch_mode']):
      print ("What is your move, '{}'?".format(name))

    move = current_robot.do_turn(game)
    move = int(move)

    log_info("'{}' chose move ({})".format(name, move))
    if (not config['batch_mode']):
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

    num_turns[identity] += 1

    if (not config['batch_mode']):
      game.show()

    if (current_robot_id == 0):
      current_robot_id = 1
    else:
      current_robot_id = 0

  result = game.get_game_state()

  if (result == 0):
    log_error("Game ended with invalid state of 0")
    quit()

  score_X = calculate_score(num_turns['X'], result == 1, result == 3)
  score_O = calculate_score(num_turns['O'], result == 2, result == 3)

  if (result == 1): # X wins
    log_info("Robot '{}' wins".format(robots[0].get_name()))
    robots[0].process_result('WIN', score_X)
    robots[1].process_result('LOSS', score_O)
  elif (result == 2): # O wins
    log_info("Robot '{}' wins".format(robots[1].get_name()))
    robots[0].process_result('LOSS', score_X)
    robots[1].process_result('WIN', score_O)
  elif (result == 3): # Tie
    log_info("It's a TIE")
    robots[0].process_result('TIE', score_X)
    robots[1].process_result('TIE', score_O)
  else:
    log_error("Game ended with invalid state ({})".format(result))
    quit()

  log_info("Scores: '{}':{:.2f} , '{}':{:.2f}".
           format(robots[0].get_name(), score_X, robots[1].get_name(), score_O))

  game_info = {'result':result,
               'scores':{'X':score_X,'O':score_O}}
  return game_info

def calculate_score(num_turns, is_win, is_draw):
  score = 10 - num_turns
  if (not is_win):
    if (is_draw):
      score = 0
    else:
      score = -score

  return score

def run_batch(config, robots):
  # Run a single batch.
  robots[0].clear_score()
  robots[1].clear_score()

  overall_results = {1:0,2:0,3:0}
  num_games_played = 0
  total_score = {'X':0,'O':0}
  for game_num in range(1, config['num_games'] + 1):
    log_info("\nRunning game {}\n".format(game_num))
    game_info = run_one_game(config, robots)
    result = game_info['result']

    num_games_played += 1
    total_score['X'] += game_info['scores']['X']
    total_score['O'] += game_info['scores']['O']

    if (config['batch_mode']):
      if (not config['no_batch_summary']):
        if (result == 1):
          print("Game {}: '{}' WINS".format(game_num, robots[0].get_name()))
          if ('stoponloss' in config and config['stoponloss'] == 'O'):
            print("Stopping because O lost a game and " +
                    "--stoponloss O was specified")
            quit()
        elif (result == 2):
          print("Game {}: '{}' WINS".format(game_num, robots[1].get_name()))
          if ('stoponloss' in config and config['stoponloss'] == 'X'):
            print("Stopping because X lost a game and " +
                    "--stoponloss X was specified")
            quit()
        elif (result == 3):
          print("Game {}: TIE".format(game_num))
        else:
          print("Invalid result received: '{}'".format(result))
          quit()

      if (result not in overall_results):
        print("No record of {} in overall_results".format(result))
        quit()
      else:
        overall_results[result] += 1

  if (config['batch_mode']):
    if (not config['no_batch_summary']):
      # Print overall results.
      print("\nRESULTS:")
      print("'{}' WINS: {}".format(robots[0].get_name(), overall_results[1]))
      print("'{}' WINS: {}".format(robots[1].get_name(), overall_results[2]))
      print("DRAW/TIE: {}".format(overall_results[3]))

    # Get average scores.
    if (num_games_played > 0):
      avg_score_X = float(total_score['X'] / num_games_played)
      avg_score_O = float(total_score['O'] / num_games_played)

      robots[0].set_score(avg_score_X)
      robots[1].set_score(avg_score_O)

      log_info("\nAverage Scores: '{}':{:.2f} , '{}':{:.2f}".
               format(robots[0].get_name(), avg_score_X, robots[1].get_name(),
                      avg_score_O))

      if (not config['no_batch_summary']):
        print("AVERAGE SCORES:\n'{}':{:.2f}\n'{}':{:.2f}".
              format(robots[0].get_name(), avg_score_X, robots[1].get_name(),
                     avg_score_O))
        print("")

  return 1


def parse_config():
  parser = argparse.ArgumentParser(description='Game Runner')
  parser.add_argument('robot1', help='First robot, e.g. "human"')
  parser.add_argument('robot2', help='Second robot')
  parser.add_argument('--batch',
                      help='Batch mode. Specify the number of games to run')
  parser.add_argument('--stoponloss',
                      help='Stop if the specified player loses')
  parser.add_argument('--genetic',
                      help='Genetic mode. Specify number of generations to run' +
                      '(Requires --batch)')
  parser.add_argument('--samples',
                      help='Number of samples per generation. ' +
                      '(Requires --batch)')
  args = parser.parse_args()

  if (not args.robot1 and not args.robot2):
    print("You need to specify two robots")
    sys.exit(1)

  config = {}

  config['console_logging']  = True
  config['batch_mode']       = False
  config['genetic_mode']     = False
  config['no_batch_summary'] = False

  if (args.stoponloss):
    config['stoponloss'] = args.stoponloss

  config['num_games']       = 1
  config['num_generations'] = 1
  config['num_samples']     = 1

  config['robot1'] = args.robot1
  config['robot2'] = args.robot2

  if (args.batch):
    config['batch_mode'] = True
    config['console_logging'] = False

    try:
      config['num_games'] = int(args.batch)
    except ValueError:
      print("Number of games per batch (--batch) must be an int, but you specified '{}'".
            format(str(args.batch)))
      sys.exit(1)

    if (config['num_games'] <= 0):
      print("Number of games (--batch) must be greater than 0")
      sys.exit(1)

    if (args.genetic):
      config['genetic_mode'] = True
      config['no_batch_summary'] = True
      try:
        config['num_generations'] = int(args.genetic)
      except ValueError:
        print("Number of generations (--genetic) must be an int, but you specified '{}'".
              format(str(args.genetic)))
        sys.exit(1)

      if (config['num_generations'] <= 0):
        print("Number of generations (--genetic) must be greater than 0")
        sys.exit(1)

      if (args.samples):
        try:
          config['num_samples'] = int(args.samples)
        except ValueError:
          print("Number of samples (--samples) must be an int, but you specified '{}'".
                format(str(args.samples)))
          sys.exit(1)

        if (config['num_samples'] <= 0):
          print("Number of samples (--samples) must be greater than 0")
          sys.exit(1)

    else:
      if (args.samples):
        print("You specified --samples without --genetic")
        sys.exit(1)

  else:
    if (args.genetic):
      print("You specified --genetic without --batch")
      sys.exit(1)

    if (args.samples):
      print("You specified --samples without --batch")
      sys.exit(1)

  return config


if __name__ == '__main__':
  config = parse_config()

  # Init logging.
  init_default_logger(LOG_BASE_PATH, console_logging = config['console_logging'])

  log_trace("Started")

  # Create robots.
  robots = []
  num_genetic_robots = 0
  genetic_robot_name = None
  for robot_name in (config['robot1'], config['robot2']):
    robot_obj = get_robot(robot_name)
    if (not robot_obj):
      log_critical("Error instantiating robot '{}'".format(robot_name))
      quit()

    robot_obj.set_name(robot_name)
    robot_obj.create()
    robots.append(robot_obj)

    if (robot_obj.genetic):
      num_genetic_robots += 1
      genetic_robot_name = robot_name

  log_trace("Robots created")

  try:
    genetic_robot_pool = []
    genetic_index = 0
    if (not robots[0].genetic):
      genetic_index = 1

    # Add the first robot.
    master_robot = robots[genetic_index]
    master_recipe = master_robot.get_recipe()

    genetic_robot_pool.append(master_robot)

    # If in genetic mode, one and only one of the robots must be a genetic robot
    if (config['genetic_mode']):
      if (num_genetic_robots < 1):
        print("One of the robots must be a genetic robot if --genetic is supplied")
        sys.exit(1)
      elif (num_genetic_robots > 1):
        print("Only one of the robots can be genetic if --genetic is supplied")
        sys.exit(1)

      assert(genetic_robot_name != None)

      # Remember we've already added the first sample.
      for s in range(1, config['num_samples']):
        robot_obj = get_robot(genetic_robot_name)
        if (not robot_obj):
          log_critical("Error instantiating robot '{}'".format(robot_name))
          quit()

        # Name it using the generation and sample number. This is generation 0.
        robot_obj.set_name(genetic_robot_name + '-0-' + str(s))
        robot_obj.create()
        genetic_robot_pool.append(robot_obj)

    gen_pool_index = 0
    baseline_score = -100
    for gen in range(config['num_generations']):
      if (config['genetic_mode']):
        print("Generation '{}':".format(str(gen)))

      highest_score       = baseline_score

      # Don't increment the generation number if the score wasn't exceeded.
      while(highest_score == baseline_score):
        highest_score_index = -1
        for s in range(len(genetic_robot_pool)):
          if (config['genetic_mode']):
            print("Sample '{}':".format(str(s)))

          # Substitute the 'genetic robot'.
          robots[genetic_index] = genetic_robot_pool[s]

          # Setup robots.
          robots[0].set_identity('X')
          robots[1].set_identity('O')

          log_trace("Robot setup completed")

          run_batch(config, robots)

          if (config['genetic_mode']):
            # Get highest score.
            if (robots[genetic_index].get_score() > highest_score):
              highest_score = robots[genetic_index].get_score()
              highest_score_index = s

        if (not config['genetic_mode']):
          break
        else:
          # Find the robot with the highest score, and create a new robot pool
          # based on that one.
          if (highest_score_index < 0):
            print("Highest score not found: '{}'".format(str(highest_score)))
            print("Repeat with more samples...");
          else:
            print ("Highest score was '{}'".format(str(highest_score)))
            baseline_score = highest_score

            master_robot = genetic_robot_pool[highest_score_index]
            master_recipe = master_robot.get_recipe()

          # Now scrap all robots and generate a new set from this master robot.
          # Should log this robot's blueprint.
          log_info("Generation '{}': Winning robot recipe is '{}'".
                   format(gen, master_recipe))

          # Add the master robot to the list - it may well be better than its
          # derivatives.
          genetic_robot_pool = [master_robot]
          for s in range(1, config['num_samples']):
            robot_obj = get_robot(genetic_robot_name)
            if (not robot_obj):
              log_critical("Error instantiating robot '{}'".format(robot_name))
              quit()

            # Name it using the generation and sample number.
            robot_obj.set_name(genetic_robot_name + '-' + str(gen + 1) + '-' + str(s))

            # Mutate the recipe
            num_mutations = random.randint(1, 50)
            mutated_recipe = master_recipe
            for n in range(num_mutations):
              mutated_recipe = robot_obj.mutate_recipe(mutated_recipe)

            robot_obj.create_from_recipe(mutated_recipe)
            genetic_robot_pool.append(robot_obj)


  except KeyboardInterrupt:
    quit("Cancelled...")

  quit("Game completed.")

