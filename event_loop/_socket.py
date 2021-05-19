import errno
import socket
import selectors
from enum import Enum
from typing import Callable

from loguru import logger

from event_loop._globals import Context, _Address


class SocketState(Enum):
    initial = 0
    connecting = 1
    connected = 2
    closed = 3


class CallbackType(Enum):
    connection = 'conn'
    sent = 'sent'
    receive = 'recv'


class Socket(Context):
    status_error_text = 'Not expected socket status'

    def __init__(self, *args):
        self._sock = socket.socket(*args)
        self._sock.setblocking(False)
        self.event_loop.register_descriptor(self._sock, self._on_event)  # closure
        self._state = SocketState.initial
        self._callbacks = {}

    @logger.catch
    def connect(self, address: _Address, callback: Callable):
        assert self._state == SocketState.initial, self.status_error_text
        self._state = SocketState.connecting
        self._callbacks[CallbackType.connection.value] = callback
        err = self._sock.connect_ex(address)
        assert errno.errorcode[err] == 'EINPROGRESS', "Operation isn't in progress"

    def recv(self, n, callback: Callable):
        assert self._state == SocketState.connected, self.status_error_text
        assert CallbackType.receive not in self._callbacks

        def _on_read_ready(err):
            if err:
                return callback(err)
            data = self._sock.recv(n)
            callback(None, data)

        self._callbacks[CallbackType.receive.value] = _on_read_ready

    def sendall(self, data, callback):
        assert self._state == SocketState.connected
        assert CallbackType.sent not in self._callbacks

        def _on_write_ready(err):
            nonlocal data
            if err:
                return callback(err)

            n = self._sock.send(data)
            if n < len(data):
                data = data[n:]
                self._callbacks[CallbackType.sent.value] = _on_write_ready
            else:
                callback(None)

        self._callbacks[CallbackType.sent.value] = _on_write_ready

    def close(self):
        self.event_loop.unregister_descriptor(self._sock)
        self._callbacks.clear()
        self._state = SocketState.closed
        self._sock.close()

    def _on_event(self, mask):
        if self._state == SocketState.connecting:
            assert mask == selectors.EVENT_WRITE, self.status_error_text
            cb = self._callbacks.pop(CallbackType.connection.value)
            err = self._get_sock_error()
            if err:
                self.close()
            else:
                self._state = SocketState.connected
            cb(err)

        if mask & selectors.EVENT_READ:
            cb = self._callbacks.get(CallbackType.receive.value)
            if cb:
                del self._callbacks[CallbackType.receive.value]
                err = self._get_sock_error()
                cb(err)

        if mask & selectors.EVENT_WRITE:
            cb = self._callbacks.get(CallbackType.sent.value)
            if cb:
                del self._callbacks[CallbackType.sent.value]
                err = self._get_sock_error()
                cb(err)

    def _get_sock_error(self):
        err = self._sock.getsockopt(socket.SOL_SOCKET,
                                    socket.SO_ERROR)
        if not err:
            return None
        return IOError('connection failed',
                       err, errno.errorcode[err])
