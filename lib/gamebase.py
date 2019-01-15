"""Base generic game object."""

from typing import Any, Dict, List

from lib.gamecontext import GameContext
from lib.gameplayer import GamePlayer


class GameBase(GameContext):
    """Base object for a game."""

    identities = ("1", "2")

    def __init__(self, parent_context: GameContext) -> None:
        """Create a new GameBase object."""
        super().__init__(parent_context=parent_context)
        self.bots = []  # type: List[GamePlayer]
        self.num_turns = {}  # type: Dict[str, int]
        self.current_bot_id = 0
        return

    def is_ended(self) -> bool:
        """Return True if the game has ended, otherwise False."""
        return True

    def start(self, bots: List[GamePlayer]) -> None:
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

    def do_turn(self) -> Any:
        """Process one game turn."""
        return

    def run(self, bots: List[GamePlayer]) -> Dict[str, Any]:
        """Run this game.

        :param bots: Tuple containing bots.
        :returns: GameResult object.
        """
        self.start(bots)

        while not self.is_ended():
            self.do_turn()

        return self.get_result()

    def get_result(self) -> Dict[str, Any]:
        """Process and return game result."""
        return {}
