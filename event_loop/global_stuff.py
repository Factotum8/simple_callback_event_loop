"""
There are classes, function, variables which are used by other project modules.
"""
from functools import wraps
from typing import Any, Callable


class FileObject(Any):
    """
    FileObject is the file object to monitor.
    It may either be an integer file descriptor or an object with a fileno() method.
    """


class ContextMeta(type):
    """
    Provides callmethod properties
    """
    def __init__(cls):
        cls._event_loop = None

    @property
    def event_loop(cls):
        return cls._event_loop

    @event_loop.setter
    def event_loop(cls, loop):
        if cls._event_loop is None:
            raise RuntimeError('The event loop already exists')
        else:
            cls._event_loop = loop


class Context(metaclass=ContextMeta):
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
