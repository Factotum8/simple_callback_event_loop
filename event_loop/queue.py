import time
import heapq
import selectors
from dataclasses import dataclass
from selectors import SelectorKey
import collections
from typing import Callable, Optional

from loguru import logger

from event_loop.global_stuff import FileObject, retry


@dataclass
class Timer:
    timestamp: int  # The timestamp in microseconds since the Epoch.
    timer_number: int  # timer id
    callback: Callable


class Queue:
    """
    There are 2 queues: _timers, _selector.
    We iterate over both.
    """
    def __init__(self):
        self._selector = selectors.DefaultSelector()
        self._timers: [Timer] = []
        self._timer_number = 0
        self._ready = collections.deque()

    @staticmethod
    def microseconds2seconds(seconds: int) -> float:
        return seconds / 10e6

    def register_timer(self, tick: int, callback: Callable):
        heapq.heappush(self._timers, Timer(tick, self._timer_number, callback))
        self._timer_number += 1

    @logger.catch
    @retry((ValueError, KeyError))
    def register_file_obj(self, file_obj: FileObject, callback: Callable) -> SelectorKey:
        """
        It may raise a ValueError in case of invalid event mask or file descriptor,
        or KeyError if the file object is already registered.
        """
        return self._selector.register(file_obj,
                                       selectors.EVENT_READ | selectors.EVENT_WRITE,  # mask
                                       callback)

    @logger.catch
    @retry((ValueError, KeyError))
    def unregister_file_obj(self, file_obj: FileObject) -> selectors.SelectorKey:
        """
        It may raise a KeyError if fileobj is not registered.
        It will raise ValueError if fileobj is invalid
        (e.g. it has no fileno() method or its fileno() method has an invalid return value).
        """
        return self._selector.unregister(file_obj)

    def pop(self, timestamp: Optional[int]) -> tuple[Callable, Optional[bytes]]:
        if self._ready:
            return self._ready.popleft()

        timeout = None
        if self._timers:
            timeout = self.microseconds2seconds(self._timers[0].timestamp - timestamp)

        events = self._selector.select(timeout)
        # If event has happened
        for key, mask in events:
            callback = key.data
            self._ready.append((callback, mask))

        # waiting event
        if not self._ready and self._timers:
            idle = (self._timers[0].timestamp - timestamp)
            if idle > 0:
                time.sleep(self.microseconds2seconds(idle))
                return self.pop(timestamp + idle)

        # If event has expired
        while self._timers and self._timers[0].timestamp <= timestamp:
            _, _, callback = heapq.heappop(self._timers)
            self._ready.append((callback, None))

        return self._ready.popleft()

    def is_empty(self) -> bool:
        return not (self._ready or self._timers or self._selector.get_map())

    def close(self):
        self._selector.close()
