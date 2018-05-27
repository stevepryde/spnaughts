"""Same as genbot1, except all moves use the magic algorithm."""


import os
import random


from games.naughts.bots.bot_base import Bot
from games.naughts.bots.genbot2 import nodes


class GENBOT2(Bot):
    """Genbot2 - all moves are determined by the brain algorithm."""

    def __init__(self, *args, **kwargs):
        """Create new GENBOT2."""
        super().__init__(*args, **kwargs)
        self.genetic = True
        self.nodes = []
        self.output_nodes = []
        return

    @property
    def recipe(self):
        """Get the recipe for this bot."""
        recipe_blocks = []
        nodelist = list(self.nodes)
        nodelist.extend(list(self.output_nodes))

        for node in nodelist:
            name = type(node).__name__
            ingredient_blocks = [name]
            for input_node in node.input_nodes:
                ingredient_blocks.append(str(input_node.index))

            recipe_blocks.append(':'.join(ingredient_blocks))
        return ','.join(recipe_blocks)

    def to_dict(self):
        """Serialise."""
        self.set_data('recipe', self.recipe)
        return super().to_dict()

    def from_dict(self, data_dict):
        """Load data and metadata from dict."""
        super().from_dict(data_dict)
        self.create_from_recipe(self.get_data('recipe'))
        return

    def create(self):
        """Create a new GENBOT2, using the specified config.

        Create new brain consisting of random nodes.
        """
        self.log_trace('Creating brain')

        self.nodes = []
        self.output_nodes = []

        # First create input nodes. 3 x 9.
        for _ in range(3):
            for _ in range(9):
                self.nodes.append(nodes.NODE_INPUT())

        # Now generate random nodes.
        num_nodes = 100
        for n in range(num_nodes):
            # Create a random node.
            node = self.get_random_node_instance()
            node.index = n

            # Connect up a random sample of input nodes.
            node.input_nodes = random.sample(self.nodes,
                                             node.num_inputs)

            # Add this node.
            self.nodes.append(node)

        # Now add output nodes.
        for n in range(9):
            # Create output node.
            node = nodes.NODE_OUTPUT()

            node.input_nodes = random.sample(self.nodes,
                                             node.num_inputs)

            self.output_nodes.append(node)

        # And we're done.
        return

    def create_from_recipe(self, recipe):
        """Create bot from recipe."""
        self.nodes = []
        self.output_nodes = []

        node_index = 0
        recipe_blocks = recipe.split(',')
        for recipe_block in recipe_blocks:
            ingredient_blocks = recipe_block.split(':')
            classname = ingredient_blocks[0]
            class_ = getattr(nodes, classname)
            instance = class_()

            if classname != 'NODE_INPUT':
                inputs_required = instance.num_inputs
                assert len(ingredient_blocks) == inputs_required + 1

                for input_number in ingredient_blocks[1:]:
                    instance.add_input_node(self.nodes[int(input_number)])

            if classname == 'NODE_OUTPUT':
                self.output_nodes.append(instance)
            else:
                self.nodes.append(instance)
                instance.index = node_index
                node_index += 1
        return

    def mutate(self):
        """Mutate the bot."""
        mutable_nodes = []
        for node in self.nodes:
            if not node.input_nodes:
                continue
            mutable_nodes.append(node)

        node = random.choice(mutable_nodes)
        num_inputs = node.num_inputs

        input_numbers = random.sample(range(node.index), num_inputs)
        node.input_nodes = []
        for num in input_numbers:
            node.input_nodes.append(self.nodes[num])
        return self

    def get_random_node_instance(self):
        """Create new random node instance."""
        nodepool = ['NOT',
                    'AND',
                    'OR',
                    'XOR',
                    'NAND',
                    'NOR',
                    'XNOR']

        selected_node_name = 'NODE_' + random.choice(nodepool)
        class_ = getattr(nodes, selected_node_name)
        instance = class_()
        return instance

    def do_turn(self, game_obj):
        """Do one turn."""
        current_board = game_obj
        moves = self.get_possible_moves(current_board)

        # ENGAGE BRAIN
        self.log.trace('Engaging brain')

        # Populate input nodes with the current board state.
        for p in range(9):
            self.nodes[p].set_value(current_board.getat(p) == ' ')

        my_id = self.identity
        for p in range(9):
            self.nodes[p + 9].set_value(current_board.getat(p) == my_id)

        their_id = self.other_identity
        for p in range(9):
            self.nodes[p + 18].set_value(current_board.getat(p) == their_id)
        self.log_trace('Input nodes are populated')

        # Now process the brain.
        for index in range(27, len(self.nodes)):
            self.nodes[index].update()

        self.log.trace('Brain has been processed')

        # And finally process the output nodes.
        for node in self.output_nodes:
            node.update()

        self.log.trace('Output nodes have been processed')

        # Now sort moves according to the value of the output nodes.
        dsort = {}
        for move in moves:
            dsort[move] = self.output_nodes[move].output

        sorted_moves = sorted(dsort, key=dsort.__getitem__, reverse=True)
        selected_move = int(sorted_moves[0])

        return selected_move
        # END OF BRAIN ENGAGEMENT
