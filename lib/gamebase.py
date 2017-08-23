"""Base generic game object."""


from lib.log import log_info


class GameBase:
    """Base object for a game."""

    identities = ('1', '2')

    def __init__(self, config):
        """Create a new GameBase object."""
        self.config = config
        self.bots = []
        self.game_log_lines = []
        self.num_turns = {}
        return

    def get_game_log(self):
        """Return the full game log."""
        return "\n".join(self.game_log_lines)

    def log_game(self, message):
        """Write the specified message to the game log."""
        if not self.config.silent:
            log_info(message)

        self.game_log_lines.append(message)
        return

    def is_ended(self):
        """Return True if the game has ended, otherwise False."""
        return True

    def start(self, bots):
        """Start a new game."""
        self.bots = bots

        for bot in self.bots:
            bot.setup()

        self.log_game("START GAME")
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
