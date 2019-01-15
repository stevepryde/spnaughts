"""Base class for all objects that create files, including log files."""

import contextlib
from typing import IO, Iterator, Optional


from lib.globals import get_config, log_error
from lib.log import LogHandler
from lib.support.pathmaker import get_unique_dir, get_unique_filename


class GameContext:
    """Base context class with log file handling."""

    def __init__(self, parent_context: Optional["GameContext"]) -> None:
        """
        Create a new GameContext object.

        :param parent_context: The GameContext used to determine the base path
            in which to create a new directory. If None, the log_base_dir
            will be used from the global config instead.
        :param subdir_prefix: The prefix to use for the sub-directory name.
            If None, no sub-directory will be created.
        """
        self.config = get_config()
        self.parent_context = parent_context
        self.log_filename = None  # type: Optional[str]
        self._path = None  # type: Optional[str]
        self.subdir_prefix = None  # type: Optional[str]

        # LogHandler object - only instantiate on first use.
        self._log = None  # type: Optional[LogHandler]
        return

    @property
    def log(self) -> LogHandler:
        """Return LogHandler object. This will be instantiated on first use."""
        if not self._log:
            self._log = LogHandler()
        return self._log

    @property
    def path(self) -> str:
        """Recursively resolve the path for this context."""
        if not self._path:
            if self.parent_context:
                # Resolve path recursively...
                base_path = self.parent_context.path
            else:
                base_path = self.config.log_base_dir

            if self.subdir_prefix:
                self._path = get_unique_dir(base_path=base_path, prefix=self.subdir_prefix)
            else:
                self._path = base_path
            assert self._path, "Failed to set path"
        return self._path

    def enable_file_logging(self, subdir_prefix: Optional[str] = None) -> None:
        """Enable logging to a file."""
        self.subdir_prefix = subdir_prefix
        self.log_filename = self.get_unique_filename(
            prefix=self.__class__.__name__.lower(), suffix=".log"
        )

        self.log.log_to_file(self.log_filename)
        return

    def enable_console_logging(self) -> None:
        """Enable logging to console."""
        self.log.log_to_console()
        return

    @contextlib.contextmanager
    def open_unique_file(
        self, prefix: str, mode: str = "wt", suffix: Optional[str] = None
    ) -> Iterator[IO]:
        """Context-manager for writing to a new unique file."""
        assert self.path, "Tried to open file before enabling file logging!"
        text = "t" in mode
        filename = get_unique_filename(base_path=self.path, prefix=prefix, text=text, suffix=suffix)
        try:
            with open(filename, mode) as f:
                yield f
        except IOError as e:
            log_error("Error writing to file '{}': {}".format(filename, str(e)))
        return

    def get_unique_filename(self, prefix: str, suffix: Optional[str] = None) -> str:
        """Get unique filename at this path location."""
        assert self.path, "Tried to open file before enabling file logging!"
        return get_unique_filename(base_path=self.path, prefix=prefix, suffix=suffix)
