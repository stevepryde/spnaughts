"""
My first attempt at a bot using a genetic algorithm.

See nodes.py for some more details.

High level description:
-----------------------

Basically we start with manually populating 27 nodes. These are all 'fixed'
input nodes. The first 9 will be set to 1 for each blank space otherwise 0.
The second set of 9 will be set to 1 for each space we own, otherwise 0. The
third set of 9 will be set to 1 for each space the opponent owns, otherwise 0.
(Perhaps that third set will be redundant? don't know)

To generate a brain, start adding nodes by choosing a new node type at random,
then add the number of required inputs from the pool of available nodes.

There are a couple of ways to do this.
1. Layer by layer. Enforce a set number of nodes at each level. When adding
   new nodes, only input nodes from the preceding layer may be used.
2. Random. Each new node can accept input from any existing nodes. That still
   favours lower-numbered nodes but does not enforce any set number of nodes
   at each level.

For now this bot only uses the second method.

It would be good to use some standard notation to serialise the brain.
For example, if we assign a letter for each node type, then we can use the
following notation: AAAAAAAAAAAAAAAAAAAAB1B4C2,3C4,10D3,2 and so on.
(NOTE: for now, genbot1 uses the full node name, followed by a colon-separated
list of inputs)

In this example, the 'A' node is the special input node, and 'B' node has only
a single input, which refers to the 'A' node at position 1. The second 'B'
node gets its input from position 4. The next node is a 'C' node, which takes
inputs from both position 2 and 3. Note that the later 'D' node can also
accept input from position 3 and 2. This allows more complex trees, and
multiple paths can do calculations based on the same input data.

Using this approach, we then just grow the brain as much as we want.
Output nodes are just special nodes with multiple inputs that are summed up
to give a value. Each output node corresponds to an available action. The
action taken is determined by the output node with the highest value.

Once we have this, then it's just a matter of 'running' the brain - which just
means setting the values of all inputs, and then calling update() for every
node beyond that in order. Just walk the node list in sequence. The 'tree'
aspect will just sort itself out.

When that's done, we just read off the outputs, and choose the valid output
(i.e. only look for moves we can actually do) with the highest value.

If there are two or more with equal value, just choose at random.
(Or if they're all 0, perhaps we should discard this bot?)

The last stage after that is the higher level process of scoring each bot
game and feeding the score back into the system so that we can 'mutate' the
best scoring brains and start over. Mutations should be easy to do. We can
just mutate any one of the nodes in the list, or even just do a basic mutation
on the "genetic" notation itself. Mutating the genetics is nicer, because we
can do funky things like insert or delete nodes (which would throw everything
off by 1) etc. This part might need some experimenting.

At the very least, we could rewire nodes easily. This is what the bot does
currently.
"""


import random
from typing import Any, Dict

from games.naughts.board import Board
from games.naughts.bots.genbot1 import nodes
from games.naughts.bots.naughtsbot import NaughtsBot


