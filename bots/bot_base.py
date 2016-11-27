"""Base class for AI naughts and crosses bots.
All bots must implement do_turn().
Bots can optionally implement setup() and process_result().
"""


import os


class Bot:
    """Base class for all bots."""

    def __init__(self):
        """Create new Bot."""

        self.__identity = '' # This will be set to X or O.
        self.__name = '' # This will be set by the game runner.

        # Temporary path where data may be stored. This is unique to this bot.
        self.temppath = None
        self.genetic = False
        self.__score = None
        self.metadata = {}
        return

    def create(self, config):
        """Create bot, with the given config."""
        return

    @property
    def identity(self):
        """str: Return the identity character for this bot ('X' or 'O')."""
        return self.__identity

    @identity.setter
    def identity(self, ident):
        """Set the identity character for this bot."""
        self.__identity = ident
        return

    @property
    def other_identity(self):
        """str: Get the identity character for the other bot."""
        if (self.identity == 'X'):
            return 'O'
        return 'X'

    @property
    def name(self):
        """str: The name of this bot."""
        return self.__name

    @name.setter
    def name(self, _name):
        """str: Set the name of this bot."""
        self.__name = _name
        return

    @property
    def score(self):
        """int: Get the score for this bot."""
        return self.__score

    @score.setter
    def score(self, newscore):
        """Set the score for this bot."""
        self.__score = newscore
        return

    @property
    def recipe(self):
        """str: Get the recipe for this bot."""
        return None

    def clear_score(self):
        """Set the score to None."""
        self.score = None
        return

    def set_metadata(self, key, value):
        """Set the specified metadata, as given by key and value."""
        self.metadata[key] = value
        return

    def get_metadata(self, key):
        """Get the metadata for this key.

        Returns:
            The metadata associated with the specified key.
        """
        return self.metadata.get(key)

    def create_from_recipe(self, recipe):
        """Create this bot from the specified recipe.

        Args:
            recipe: The recipe from which to create this bot.
        """
        return

    def get_temp_path(self):
        """Get the temp path for this bot, creating it if necessary.

        Returns:
            The temporary path for this bot.
        """
        assert self.temppath is not None
        os.makedirs(self.temppath, exist_ok=True)
        return self.temppath

    def set_temp_path_base(self, temppathbase):
        """Set the base temp path.

        Args:
            temppathbase: The base temp path to set.
        """
        lcname = str(self.__class__.__name__).lower()
        self.temppath = os.path.join(temppathbase, lcname)
        return

    def setup(self):
        """Set up this bot."""
        return

    def do_turn(self, current_board):
        """The main method for this bot. The game runner will supply the
        current board, and this method must return a position 0-8 for this turn.

        Returns:
            The position of the proposed move.
        """
        return 0

    def process_result(self, status, score):
        """Process the result.

        Args:
            status (str): One of, 'TiE', 'WIN', or 'LOSS'.
            score (float): The score achieved by this bot.
        """
        return

    ############################################################################
    #
    # HELPER METHODS
    # These are methods that are probably generally useful to several bots.
    #
    ############################################################################

    def get_possible_moves(self, current_board):
        """Get all possible moves for the specified board.

        Args:
            current_board: The specified board to find possible moves for.

        Returns:
            List of possible moves.
        """
        possible = []
        for pos in range(9):
            if (current_board.getat(pos) == ' '):
                possible.append(pos)

        return possible

    def get_sequence_info(self, _board, sequence):
        """Return info about the given sequence, in the form of 3 lists.

        Args:
            _board: The board to query.
            sequence: The sequence to get information for.

        Returns:
            Tuple containing 3 lists.
            The first list will be all positions matching my own identity.
            The second list will be all positions matching the other identity.
            The third list will be all blank positions.
        """

        ours = []
        theirs = []
        blanks = []

        seq_list = [int(x) for x in list(sequence)]

        for c in seq_list:
            val = _board.getat(c)
            if (val == self.identity):
                ours.append(c)
            elif (val == ' '):
                blanks.append(c)
            else:
                theirs.append(c)

        return (ours, theirs, blanks)

    def get_unrotated_move(self, move, rotations):
        """
        Return the correct, unrotated move that corresponds to the move we
        would make on a board rotated the specified number of times.
        For example, if rotations is 1, and I want to get the corrected move for
        move 0, this would return 6. If rotations is 2, and I want the corrected
        move for 1, this would return 7.

        Args:
            move: The move to make.
            rotations: The number of 90 degree rotations, in a clockwise
                       direction.

        Returns:
            The move, rotated anti-clockwise by the number of specified
            rotations.
        """

        rotations = int(rotations) % 4

        # Don't do anything if we don't have to.
        if (rotations == 0):
            return int(move)

        transform_map = [6, 3, 0, 7, 4, 1, 8, 5, 2]
        for _ in range(rotations):
            move = transform_map[int(move)]

        return move

    def get_opponent(self, me=None):
        """Get the identity of the opponent.

        Args:
            me: Identity character for this bot. If not specified,
                self.identity will be used.

        Returns:
            The identity character of the other bot.
        """
        if (not me):
            me = self.identity

        if (me == 'X'):
            return 'O'

        return 'X'

    def get_filename(self, _basename):
        """Get the filename for this bot.

        Args:
            _basename: The base filename to use.
        """
        assert self.temppath is not None
        return os.path.join(self.temppath, _basename)
