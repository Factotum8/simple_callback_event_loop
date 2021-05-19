import socket as _socket

from loguru import logger

from event_loop import EventLoop, Context, Socket


def main(*_):
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

            raise Exception('Do not throw from callbacks')

            sock.recv(1024, on_resp)

        message = 'GET / HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n'
        logger.info(f"sent: {message}")
        sock.sendall(message.encode(), on_sent)

    sock.connect(('127.0.0.1', 8080), on_conn)


if __name__ == '__main__':
    event_loop = EventLoop()
    Context.set_event_loop(event_loop)
    event_loop.run(main)
