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

    def __init__(self) -> None:
        """Create a new GamePlayer object."""
        super().__init__()
        self.identity = ""
        self._score = None  # type: Optional[float]
        self.genetic = False
        self.data = {}  # type: Dict[str, Any]
        self.name = ""
        return

    def clone_from(self, other: "GamePlayer") -> None:
        """Clone the data and metadata from another bot."""
        self.set_state(other.get_state())
        return

    @property
    def score(self) -> float:
        """Get the bot score (only available after the game has finished)."""
        assert self._score is not None, "Bot score accessed before game end!"
        return self._score

    @score.setter
    def score(self, value: float) -> None:
        """Set the score."""
        self._score = value
        return

    def clear_score(self) -> None:
        """Clear the player score."""
        self._score = None
        return

    @property
    def label(self) -> str:
        """Return the name of this player, as a string."""
        return "{} ({})".format(self.__class__.__name__, self.identity)

    def set_data(self, key: str, value: Any) -> None:
        """Set the specified data, as given by key and value."""
        self.data[key] = value
        return

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get the data for this key."""
        return self.data.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Get full bot state. Subclasses should override get_state() instead."""
        state = self.data
        state["name"] = self.name
        state.update(self.get_state())
        return state

    def from_dict(self, state: Dict[str, Any]) -> None:
        """Load state from dict. Subclasses should override set_state() instead."""
        self.data = copy.deepcopy(state)
        self.set_state(state)
        return

    def get_state(self) -> Dict[str, Any]:
        """Get current state as dict. Override as needed."""
        return {}

    def set_state(self, state: Dict[str, Any]) -> None:
        """Load state from dict. Override as needed."""
        return

    def create(self, game_info: Dict[str, Any]) -> None:
        """Create the bot. Called immediately following instantiation."""
        return

    def mutate(self) -> None:
        """Mutate this bot's state (genetic bots only)."""
        assert self.genetic, "Attempted to mutate non-genetic bot!"
        return

    def setup(self) -> None:
        """Set up this bot. Called before every game."""
        return

    def process(self, inputs: List[float], available_moves: List[float]) -> float:
        """Process one game turn."""
        return 0.0
