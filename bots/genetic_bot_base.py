"""Base class for genetic bots, so that we know which methods need to be
implemented.
"""


from bots.bot_base import Bot


class GeneticBot(Bot):
    """Genetic Bot class"""

    def __init__(self):
        """Create a new GeneticBot."""
        super().__init__()
        self.genetic = True
        return

    def mutate_recipe(self, recipe):
        """Mutate the specified recipe.

        Args:
            recipe: The recipe to mutate.

        Returns:
            The mutated recipe.
        """
        return recipe

    def get_mutated_recipe(self, num_mutations):
        """Mutate the internal recipe the specified number of times.

        Args:
            num_mutations: The number of times to mutate the recipe.

        Returns:
            The final mutated recipe.
        """
        recipe = self.recipe
        for _ in range(num_mutations):
            recipe = self.mutate_recipe(recipe)
        return recipe
