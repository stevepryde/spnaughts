"""Basic neural network with blind genetic algorithm and no back propagation."""

import json
import os
import random
from typing import Any, Dict, List

from lib.gameplayer import GamePlayer
from .neurons import InputNeuron, Neuron, NeuronLayer, sigmoid


class NBot1(GamePlayer):
    """NBOT1 - all moves are determined by the neural net."""

    def __init__(self):
        """Create new NBOT1."""
        super().__init__()
        self.genetic = True
        self.input_nodes = []
        self.layers = []
        self.nodes_per_layer = 9
        self.num_layers = 4
        self.created = False
        return

    @property
    def recipe(self):
        """Get the recipe for this bot."""
        dlayers = [x.to_dict() for x in self.layers]
        return json.dumps({"nodes": self.nodes_per_layer, "layers": dlayers})

    def get_state(self) -> Dict[str, Any]:
        """Get current state as dict. Override as needed."""
        return {"recipe": self.recipe}

    def set_state(self, state: Dict[str, Any]) -> None:
        """Load state from dict. Override as needed."""
        self.create_from_recipe()
        return

    def create(self, game_info: Dict[str, Any]) -> None:
        """Create a new NBOT1, using the specified config.

        Create new brain consisting of random nodes.
        """
        self.log.trace("Creating brain")

        self.input_nodes = []
        self.layers = []
        self.set_data("game_info", game_info)

        for _ in range(game_info.get("input_count", 1)):
            self.input_nodes.append(InputNeuron())

        prev_layer_nodes = self.input_nodes
        for _ in range(self.num_layers):
            layer = NeuronLayer.generate(
                num_nodes=self.nodes_per_layer, parent_nodes=prev_layer_nodes
            )
            self.layers.append(layer)
            prev_layer_nodes = layer.nodes

        # Output layer.
        layer = NeuronLayer.generate(
            num_nodes=game_info.get("output_count", 1), parent_nodes=prev_layer_nodes
        )
        self.layers.append(layer)

        # And we're done.
        return

    def create_from_recipe(self, input_count: int = 0):
        """Create bot from recipe."""
        recipe = self.get_data("recipe")
        assert recipe, "Recipe not found!"

        game_info = self.get_data("game_info")
        assert game_info, "Game info not set!"

        d = json.loads(recipe)
        self.input_nodes = []
        self.layers = []

        for _ in range(game_info.get("input_count", 1)):
            self.input_nodes.append(InputNeuron())

        dlayers = d.get("layers", [])
        prev_layer_nodes = self.input_nodes

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
                node.input_weights[i] = sigmoid((random.random() * 2.0) - 1.0)
            else:
                node.bias = sigmoid((random.random() * 2.0) - 1.0)

        return self

    def process(self, inputs: List[float], available_moves: List[float]) -> float:
        """Process one game turn."""
        for p, input_value in enumerate(inputs):
            self.input_nodes[p].output = input_value

        # Now process the brain.
        for layer in self.layers:
            layer.process()

        # And finally process the output nodes.
        output_layer = self.layers[-1]

        # Now sort moves according to the value of the output nodes.
        dsort = {}
        for move in available_moves:
            dsort[move] = output_layer.nodes[move].output

        sorted_moves = sorted(dsort, key=dsort.get, reverse=True)
        selected_move = int(sorted_moves[0])

        return selected_move
