"""
Brain node classes.

These are basically all of the standard boolean logic operators.
The higher-level 'emergent' behaviour stems from combinations of these nodes.
"""

from bots.genbot2.nodebase import NodeBase, NodeBase2


class NODE_INPUT(NodeBase):
    """The input node is a custom node that gets pre-set with each move. This is
    done by the robot itself, by reading the game board and populating each
    input node manually.

    This node is not available for inclusion in the rest of the brain.
    """

    def set_value(self, value):
        """Set the value for this node. This method is unique to input nodes."""
        self.output = value
        return


class NODE_NOT(NodeBase):
    """NODE NOT: return 1 if input is 0, otherwise return 0."""

    def process(self, inputs):
        """Process this node."""
        return not inputs[0]


class NODE_AND(NodeBase2):
    """NODE_AND: return 1 if both inputs are 1."""

    def process(self, inputs):
        """Process this node."""
        return inputs[0] and inputs[1]


class NODE_OR(NodeBase2):
    """NODE OR: return 1 if either input is 1."""

    def process(self, inputs):
        """Process this node."""
        return inputs[0] or inputs[1]


class NODE_XOR(NodeBase2):
    """NODE XOR: return 1 if either input is 1 but not both."""

    def process(self, inputs):
        """Process this node."""
        if (inputs[0] and inputs[1]):
            return 0

        return inputs[0] or inputs[1]


class NODE_NAND(NodeBase2):
    """NODE NAND: return 1 if either input is 0, otherwise 0."""

    def process(self, inputs):
        """Process this node."""
        if (inputs[0] and inputs[1]):
            return 0

        return 1


class NODE_NOR(NodeBase2):
    """NODE NOR: return 1 if both inputs are 0, otherwise 0."""

    def process(self, inputs):
        """Process this node."""
        if (inputs[0] or inputs[1]):
            return 0

        return 1


class NODE_XNOR(NodeBase2):
    """NODE XNOR: return 1 if both inputs are equal, otherwise 0."""

    def process(self, inputs):
        """Process this node."""
        if (inputs[0] and inputs[1]):
            return 1

        if (inputs[0] or inputs[1]):
            return 0

        return 1


class NODE_OUTPUT(NodeBase):
    """This node is just one idea for ways to generate an output node.
    The more inputs, the more easily we can sort between outcomes.
    The number of inputs should be at least the number of possible actions.
    """

    def __init__(self):
        """Create output node."""
        super().__init__()
        self.num_inputs = 10 # Some number greater than 9.
        return

    def process(self, inputs):
        """Process this node."""
        total = 0
        for i in inputs:
            total += i

        return total
