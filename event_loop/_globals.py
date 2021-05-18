"""
There are classes, function, variables which are used by other project modules.
"""
from functools import wraps
from typing import Any, Callable, Union

# FileObject is the file object to monitor.
# It may either be an integer file descriptor or an object with a fileno() method.
FileObject = Any
_Address = [Union[tuple, str], bytes]


class Context:
    """
    The class provides closure for the event loop
    """
    _event_loop = None

    @classmethod
    def set_event_loop(cls, event_loop):
        cls._event_loop = event_loop

    @property
    def event_loop(self):
        return self._event_loop


class CallLater(Context):
    def __init__(self, duration, callback):
        """
        Put the init/first callback to a event loop
        """
        self.event_loop.set_timer(duration, callback)


def retry(exceptions: [Exception] = None, try_count: int = 3) -> Callable:
    """
    Retry executing function
    """
    exceptions = exceptions or Exception

    def decorator(function: Callable):
        @wraps(function)
        def wrapper(*args, **kwargs):
            for i in range(try_count):
                try:
                    return function(*args, **kwargs)
                except exceptions as e:
                    if i == try_count:
                        raise e

        return wrapper

    return decorator
