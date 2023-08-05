import os
import stat
import glob
import log_config
import logging

log: logging.Logger = log_config.get_logger("SourceData")


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

    def parse_input(self) -> bool:
        if self.is_script:
            if not self.determine_if_file():
                log.error(
                    "Source script is not a file. Unable to determine '{}'".format(
                        self.input
                    )
                )
            elif not self.determine_if_executable():
                log.error(
                    "Source script is not executable. Destination will not be able to run '{}'".format(
                        self.absolute
                    )
                )
            else:
                return True
        elif self.determine_if_glob():
            return True
        elif self.determine_if_file():
            return True
        elif self.determine_if_directory():
            return True
        else:
            log.error(
                "Source data is not a file or folder. Unable to determine '{}'".format(
                    self.input
                )
            )

        self.is_valid = False
        return False

    def determine_if_glob(self) -> bool:
        self.is_glob = glob.has_magic(self.input)
        if not self.is_glob:
            return False

        matching = glob.glob(self.input, include_hidden=True, recursive=True)
        if len(matching) == 0:
            log.warn("Glob {} does not match any files or folders.".format(self.input))
            self.glob_warn = True
        else:
            log.info("Glob {} will match {} items.".format(self.input, len(matching)))

        return True

    def determine_if_file(self) -> bool:
        self.is_file = os.path.isfile(self.input)
        if not self.is_file:
            return False
        is_abs = os.path.isabs(self.input)
        if not is_abs:
            self.absolute = os.path.abspath(self.input)
            log.info(
                "Expanding relative file path {} to absolute {}".format(
                    self.input, self.absolute
                )
            )
        else:
            self.absolute = self.input

        log.info("Source identified as file with path {}".format(self.absolute))

        if len(self.destination) == 0:
            log.info(
                "Source file {} will be copied to same destination as source".format(
                    self.absolute
                )
            )
            self.destination = self.absolute
        else:
            log.info(
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
            log.info(
                "Expanding relative directory {} to absolute {}".format(
                    self.input, self.absolute
                )
            )
        else:
            self.absolute = self.input

        log.info("Source identified as directory with path {}".format(self.absolute))

        if len(self.destination) == 0:
            log.info(
                "Source directory {} will be copied to same destination as source".format(
                    self.absolute
                )
            )
            self.destination = self.absolute
        else:
            log.info(
                "Source directory {} will be copied to alternate destination {}".format(
                    self.absolute, self.destination
                )
            )
        return True

    def determine_if_executable(self) -> bool:
        status = os.stat(self.absolute)
        readable_filemode = stat.filemode(status.st_mode)
        if readable_filemode.count("x") > 0:
            log.info(
                "Source script {} is executable. Permissions are '{}'.".format(
                    self.absolute, readable_filemode
                )
            )
            return True
        else:
            log.warn(
                "Source script {} is not executable. Permissions are '{}".format(
                    self.absolute, readable_filemode
                )
            )
            return False

    def get_source_list(self) -> list[str]:
        if not self.is_valid:
            return []
        elif not self.is_glob:
            return [self.absolute]
        globbys: list[str] = []
        for g in glob.glob(pathname=self.input, recursive=True, include_hidden=True):
            if os.path.isabs(g):
                globbys.append(g)
            else:
                globbys.append(os.path.abspath(g))
        return globbys
