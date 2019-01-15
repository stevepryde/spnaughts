"""Helper functions for constructing unique paths and filenames."""

import datetime
import os
import tempfile
from typing import Optional


def prefix_datetime(prefix: str, add_date: bool, add_time: bool) -> str:
    """Append the date/time to the specified prefix."""
    if add_date:
        now = datetime.datetime.now()
        prefix += "_{:%Y%m%d}".format(now)

    if add_time:
        now = datetime.datetime.now()
        prefix += "_{:%H%M%S}".format(now)

    return prefix


def get_unique_dir(
    base_path: str,
    prefix: str,
    add_date: bool = True,
    add_time: bool = True,
    suffix: Optional[str] = None,
) -> str:
    """Create new unique dir at the specified path, and return its path."""
    prefix = prefix_datetime(prefix=prefix, add_date=add_date, add_time=add_time)
    os.makedirs(base_path, exist_ok=True)
    return tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=base_path)


def get_unique_filename(
    base_path: str,
    prefix: str,
    add_date: bool = True,
    add_time: bool = True,
    suffix: Optional[str] = None,
    text: bool = True,
):
    """Create new unique file at the specified path, and return its path."""
    prefix = prefix_datetime(prefix=prefix, add_date=add_date, add_time=add_time)
    os.makedirs(base_path, exist_ok=True)
    fd, filename = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=base_path, text=text)
    os.close(fd)
    return filename
