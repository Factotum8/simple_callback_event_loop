import time
from selectors import SelectorKey
from typing import Callable

from loguru import logger

from event_loop.queue import Queue, FileObject


class EventLoop:
    def __init__(self, queue: Queue = None):
        self._queue = queue or Queue()
        self._time = None

    def run(self, entry_point: Callable, *args):
        # TODO
        """
        The main part contains loop.
        :param entry_point:
        :param args:
        :return:
        """
        self._execute(entry_point, *args)

        while not self._queue.is_empty():
            # TODO rename it is not mask
            callback, mask = self._queue.pop(self._time)
            self._execute(callback, mask)

        self._queue.close()

    def register_descriptor(self, descriptor: FileObject, callback: Callable):
        self._queue.register_fileobj(descriptor, callback)

    def unregister_descriptor(self, descriptor: FileObject):
        self._queue.unregister_fileobj(descriptor)

    def set_timer(self, duration, callback):
        self._time = now()
        self._queue.register_timer(self._time + duration,
                                   lambda _: callback())

    @logger.catch
    def _execute(self, callback, *args):
        self._time = now()
        callback(*args)  # new callstack starts
        self._time = now()


def now() -> int:
    """
    Returns time in microseconds.
    """
    return int(time.time() * 10e6)
