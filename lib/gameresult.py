"""Object containing all game result details."""


STATUS_NONE = "NONE"
STATUS_WIN = "WIN"
STATUS_LOSS = "LOSS"
STATUS_TIE = "TIE"


class GameResult:
    """Object containing game result."""

    def __init__(self) -> None:
        """Create a new GameResult object."""
        self.score = None
        self.status = STATUS_NONE
        return
