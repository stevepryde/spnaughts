#!/usr/bin/env python
"""Simple naughts and crosses game for developing AI bots."""

import random

from lib.log import log_info, log_trace
from lib.gameconfig import GameConfig, quit_game
from lib.runners import singlerunner, batchrunner, geneticrunner


if __name__ == '__main__':
    config = GameConfig()
    log_trace("Started")

    try:
        runner = None
        if config.genetic_mode:
            log_info("Using GENETIC game runner")
            runner = geneticrunner.GeneticRunner(config)
        elif config.batch_mode:
            log_info("Using BATCH game runner")
            runner = batchrunner.BatchRunner(config)
        else:
            log_info("Using SINGLE game runner")
            runner = singlerunner.SingleRunner(config)

        runner.run()
        log_trace("Completed")

    except KeyboardInterrupt:
        quit_game("Cancelled...")

    quit_game("Game completed.")
