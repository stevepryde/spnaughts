"""Same as genbot1, except all moves use the magic algorithm."""


import random
from typing import Any, Dict, List

from lib.gameplayer import GamePlayer
from bots.genbot3 import nodes


class GenBot3(GamePlayer):
    """Genbot3 :: Generic Edition. All moves are determined by the brain algorithm."""

    def __init__(self):
        """Create new GenBot3."""
        super().__init__()
        self.genetic = True
        self.nodes = []
        self.output_nodes = []
        return

    def get_recipe(self):
        """Get the recipe for this bot."""
        recipe_blocks = []
        nodelist = list(self.nodes)
        nodelist.extend(list(self.output_nodes))

        for node in nodelist:
            name = type(node).__name__
            ingredient_blocks = [name]
            for input_node in node.input_nodes:
                ingredient_blocks.append(str(input_node.index))

            recipe_blocks.append(":".join(ingredient_blocks))
        return ",".join(recipe_blocks)

    def get_state(self) -> Dict[str, Any]:
        """Save bot data."""
        return {"recipe": self.get_recipe()}

    def set_state(self, state: Dict[str, Any]) -> None:
        """Load bot from previous state."""
        recipe = state["recipe"]
        self.create_from_recipe(recipe)
        return

    def create(self, game_info: Dict[str, Any]) -> None:
        """Create a new GENBOT2, using the specified config.

        Create new brain consisting of random nodes.
        """
        self.nodes = []
        self.output_nodes = []

        # First create input nodes.
        for n in range(game_info.get("input_count", 1)):
            node = nodes.NODE_INPUT()
            node.index = n
            self.nodes.append(node)

        # Now generate random nodes.
        num_nodes = 100
        next_index = len(self.nodes)
        for n in range(num_nodes):
            # Create a random node.
            node = self.get_random_node_instance()
            node.index = next_index

            # Connect up a random sample of input nodes.
            node.input_nodes = random.sample(self.nodes, node.num_inputs)

            # Add this node.
            self.nodes.append(node)
            next_index += 1

        # Now add output nodes.
        for _ in range(game_info.get("output_count", 1)):
            # Create output node.
            node = nodes.NODE_OUTPUT()
            node.input_nodes = random.sample(self.nodes, node.num_inputs)
            self.output_nodes.append(node)

        # And we're done.
        return

    def create_from_recipe(self, recipe):
        """Create bot from recipe."""
        self.nodes = []
        self.output_nodes = []

        node_index = 0
        recipe_blocks = recipe.split(",")
        for recipe_block in recipe_blocks:
            ingredient_blocks = recipe_block.split(":")
            classname = ingredient_blocks[0]
            class_ = getattr(nodes, classname)
            instance = class_()

            if classname != "NODE_INPUT":
                inputs_required = instance.num_inputs
                assert len(ingredient_blocks) == inputs_required + 1

                for input_number in ingredient_blocks[1:]:
                    instance.add_input_node(self.nodes[int(input_number)])

            if classname == "NODE_OUTPUT":
                self.output_nodes.append(instance)
            else:
                self.nodes.append(instance)
                instance.index = node_index
                node_index += 1
        return

    def mutate_output_node(self):
        """Mutate output node."""
        node_indexes = []
        for index, node in enumerate(self.nodes):
            if not node.input_nodes:
                continue
            node_indexes.append(index)

        node = random.choice(self.output_nodes)
        index = random.randint(0, len(node.input_nodes) - 1)
        node.input_nodes[index] = self.nodes[random.choice(node_indexes)]
        return

    def mutate(self):
        """Mutate the bot."""
        if random.choice([0, 1]):
            self.mutate_output_node()
            return

        mutable_node_indexes = []
        for index, node in enumerate(self.nodes):
            if not node.input_nodes:
                continue
            mutable_node_indexes.append(index)

        node_index = random.choice(mutable_node_indexes)
        if random.choice([0, 1]):
            node = self.get_random_node_instance()
            node.index = node_index
            self.nodes[node_index] = node
        else:
            node = self.nodes[node_index]

        # Also change/set inputs.
        num_inputs = node.num_inputs

        input_numbers = random.sample(range(node.index), num_inputs)
        node.input_nodes = []
        for num in input_numbers:
            node.input_nodes.append(self.nodes[num])
        return

    def get_random_node_instance(self):
        """Create new random node instance."""
        nodepool = ["NOT", "AND", "OR", "XOR", "NAND", "NOR", "XNOR"]

        selected_node_name = "NODE_" + random.choice(nodepool)
        class_ = getattr(nodes, selected_node_name)
        instance = class_()
        return instance

    def process(self, inputs: List[float], available_moves: List[float]) -> float:
        """Process one game turn."""
        for p, input_value in enumerate(inputs):
            self.nodes[p].set_value(input_value)

        # ENGAGE BRAIN.
        for index in range(len(inputs), len(self.nodes)):
            self.nodes[index].update()

        # And finally process the output nodes.
        for node in self.output_nodes:
            node.update()

        # Get best move.
        best_move = available_moves[0]
        best_output = 0
        for m in available_moves:
            if self.output_nodes[m].output > best_output:
                best_move = m
                best_output = self.output_nodes[m].output

        return best_move
        # END OF BRAIN ENGAGEMENT
