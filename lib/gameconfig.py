"""Game config object."""

import argparse
import importlib
import os
import sys
import traceback


from lib.globals import log_critical
from lib.support.topbots import TopBots


# All system logs go here.
LOG_BASE_PATH = "logs"
DATA_BASE_PATH = "data"
SUPPORTED_GAMES = ["naughts"]


def quit_game(message="Exiting..."):
    """Quit the game, displaying a message."""
    print(message)
    sys.exit(1)


def check_int1plus(value):
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


def check_int0plus(value):
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

    def __init__(self, base_path):
        """Create a new GameConfig object."""
        self.base_path = base_path
        self.game = None
        self.silent = False
        self.console_logging = False
        self.batch_mode = False
        self.genetic_mode = False
        self.no_batch_summary = False
        self.stop_on_loss = ""
        self.custom_arg = None
        self.batch_size = 1
        self.num_generations = 1
        self.num_samples = 1
        self.keep_samples = 1
        self.use_top_bots = False

        args = self.define_args()
        self.parse_args(args)

        self.init_logging()

        self.top_bots = TopBots(self.data_path)
        return

    def define_args(self):
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
            "--magic",
            action="store_true",
            help="Use 'magic' batch type (omnibot only!)",
        )
        parser.add_argument("--stoponloss", help="Stop if the specified player loses")
        parser.add_argument(
            "--genetic",
            type=check_int1plus,
            help="Genetic mode. Specify number of generations "
            "to run (Requires --batch)",
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
            "--top",
            action="store_true",
            help="Start with the top bots for this bot type. " "(Requires --genetic)",
        )
        parser.add_argument("--custom", help="Custom argument (passed to bot)")
        parser.add_argument(
            "--loggames",
            action="store_true",
            help="Also log individual games (may require a " "lot of disk space!)",
        )

        args = parser.parse_args()

        if not args.bot1 or not args.bot2:
            print("You need to specify two bots")
            sys.exit(1)

        # Check argument dependencies.
        requires_batch = ["genetic", "samples", "keep", "top"]

        requires_genetic = ["samples", "keep", "top"]

        args_dict = vars(args)
        if args.genetic and args.magic:
            if args.batch:
                parser.error("Cannot use --magic and --batch together")
        elif not args.batch:
            for req in requires_batch:
                if req in args_dict and args_dict[req]:
                    parser.error("Option --{} requires --batch".format(req))

        if not args.genetic:
            for req in requires_genetic:
                if req in args_dict and args_dict[req]:
                    parser.error("Option --{} requires --genetic".format(req))

        return args

    def parse_args(self, args):
        """Parse the command-line arguments."""
        self.game = args.game

        if args.stoponloss:
            self.stop_on_loss = args.stoponloss

        if args.custom:
            self.custom_arg = args.custom

        self.log_games = args.loggames
        self.bot1 = args.bot1
        self.bot2 = args.bot2

        if args.magic or args.batch > 0:
            if args.magic:
                self.batch_size = 0
            else:
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

                if args.top:
                    self.use_top_bots = True
        return

    def init_logging(self):
        """Set up logging functionality."""
        self.log_base_dir = os.path.join(
            self.base_path, LOG_BASE_PATH, "games", self.game
        )

        try:
            os.makedirs(self.log_base_dir, exist_ok=True)
        except IOError as e:
            quit_game(
                "Error creating game log dir '{}': {}".format(self.log_base_dir, str(e))
            )

        self.data_path = os.path.join(self.base_path, DATA_BASE_PATH)
        try:
            os.makedirs(self.data_path, exist_ok=True)
        except IOError as e:
            quit_game("Error creating data dir '{}': {}".format(self.data_path, str(e)))
        return

    def get_game_class(self):
        """Get the class for the SingleGame object for the game type."""
        module_name = "games.{}.singlegame".format(self.game)
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            log_critical("Failed to import game module '{}': {}".format(module_name, e))
            log_critical(traceback.format_exc())
            return

        class_ = getattr(module, "SingleGame")
        return class_

    def get_game_obj(self, parent_context):
        """Get a new instance of the SingleGame object for the game type."""
        class_ = self.get_game_class()
        return class_(parent_context=parent_context)
