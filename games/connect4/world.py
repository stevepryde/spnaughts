"""
The World class provides a representation of a Connect 4 stand.

It consists of 7 rows of 7-character strings.
Each character in a string can be blank, or contain 'X' or 'O'.
"""

from typing import Any, Dict, List


NEW_WORLD = ["       " for _ in range(7)]


class World:
    """Representation of a Connect 4 stand."""

    def __init__(self) -> None:
        """Create a new World object."""
        self.data = list(NEW_WORLD)
        return

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict."""
        return {"data": self.data}

    def from_dict(self, d: Dict[str, Any]) -> None:
        """Load from dict."""
        self.data = d.get("data", list(NEW_WORLD))
        return

    def copy(self) -> "World":
        """Clone this World instance."""
        b = World()
        b.data = self.data
        return b

    def getat(self, col: int, row: int) -> str:
        """
        Get the character at the specified position.

        :param col: The 0-based column (left to right).
        :param row: The 0-based row (0 = bottom row).

        :returns: Character at the specified position. One of 'X', 'O', or ' '.
        """
        return self.data[int(row)][int(col)]

    def setat_raw(self, col: int, row: int, turn: str) -> None:
        """Set the character at the specified position, without gravity."""
        newrow = list(self.data[int(row)])
        newrow[int(col)] = turn
        newrow_str = "".join(newrow)

        assert len(newrow_str) == 7, "Invalid row length after set!"
        self.data[int(row)] = newrow_str
        return

    def setat(self, col: int, turn: str) -> None:
        """Set the character at the specified position.

        :param col: The 0-based column (left to right).

        :param turn: The character to set.
        """
        row = 0
        for r in reversed(range(7)):
            c = self.getat(col, r)
            if c != " ":
                assert r < 6, "Cannot place character at position {}".format(col)
                row = r + 1
                break

        self.setat_raw(col, row, turn)
        return

    def show(self, indent: int = 0) -> None:
        """Print the current world contents, with optional indent."""
        prefix = "  "
        if indent > 0:
            prefix += " " * indent

        for r in reversed(range(7)):
            if r < 6:
                print(prefix + "|" + "-" * 27 + "|")
            print(prefix + "| " + " | ".join(list(self.data[int(r)])) + " |")

        print(prefix + "\\" + "-" * 27 + "/")
        print("")
        return

    def get_game_state(self) -> int:
        """
        Get current game state.

        :returns: Current game state, as int.
            0 = Not completed.
            1 = X win.
            2 = O win.
            3 = draw.
        """
        # Oops - this is a bug! suppose the last move is a win!
        if " " not in self.data[6]:
            return 3

        # For every item we encounter, see if it is part of a win in any direction.
        d = self.data
        for row in range(7):
            for col in range(7):
                c = d[row][col]
                if c == " ":
                    continue

                # Start search. Note that we only need to search to the right, up, and both upward diagonals.
                if (
                    col < 4
                    and d[row][col + 1] == c
                    and d[row][col + 2] == c
                    and d[row][col + 3] == c
                ):
                    return 1 if c == "X" else 2

                # Up
                if row > 3:
                    # Can't have 4-in-a-row if the bottom piece is > row 3.
                    continue

                if d[row + 1][col] == c and d[row + 2][col] == c and d[row + 3][col] == c:
                    return 1 if c == "X" else 2

                # Diagonal left and up.
                if (
                    col > 2
                    and d[row + 1][col - 1] == c
                    and d[row + 2][col - 2] == c
                    and d[row + 3][col - 3] == c
                ):
                    return 1 if c == "X" else 2

                # Diagonal right and up.
                if (
                    col < 4
                    and d[row + 1][col + 1] == c
                    and d[row + 2][col + 2] == c
                    and d[row + 3][col + 3] == c
                ):
                    return 1 if c == "x" else 2
        return 0

    def is_ended(self) -> bool:
        """Return True if game has ended, otherwise False."""
        return self.get_game_state() != 0

    def get_winner(self) -> str:
        """Get the game winner, if there is one."""
        state = self.get_game_state()

        if state == 1:
            return "X"

        if state == 2:
            return "O"
        return ""

    def get_possible_moves(self) -> List[int]:
        """
        Get all possible moves for the specified board.

        :returns: List of possible moves.
        """
        return [x for x in range(7) if self.data[6][x] == " "]
