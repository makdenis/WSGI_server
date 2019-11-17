import socket
import sys
import importlib
import typing
import logging

from server.workers import start_workers
from server.config import Config


def create_socket(server_address: typing.Tuple[str, int], request_queue_size: int):
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    socket_listen = socket.socket(
        address_family,
        socket_type
    )
    socket_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_listen.bind(server_address)
    socket_listen.listen(request_queue_size)

    return socket_listen


if __name__ == '__main__':
    config = Config('./config.conf')
    if config.path_project != './':
        sys.path.insert(0, config.path_project)
    wsgi = importlib.import_module(config.app_module)
    application = getattr(wsgi, config.app_name)

    server_address = (config.host, config.port)
    socket_listen = create_socket(server_address, config.request_queue_size)
    logging.info(f'WSGIServer: Serving HTTP on port {config.port} ...\n')
    start_workers(config, socket_listen, application)
