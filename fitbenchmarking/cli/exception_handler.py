"""
This file holds an exception handler decorator that should wrap all cli
functions to provide cleaner output.
"""

from functools import wraps
import sys

from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


def exception_handler(f):
    """
    Decorator to simplify handling exceptions within FitBenchmarking

    :param f: The function to wrap
    :type f: python function
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except exceptions.FitBenchmarkException as e:
            LOGGER.error('Error while running FitBenchmarking. Exiting. '
                         'See below for more information.')
            LOGGER.error(str(e))
            sys.exit(1)
        except Exception as e:
            LOGGER.error('Unknown exception. Exiting.')
            LOGGER.error(str(e))
            sys.exit(1)

    return wrapped
