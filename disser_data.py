import os
import stat
import glob
import log
import logging


class Server:
    def __init__(
        self, hostname: str, username: str = "", password=None, port: int = 22
    ) -> None:
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.log: logging.Logger = log.get_logger("Server")


class SourceData:
    def __init__(
        self, input: str, destination: str = "", is_script: bool = False
    ) -> None:
        self.input: str = input
        self.absolute: str = ""
        self.destination: str = destination
        self.base_dir: str = ""
        self.is_file: bool = False
        self.is_glob: bool = False
        self.glob_warn: bool = False
        self.is_directory: bool = False
        self.is_valid: bool = True
        self.is_script: bool = is_script
        self.log: logging.Logger = log.get_logger("SourceData")

    def parse_input(self) -> bool:
        if self.is_script:
            if not self.determine_if_file:
                self.log.error(
                    "Source script is not a file. Unable to determine '{}'".format(
                        self.input
                    )
                )
            elif not self.determine_if_executable:
                self.log.error(
                    "Source script is not executable. Destination will not be able to run '{}'".format(
                        self.absolute
                    )
                )
            else:
                return True
        elif self.determine_if_glob:
            return True
        elif self.determine_if_file:
            return True
        elif self.determine_if_directory:
            return True
        else:
            self.log.error(
                "Source data is not a file or folder. Unable to determine '{}'",
                self.input,
            )

        self.is_valid = False
        return False

    def determine_if_glob(self) -> bool:
        self.is_glob = glob.has_magic(self.input)
        if not self.is_glob:
            return False

        matching = glob.glob(self.input, include_hidden=True, recursive=True)
        if len(matching) is 0:
            self.log.warn(
                "Glob {} does not match any files or folders.".format(self.input)
            )
            self.glob_warn = True
        else:
            self.log.info(
                "Glob {} will match {} items.".format(self.input, len(matching))
            )

        return True

    def determine_if_file(self) -> bool:
        self.is_file = os.path.isfile(self.input)
        if not self.is_file:
            return False
        is_abs = os.path.isabs(self.input)
        if not is_abs:
            self.absolute = os.path.abspath(self.input)
            self.log.info(
                "Expanding relative file path {} to absolute {}".format(
                    self.input, self.absolute
                )
            )
        else:
            self.absolute = self.input

        self.log.info("Source identified as file with path {}".format(self.absolute))

        if len(self.destination) is 0:
            self.log.info(
                "Source file {} will be copied to same destination as source".format(
                    self.absolute
                )
            )
            self.destination = self.absolute
        else:
            self.log.info(
                "Source file {} will be copied to alternate destination {}".format(
                    self.absolute, self.destination
                )
            )

        return True

    def determine_if_directory(self) -> bool:
        self.is_directory = os.path.isdir(self.input)
        if not self.is_directory:
            return False
        is_abs = os.path.isabs(self.input)
        if not is_abs:
            self.absolute = os.path.abspath(self.input)
            self.log.info(
                "Expanding relative directory {} to absolute {}".format(
                    self.input, self.absolute
                )
            )
        else:
            self.absolute = self.input

        self.log.info(
            "Source identified as directory with path {}".format(self.absolute)
        )

        if len(self.destination) is 0:
            self.log.info(
                "Source directory {} will be copied to same destination as source".format(
                    self.absolute
                )
            )
            self.destination = self.absolute
        else:
            self.log.info(
                "Source directory {} will be copied to alternate destination {}".format(
                    self.absolute, self.destination
                )
            )
        return True

    def determine_if_executable(self) -> bool:
        status = os.stat(self.absolute)
        readable_filemode = stat.filemode(status.st_mode)
        if readable_filemode.count("x") > 0:
            self.log.info(
                "Source script {} is executable. Permissions are '{}'.".format(
                    self.absolute, readable_filemode
                )
            )
            return True
        else:
            self.log.warn(
                "Source script {} is not executable. Permissions are '{}".format(
                    self.absolute, readable_filemode
                )
            )
            return False
