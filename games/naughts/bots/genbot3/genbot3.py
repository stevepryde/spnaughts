"""Same as genbot2, but with smart mutation."""

from collections import deque
import os
import random


from games.naughts.bots.bot_base import NaughtsBot
from games.naughts.bots.genbot3 import nodes


NODES = [
    nodes.NODE_INPUT,
    nodes.NODE_OUTPUT,
    nodes.NODE_NOT,
    nodes.NODE_AND,
    nodes.NODE_OR,
    nodes.NODE_XOR,
    nodes.NODE_NAND,
    nodes.NODE_NOR,
    nodes.NODE_XNOR,
]

NODE_DEFS = {k: v for k, v in enumerate(NODES)}


def get_node_type_index(node):
    """Get index for node type."""
    return NODES.index(node.__class__)


class GENBOT3(NaughtsBot):
    """Genbot3 - as per genbot2 but with smart mutation."""

    def __init__(self, *args, **kwargs):
        """Create new GENBOT2."""
        super().__init__(*args, **kwargs)
        self.genetic = True
        self.nodes = []
        self.output_nodes = []
        self.node_hits = {}
        self.num_nodes = 100
        return

    @property
    def recipe(self):
        """Get the recipe for this bot."""
        recipe = ""
        for node in [*self.nodes, *self.output_nodes]:
            nodetype = get_node_type_index(node)
            ingredient = str(nodetype)
            for input_node in node.input_nodes:
                ingredient += ":{}".format(input_node.index)

            if recipe:
                recipe += ",{}".format(ingredient)
            else:
                recipe = ingredient

        return recipe

    def to_dict(self):
        """Serialise."""
        self.set_data("recipe", self.recipe)
        return super().to_dict()

    def from_dict(self, data_dict):
        """Load data and metadata from dict."""
        super().from_dict(data_dict)
        self.create_from_recipe(self.get_data("recipe"))
        return

    def create(self):
        """Create a new GENBOT2, using the specified config.

        Create new brain consisting of random nodes.
        """
        self.log_trace("Creating brain")

        self.nodes = []
        self.output_nodes = []

        # First create input nodes. 3 x 9.
        for _ in range(3):
            for _ in range(9):
                self.nodes.append(nodes.NODE_INPUT())

        # Now generate random nodes.
        for n in range(self.num_nodes):
            # Create a random node.
            node = self.get_random_node_instance()
            node.index = n

            # Connect up a random sample of input nodes.
            node.input_nodes = random.sample(self.nodes, node.num_inputs)

            # Add this node.
            self.nodes.append(node)

        # Now add output nodes.
        for n in range(9):
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
            nodetype = int(ingredient_blocks[0])
            class_ = NODE_DEFS[nodetype]
            instance = class_()

            if nodetype != 0:  # NODE_INPUT
                inputs_required = instance.num_inputs
                assert len(ingredient_blocks) == inputs_required + 1

                for input_number in ingredient_blocks[1:]:
                    instance.add_input_node(self.nodes[int(input_number)])

            if nodetype == 1:  # NODE_OUTPUT
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

        # Always pick the worst node.
        bad_nodes = self.get_metadata("bad_nodes")
        # print("BAD NODE: {}".format(bad_nodes[0]))

        # for index in range(10):
        index = random.choice(bad_nodes[:20])
        node = self.nodes[index]  # random.choice(mutable_nodes)
        num_inputs = node.num_inputs

        input_numbers = random.sample(range(node.index), num_inputs)
        node.input_nodes = []
        for num in input_numbers:
            node.input_nodes.append(self.nodes[num])
        return self

    def get_random_node_instance(self):
        """Create new random node instance."""
        nodepool = ["NOT", "AND", "OR", "XOR", "NAND", "NOR", "XNOR"]

        selected_node_name = "NODE_" + random.choice(nodepool)
        class_ = getattr(nodes, selected_node_name)
        instance = class_()
        return instance

    def setup(self):
        """Setup bot - called before every game."""
        self.node_hits = {}
        return

    def do_turn(self, game_obj):
        """Do one turn."""
        current_board = game_obj
        moves = self.get_possible_moves(current_board)

        # ENGAGE BRAIN
        self.log.trace("Engaging brain")

        # Populate input nodes with the current board state.
        for p in range(9):
            self.nodes[p].set_value(current_board.getat(p) == " ")

        my_id = self.identity
        for p in range(9):
            self.nodes[p + 9].set_value(current_board.getat(p) == my_id)

        their_id = self.other_identity
        for p in range(9):
            self.nodes[p + 18].set_value(current_board.getat(p) == their_id)
        self.log_trace("Input nodes are populated")

        # Now process the brain.
        for index in range(27, len(self.nodes)):
            self.nodes[index].update()

        self.log.trace("Brain has been processed")

        # And finally process the output nodes.
        for node in self.output_nodes:
            node.update()

        self.log.trace("Output nodes have been processed")

        # Now sort moves according to the value of the output nodes.
        dsort = {}
        for move in moves:
            dsort[move] = self.output_nodes[move].output

        sorted_moves = sorted(dsort, key=dsort.__getitem__, reverse=True)
        selected_move = int(sorted_moves[0])

        # Trace output node back
        self.back_propagation(selected_move)

        return selected_move
        # END OF BRAIN ENGAGEMENT

    def back_propagation(self, move):
        """Trace output node back to input and flag the active nodes."""
        q = deque()
        q.append(self.output_nodes[move])

        while q:
            node = q.popleft()
            self.node_hits.setdefault(node.index, 0)
            self.node_hits[node.index] += 1
            if node.input_nodes:
                q.extend(node.input_nodes)
        return

    def process_game_result(self, result):
        """
        Process the result of a single game.

        Note that this bot instance will not accumulate any state from other
        games. Use it to update the state, and then process the state data
        from all games in process_batch_result().

        :param result: GameResult object.
        """
        return

    def process_batch_result(self, score, score_other, clones):
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
        node_hits_total = {}
        for clone in clones:
            for k, v in clone.node_hits.items():
                node_hits_total.setdefault(k, 0)
                if clone.score < 0:  # LOSS
                    node_hits_total[k] -= v
                else:  # WIN
                    node_hits_total[k] += v

        # TODO: this needs work - it performs worse than genbot2 :(

        # prioritise nodes that weren't touched.
        # for node_index in range(27, self.num_nodes):
        #     node_hits_total.setdefault(node_index, 0)

        bad_node_list = sorted(node_hits_total, key=node_hits_total.__getitem__)

        # Exclude input nodes
        # TODO: obviously it would be better to exclude these earlier!
        new_node_list = [x for x in bad_node_list if x >= 27]

        # print("BAD NODE: {} score {}".format(
        #     new_node_list[0], node_hits_total[new_node_list[0]]))
        self.set_metadata("bad_nodes", new_node_list)
        return

