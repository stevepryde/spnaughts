"""Module providing simple logging capabilities."""


import datetime
import logging
import os
import sys


# pip install rainbow_logging_handler.
from rainbow_logging_handler import RainbowLoggingHandler


DEBUG = True
TRACE = False

DEFAULT_LOG_NAME = 'log'

COLOURS = {'trace': 'yellow',
           'debug': 'orange',
           'info': 'green',
           'warning': 'blue',
           'error': 'magenta',
           'critical': 'red'}


def init_default_logger(logpath, **kwargs):
    """
    Init default logger.

    :param logpath: The base path for the log file.
    """
    ts = str(datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S%f'))
    logfn = os.path.join(logpath, "logfile_" + ts + ".log")
    init_logger(DEFAULT_LOG_NAME, logfn, **kwargs)
    return


def init_logger(name, logfn, console_logging=False):
    """
    Init logger.

    :param name: The log name.
    :param logfn: The filename for this log.
    :param console_logging: True if the log should also log to the console.
    """
    # Create logger.
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create file handler which logs everything.
    fh = logging.FileHandler(logfn)
    fh.setLevel(logging.DEBUG)

    # Create formatter and add it to the handlers.
    formatter = logging.Formatter(fmt='%(asctime)s %(name)s:%(levelname)s :: '
                                      '%(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p')

    fh.setFormatter(formatter)
    logger.addHandler(fh)

    if console_logging:
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
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return


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


def write_log(*args, **kwargs):
    """Alias for log_info()."""
    log_info(*args, **kwargs)
    return


def log_info(text, log_name=DEFAULT_LOG_NAME):
    """Write text to the log at INFO level."""
    logobj = logging.getLogger(log_name)
    lines = get_lines(text)
    for line in lines:
        logobj.info(line)
    return


def log_error(text, log_name=DEFAULT_LOG_NAME):
    """Write text to the log at ERROR level."""
    logobj = logging.getLogger(log_name)
    lines = get_lines(text)
    for line in lines:
        logobj.error(line)
    return


def log_warning(text, log_name=DEFAULT_LOG_NAME):
    """Write text to the log at WARNING level."""
    logobj = logging.getLogger(log_name)
    lines = get_lines(text)
    for line in lines:
        logobj.warning(line)

    return


def log_debug(text, log_name=DEFAULT_LOG_NAME):
    """Write text to the log at DEBUG level."""
    logobj = logging.getLogger(log_name)
    lines = get_lines(text)
    for line in lines:
        logobj.debug(line)
    return


def log_trace(text, log_name=DEFAULT_LOG_NAME):
    """
    Write text to the log at TRACE level.

    Trace is the same as debug but is only output when TRACE is True.
    See the constant at the top of this module.
    """
    if TRACE:
        logobj = logging.getLogger(log_name)
        lines = get_lines(text)
        for line in lines:
            logobj.debug(line)
    return


def log_critical(text, log_name=DEFAULT_LOG_NAME):
    """Write text to the log at CRITICAL level."""
    logobj = logging.getLogger(log_name)
    lines = get_lines(text)
    for line in lines:
        logobj.critical(line)
    return
