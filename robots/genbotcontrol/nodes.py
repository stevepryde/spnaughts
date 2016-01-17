# nodebase.py
#
# Base brain node class.

from robots.genbot1.nodebase import NODEBASE, NODEBASE2

# The input node is a custom node that gets pre-set with each move. This is
# done by the robot itself, by reading the game board and populating each input
# node manually.
#
# This node is not available for inclusion in the rest of the brain.
class NODE_INPUT(NODEBASE):
  def set_value(self, value):
    self.output = value
    return

# NODE NOT: return 1 if input is 0, otherwise return 0.
class NODE_NOT(NODEBASE):
  def process(self, inputs):
    return not inputs[0]

##
# NODE_AND: return 1 if both inputs are 1.
class NODE_AND(NODEBASE2):
  def process(self, inputs):
    return inputs[0] and inputs[1]

##
# NODE OR: return 1 if either input is 1.
class NODE_OR(NODEBASE2):
  def process(self, inputs):
    return inputs[0] or inputs[1]

##
# NODE XOR: return 1 if either input is 1 but not both.
class NODE_XOR(NODEBASE2):
  def process(self, inputs):
    if (inputs[0] and inputs[1]):
      return 0

    return inputs[0] or inputs[1]

class NODE_NAND(NODEBASE2):
  def process(self, inputs):
    if (inputs[0] and inputs[1]):
      return 0

    return 1

class NODE_NOR(NODEBASE2):
  def process(self, inputs):
    if (inputs[0] or inputs[1]):
      return 0

    return 1

class NODE_XNOR(NODEBASE2):
  def process(self, inputs):
    if (inputs[0] and inputs[1]):
      return 1

    if (inputs[0] or inputs[1]):
      return 0

    return 1

##
# The following node is just one idea for ways to generate an output node.
# It is probably analogous to the below idea, and much simpler.
# The more inputs, the more easily we can sort between outcomes.
class NODE_OUTPUT(NODEBASE):
  def __init__(self):
    super(NODE_OUTPUT, self).__init__()
    self.num_inputs = 10
    return

  def process(self, inputs):
    total = 0
    for i in inputs:
      total += i

    return total


##
#
# IDEA: set up a special "OUTPUT" node, which is a node that stores a value 0-8
# and a callback. If it receives a 'true' signal, it calls the callback with that
# value, otherwise it just returns the signal it receives.
#
# The robot can determine which move to make by choosing the move 0-8 that has the highest count.
# That is, more output nodes for that position have fired than any others.
# The robot would only check the values for the valid available moves, which it knows already.

