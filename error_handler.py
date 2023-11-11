import sys
import logging
from functools import wraps
import psutil


def error_handler(func):
    """
    A decorator that wraps the passed in function and logs exceptions should one occur.

    The purpose of this decorator is to handle exceptions that might be raised during
    the execution of various methods in classes like ProcessMonitor and MemoryLeakDetector.
    It specifically handles exceptions related to process management (using psutil) and
    other general exceptions.

    Parameters:
    func (function): The function to be wrapped by the decorator.

    Returns:
    function: The wrapped function with exception handling.

    Exception Handling:
    - psutil.NoSuchProcess: Raised when a process with the specified identifier is not found.
      Logs an error message and exits the program with status 1.
    - psutil.AccessDenied: Raised when there is insufficient permission to access the process.
      Logs an error message and exits the program with status 1.
    - Exception: Catches any other general exceptions that are not explicitly handled.
      Logs the error message and exits the program with status 1.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except psutil.NoSuchProcess:
            logging.error(f"No process found: {args[0].identifier}")
            sys.exit(1)
        except psutil.AccessDenied:
            logging.error(f"Access denied to process: {args[0].identifier}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            sys.exit(1)

    return wrapper
