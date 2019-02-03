"""Game config object."""

from typing import Any, Callable, Dict, List, Type

import argparse
import binascii
import importlib
import os
import sys
import traceback

from lib.gamebase import GameBase
from lib.gamecontext import GameContext
from lib.globals import log_critical


# All system logs go here.
LOG_BASE_PATH = "logs"
DATA_BASE_PATH = "data"
SUPPORTED_GAMES = ["naughts"]


def quit_game(message: str = "Exiting...") -> None:
    """Quit the game, displaying a message."""
    print(message)
    sys.exit(1)


def check_int1plus(value: str) -> int:
    """Validate - int greater than one."""
    try:
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(
                "Expected an int greater than " "one, but got {}".format(ivalue)
            )
    except ValueError:
        raise argparse.ArgumentTypeError("Expected an int, but got '{}'".format(value))
    return ivalue


def check_int0plus(value: str) -> int:
    """Validate - int greater than zero."""
    try:
        ivalue = int(value)
        if ivalue < 0:
            raise argparse.ArgumentTypeError(
                "Expected an int greater than " "zero, but got {}".format(ivalue)
            )
    except ValueError:
        raise argparse.ArgumentTypeError("Expected an int, but got '{}'".format(value))
    return ivalue


class GameConfig:
    """Game config object."""

    def __init__(self, base_path: str) -> None:
        """Create a new GameConfig object."""
        # Game ID is a randomly generated 32-character hex string.
        self.game_id = binascii.b2a_hex(os.urandom(16)).decode("utf-8")
        self.base_path = base_path
        self.game = ""
        self.silent = False
        self.console_logging = False
        self.batch_mode = False
        self.genetic_mode = False
        self.no_batch_summary = False
        self.batch_size = 1
        self.num_generations = 1
        self.num_samples = 1
        self.keep_samples = 1
        self.botdb = False
        self.bot_id = None
        self.bot1 = ""
        self.bot2 = ""

        args = self.define_args()
        self.parse_args(args)

        self.init_logging()
        return

    @property
    def bot_names(self) -> List[str]:
        """Get the list of bot names."""
        # TODO: This will need updating when we get to 3+ player games.
        return [self.bot1, self.bot2]

    def define_args(self) -> argparse.Namespace:
        """Define command-line arguments."""
        parser = argparse.ArgumentParser(description="Game Runner")
        parser.add_argument("bot1", help='First bot, e.g. "human"')
        parser.add_argument("bot2", help="Second bot")
        parser.add_argument(
            "--game",
            type=str,
            metavar="GAME",
            choices=SUPPORTED_GAMES,
            required=True,
            help="The game to run",
        )
        parser.add_argument(
            "--batch",
            type=check_int0plus,
            default=0,
            help="Batch mode. Specify the number of games to " "run",
        )
        parser.add_argument(
            "--genetic",
            type=check_int1plus,
            help="Genetic mode. Specify number of generations " "to run (Requires --batch)",
        )
        parser.add_argument(
            "--samples",
            type=check_int1plus,
            help="Number of samples per generation. " "(Requires --genetic)",
        )
        parser.add_argument(
            "--keep",
            type=check_int1plus,
            help='Number of winning samples to "keep" ' "(Requires --genetic)",
        )
        parser.add_argument(
            "--botdb", action="store_true", help="Enable storing and loading bots with BotDB"
        )
        parser.add_argument("--botid", action="store", help="Play against this bot id (genetic)")

        args = parser.parse_args()

        if not args.bot1 or not args.bot2:
            print("You need to specify two bots")
            sys.exit(1)

        # Check argument dependencies.
        requires_batch = ["genetic", "samples", "keep", "top"]

        requires_genetic = ["samples", "keep", "top"]

        args_dict = vars(args)
        if not args.batch:
            for req in requires_batch:
                if req in args_dict and args_dict[req]:
                    parser.error("Option --{} requires --batch".format(req))

        if not args.genetic:
            for req in requires_genetic:
                if req in args_dict and args_dict[req]:
                    parser.error("Option --{} requires --genetic".format(req))
        return args

    def parse_args(self, args: argparse.Namespace) -> None:
        """Parse the command-line arguments."""
        self.game = args.game

        self.bot1 = args.bot1
        self.bot2 = args.bot2

        if args.botdb:
            self.botdb = True

        if args.batch > 0:
            self.batch_size = int(args.batch)
            self.batch_mode = True
            self.silent = True

            if args.genetic:
                self.genetic_mode = True
                self.no_batch_summary = True
                self.num_generations = int(args.genetic)

                if args.samples:
                    self.num_samples = int(args.samples)

                if args.keep:
                    self.keep_samples = int(args.keep)

                if args.botid:
                    self.botdb = True
                    self.bot_id = args.botid
        return

    def init_logging(self) -> None:
        """Set up logging functionality."""
        self.log_base_dir = os.path.join(self.base_path, LOG_BASE_PATH, str(self.game))

        try:
            os.makedirs(self.log_base_dir, exist_ok=True)
        except IOError as e:
            quit_game("Error creating game log dir '{}': {}".format(self.log_base_dir, str(e)))

        self.data_path = os.path.join(self.base_path, DATA_BASE_PATH)
        try:
            os.makedirs(self.data_path, exist_ok=True)
        except IOError as e:
            quit_game("Error creating data dir '{}': {}".format(self.data_path, str(e)))
        return

    def get_batch_config(self) -> Dict[str, Any]:
        """Get config required for batches."""
        return {
            "batch_size": self.batch_size,
            "bot_config": self.get_bot_config(),
            "game": self.game,
            "game_id": self.game_id,
        }

    def get_bot_config(self) -> Dict[str, Any]:
        """Get config required for bots."""
        return {
            "bot_names": self.bot_names,
            "bot_id": self.bot_id,
            "game": self.game,
            "botdb": self.botdb,
        }

