"""Module providing simple logging capabilities."""


import datetime
import logging
import os
import sys


# pip install rainbow_logging_handler.
from rainbow_logging_handler import RainbowLoggingHandler

from lib.globals import set_default_log

DEBUG = True
TRACE = False

DEFAULT_LOG_NAME = 'log'

COLOURS = {'trace': 'yellow',
           'debug': 'orange',
           'info': 'green',
           'warning': 'blue',
           'error': 'magenta',
           'critical': 'red'}


def get_lines(text):
    """Convert the string (or list of strings) into a list of lines."""
    if not isinstance(text, list):
        text = [text]

    lines = []
    for line in text:
        line = line.rstrip()
        sublines = line.split("\n")
        for subline in sublines:
            lines.append(subline)
    return lines


class LogHandler:
    """Object that provides logging capabilities."""

    def __init__(self, name):
        """
        Create new LogHandler object.

        :param name: Unique name for this log.
        :param filename: The filename for the log file, including full path.
        :param console_logging: True if the log should also write to the
            console.
        """
        self.name = name
        self.filename = None
        self.file_logging = False
        self.console_logging = False

        # Log in memory if no console or file configured.
        self.log_lines = []

        # Create formatter and add it to the handlers.
        self.formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)s :: %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p')
        return

    @property
    def is_configured(self):
        """Return True if logging has been activated."""
        return self.file_logging or self.console_logging

    def log_to_file(self, filename):
        """Set up file logging."""
        self.filename = filename
        self.file_logging = True

        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)

        # Create file handler which logs everything.
        fh = logging.FileHandler(self.filename)
        fh.setLevel(logging.DEBUG)

        fh.setFormatter(self.formatter)
        logger.addHandler(fh)
        return

    def log_to_console(self):
        """Set up console logging."""
        self.console_logging = True
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)

        # Create console handler with a higher log level.
        ch = RainbowLoggingHandler(
            sys.stdout,
            # Foreground colour, background colour, bold flag.
            color_message_debug=(COLOURS['debug'], 'None', False),
            color_message_info=(COLOURS['info'], 'None', False),
            color_message_warning=(COLOURS['warning'], 'None', False),
            color_message_error=(COLOURS['error'], 'None', True),
            color_message_critical=(COLOURS['critical'], 'None', True))

        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        logger.addHandler(ch)
        return

    def set_as_default(self):
        """Set this as the default logger."""
        set_default_log(self)
        return

    def get_log_obj(self):
        """Get the logger object."""
        if self.is_configured:
            return logging.getLogger(self.name)
        return None

    def log_it(self, text, loglevel):
        """Write the text to the log at the specified log level."""
        logobj = self.get_log_obj()

        lines = get_lines(text)
        if logobj:
            for line in lines:
                func = getattr(logobj, loglevel)
                func(line)
        else:
            for line in lines:
                self.log_lines.append("{}: {}".format(loglevel, line))
        return

    def trace(self, text):
        """
        Write text to the log at TRACE level.

        TRACE is the same as debug but is only output when TRACE is True.
        """
        if TRACE:
            self.log_it(text, 'debug')
        return

    def debug(self, text):
        """Write text to the log at DEBUG level."""
        self.log_it(text, 'debug')
        return

    def info(self, text):
        """Write text to the log at INFO level."""
        self.log_it(text, 'info')
        return

    def warning(self, text):
        """Write text to the log at WARNING level."""
        self.log_it(text, 'warning')
        return

    def error(self, text):
        """Write text to the log at ERROR level."""
        self.log_it(text, 'error')
        return

    def critical(self, text):
        """Write text to the log at CRITICAL level."""
        self.log_it(text, 'critical')
        return
