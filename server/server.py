import io
import socket
import sys
import urllib
import logging


class WSGIServer:
    def __init__(self, socket_listen: socket.socket, application):
        self.socket_listen = socket_listen
        host, port = self.socket_listen.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        self.headers = []
        self.application = application

    def serve_requests(self):
        socket_listen = self.socket_listen
        while True:
            self.client_connection, client_address = socket_listen.accept()
            try:
                self.handle_request()
            except Exception as e:
                logging.error('Exception while handle', e)

    def handle_request(self):
        request_data = self.client_connection.recv(1024)
        self.request_data = request_data.decode('utf-8')
        if self.request_data:
            self.parse_request(self.request_data)
            env = self.get_environment()
            result = self.application(env, self.start_response)
            self.finish_response(result)
        else:
            self.client_connection.close()

    def parse_request(self, text):
        lines = text.splitlines()
        request_line = lines[0]
        request_line = request_line.rstrip('\r\n')
        (
            self.request_method,
            self.path,
            self.request_version
        ) = request_line.split()

    def get_environment(self):
        env = {
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': io.StringIO(self.request_data),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'REQUEST_METHOD': self.request_method
        }

        if '?' in self.path:
            path, query = self.path.split('?', 1)
        else:
            path, query = self.path, ''

        env['PATH_INFO'] = urllib.parse.unquote(path, 'iso-8859-1')
        env['QUERY_STRING'] = query
        env['SERVER_NAME'] = self.server_name
        env['SERVER_PORT'] = str(self.server_port)

        return env

    def start_response(self, status, response_headers, exc_info=None):
        server_headers = [
            ('Server', 'WSGIServer 1.0'),
        ]
        self.headers = [status, response_headers + server_headers]

    def finish_response(self, result):
        try:
            status, resp_headers = self.headers
            response = f'HTTP/1.1 {status}\r\n'
            for header in resp_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in result:
                response += data.decode('utf-8', errors='ignore')
            response_bytes = response.encode()
            self.client_connection.sendall(response_bytes)
        except Exception as e:
            logging.error('Exception while finishing response', e)
        finally:
            self.client_connection.close()
