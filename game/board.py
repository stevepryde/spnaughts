"""
The Board class provides a representation of a naughts and crosses board.

It consists of 9 characters,
3 lots of 3, reading left to right, top to bottom.
- = blank space. X and O are represented by exactly those letters (uppercase).
"""

class Board:
    """Representation of a naughts and crosses board."""

    def __init__(self):
        """Create a new Board object."""
        self.data = '---------'
        return




    def copy(self):
        """Clone this Board instance.

        Returns:
            New Board object that is a clone of this instance.
        """

        b = Board()
        b.data = self.data
        return b

    def getat(self, pos):
        """Get the character at the specified position.

        Args:
            pos: The 0-based position within 'data'.
                 i.e.
                  0 | 1 | 2
                 -----------
                  3 | 4 | 5
                 -----------
                  6 | 7 | 8

        Returns:
            Character at the specified position. One of 'X', 'O', or ' '.
        """
        c = self.data[int(pos)]
        if (c == '-'):
            c = ' '

        return c

    def setat(self, pos, turn):
        """Set the character at the specified position.

        Args:
            pos: The 0-based position within 'data'.
                 i.e.
                  0 | 1 | 2
                 -----------
                  3 | 4 | 5
                 -----------
                  6 | 7 | 8

            turn: The character to set.
        """
        c = self.getat(pos)
        assert c == ' ', ("Tried setting '{}' at pos {} but it already "
                          "contained '{}'").format(turn, pos, c)

        # Can't modify strings in place, so use a list instead.
        newdata = list(self.data)
        newdata[pos] = turn
        newdata_str = ''.join(newdata)

        assert len(newdata_str) == 9, ("Invalid board length after set. "
                                       "New data is '{}'".format(newdata_str))
        self.data = newdata_str
        return

    def show(self, indent=0):
        """Print the current board contents, with optional indent.

        Args:
            indent: The number of spaces to use as indent. Default is 0.
        """

        prefix = '  '
        if (indent > 0):
            prefix += ' ' * indent

        i = 0
        for r in range(0,3):
            print(prefix + " {} | {} | {} ".
                  format(self.getat(i), self.getat(i+1), self.getat(i+2)))

            if (r < 2):
                print(prefix + "-----------")

            i += 3

        print("")
        return

    def get_game_state(self):
        """Get current game state.

        Returns:
            Current game state, as int.
            0 = Not completed.
            1 = X win.
            2 = O win.
            3 = draw.
        """

        sequences = ['012',
                     '345',
                     '678',
                     '036',
                     '147',
                     '258',
                     '048',
                     '246'
                     ]

        for seq in sequences:
            val = ''
            for n in range(len(seq)):
                c = seq[n]
                val += self.getat(int(c))

            if (val == 'XXX'):
                return 1
            elif (val == 'OOO'):
                return 2

            is_draw = True
            for pos in range(9):
                val = self.getat(pos)
                if (val != 'X' and val != 'O'):
                    is_draw = False

            if (is_draw):
                return 3

        return 0

    def is_ended(self):
        """Return True if game has ended.

        Returns:
            True if the game has ended, otherwise False.
        """
        return self.get_game_state() != 0

    def get_winner(self):
        """Get the game winner, if there is one.

        Returns:
            Character identifying the game winner, or None if the game has not
            been won (includes draw).
        """
        state = self.get_game_state()

        if (state == 1):
            return 'X'

        if (state == 2):
            return 'O'

        return


    ##########################################################
    # HELPER METHODS for use in bots.
    ##########################################################

    def getat_multi(self, pos_str):
        """
        Return a string containing just the contents at the specified positions.
        For example, if I pass in '012', it will return a string identifying the
        contents of the top row.

        Args:
            pos_str: List of positions.

        Returns:
            String containing the characters at the specified positions.
        """

        contents = ''
        for n in range(len(pos_str)):
            contents += self.getat(int(pos_str[n]))

        return contents

    def get_rotated_board(self, rotations):
        """
        Return a copy of the board, rotated 90/180/270 degrees clockwise.
        The number of rotations is 1 for 90 degrees, 2 for 180 degrees,
        and 3 for 270 degrees.

        Args:
            rotations: Number of 90 degree rotations in a clockwise direction.

        Returns:
            Board object that is a rotated copy of this one.
        """

        rotations = int(rotations) % 4

        board_copy = self.copy()
        transform_map = [6, 3, 0, 7, 4, 1, 8, 5, 2]

        # Minor optimisation. Don't do anything if we don't have to.
        if (rotations == 0):
            return board_copy

        for _ in range(rotations):
            orig_data = board_copy.data

            new_data = list(orig_data)
            for index, pos in enumerate(transform_map):
                new_data[index] = orig_data[pos]

            board_copy.data = ''.join(new_data)

        return board_copy

    def get_first_empty_space(self, positions):
        """Get the first empty position from the list of positions.

        Args:
            positions: List of positions to check.

        Returns:
            First empty position as int, or -1 if no position was empty.
        """
        pos_list = list(positions)

        for pos in pos_list:
            if (self.getat(int(pos)) == ' '):
                return int(pos)

        return -1
