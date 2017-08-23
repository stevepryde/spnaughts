"""Base class for genetic bots."""


from games.naughts.bots.bot_base import Bot


class GeneticBot(Bot):
    """Genetic Bot class."""

    def __init__(self, *args, **kwargs):
        """Create a new GeneticBot."""
        super().__init__(*args, **kwargs)
        self.genetic = True
        return

    def mutate_recipe(self, recipe, num_mutations=1):
        """Mutate the specified recipe."""
        return recipe

    def get_mutated_recipe(self, num_mutations):
        """Mutate the internal recipe the specified number of times."""
        recipe = self.recipe
        for _ in range(num_mutations):
            recipe = self.mutate_recipe(recipe)
        return recipe
