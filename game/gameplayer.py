"""Object containing player details."""

# TODO: this will be the base class for bot_base. bot_base will then be
# specific to naughts and crosses.


class GamePlayer:
    """Object containing player details."""

    def __init__(self):
        """Create a new GamePlayer object."""
        self._score = None
        self.identity = None
        self.metadata = {}
        return

    @property
    def name(self):
        """The name of this player, as a string."""
        return "{} ({})".format(self.__class__.__name__, self.identity)

    @property
    def score(self):
        assert self._score is not None, "Score for player '{}' not set". \
            format(self.name)
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        return

    def do_turn(self, game_obj):
        """Process one turn."""
        return

    def set_metadata(self, key, value):
        """Set the specified metadata, as given by key and value."""
        self.metadata[key] = value
        return

    def get_metadata(self, key):
        """Get the metadata for this key."""
        return self.metadata.get(key)
