"""Base brain node class."""


class NodeBase:
    """Base class for brain nodes."""

    def __init__(self):
        """Create new NodeBase."""
        self.num_inputs = 1
        self.input_nodes = []
        self.output = 0
        self.index = 0
        return

    def add_input_node(self, node):
        """Append the specified node to the list of input nodes."""
        self.input_nodes.append(node)
        return

    def process(self, inputs):
        """Process this node, given the specified inputs."""
        return 1

    def update(self):
        """
        Process this node.

        Get the output values from each of the linked inputs, and pass
        those values to process(), and then store the returned value in
        self.output.
        By calling update() on every node in sequence, we can process the
        entire tree.
        """
        inputs = []
        for node in self.input_nodes:
            inputs.append(node.output)

        self.output = self.process(inputs)
        return


class NodeBase2(NodeBase):
    """Second base node class, used for nodes with 2 inputs."""

    def __init__(self):
        """Create new NodeBase2."""
        super().__init__()
        self.num_inputs = 2
        return
