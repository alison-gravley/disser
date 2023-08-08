import log_config
import logging
import os
from stat import S_IMODE
from server_data import Server
from source_data import SourceData
from sftpretty import CnOpts, Connection
import sftpretty

log: logging.Logger = log_config.get_logger("Disser")


class Disser:
    def __init__(self):
        self.targets: list[Server] = []
        self.source_data: list[SourceData] = []

    def add_file_source(self, input: str, destination: str = ""):
        self.source_data.append(SourceData(input, destination))

    def add_script_source(self, input: str, destination: str = ""):
        self.source_data.append(SourceData(input, destination, True))

    def add_server(self, server: Server):
        self.targets.append(server)

    def get_file_list(self) -> list[tuple[str, str, bool]]:
        files: list[tuple[str, str, bool]] = []
        for sources in self.source_data:
            files.extend(sources.get_source_list())

        log.info("Files to be copied: ")
        for file in files:
            log.info(file)
        return files

    def get_script_list(self) -> list[str]:
        files: list[str] = []
        for sources in self.source_data:
            if sources.is_script and sources.is_valid:
                files.append(sources.destination)

        log.info("Scripts to be ran: ")
        for file in files:
            log.info(file)
        return files

    def transfer_files(self):
        files: list[tuple[str, str, bool]] = self.get_file_list()
        for target in self.targets:
            self.transfer_to_target(target, files)

    def transfer_to_target(self, server: Server, files: list[tuple[str, str, bool]]):
        port: int = 22
        if server.port is not None:
            port = int(server.port)
        try:
            with Connection(
                host=str(server.hostname),
                username=server.username,
                password=server.password,
                port=port,
                private_key=server.identity_file,
            ) as sftp:
                for file in files:
                    try:
                        if file[2]:
                            self.transfer_directory(file[0], file[1], sftp)
                        else:
                            self.transfer_file(file[0], file[1], sftp)
                    except (OSError, IOError) as ose:
                        log.error("Failed to transfer file {}".format(file))
                        log.exception(ose)

        except sftpretty.ConnectionException as conne:
            log.error("Server ({}) unable to connect".format(server._to_string()))
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
                    server._to_string()
                )
            )
            log.exception(authe)

    def transfer_directory(self, source: str, destination: str, sftp: Connection):
        directory_structure = os.path.dirname(destination)
        statmod = os.stat(source)
        chmod_val = int(oct(statmod.st_mode)[-3:])
        sftp.mkdir_p(directory_structure)
        sftp.put_r(
            localdir=source,
            remotedir=destination,
            logger=log,
            confirm=True,
            tries=5,
        )
        log.info(
            "Successfully transferred directory ({}) to ({})".format(
                source, destination
            )
        )
        log.info("Setting chmod to {} for {}".format(chmod_val, destination))
        sftp.chmod(destination, chmod_val)

    def transfer_file(self, source: str, destination: str, sftp: Connection):
        directory_structure = os.path.dirname(destination)
        statmod = os.stat(source)
        chmod_val = int(oct(statmod.st_mode)[-3:])
        sftp.mkdir_p(directory_structure)
        sftp.put(
            localfile=source,
            remotepath=destination,
            logger=log,
            confirm=True,
            tries=5,
        )
        log.info(
            "Successfully transferred file ({}) to ({})".format(source, destination)
        )
        log.info("Setting chmod to {} for {}".format(chmod_val, destination))
        sftp.chmod(destination, chmod_val)

    def run_scripts(self):
        scripts: list[str] = self.get_script_list()
        for target in self.targets:
            self.execute_on_target(target, scripts)

    def execute_on_target(self, server: Server, scripts: list[str]):
        port: int = 22
        if server.port is not None:
            port = int(server.port)
        try:
            with Connection(
                host=str(server.hostname),
                username=server.username,
                password=server.password,
                port=port,
                private_key=server.identity_file,
            ) as sftp:
                for script in scripts:
                    try:
                        self.execute_script(script, sftp)
                    except (ValueError, IOError) as ose:
                        log.error("Failed to execute script {}".format(script))
                        log.exception(ose)

        except sftpretty.ConnectionException as conne:
            log.error("Server ({}) unable to connect".format(server._to_string()))
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
                    server._to_string()
                )
            )
            log.exception(authe)

    def execute_script(self, script: str, sftp: Connection):
        log.info("Running script ({})".format(script))
        cd_to: str = os.path.dirname(script)
        command: str = "(cd " + cd_to + " && " + script + ")"
        results: list[str] = sftp.execute(
            command=command,
            logger=log,
        )
        log.info("Script {} results: ".format(command))
        for result in results:
            log.info(result)
