"""Object containing player details."""


class GamePlayer:
    """Object containing player details."""

    def __init__(self, config):
        """Create a new GamePlayer object."""
        self.config = config
        self._score = None
        self.identity = ''
        self.temppath = None
        self.genetic = False
        self.metadata = {}
        self.name = ''
        return

    @property
    def label(self):
        """Return the name of this player, as a string."""
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
