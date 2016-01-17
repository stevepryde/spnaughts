# nodebase.py
#
# Base brain node class.

class NODEBASE(object):
  def __init__(self):
    self.num_inputs = 1
    self.input_nodes = []
    self.output = 0
    return

  def get_num_inputs(self):
    return self.num_inputs

  def get_output(self):
    return self.output

  def add_input_node(self, node):
    self.input_nodes.append(node)
    return

  def set_input_nodes(self, nodes):
    self.input_nodes = nodes
    return

  def process(self, inputs):
    return 1

  def update(self):
    """
    Process this node, getting the output values from each of the linked
    inputs, and passing those values to process(), and then storing the returned
    value in self.output.
    By calling update() on every node in sequence, we can process the entire tree.
    """
    inputs = []
    for node in self.input_nodes:
      inputs.append(node.get_output())

    self.output = self.process(inputs)
    return

class NODEBASE2(NODEBASE):
  def __init__(self):
    super(NODEBASE2, self).__init__()
    self.num_inputs = 2
    return