class GenBot1(NaughtsBot):
    """My first genetic bot attempted."""

    def __init__(self, *args, **kwargs):
        """Create new GenBot1."""
        super().__init__(*args, **kwargs)
        self.genetic = True
        self.nodes = []
        self.output_nodes = []
        return

    def get_recipe(self) -> str:
        """Get the recipe for this bot."""
        recipe_blocks = []
        nodelist = list(self.nodes)
        nodelist.extend(list(self.output_nodes))

        for node in nodelist:
            name = type(node).__name__
            ingredient_blocks = [name]
            for input_node in node.input_nodes:
                ingredient_blocks.append(str(input_node.index))

            recipe_blocks.append(":".join(ingredient_blocks))

        return ",".join(recipe_blocks)

    def get_state(self) -> Dict[str, Any]:
        """Save bot data."""
        return {"recipe": self.get_recipe()}

    def set_state(self, state: Dict[str, Any]) -> None:
        """Load bot from previous state."""
        recipe = state["recipe"]
        self.create_from_recipe(recipe)
        return

    def create(self, game_info: Dict[str, Any]) -> None:
        """Create a new GENBOT1, using the specified config.

        Create new brain consisting of random nodes.
        """
        self.nodes = []
        self.output_nodes = []

        # First create input nodes. 3 x 9.
        for _ in range(3):
            for _ in range(9):
                self.nodes.append(nodes.NODE_INPUT())

        # Now generate random nodes.
        num_nodes = 500
        for n in range(num_nodes):
            # Create a random node.
            node = self.get_random_node_instance()
            node.index = n
            # Connect up a random sample of input nodes.
            node.input_nodes = random.sample(self.nodes, node.num_inputs)
            # Add this node.
            self.nodes.append(node)

        # Now add output nodes.
        for n in range(9):
            # Create output node.
            node = nodes.NODE_OUTPUT()
            node.input_nodes = random.sample(self.nodes, node.num_inputs)
            self.output_nodes.append(node)

        # And we're done.
        return

    def create_from_recipe(self, recipe: str) -> None:
        """Create new bot from recipe."""
        self.nodes = []
        self.output_nodes = []

        node_index = 0
        recipe_blocks = recipe.split(",")
        for recipe_block in recipe_blocks:
            ingredient_blocks = recipe_block.split(":")
            classname = ingredient_blocks[0]
            class_ = getattr(nodes, classname)
            instance = class_()

            if classname != "NODE_INPUT":
                inputs_required = instance.num_inputs
                assert len(ingredient_blocks) == inputs_required + 1

                for input_number in ingredient_blocks[1:]:
                    instance.add_input_node(self.nodes[int(input_number)])

            if classname == "NODE_OUTPUT":
                self.output_nodes.append(instance)
            else:
                self.nodes.append(instance)
                instance.index = node_index
                node_index += 1
        return

    def mutate(self) -> None:
        """Mutate the bot."""
        mutable_nodes = []
        for node in self.nodes:
            if not node.input_nodes:
                continue
            mutable_nodes.append(node)

        node = random.choice(mutable_nodes)
        num_inputs = node.num_inputs

        input_numbers = random.sample(range(node.index), num_inputs)
        node.input_nodes = []
        for num in input_numbers:
            node.input_nodes.append(self.nodes[num])
        return

    def get_random_node_instance(self) -> nodes.NodeBase:
        """Create random node instance."""
        nodepool = ["NOT", "AND", "OR", "XOR", "NAND", "NOR", "XNOR"]

        selected_node_name = "NODE_" + random.choice(nodepool)
        class_ = getattr(nodes, selected_node_name)
        instance = class_()
        return instance

    def do_turn(self, current_board: Board):
        """Do one turn."""
        moves = current_board.get_possible_moves()

        # First, win the game if we can.
        straight_sequences = ["012", "345", "678", "036", "147", "258", "048", "246"]

        for seq in straight_sequences:
            (ours, theirs, blanks) = self.get_sequence_info(current_board, seq)
            if len(ours) == 2 and len(blanks) == 1:
                # Move into the blank for the win.
                return int(blanks[0])

        # Second, if we can't win, make sure the opponent can't win either.
        for seq in straight_sequences:
            (ours, theirs, blanks) = self.get_sequence_info(current_board, seq)
            if len(theirs) == 2 and len(blanks) == 1:
                # Move into the blank to block the win.
                return int(blanks[0])

        # If this is the first move...
        (ours, theirs, blanks) = self.get_sequence_info(current_board, "012345678")
        if not ours:
            # If we're the second player:
            if theirs:
                if 4 in moves:
                    return 4

                # Otherwise take the upper left.
                return 0

        # ENGAGE BRAIN
        # Populate input nodes with the current board state.
        for p in range(9):
            self.nodes[p].set_value(current_board.getat(p) == " ")

        my_id = self.identity
        for p in range(9):
            self.nodes[p + 9].set_value(current_board.getat(p) == my_id)

        their_id = self.other_identity
        for p in range(9):
            self.nodes[p + 18].set_value(current_board.getat(p) == their_id)

        # Now process the brain.
        for index in range(27, len(self.nodes)):
            self.nodes[index].update()

        # And finally process the output nodes.
        for node in self.output_nodes:
            node.update()

        # Now sort moves according to the value of the output nodes.
        dsort = {}
        for move in moves:
            dsort[move] = self.output_nodes[move].output

        sorted_moves = sorted(dsort, key=dsort.__getitem__, reverse=True)
        return int(sorted_moves[0])
        # END OF BRAIN ENGAGEMENT
