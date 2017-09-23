"""Object containing player details."""

from lib.gamecontext import GameContext


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
        self.name = ''
        return

    @property
    def recipe(self):
        """Get the recipe for this bot."""
        return ''

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

    def mutate_recipe(self, recipe, num_mutations=1):
        """Mutate the specified recipe (genetic bots only)."""
        return recipe

    def get_mutated_recipe(self, num_mutations):
        """Mutate the internal recipe the specified number of times."""
        recipe = self.recipe
        for _ in range(num_mutations):
            recipe = self.mutate_recipe(recipe)
        return recipe
