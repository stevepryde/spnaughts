"""Basic neural network with blind genetic algorithm and no back propagation."""

import json
import os
import random


from games.naughts.bots.bot_base import NaughtsBot
from games.naughts.bots.nbot1.neurons import InputNeuron, Neuron, NeuronLayer


class NBOT1(NaughtsBot):
    """NBOT1 - all moves are determined by the neural net."""

    def __init__(self, *args, **kwargs):
        """Create new NBOT1."""
        super().__init__(*args, **kwargs)
        self.genetic = True
        self.input_nodes = []
        self.layers = []
        self.nodes_per_layer = 50
        return

    @property
    def recipe(self):
        """Get the recipe for this bot."""
        dlayers = [x.to_dict() for x in self.layers]
        return json.dumps({"nodes": self.nodes_per_layer, "layers": dlayers})

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
        """Create a new NBOT1, using the specified config.

        Create new brain consisting of random nodes.
        """
        self.log_trace("Creating brain")

        self.input_nodes = []
        self.layers = []

        for _ in range(9 * 2):
            self.input_nodes.append(InputNeuron())

        prev_layer_nodes = self.input_nodes
        for _ in range(5):
            layer = NeuronLayer.generate(
                num_nodes=self.nodes_per_layer, parent_nodes=prev_layer_nodes
            )
            self.layers.append(layer)
            prev_layer_nodes = layer.nodes

        # Output layer.
        layer = NeuronLayer.generate(num_nodes=9, parent_nodes=prev_layer_nodes)
        self.layers.append(layer)

        # And we're done.
        return

    def create_from_recipe(self, recipe):
        """Create bot from recipe."""
        d = json.loads(recipe)
        self.input_nodes = []
        self.layers = []

        for _ in range(9 * 2):
            self.input_nodes.append(InputNeuron())

        prev_layer_nodes = self.input_nodes
        dlayers = d.get("layers", [])
        for dlayer in dlayers:
            layer = NeuronLayer.from_dict(dlayer, prev_layer_nodes)
            self.layers.append(layer)
            prev_layer_nodes = layer.nodes
        return

    def mutate(self):
        """Mutate one weight of one input of one node of one layer."""
        for _ in range(1):
            layer = random.choice(self.layers)
            node = random.choice(layer.nodes)
            if random.choice(["weight", "bias"]) == "weight":
                i = random.randint(0, len(node.input_weights) - 1)
                node.input_weights[i] += (random.random() * 0.2) - 0.1
            else:
                node.bias += (random.random() * 0.2) - 0.1
        return self

    def do_turn(self, game_obj):
        """Do one turn."""
        current_board = game_obj
        moves = self.get_possible_moves(current_board)

        # ENGAGE BRAIN
        self.log.trace("Engaging brain")

        # Populate input nodes with the current board state.
        for p in range(9):
            c = current_board.getat(p)
            v1 = 0
            v2 = 0
            if c == self.identity:
                v1 = 1.0
            elif c == self.other_identity:
                v2 = 1.0

            self.input_nodes[p].output = v1
            self.input_nodes[p + 9].output = v2

        self.log_trace("Input nodes are populated")

        # Now process the brain.
        for layer in self.layers:
            layer.process()

        self.log.trace("Brain has been processed")

        # And finally process the output nodes.
        output_layer = self.layers[-1]

        # Now sort moves according to the value of the output nodes.
        dsort = {}
        for move in moves:
            dsort[move] = output_layer.nodes[move].output

        sorted_moves = sorted(dsort, key=dsort.__getitem__, reverse=True)
        selected_move = int(sorted_moves[0])

        return selected_move
        # END OF BRAIN ENGAGEMENT
