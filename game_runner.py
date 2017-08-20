#!/usr/bin/env python
"""Simple naughts and crosses game for developing AI bots."""

import random
import sys

from game.log import log_debug, log_info, log_trace
from game.gameconfig import GameConfig, quit_game
from game.runners import singlerunner


if __name__ == '__main__':
    config = GameConfig()
    log_trace("Started")

    # Make randomness somewhat repeatable.
    # TODO: set random seed in game runner instead - this way when running
    # multiple genetic samples against a single random bot, the random bot can
    # use the same seed against each sample.
    random.seed(1)

    try:
        runner = None
        if config.genetic_mode:
            log_info("Using GENETIC game runner")
            # runner = geneticrunner.GeneticRunner(config)
        elif config.batch_mode:
            log_info("Using BATCH game runner")
            # runner = batchrunner.BatchRunner(config)
        else:
            log_info("Using SINGLE game runner")
            runner = singlerunner.SingleRunner(config)

        runner.run()
        log_trace("Completed")

    except KeyboardInterrupt:
        quit_game("Cancelled...")

    quit_game("Game completed.")
