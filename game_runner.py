#!/usr/bin/env python
"""Simple naughts and crosses game for developing AI bots."""

import argparse
import os
import random
import sys

from game.log import (init_default_logger, log_critical, log_debug, log_info,
                      log_trace)
from game.botmanager import BotManager
from game.runners import singlerunner, batchrunner, geneticrunner

# All system logs go here.
LOG_BASE_PATH = 'logs'
DATA_BASE_PATH = 'data'


def quit_game(message='Exiting...'):
    """Quit the game, displaying a message."""
    log_debug(message)
    sys.exit(1)


def check_int1plus(value):
    """Validator for checking that value is an int greater than one."""
    try:
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError("Expected an int greater than "
                                             "one, but got {}".format(ivalue))
    except ValueError:
        raise argparse.ArgumentTypeError("Expected an int, but got '{}'".
                                         format(value))
    return ivalue


def check_int0plus(value):
    """Validator for checking that value is an int greater than zero."""
    try:
        ivalue = int(value)
        if ivalue < 0:
            raise argparse.ArgumentTypeError("Expected an int greater than "
                                             "zero, but got {}".format(ivalue))
    except ValueError:
        raise argparse.ArgumentTypeError("Expected an int, but got '{}'".
                                         format(value))
    return ivalue


def parse_config():
    """Parse the input arguments and game configuration.

    Returns:
        Dictionary containing configuration details.
    """

    parser = argparse.ArgumentParser(description='Game Runner')
    parser.add_argument('bot1', help='First bot, e.g. "human"')
    parser.add_argument('bot2', help='Second bot')
    parser.add_argument('--batch', type=check_int0plus,
                        help='Batch mode. Specify the number of games to run')
    parser.add_argument('--stoponloss',
                        help='Stop if the specified player loses')
    parser.add_argument('--genetic', type=check_int1plus,
                        help='Genetic mode. Specify number of generations to '
                             'run (Requires --batch)')
    parser.add_argument('--samples', type=check_int1plus,
                        help='Number of samples per generation. '
                             '(Requires --genetic)')
    parser.add_argument('--keep', type=check_int1plus,
                        help='Number of winning samples to "keep" '
                             '(Requires --genetic)')
    parser.add_argument('--top', action="store_true",
                        help='Start with the top bots for this bot type. '
                             '(Requires --genetic)')
    parser.add_argument('--custom', help='Custom argument (passed to bot)')
    parser.add_argument('--loggames', action="store_true",
                        help='Also log individual games (may require a lot of '
                             'disk space!)')
    args = parser.parse_args()

    if not args.bot1 or not args.bot2:
        print("You need to specify two bots")
        sys.exit(1)

    config = {}

    # Check argument dependencies.
    requires_batch = ['genetic',
                      'samples',
                      'keep',
                      'top']

    requires_genetic = ['samples',
                        'keep',
                        'top']

    args_dict = vars(args)
    if args.batch is None:
        for req in requires_batch:
            if req in args_dict and args_dict[req]:
                parser.error("Option --{} requires --batch".format(req))

    if not args.genetic:
        for req in requires_genetic:
            if req in args_dict and args_dict[req]:
                parser.error("Option --{} requires --genetic".format(req))

    # Set the relevant config based on provided args.
    config['console_logging'] = True
    config['batch_mode'] = False
    config['genetic_mode'] = False
    config['no_batch_summary'] = False

    if args.stoponloss:
        config['stoponloss'] = args.stoponloss

    config['custom'] = None
    if args.custom:
        config['custom'] = args.custom

    config['loggames'] = args.loggames
    config['num_games'] = 1
    config['num_generations'] = 1
    config['num_samples'] = 1

    config['bot1'] = args.bot1
    config['bot2'] = args.bot2

    if args.batch is not None:
        config['batch_mode'] = True
        config['silent'] = True
        config['num_games'] = int(args.batch)

        if args.genetic:
            config['genetic_mode'] = True
            config['no_batch_summary'] = True
            config['num_generations'] = int(args.genetic)

            if args.samples:
                config['num_samples'] = int(args.samples)

            if args.keep:
                config['keep_samples'] = int(args.keep)

            if args.top:
                config['use_top_bots'] = True

    return config


if __name__ == '__main__':
    config = parse_config()

    # Set up logging.
    config['log_base_dir'] = os.path.join(LOG_BASE_PATH, 'games')

    try:
        os.makedirs(config['log_base_dir'], exist_ok=True)
    except IOError as e:
        log_critical("Error creating game log dir '{}': {}".
                     format(config['log_base_dir'], str(e)))
        quit_game("Failed to create log dir")

    config['data_path'] = DATA_BASE_PATH
    try:
        os.makedirs(config['data_path'], exist_ok=True)
    except IOError as e:
        log_critical("Error creating data dir '{}': {}".
                     format(config['data_path'], str(e)))
        quit_game("Failed to create data dir")

    init_default_logger(LOG_BASE_PATH,
                        console_logging=config['console_logging'])

    log_trace("Started")

    # Make randomness somewhat repeatable.
    random.seed(1)

    manager = BotManager()
    bots = manager.create_bots(config)

    log_trace("Bots created")

    try:
        runner = None
        if config['genetic_mode']:
            log_info("Using GENETIC game runner")
            runner = geneticrunner.GeneticRunner()
        elif config['batch_mode']:
            log_info("Using BATCH game runner")
            runner = batchrunner.BatchRunner()
        else:
            log_info("Using SINGLE game runner")
            runner = singlerunner.SingleRunner()

        runner.run(config, bots)

    except KeyboardInterrupt:
        quit_game("Cancelled...")

    quit_game("Game completed.")
