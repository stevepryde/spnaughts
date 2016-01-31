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
# genbot2.py
#
# Same as genbot1, except all of the moves are determined by the magic
# algorithm, not just the non-obvious ones.
#
#
#

import os, random
from game.log import *
from robots.genetic_robot_base import GeneticRobot
from robots.genbot2 import nodes

class GENBOT2(GeneticRobot):
  def create(self, config):
    self.nodes = []
    self.output_nodes = []

    self.initial_recipe = None
    if (config['custom']):
      params = config['custom'].split(',')
      for param in params:
        parts = param.split(':')
        if (parts[0] == 'recipefile'):
          recipefn = parts[1]
          if (not os.path.exists(recipefn)):
            log_error("Recipe file '{}' not found".format(recipefn))
          else:
            try:
              with open(recipefn, 'rb') as rf:
                self.initial_recipe = rf.read()

              # Strip trailing newline chars.
              self.initial_recipe = self.initial_recipe.decode('UTF8')
              self.initial_recipe = self.initial_recipe.rstrip('\n')
              self.log_debug("Loaded recipe from file '{}'".format(recipefn))
            except OSError as e:
              log_error("Error reading recipe from file '{}': {}".
                        format(recipefn, str(e)))
              return

    if (self.initial_recipe):
      self.create_from_recipe(self.initial_recipe)
    else:
      self.create_brain()

    return

  def create_brain(self):
    self.log_trace('Creating brain')

    self.nodes = []
    self.output_nodes = []

    # First create input nodes. 3 x 9.
    for n in range(3):
      for i in range(9):
        self.nodes.append(nodes.NODE_INPUT())

    # Now generate random nodes.
    num_nodes = 500
    for n in range(num_nodes):
      # Create a random node.
      node = self.get_random_node_instance()
      node.index = n

      # Connect up a random sample of input nodes.
      node.set_input_nodes(random.sample(self.nodes, node.get_num_inputs()))

      # Add this node.
      self.nodes.append(node)

    # Now add output nodes.
    for n in range(9):
      # Create output node.
      node = nodes.NODE_OUTPUT()

      node.set_input_nodes(random.sample(self.nodes, node.get_num_inputs()))

      self.output_nodes.append(node)

    # And we're done.

    return

  def get_recipe(self):
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

  def create_from_recipe(self, recipe):
    self.nodes = []
    self.output_nodes = []

    node_index = 0
    recipe_blocks = recipe.split(',')
    for recipe_block in recipe_blocks:
      ingredient_blocks = recipe_block.split(':')
      classname = ingredient_blocks[0]
      class_ = getattr(nodes, classname)
      instance = class_()

      if (classname != 'NODE_INPUT'):
        inputs_required = instance.get_num_inputs()
        assert(len(ingredient_blocks) == inputs_required + 1)

        for input_number in ingredient_blocks[1:]:
          instance.add_input_node(self.nodes[int(input_number)])

      if (classname == 'NODE_OUTPUT'):
        self.output_nodes.append(instance)
      else:
        self.nodes.append(instance)

        instance.index = node_index
        node_index += 1

    return

  def mutate_recipe(self, recipe):
    recipe_blocks = recipe.split(',')

    # Get list of non-output nodes.
    normal_node_count = 0
    for block in recipe_blocks:
      ingredient = block.split(':')

      if (ingredient[0] == 'NODE_OUTPUT'):
        break

      normal_node_count += 1

    # If we hit an input node, try again, up to 10 times.
    for num_tries in range(10):
      mutated_index = random.randrange(len(recipe_blocks))

      ingredient = recipe_blocks[mutated_index]
      ingredient_blocks = ingredient.split(':')

      name = ingredient_blocks[0]
      if (name == 'NODE_INPUT'):
        continue

      node = None

      if (name == 'NODE_OUTPUT'):
        class_ = getattr(nodes, name)
        node = class_()
      else:
        # Output nodes must stay as output nodes, but all others can be changed.
        node = self.get_random_node_instance()
        name = type(node).__name__

      num_inputs = node.get_num_inputs()
      new_ingredient_blocks = [name]

      # The inputs must come from non-output nodes, and with an index lower than
      # the current index.
      max_index = min(mutated_index, normal_node_count - 1)

      input_numbers = random.sample(range(max_index), num_inputs)
      for num in input_numbers:
        new_ingredient_blocks.append(str(num))

      # Replace the ingredient.
      recipe_blocks[mutated_index] = ':'.join(new_ingredient_blocks)
      break

    return ','.join(recipe_blocks)

  def get_random_node_instance(self):
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

  def do_turn(self, current_board):
    moves = self.get_possible_moves(current_board)

    # ENGAGE BRAIN

    self.log_trace('Engaging brain')

    # Populate input nodes with the current board state.
    i = 0
    for p in range(9):
      if (current_board.getat(p) == ' '):
        self.nodes[i].set_value(1)
      else:
        self.nodes[i].set_value(0)

      i += 1

    my_id = self.get_identity()

    for p in range(9):
      if (current_board.getat(p) == my_id):
        self.nodes[i].set_value(1)
      else:
        self.nodes[i].set_value(0)

      i += 1

    their_id = self.get_their_identity()

    for p in range(9):
      if (current_board.getat(p) == their_id):
        self.nodes[i].set_value(1)
      else:
        self.nodes[i].set_value(0)

      i += 1

    self.log_trace('Input nodes are populated')

    # Now process the brain.
    for index in range(i, len(self.nodes)):
      self.nodes[index].update()

    self.log_trace('Brain has been processed')

    # And finally process the output nodes.
    for node in self.output_nodes:
      node.update()

    self.log_trace('Output nodes have been processed')

    # Now sort moves according to the value of the output nodes.
    dsort = {}
    for move in moves:
      dsort[move] = self.output_nodes[move].get_output()

    sorted_moves = sorted(dsort, key=dsort.__getitem__, reverse=True)

    return int(sorted_moves[0])

    # END OF BRAIN ENGAGEMENT

  def log_debug(self, message):
    log_debug("[GENBOT2]: " + message)
    return

  def log_trace(self, message):
    log_trace("[GENBOT2]: " + message)
    return
