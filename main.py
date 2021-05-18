import sys
import json
import random
import socket as _socket

from loguru import logger

from event_loop import EventLoop, Context, Socket, CallLater


class Client:
    def __init__(self, address):
        self.address = address

    def get_user(self, user_id, callback):
        self._get(f'GET user {user_id}\n', callback)

    def get_balance(self, account_id, callback):
        self._get(f'GET account {account_id}\n', callback)

    def _get(self, req, callback):
        sock = Socket(_socket.AF_INET, _socket.SOCK_STREAM)

        def _on_conn(err):
            if err:
                return callback(err)

            def _on_sent(err):
                if err:
                    sock.close()
                    return callback(err)

                def _on_resp(err, resp=None):
                    sock.close()
                    if err:
                        return callback(err)
                    callback(None, json.loads(resp))

                sock.recv(1024, _on_resp)

            sock.sendall(req.encode('utf8'), _on_sent)

        sock.connect(self.address, _on_conn)


def get_user_balance(serv_addr, user_id, done):
    client = Client(serv_addr)

    def on_timer():

        def on_user(err, user=None):
            if err:
                return done(err)

            def on_account(err, acc=None):
                if err:
                    return done(err)
                done(None, f'User {user["name"]} has {acc["balance"]} USD')

            if user_id % 5 == 0:
                raise Exception('Do not throw from callbacks')
            client.get_balance(user['account_id'], on_account)

        client.get_user(user_id, on_user)

    CallLater(random.randint(0, int(10e6)), on_timer)


def main1(serv_addr):
    def on_balance(err, balance=None):
        if err:
            logger.error('ERROR', err)
        else:
            logger.info(balance)

    for i in range(10):
        get_user_balance(serv_addr, i, on_balance)


def main2(*args):
    sock = Socket(_socket.AF_INET, _socket.SOCK_STREAM)

    def on_conn(err):
        if err:
            logger.error(err)
            return

        def on_sent(err):
            if err:
                sock.close()
                logger.error(err)
                return

            def on_resp(err, resp=None):
                sock.close()
                if err:
                    logger.error(err)
                    return

                logger.info(resp)

            sock.recv(1024, on_resp)

        sock.sendall(b'GET / HTTP/1.1\r\nHost: t.co\r\n\r\n', on_sent)

    sock.connect(('t.co', 80), on_conn)


if __name__ == '__main__':
    logger.info('Run main1()')
    event_loop = EventLoop()
    Context.event_loop = event_loop

    serv_addr = ('127.0.0.1', int(sys.argv[1]))
    event_loop.run(main1, serv_addr)

    logger.info('Run main2()')
    event_loop = EventLoop()
    Context.event_loop = event_loop
    event_loop.run(main2)
