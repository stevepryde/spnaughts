"""Base class for all objects that create files, including log files."""


import contextlib
import os
import re

from lib.globals import get_config, log_error
from lib.log import LogHandler
from lib.support.pathmaker import get_unique_dir, get_unique_filename


class GameContext:
    """Base context class with log file handling."""

    def __init__(self, parent_context, subdir_prefix=None):
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
        if self.parent_context:
            base_path = self.parent_context.path
        else:
            base_path = self.config.log_base_dir

        if subdir_prefix:
            self.path = get_unique_dir(base_path=base_path,
                                       prefix=subdir_prefix)
        else:
            self.path = base_path

        self.log_filename = self.get_unique_filename(
            prefix=self.__class__.__name__.lower(),
            suffix='.log')
        # The log name is just a unique name used to identify this log
        # within the code. We use the filename to quarantee uniqueness.
        self.log_name = re.sub(r'[^a-z0-9\-\_]', '', self.log_filename.lower())
        self.log = LogHandler(name=self.log_name)
        return

    def enable_file_logging(self):
        """Enable logging to a file."""
        self.log.log_to_file(self.log_filename)
        return

    def enable_console_logging(self):
        """Enable logging to console."""
        self.log.log_to_console()
        return

    @contextlib.contextmanager
    def open_unique_file(self, prefix, mode='wt', suffix=None):
        """Context-manager for writing to a new unique file."""
        text = 't' in mode
        filename = get_unique_filename(base_path=self.path, prefix=prefix,
                                       text=text, suffix=suffix)
        try:
            with open(filename, mode) as f:
                yield f
        except IOError as e:
            log_error("Error writing to file '{}': {}".
                      format(filename, str(e)))
        return

    def get_unique_filename(self, prefix, suffix=None):
        """Get unique filename at this path location."""
        return get_unique_filename(base_path=self.path, prefix=prefix,
                                   suffix=suffix)
