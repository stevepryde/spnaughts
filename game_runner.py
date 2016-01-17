#!/usr/bin/env python
################################################################################
# SP Naughts - Simple naughts and crosses game including a collection of AI bots
# Copyright (C) 2015, 2016 Steve Pryde
#
# This file is part of SP Naughts.
#
# SP Naughts is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SP Naughts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SP Naughts.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
"""
Simple naughts and crosses game for developing AI robots.

The robot must derive from robot_base.py
"""

import sys
import time
import copy
import argparse

import traceback
import random

from game.log import *
import game.board as board
import game.robotmanager
import game.geneticrunner
import game.batchrunner
import game.singlerunner

# All system logs go here.
LOG_BASE_PATH = 'logs'

def quit(message = 'Exiting...'):
  log_debug(message)
  sys.exit(1)

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
  parser.add_argument('--custom',
                      help='Custom argument (passed to bot)')
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

  config['custom'] = None
  if (args.custom):
    config['custom'] = args.custom

  config['num_games']       = 1
  config['num_generations'] = 1
  config['num_samples']     = 1

  config['robot1'] = args.robot1
  config['robot2'] = args.robot2

  if (args.batch):
    config['batch_mode'] = True
    #config['console_logging'] = False
    config['silent'] = True

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

  config['log_base_dir'] = os.path.join(LOG_BASE_PATH, 'games')

  try:
    os.makedirs(config['log_base_dir'], exist_ok=True)
  except Exception as e:
    log_critical("Error creating game log dir '{}': {}".
                 format(config['log_base_dir'], str(e)))
    quit("Failed to create log dir")

  # Init logging.
  init_default_logger(LOG_BASE_PATH, console_logging = config['console_logging'])

  log_trace("Started")

  # Make randomness somewhat repeatable.
  random.seed(1)

  manager = game.robotmanager.ROBOTMANAGER()
  robots  = manager.create_robots(config)

  log_trace("Robots created")

  try:
    runner = None
    if (config['genetic_mode']):
      log_info("Using GENETIC game runner")
      runner = game.geneticrunner.GENETICRUNNER()
    elif (config['batch_mode']):
      log_info("Using BATCH game runner")
      runner = game.batchrunner.BATCHRUNNER()
    else:
      log_info("Using SINGLE game runner")
      runner = game.singlerunner.SINGLERUNNER()

    runner.run(config, robots)

  except KeyboardInterrupt:
    quit("Cancelled...")

  quit("Game completed.")
