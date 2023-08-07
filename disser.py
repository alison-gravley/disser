import log_config
import logging
import os
from server_data import Server
from source_data import SourceData
from sftpretty import CnOpts, Connection
import sftpretty

log: logging.Logger = log_config.get_logger("Disser")


class Disser:
    def __init__(self) -> None:
        self.targets: list[Server] = []
        self.source_data: list[SourceData] = []

    def add_file_source(self, input: str, destination: str = ""):
        self.source_data.append(SourceData(input, destination))

    def add_script_source(self, input: str, destination: str = ""):
        self.source_data.append(SourceData(input, destination, True))

    def add_server(self, server: Server):
        self.targets.append(server)

    def get_file_list(self) -> list[tuple[str, str]]:
        files: list[tuple[str, str]] = []
        for sources in self.source_data:
            if sources.parse_input():
                files.extend(sources.get_source_list())

        log.info("Files to be copied: ")
        for file in files:
            log.info(file)
        return files

    def transfer_files(self):
        files: list[tuple[str, str]] = self.get_file_list()
        for target in self.targets:
            try:
                port: int = 22
                if target.port is not None:
                    port = int(target.port)
                with Connection(
                    host=str(target.hostname),
                    username=target.username,
                    password=target.password,
                    port=port,
                    private_key=target.identity_file,
                ) as sftp:
                    for file in files:
                        try:
                            # first make the directories, then put the files. Will need to strip the filename off first
                            directory_structure = os.path.dirname(file[0])
                            sftp.mkdir_p(directory_structure)
                            # TODO - Need to deal with directories separately. :(
                            sftp.put(
                                localfile=file[0],
                                remotepath=file[1],
                                logger=log,
                            )
                            log.info(
                                "Successfully transferred ({}) to ({})".format(
                                    file[0], file[1]
                                )
                            )
                        except (OSError, IOError) as ose:
                            log.error("Failed to transfer file {}".format(file))
                            log.exception(ose)

            except sftpretty.ConnectionException as conne:
                log.error("Server ({}) unable to connect".format(target._to_string()))
                log.exception(conne)
            except (
                sftpretty.CredentialException,
                sftpretty.HostKeysException,
                sftpretty.SSHException,
                sftpretty.PasswordRequiredException,
                sftpretty.LoggingException,
                sftpretty.SSHException,
            ) as authe:
                log.error(
                    "Server ({}) is unable to authenticate or ssh.".format(
                        target._to_string()
                    )
                )
                log.exception(authe)

    def transfer_files_with_connection(self, sftp: Connection):
        files: list[tuple[str, str]] = self.get_file_list()
        for file in files:
            try:
                # first make the directories, then put the files. Will need to strip the filename off first
                directory_structure = os.path.dirname(file[0])
                sftp.mkdir_p(directory_structure)
                sftp.put(localfile=file[0], remotepath=file[1])
                log.info(
                    "Successfully transferred ({}) to ({})".format(file[0], file[1])
                )
            except (OSError, IOError) as ose:
                log.error("Failed to transfer file {}".format(file))
                log.exception(ose)
