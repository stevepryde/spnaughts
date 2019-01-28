"""
Base generic game object.

Run games thus:
    game = GameBase()  # Actually you would use a subclass here.
    game.start(bots)  # Or if existing state, game.load_from_state(bots, state)
    game.run()
"""

from typing import Any, Dict, List, Tuple

from lib.errors import GameCreateError
from lib.gamecontext import GameContext
from lib.gameplayer import GamePlayer
from lib.gameresult import GameResult


class GameBase(GameContext):
    """Base object for a game."""

    identities = ("1", "2")
    input_count = 0  # This MUST be overridden by subclass.

    def __init__(self) -> None:
        """Create a new GameBase object."""
        super().__init__()
        self.bots = []  # type: List[GamePlayer]
        self.num_turns = {}  # type: Dict[str, int]
        self.current_bot_index = 0

        # State is explicitly saved after each move.
        self.saved_state = {}  # type: Dict[str, Any]
        return

    @classmethod
    def get_game_info(cls) -> Dict[str, Any]:
        """Get game info."""
        return {"input_count": cls.input_count}

    @property
    def current_identity(self) -> str:
        """Get the current bot identity."""
        return self.identities[self.current_bot_index]

    def start(self, bots: List[GamePlayer]) -> None:
        """Start a new game."""
        if self.input_count <= 0:
            raise GameCreateError("Game input_count has not been set!")

        self.bots = bots
        assert len(self.bots) == len(
            self.identities
        ), "Unexpected number of bots provided. Expected {}, got {}".format(
            len(self.identities), len(self.bots)
        )

        for i, bot in enumerate(self.bots):
            # NOTE: The bot identity is set in the bot for the bot's use only.
            # The game object should not trust this identity to be accurate.
            # The game object should use self.current_identity instead.
            bot.identity = self.identities[i]
            bot.setup()

        self.num_turns = {k: 0 for k in self.identities}
        return

    def load_from_state(self, bots: List[GamePlayer], state: Dict[str, Any]) -> None:
        """Load game from saved state."""
        self.start(bots)
        self.set_state(state)
        return

    def do_turn(self, bot: GamePlayer) -> Any:
        """Process one game turn."""
        self.num_turns[self.current_identity] += 1
        inputs, available_moves = self.get_inputs(self.current_identity)
        assert (
            len(inputs) == self.input_count
        ), "Incorrect number of inputs returned from get_inputs(): Expected {}, got {}".format(
            self.input_count, len(inputs)
        )
        output = bot.process(inputs, available_moves)
        self.update(self.current_identity, output)
        return

    def run(self) -> GameResult:
        """Run this game and return the result."""
        while not self.is_ended():
            self.do_turn(self.bots[self.current_bot_index])
            self.current_bot_index += 1
            if self.current_bot_index >= len(self.bots):
                self.current_bot_index = 0
            self.saved_state = self.get_state()

        # Get scores and update bots.
        result = self.get_result()
        for i, bot in enumerate(self.bots):
            bot.score = result.get_score(self.identities[i])
        return result

    ############################################################################
    # GAME METHODS: Game is defined by the following overridden methods.
    ############################################################################

    def set_initial_state(self) -> None:
        """Set the initial game state."""
        return

    def set_state(self, state: Dict[str, Any]) -> None:
        """Apply state to this game object."""
        self.num_turns = state.get("num_turns", {})
        self.current_bot_index = state.get("current_bot_index", 0)
        bot_state = state.get("bots", {})

        for i, identity in enumerate(self.identities):
            bs = bot_state.get(identity, {})
            self.bots[i].set_state(bs)
        return

    def get_state(self) -> Dict[str, Any]:
        """Get the game state."""
        state = {"num_turns": self.num_turns, "current_bot_index": self.current_bot_index}
        bot_state = {}

        for i, identity in enumerate(self.identities):
            bot_state[identity] = self.bots[i].get_state()

        state["bots"] = bot_state
        return state

    def get_inputs(self, identity: str) -> Tuple[List[float], List[float]]:
        """Convert current game state into a list of player-specific inputs."""
        return ([], [])

    def update(self, identity: str, output: float) -> None:
        """Update the current game state based on the specified output."""
        return

    def is_ended(self) -> bool:
        """Return True if the game has ended, otherwise False."""
        return True

    def get_result(self) -> GameResult:
        """Process and return game result."""
        return GameResult()

