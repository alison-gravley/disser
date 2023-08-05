import log_config
import logging
import pysftp

log: logging.Logger = log_config.get_logger("Server")


class Server:
    def __init__(
        self,
        name: str,
        hostname: str,
        username=None,
        password=None,
        port: int = 22,
    ) -> None:
        self.name = name
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port