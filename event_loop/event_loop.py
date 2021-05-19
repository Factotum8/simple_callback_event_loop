import time
from typing import Callable
from selectors import SelectorKey

from loguru import logger

from event_loop.queue import Queue
from event_loop._globals import FileObject


class EventLoop:
    def __init__(self, queue: Queue = None):
        self._queue = queue or Queue()
        self._time = None

    @logger.catch
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
            callback, mask = self._queue.pop(self._time)
            self._execute(callback, mask)

        self._queue.close()

    @logger.catch
    def register_descriptor(self, descriptor: FileObject, callback: Callable) -> SelectorKey:
        return self._queue.register_file_obj(descriptor, callback)

    @logger.catch
    def unregister_descriptor(self, descriptor: FileObject) -> SelectorKey:
        return self._queue.unregister_file_obj(descriptor)

    def set_timer(self, duration, callback):
        self._time = now()
        self._queue.register_timer(self._time + duration,
                                   lambda _: callback())

    def _execute(self, callback, *args):
        self._time = now()
        try:
            callback(*args)  # new callstack starts
        except Exception as e:
            logger.exception(f'Uncaught exception: \n{e}')
            # logger.error(f'Uncaught exception: \n{e}')
        self._time = now()


def now() -> int:
    """
    It returns converting seconds in microseconds.
    """
    return int(time.time() * 10e6)
