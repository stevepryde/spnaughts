"""Helper functions for constructing unique paths and filenames."""

import datetime
import os
import tempfile


def prefix_datetime(prefix, add_date, add_time):
    """Append the date/time to the specified prefix."""
    if add_date:
        now = datetime.datetime.now()
        prefix += "_{:%Y%m%d}".format(now)

    if add_time:
        now = datetime.datetime.now()
        prefix += "_{:%H%M%S}".format(now)

    return prefix


def get_unique_dir(base_path, prefix, add_date=True, add_time=True,
                   suffix=None):
    """Create new unique dir at the specified path, and return its path."""
    prefix = prefix_datetime(prefix=prefix, add_date=add_date,
                             add_time=add_time)
    os.makedirs(base_path, exist_ok=True)
    return tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=base_path)


def get_unique_filename(base_path, prefix, add_date=True, add_time=True,
                        suffix=None, text=True):
    """Create new unique file at the specified path, and return its path."""
    prefix = prefix_datetime(prefix=prefix, add_date=add_date,
                             add_time=add_time)
    os.makedirs(base_path, exist_ok=True)
    fd, filename = tempfile.mkstemp(suffix=suffix, prefix=prefix,
                                    dir=base_path, text=text)
    os.close(fd)
    return filename
