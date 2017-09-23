"""Globals accessible from anywhere."""


DEFAULT_LOG = None
GLOBAL_CONFIG = None


def set_global_config(config):
    """Set the global config object."""
    global GLOBAL_CONFIG
    assert GLOBAL_CONFIG is None
    GLOBAL_CONFIG = config
    return


def get_config():
    """Get the global GameConfig object."""
    return GLOBAL_CONFIG


def set_default_log(log_handler):
    """Set the global log handler object."""
    global DEFAULT_LOG
    assert DEFAULT_LOG is None
    DEFAULT_LOG = log_handler
    return


def log_trace(text):
    """Write to log at TRACE level."""
    if DEFAULT_LOG:
        DEFAULT_LOG.trace(text)
    return


def log_debug(text):
    """Write to log at DEBUG level."""
    if DEFAULT_LOG:
        DEFAULT_LOG.debug(text)
    return


def log_info(text):
    """Write to log at INFO level."""
    if DEFAULT_LOG:
        DEFAULT_LOG.info(text)
    return


def log_warning(text):
    """Write to log at WARNING level."""
    if DEFAULT_LOG:
        DEFAULT_LOG.warning(text)
    return


def log_error(text):
    """Write to log at ERROR level."""
    if DEFAULT_LOG:
        DEFAULT_LOG.error(text)
    return


def log_critical(text):
    """Write to log at CRITICAL level."""
    if DEFAULT_LOG:
        DEFAULT_LOG.critical(text)
    return
