# log.py

# Python 2/3 compatibility.
from __future__ import unicode_literals
from __future__ import print_function
from builtins import dict, range, str, bytes

import sys,os
import datetime
import logging

# pip install rainbow_logging_handler.
from rainbow_logging_handler import RainbowLoggingHandler

DEBUG = True
TRACE = False

DEFAULT_LOG_NAME = 'log'

COLOURS = {'trace'   : 'yellow',
           'debug'   : 'orange',
           'info'    : 'green',
           'warning' : 'blue',
           'error'   : 'magenta',
           'critical': 'red'}


def init_default_logger(logpath='', **kwargs):
  ts = str(datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S%f'))
  logfn = os.path.join(logpath, "logfile_" + ts + ".log")

  init_logger(DEFAULT_LOG_NAME, logfn, **kwargs)

  return

def init_logger(name, logfn, **kwargs):

  console_logging = False
  if ('console_logging' in kwargs):
    console_logging = kwargs['console_logging']

  # Create logger.
  logger = logging.getLogger(name)
  logger.setLevel(logging.DEBUG)

  # Create file handler which logs everything.
  fh = logging.FileHandler(logfn)
  fh.setLevel(logging.DEBUG)

  # Create formatter and add it to the handlers.
  formatter = \
    logging.Formatter(fmt='%(asctime)s %(name)s:%(levelname)s :: %(message)s',
                      datefmt='%m/%d/%Y %I:%M:%S %p')

  fh.setFormatter(formatter)
  logger.addHandler(fh)

  if (console_logging):
    # Create console handler with a higher log level.
    ch = RainbowLoggingHandler(sys.stdout,
                  # Foreground colour, background colour, bold flag.
                  color_message_debug    = (COLOURS['debug'], 'None', False),
                  color_message_info     = (COLOURS['info'], 'None', False),
                  color_message_warning  = (COLOURS['warning'], 'None', False),
                  color_message_error    = (COLOURS['error'], 'None', True),
                  color_message_critical = (COLOURS['critical'], 'None', True))

    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

  return

def get_lines(text):
  if (type(text) is not list):
    text = [text]

  lines = []
  for line in text:
    line = line.rstrip()
    sublines = line.split("\n")
    for subline in sublines:
      lines.append(subline)

  return lines

def write_log(text, log_name = DEFAULT_LOG_NAME):
  lines = get_lines(text)
  for line in lines:
    log_info(line, log_name)
  return

def log_info(text, log_name = DEFAULT_LOG_NAME):
  logobj = logging.getLogger(log_name)
  lines = get_lines(text)
  for line in lines:
    logobj.info(line)
  return

def log_error(text, log_name = DEFAULT_LOG_NAME):
  logobj = logging.getLogger(log_name)
  lines = get_lines(text)
  for line in lines:
    logobj.error(line)

  return

def log_warning(text, log_name = DEFAULT_LOG_NAME):
  logobj = logging.getLogger(log_name)
  lines = get_lines(text)
  for line in lines:
    logobj.warning(line)

  return

def log_debug(text, log_name = DEFAULT_LOG_NAME):
  logobj = logging.getLogger(log_name)
  lines = get_lines(text)
  for line in lines:
    logobj.debug(line)
  return

def log_trace(text, log_name = DEFAULT_LOG_NAME):
  # Trace is the same as debug but only output when TRACE == 1 (see top of this
  # module).

  if (TRACE):
    logobj = logging.getLogger(log_name)
    lines = get_lines(text)
    for line in lines:
      logobj.debug(line)

  return


def log_critical(text, log_name = DEFAULT_LOG_NAME):
  logobj = logging.getLogger(log_name)
  lines = get_lines(text)
  for line in lines:
    logobj.critical(line)

  return
