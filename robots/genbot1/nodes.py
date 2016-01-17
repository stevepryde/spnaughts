################################################################################
# SP Naughts - Simple naughts and crosses game including a collection of AI bots
# Copyright (C) 2015, 2016 Steve Pryde
#
# This file is part of SP Naughts.
#
# SP Naughts is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SP Naughts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SP Naughts.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
# nodebase.py
#
# Brain node classes.
#
# These are basically all of the standard boolean logic operators.
# The higher-level 'emergent' behaviour stems from combinations of these nodes.
#

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
# The more inputs, the more easily we can sort between outcomes.
# The number of inputs should be at least the number of possible actions.
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
