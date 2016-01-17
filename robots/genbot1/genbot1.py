# genbot1.py
#
# The first attempt at a bot using a genetic algorithm to 'grow' it's own
# "brain".
#
# See nodes.py for some more details.
#
# Basically we start with manually populating 27 nodes. These are all 'fixed'
# input nodes. The first 9 will be set to 1 for each blank space otherwise 0.
# The second set of 9 will be set to 1 for each space we own, otherwise 0. The
# third set of 9 will be set to 1 for each space the opponent owns, otherwise 0.
# (Perhaps that third set will be redundant? don't know)
#
# To generate a brain, start adding nodes by choosing a new node type at random,
# then add the number of required inputs from the pool of available nodes.
#
# There are a couple of ways to do this.
# 1. Layer by layer. Enforce a set number of nodes at each level. When adding
#    new nodes, only input nodes from the preceding layer may be used.
# 2. Random. Each new node can accept input from any existing nodes. That still
#    favours lower-numbered nodes but does not enforce any set number of nodes
#    at each level.
#
# Might need to experiment with either approach.
# It would be good to use some standard notation to serialise the brain.
# For example, if we assign a letter for each node type, then we can use the
# following notation: AAAAAAAAAAAAAAAAAAAAB1B4C2,3C4,10D3,2 and so on.
# In this example, the 'A' node is the special input node, and 'B' node has only
# a single input, which refers to the 'A' node at position 1. The second 'B' node
# gets its input from position 4. The next node is a 'C' node, which takes inputs
# from both position 2 and 3. Note that the later 'D' node can also accept input
# from position 3 and 2. This allows more complex trees, and multiple paths can
# do calculations based on the same input data.
#
# Using this approach, we then just grow the brain as much as we want. We need
# to make sure we insert OUTPUT nodes throughout, and we need to make sure we
# at least have an OUTPUT node for each position from 0-8. It would be good to
# enforce the same number of OUTPUT nodes for each position, too.
#
# Once we have this, then it's just a matter of "running" the brain - which just
# means setting the values of all inputs, and then calling update() for every
# node beyond that in order. Just walk the node list in sequence. The "tree"
# aspect will just sort itself out.
#
# When that's done, we just read off the outputs (these will have been incremented
# during processing when each relevant output node was triggered), and choose
# the valid output (i.e. only look for moves we can actually do) with the highest
# value.
#
# If there are two or more with equal value, just choose at random. Or if they're all 0,
# perhaps we should discard this robot?
#
# The last stage after that is the higher level process of scoring each robot game
# and feeding the score back into the system so that we can 'mutate' the best scoring
# brains and start over. Mutations should be easy to do. We can just mutate any one
# of the nodes in the list, or even just do a basic mutation on the "genetic" notation itself.
# Mutating the genetics is nicer, because we can do funky things like insert or delete nodes
# (which would throw everything off by 1) etc. This part might need some experimenting.
# At the very least, we could rewire nodes easily.
#
# This is the point where things will get interesting, or not. It could all be
# a flop. We won't know until we get to here. And even then it will probably be
# difficult to debug. But there are ways to do it. Probably need to construct contrived
# simple brains and step through it all. Won't that be fun.
#
# NOTES:
# Completed implementation 2016-01-08.
# Not seeing good results - probably because the scoring is too coarse, and
# I don't have good bots to train against.
# Perhaps I need to try this with a more complex "game".
#
# Update: 2016-01-17
# - Using randombot as the first player and genbot1 as the second player,
#   with batch size of 1000 and sample size of 100, I'm seeing more interesting
#   results. The scores are more fine-grained.
# - When compared with genbotcontrol, genbot1 consistently achieves higher
#   scores. This tells me that some level of improvement has been achieved.
#   One wonders how many generations are needed to get close to a 'perfect' bot.
# - Games run quite slowly for this sort of testing. I need to speed things up.
#
# ------
#
# - So I've managed to clean up the game runner code and implement
#   multi-threading (using the multiprocesing module) - it runs a lot faster now.

import os, random
from game.log import *
from robots.genetic_robot_base import GeneticRobot
from robots.genbot1 import nodes

class GENBOT1(GeneticRobot):
  def create(self, config):

    # Create temp path if it doesn't exist.
    #self.get_temp_path()
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

    # First, win the game if we can.
    straight_sequences = ['012',
                          '345',
                          '678',
                          '036',
                          '147',
                          '258',
                          '048',
                          '246']

    for seq in straight_sequences:
      (ours, theirs, blanks) = self.get_sequence_info(current_board, seq)
      if (len(ours) == 2 and len(blanks) == 1):
        # Move into the blank for the win.
        return int(blanks[0])

    # Second, if we can't win, make sure the opponent can't win either.
    for seq in straight_sequences:
      (ours, theirs, blanks) = self.get_sequence_info(current_board, seq)
      if (len(theirs) == 2 and len(blanks) == 1):
        # Move into the blank to block the win.
        return int(blanks[0])

    # If this is the first move...
    (ours, theirs, blanks) = self.get_sequence_info(current_board, '012345678')
    if (len(ours) == 0):
      # If we're the second player:
      if (len(theirs) > 0):
        if (4 in moves):
          return 4

        # Otherwise take the upper left.
        return 0

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

    # # Otherwise pick the first move from a series of preferred moves.
    # self.log_debug("Fall back to next move in preferred list")
    # preferred_moves_str = '402681357'
    # preferred_moves = list(preferred_moves_str)
    # for move in preferred_moves:
    #   if (int(move) in moves):
    #     return int(move)

    # print("MOVES contains: " + str(moves))
    # # Shouldn't be here!
    # raise Exception("GENBOT1 failed!")

    # return random.choice(moves)

  def log_debug(self, message):
    log_debug("[GENBOT1]: " + message)
    return

  def log_trace(self, message):
    log_trace("[GENBOT1]: " + message)
    return
