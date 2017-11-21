"""Object containing player details."""

import copy
import json

from lib.gamecontext import GameContext
from lib.globals import log_error


class GamePlayer(GameContext):
    """Object containing player details."""

    def __init__(self, parent_context):
        """Create a new GamePlayer object."""
        super().__init__(parent_context)
        self._score = None
        self.identity = ''
        self.temppath = None
        self.genetic = False
        self.metadata = {}
        self.data = {}
        self.name = ''
        return

    def clone_from(self, other):
        """Clone the data and metadata from another bot."""
        self.data = copy.deepcopy(other.data)
        self.metadata = copy.deepcopy(other.metadata)
        self.score = other.score
        return

    @property
    def label(self):
        """Return the name of this player, as a string."""
        return "{} ({})".format(self.__class__.__name__, self.identity)

    @property
    def score(self):
        """Get the bot's score."""
        assert self._score is not None, "Score for player '{}' not set". \
            format(self.name)
        return self._score

    @score.setter
    def score(self, value):
        """Set the bot's score."""
        self._score = value
        return

    def clear_score(self):
        """Set the score to None."""
        self.score = None
        return

    def set_data(self, key, value):
        """Set the specified data, as given by key and value."""
        self.data[key] = value
        return

    def get_data(self, key, default=None):
        """Get the data for this key."""
        return self.data.get(key, default)

    def set_metadata(self, key, value):
        """Set the specified metadata, as given by key and value."""
        self.metadata[key] = value
        return

    def get_metadata(self, key, default=None):
        """Get the metadata for this key."""
        return self.metadata.get(key, default)

    def to_dict(self):
        """Serialise the data and metadata and return dict."""
        all_data = {'data': self.data,
                    'metadata': self.metadata,
                    'score': self.score}
        return all_data

    def from_dict(self, data_dict):
        """Load data and metadata from dict."""
        self.data = data_dict.get('data', {})
        self.metadata = data_dict.get('metadata', {})
        self.score = data_dict.get('score')
        return

    def mutate(self):
        """Mutate this bot (genetic bots only)."""
        assert self.genetic, "Attempted to mutate non-genetic bot!"
        return self

    def setup(self):
        """Set up this bot. Called before every game."""
        return

    def do_turn(self, game_obj):
        """Process one game turn."""
        return

    def process_result(self, status, score):
        """
        Process the result of a single game.

        :param status: One of, 'TIE', 'WIN', or 'LOSS'.
        :param score: The score achieved by this bot.
        """
        return
