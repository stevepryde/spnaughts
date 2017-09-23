"""Base generic game object."""


from lib.gamecontext import GameContext
from lib.globals import get_config, log_info


class GameBase(GameContext):
    """Base object for a game."""

    identities = ('1', '2')

    def __init__(self, parent_context):
        """Create a new GameBase object."""
        super().__init__(parent_context)
        self.bots = []
        self.num_turns = {}
        self.current_bot_id = 0
        return

    def is_ended(self):
        """Return True if the game has ended, otherwise False."""
        return True

    def start(self, bots):
        """Start a new game."""
        self.bots = bots

        for bot in self.bots:
            bot.setup()

        self.log.info("START GAME")
        self.current_bot_id = 0
        self.num_turns = {}
        for identity in self.identities:
            self.num_turns[identity] = 0
        return

    def do_turn(self):
        """Process one game turn."""
        return

    def run(self, bots):
        """Run this game.

        :param bots: Tuple containing bots.
        :returns: GameResult object.
        """
        self.start(bots)

        while not self.is_ended():
            self.do_turn()

        return self.get_result()

    def get_result(self):
        """Process and return game result."""
        return
