import json
import sys
from socketserver import BaseRequestHandler, TCPServer

from loguru import logger


class Handler(BaseRequestHandler):
    users = {}
    accounts = {}

    def handle(self):
        client = f'client {self.client_address}'
        request = self.request.recv(1024)
        if not request:
            logger.info(f'{client} unexpectedly disconnected')
            return

        logger.info(f'{client} < {request}')
        request = request.decode('utf8')
        if request[-1] != '\n':
            raise Exception('Max requestuest length exceeded')

        self.send(f'Echo serve: {request}'.encode())
        return

    def send(self, data: bytes):
        logger.info(f'client {self.client_address} > {data}')
        self.request.sendall(data)


if __name__ == '__main__':
    port = int(sys.argv[1])
    with TCPServer(('127.0.0.1', port), Handler) as server:
        server.serve_forever()

