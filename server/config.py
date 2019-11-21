import configparser


class Config:
    def __init__(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        self.path_project = config.get("wsgi_server", "project_path")
        self.app_module = config.get("wsgi_server", "app_module")
        self.app_name = config.get("wsgi_server", "app_name")
        self.workers_amount = int(config.get("wsgi_server", "workers_amount"))
        self.host = config.get("wsgi_server", "host")
        self.port = int(config.get("wsgi_server", "port"))
        self.request_queue_size = int(config.get("wsgi_server", "request_queue_size"))
