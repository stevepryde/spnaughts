"""Globals accessible from anywhere."""

import contextlib
import time
from typing import Any, Callable, Iterator, TYPE_CHECKING


DEFAULT_LOG = None
GLOBAL_CONFIG = None

if TYPE_CHECKING:
    from lib.gameconfig import GameConfig
    from lib.log import LogHandler


def set_default_log(log_handler: "LogHandler") -> None:
    """Set the global log handler object."""
    global DEFAULT_LOG
    assert DEFAULT_LOG is None
    DEFAULT_LOG = log_handler
    return


def log_trace(text: str) -> None:
    """Write to log at TRACE level."""
    if DEFAULT_LOG:
        DEFAULT_LOG.trace(text)
    return


def log_debug(text: str) -> None:
    """Write to log at DEBUG level."""
    if DEFAULT_LOG:
        DEFAULT_LOG.debug(text)
    return


def log_info(text: str) -> None:
    """Write to log at INFO level."""
    if DEFAULT_LOG:
        DEFAULT_LOG.info(text)
    return


def log_warning(text: str) -> None:
    """Write to log at WARNING level."""
    if DEFAULT_LOG:
        DEFAULT_LOG.warning(text)
    return


def log_error(text: str) -> None:
    """Write to log at ERROR level."""
    if DEFAULT_LOG:
        DEFAULT_LOG.error(text)
    return


def log_critical(text: str) -> None:
    """Write to log at CRITICAL level."""
    if DEFAULT_LOG:
        DEFAULT_LOG.critical(text)
    return


def time_this(func: Callable) -> Callable:
    def inner(*args, **kwargs) -> Any:
        start_time = time.monotonic()
        ret = func(*args, **kwargs)
        end_time = time.monotonic()
        duration = end_time - start_time
        log_debug("TIME [{}]: {:.2f} seconds".format(func.__name__, duration))
        return ret

    return inner


@contextlib.contextmanager
def timer(label: str) -> Iterator[None]:
    start_time = time.monotonic()
    yield
    end_time = time.monotonic()
    duration = end_time - start_time
    log_debug("TIME [{}]: {:.2f} seconds".format(label, duration))
    return
