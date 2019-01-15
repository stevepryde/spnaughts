#!/usr/bin/env python
"""Simple naughts and crosses game for developing AI bots."""

import os
import random
from typing import Optional

from lib.runners.gamerunnerbase import GameRunnerBase
from lib.gameconfig import GameConfig, quit_game
from lib.globals import set_global_config
from lib.runners import singlerunner, batchrunner, geneticrunner


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.dirname(__file__))
    config = GameConfig(base_path=base_dir)
    set_global_config(config)
    print("Started")

    try:
        runner = None  # type: Optional[GameRunnerBase]
        if config.genetic_mode:
            print("Using GENETIC game runner")
            runner = geneticrunner.GeneticRunner()
        elif config.batch_mode:
            print("Using BATCH game runner")
            runner = batchrunner.BatchRunner()
        else:
            print("Using SINGLE game runner")
            runner = singlerunner.SingleRunner()

        runner.run()
    except KeyboardInterrupt:
        quit_game("Cancelled...")

    quit_game("Game completed.")
