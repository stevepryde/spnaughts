"""Classes for managing neurons."""

import math
import random


def sigmoid(x):
    return 1 / (1 + math.e ** -x)


class InputNeuron:
    """InputNeuron."""

    def __init__(self):
        """Create new InputNeuron."""
        self.output = 0
        return

    def process(self):
        """Process this input."""
        return self.output


class Neuron:
    """Simple brain neuron."""

    def __init__(self):
        """Create new NodeBase."""
        self.input_nodes = []
        self.input_weights = []
        self.bias = 0
        self.output = 0
        return

    @staticmethod
    def generate(parent_nodes):
        """Generate new Neuron."""
        n = Neuron()
        n.bias = 0  # (random.random() * 0.2) - 0.1
        n.input_nodes = list(parent_nodes)

        for _ in range(len(parent_nodes)):
            w = 0  # (random.random() * 2.0) - 1.0
            n.input_weights.append(w)
        return n

    @staticmethod
    def from_dict(d, parent_nodes):
        """Generate from dict."""
        n = Neuron()
        n.bias = d.get("bias", 0)
        n.input_nodes = list(parent_nodes)
        n.input_weights = d.get("input_weights", [])
        assert len(n.input_weights) == len(
            parent_nodes
        ), "Number of input weights does not match number of parent nodes!"
        return n

    def to_dict(self):
        """String representation."""
        return {"bias": self.bias, "input_weights": self.input_weights}

    def process(self):
        """Process this neuron, given the specified inputs."""
        output_sum = 0
        for i, node in enumerate(self.input_nodes):
            output_sum += node.output * self.input_weights[i]
        self.output = sigmoid(output_sum + self.bias)
        return


class NeuronLayer:
    """A single layer of neurons."""

    def __init__(self):
        """A layer of neurons."""
        self.nodes = []
        return

    @staticmethod
    def generate(num_nodes, parent_nodes):
        """Generate layer with random weights."""
        layer = NeuronLayer()
        for _ in range(num_nodes):
            layer.nodes.append(Neuron.generate(parent_nodes))
        return layer

    @staticmethod
    def from_dict(d, parent_nodes):
        """Create layer from recipe."""
        layer = NeuronLayer()
        layer.nodes = [Neuron.from_dict(x, parent_nodes) for x in d.get("nodes", [])]
        return layer

    def to_dict(self):
        """Get layer as a string."""
        return {"nodes": [x.to_dict() for x in self.nodes]}

    def process(self):
        """Process all nodes in this layer."""
        for n in self.nodes:
            n.process()
        return

