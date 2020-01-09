import socket
import typing
from multiprocessing import Process

from server.config import Config
from server.server import WSGIServer


def make_server(config: Config, listen_socket: socket.socket, application):
    server = WSGIServer(listen_socket, application)
    server.serve_requests(config)


def start_workers(config: Config, socket_listen: socket.socket, application):
    process_pool: typing.List[Process] = []
    for worker in range(config.workers_amount):
        process = Process(target=make_server, args=(config, socket_listen, application,))
        process.start()
        process_pool.append(process)
    try:
        for process in process_pool:
            process.join()
    except KeyboardInterrupt:
        for process in process_pool:
            process.terminate()
        socket_listen.close()
