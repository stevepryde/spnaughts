"""Object containing player details."""

import copy
import json
from typing import Any, Dict, List, Optional, TYPE_CHECKING


from lib.gamecontext import GameContext
from lib.gameresult import GameResult
from lib.globals import log_error

if TYPE_CHECKING:
    from lib.gamebase import GameBase


class GamePlayer(GameContext):
    """Object containing player details."""

    def __init__(self, parent_context: GameContext) -> None:
        """Create a new GamePlayer object."""
        super().__init__(parent_context)
        self._score = None  # type: Optional[float]
        self.identity = ""
        self.temppath = None  # type: Optional[str]
        self.genetic = False
        self.metadata = {}  # type: Dict[str, Any]
        self.data = {}  # type: Dict[str, Any]
        self.name = ""
        return

    def clone_from(self, other: "GamePlayer") -> None:
        """Clone the data and metadata from another bot."""
        self.data = copy.deepcopy(other.data)
        self.metadata = copy.deepcopy(other.metadata)
        self.score = other.score
        return

    @property
    def label(self) -> str:
        """Return the name of this player, as a string."""
        return "{} ({})".format(self.__class__.__name__, self.identity)

    @property
    def score(self) -> float:
        """Get the bot's score."""
        assert self._score is not None, "Score for player '{}' not set".format(self.name)
        return self._score

    @score.setter
    def score(self, value: Optional[float]) -> None:
        """Set the bot's score."""
        self._score = value
        return

    def clear_score(self) -> None:
        """Set the score to None."""
        self.score = None  # type: ignore
        return

    def set_data(self, key: str, value: Any) -> None:
        """Set the specified data, as given by key and value."""
        self.data[key] = value
        return

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get the data for this key."""
        return self.data.get(key, default)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set the specified metadata, as given by key and value."""
        self.metadata[key] = value
        return

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get the metadata for this key."""
        return self.metadata.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the data and metadata and return dict."""
        all_data = {"data": self.data, "metadata": self.metadata, "score": self.score}
        return all_data

    def from_dict(self, data_dict: Dict[str, Any]) -> None:
        """Load data and metadata from dict."""
        self.data = data_dict.get("data", {})
        self.metadata = data_dict.get("metadata", {})
        self.score = data_dict.get("score")  # type: ignore
        return

    def mutate(self) -> "GamePlayer":
        """Mutate this bot (genetic bots only)."""
        assert self.genetic, "Attempted to mutate non-genetic bot!"
        return self

    def create(self) -> None:
        """Create the bot. Called immediately following instantiation."""
        return

    def setup(self) -> None:
        """Set up this bot. Called before every game."""
        return

    def do_turn(self, game_obj: "GameBase") -> Any:
        """Process one game turn."""
        return

    def process_game_result(self, result: GameResult) -> None:
        """
        Process the result of a single game.

        Note that this bot instance will not accumulate any state from other
        games. Use it to update the state, and then process the state data
        from all games in process_batch_result().

        :param result: GameResult object.
        """
        return

    def process_batch_result(
        self, score: float, score_other: float, clones: List["GamePlayer"]
    ) -> None:
        """
        Process the result of a batch.

        Each game creates a new clone, and each clone holds the data from
        process_game_result(). This function is called at the end of the
        batch to allow processing of the data from all of the games,
        represented by the list of clones.

        Note that the bot instance on which process_batch_result() is called
        knows nothing about the previous games, and must use the clones to
        process the data collected during games.

        :param score: My average score.
        :param score_other: The other bot's average score.
        :param clones: List of bot clones, each containing data.

        """
        return
