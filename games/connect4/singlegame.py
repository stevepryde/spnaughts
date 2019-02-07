"""Module for running a single game of Connect 4."""


from typing import Any, Dict, List, Optional, Tuple

from games.connect4.world import World
from lib.gamebase import GameBase
from lib.gameresult import GameResult


class SingleGame(GameBase):
    """Run a single game of Connect 4."""

    identities = ("X", "O")
    input_count = 98  # 49 for each player.
    output_count = 7

    def __init__(self) -> None:
        """Create a new SingleGame object."""
        super().__init__()
        self.world = None  # type: Optional[World]
        return

    def set_initial_state(self) -> None:
        """Set the initial game state."""
        self.world = World()
        return

    def set_state(self, state: Dict[str, Any]) -> None:
        """Apply state to this game object."""
        self.world = World()
        self.world.from_dict(state.get("world", {}))
        return

    def get_state(self) -> Dict[str, Any]:
        """Get the game state."""
        assert self.world, "World not loaded"
        return {"world": self.world.to_dict()}

    def get_inputs(self, identity: str) -> Tuple[List[float], List[float]]:
        """Convert current game state into a list of player-specific inputs."""
        assert self.world, "World not loaded"
        inputs = []
        for row in range(7):
            for col in range(7):
                c = self.world.getat(col, row)
                if c == identity:
                    inputs.append(1.0)
                else:
                    inputs.append(0.0)

        for row in range(7):
            for col in range(7):
                c = self.world.getat(col, row)
                if c == identity or c == " ":
                    inputs.append(0.0)
                else:
                    inputs.append(1.0)
        return inputs, self.world.get_possible_moves()

    def update(self, identity: str, output: float) -> None:
        """Assign closest valid move to this bot."""
        assert self.world, "World not loaded"
        # TODO: The next step is to abort games if a bot returned an invalid move.
        #       This will force bots to learn the game rules first.
        moves = self.world.get_possible_moves()
        assert moves, "No valid move available!"

        target_move = None
        if len(moves) == 1:
            target_move = moves[0]
        else:
            lowest_diff = None
            for move in moves:
                diff = abs(output - move)
                if lowest_diff is None or diff < lowest_diff:
                    lowest_diff = diff
                    target_move = move

        assert target_move is not None, "BUG: update() failed to select target move!"
        self.world.setat(target_move, identity)
        return

    def is_ended(self) -> bool:
        """Return True if the game has ended, otherwise False."""
        assert self.world, "World not loaded"
        return self.world.is_ended()

    def get_result(self) -> GameResult:
        """Process and return game result."""
        assert self.world, "World not loaded"
        for bot in self.bots:
            bot.show_result(self.world)

        result = GameResult()

        assert len(self.bots) == 2, "BUG: bots have not been set up - was this game started?"

        outcome = self.world.get_game_state()
        assert outcome > 0, "BUG: Game ended with invalid state of 0 - was this game finished?"

        outcomes = [0, 0]
        result.set_tie()
        if outcome == 1:
            result.set_win()
            outcomes = [1, -1]
        elif outcome == 2:
            result.set_win()
            outcomes = [-1, 1]
        elif outcome > 3:
            assert (
                False
            ), "BUG: Invalid game outcome returned from board.get_game_state(): {}".format(outcome)

        for i, x in enumerate(self.identities):
            result.set_score(x, self.calculate_score(self.num_turns[x], outcomes[i]))

        return result

    def calculate_score(self, num_turns: int, outcome: int) -> float:
        """
        Calculate the 'score' for this game.

        :param num_turns: The number of turns played.
        :param outcome: 1 if this player won, 0 for a draw, or -1 for a loss.
        :returns: The game score, as float.
        """
        score = 25 - num_turns
        multiplier = 0
        if outcome > 0:
            multiplier = 1
        elif outcome < 0:
            multiplier = -10

        return score * multiplier
