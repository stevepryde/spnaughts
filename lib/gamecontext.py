"""Base class for all objects that create files, including log files."""

import contextlib
from typing import IO, Iterator, Optional


from lib.log import LogHandler
from lib.support.pathmaker import get_unique_dir, get_unique_filename


class GameContext:
    """
    Base context class with log file handling.
    
    The GameContext is inherited by GamePlayer and GameBase, and is intended
    to provide support methods as required, such as logging.

    By default, logging is instantiated on the first reference to self.log, 
    and provides a no-op LogHandler. To enable logging to a file or to the 
    console, call self.log.log_to_file() or self.log.log_to_console().
    Logging should be disabled if possible, for performance, and is 
    intended for debugging purposes only.
    """

    def __init__(self) -> None:
        """Create a new GameContext object."""
        # LogHandler object - only instantiate on first use.
        self._log = None  # type: Optional[LogHandler]
        return

    @property
    def log(self) -> LogHandler:
        """Return LogHandler object. This will be instantiated on first use."""
        if not self._log:
            self._log = LogHandler()
        return self._log
