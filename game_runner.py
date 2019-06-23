#!/usr/bin/env python
"""Simple naughts and crosses game for developing AI bots."""

import os
import random
import time
from typing import Optional

from lib.errors import BotCreateError, GameCreateError
from lib.gameconfig import GameConfig, quit_game
from lib.runners import singlerunner, batchrunner, geneticrunner
from lib.runners.gamerunnerbase import GameRunnerBase


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.dirname(__file__))
    config = GameConfig(base_path=base_dir)
    print("Started")

    try:
        runner = None  # type: Optional[GameRunnerBase]
        if config.genetic_mode:
            print("Using GENETIC game runner")
            runner = geneticrunner.GeneticRunner(config=config)
        elif config.batch_mode:
            print("Using BATCH game runner")
            runner = batchrunner.BatchRunner(config=config)
        else:
            print("Using SINGLE game runner")
            runner = singlerunner.SingleRunner(config=config)

        start_time = time.monotonic()
        runner.run()
        elapsed = time.monotonic() - start_time
        runner.log.info("Completed in {:.3f} seconds.".format(elapsed))
    except BotCreateError as e:
        quit_game("ERROR: Could not create bot: {}".format(e))
    except GameCreateError as e:
        quit_game("ERROR: Could not create game: {}".format(e))
    except KeyboardInterrupt:
        quit_game("Cancelled...")

    quit_game("Game completed.")
