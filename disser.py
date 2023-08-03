from disser_data import Server
from disser_data import SourceData
import logging
import log


class Disser:
    def __init__(self) -> None:
        self.targets: list[Server] = []
        self.source_data: list[SourceData] = []
        self.log: logging.Logger = log.get_logger("Disser")

    def addFileSource(self, input: str, destination: str = ""):
        self.source_data.append(SourceData(input, destination))

    def addScriptSource(self, input: str, destination: str = ""):
        self.source_data.append(SourceData(input, destination, True))
