"""Object containing all game result details."""

from typing import Dict

STATUS_NONE = "NONE"
STATUS_WIN = "WIN"
STATUS_TIE = "TIE"
STATUS_BATCH = "BATCH"


class GameResult:
    """Object containing game result."""

    def __init__(self) -> None:
        """Create a new GameResult object."""
        self.scores = {}  # type: Dict[str, float]
        self.status = STATUS_NONE
        self.winner = ""
        return

    def __repr__(self) -> str:
        """Get representation."""
        return str(self)

    def __str__(self) -> str:
        """Get string representation."""
        if self.status == STATUS_NONE:
            return "Game in progress"
        elif self.status == STATUS_TIE:
            return "RESULT: Tie"
        elif self.status == STATUS_WIN:
            return "RESULT: {} wins!".format(self.get_winner())
        elif self.status == STATUS_BATCH:
            return "BATCH RESULT: {}".format(self.scores)
        assert False, "Invalid result!"

    def set_score(self, identity: str, score: float) -> None:
        """Set the score for the specified identity."""
        self.scores[identity] = score
        return

    def get_score(self, identity: str) -> float:
        """Get the score for the specified identity."""
        assert identity in self.scores, "Score accessed before it was set!"
        return self.scores[identity]

    def get_winner(self) -> str:
        """Get the winner."""
        if self.winner:
            return self.winner

        # Otherwise infer it from score.
        assert self.scores, "BUG: No winner - no scores set yet!"
        return max(self.scores, key=self.scores.get)

    def set_win(self) -> None:
        """Set status to STATUS_WIN."""
        self.status = STATUS_WIN
        return

    def set_tie(self) -> None:
        """Set status to STATUS_TIE."""
        self.status = STATUS_TIE
        return

    def set_batch(self) -> None:
        """Set status STATUS_BATCH."""
        self.status = STATUS_BATCH
        return

    def is_win(self) -> bool:
        """Return True if game has a winner."""
        return self.status == STATUS_WIN

    def is_tie(self) -> bool:
        """Return True if game was a draw."""
        return self.status == STATUS_TIE

    def is_batch(self) -> bool:
        """Return True if game result is from a batch."""
        return self.status == STATUS_BATCH
