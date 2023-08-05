import log_config
import logging
import os
import pysftp
from server_data import Server
from source_data import SourceData


log: logging.Logger = log_config.get_logger("Disser")


class Disser:
    def __init__(self) -> None:
        self.targets: list[Server] = []
        self.source_data: list[SourceData] = []

    def add_file_source(self, input: str, destination: str = ""):
        self.source_data.append(SourceData(input, destination))

    def add_script_source(self, input: str, destination: str = ""):
        self.source_data.append(SourceData(input, destination, True))

    def add_server(self, name: str, hostname: str, username, password, port: int):
        self.targets.append(Server(name, hostname, username, password, port))

    def get_file_list(self) -> list[str]:
        files: list[str] = []
        for sources in self.source_data:
            if sources.parse_input():
                files.extend(sources.get_source_list())

        log.info("Files to be copied: ")
        for file in files:
            log.info(file)
        return files

    def get_directory_list(self) -> list[str]:
        return []

    def transfer_files(self):
        files: list[str] = self.get_file_list()
        for target in self.targets:
            with pysftp.Connection(
                host=target.hostname,
                username=target.username,
                password=target.password,
                port=target.port,
            ) as sftp:
                for file in files:
                    # first make the directories, then put the files. Will need to strip the filename off first

                    sftp.put(localpath=file, remotepath=file)
