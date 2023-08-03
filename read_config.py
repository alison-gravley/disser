import yaml
import logging
import log
import os
from disser import Disser
from disser_data import Server
from disser_data import SourceData


class DisserImport:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.log: logging.Logger = log.get_logger("DisserImport")
        self.disser: Disser = Disser()

    def import_config(self) -> bool:
        if self.filename is None:
            self.log.error("Input File is None")
            return False
        elif not os.path.isfile(self.filename):
            self.log.error("File {} not found".format(self.filename))
            return False
        elif not os.access(self.filename, os.R_OK):
            self.log.error("Unable to read File {}".format(self.filename))
            return False

        with open(self.filename, "r") as file:
            config = yaml.safe_load(file)
            if len(config) == 0:
                self.log.error(
                    "Parsed config is empty for file {}".format(self.filename)
                )
                return False
            elif type(config) is not dict:
                self.log.error(
                    "Parsed config is not a dict. Type {}".format(type(config))
                )
                return False
            else:
                return self.parse_config(config)

    def parse_config(self, config: dict) -> bool:
        found_source: bool = False
        found_target: bool = False
        for keys in config:
            match keys:
                case "source":
                    self.log.info("Found source section")
                    if len(config[keys]) == 0:
                        self.log.error("Source section is empty!")
                    elif self.parse_source_tag(config[keys]):
                        self.log.info("Source successfully parsed!")
                        found_source = True
                    else:
                        self.log.error(
                            "Source section failed to parse. Section required."
                        )

                case "target":
                    self.log.info("Found Target section!")
                    if len(config[keys]) == 0:
                        self.log.error("Target section is empty!")
                    elif self.parse_targets_tag(config[keys]):
                        self.log.info("Target successfully parsed!")
                        found_target = True
                    else:
                        self.log.error(
                            "Target section failed to parse. Section required."
                        )
                case _:
                    self.log.error("Unknown section {}. Ignoring.".format(keys))
        return found_source and found_target

    # Source

    def parse_source_tag(self, source: dict) -> bool:
        found_files: bool = False
        found_scripts: bool = False
        for keys in source:
            match keys:
                case "files":
                    if len(source["files"]) == 0:
                        self.log.error("Files tag is empty!")
                    elif type(source["files"]) is not list:
                        self.log.error("Files tag is not a list.")
                    else:
                        found_files = self.parse_files_tag(source[keys])
                case "scripts":
                    if len(source["scripts"]) == 0:
                        self.log.error("scripts tag is empty!")
                    elif type(source["scripts"]) is not list:
                        self.log.error("Scripts tag is not a list.")
                    else:
                        found_scripts = self.parse_scripts_tag(source[keys])
                case _:
                    self.log.error(
                        "Unknown tag {} under Source. Ignoring.".format(keys)
                    )
        if found_files or found_scripts:
            self.log.info(
                "Source tag parsed. Files {}, Scripts {}".format(
                    found_files, found_scripts
                )
            )
            return True
        else:
            self.log.error("No files or scripts found in Source tag!")
            return False

    def parse_files_tag(self, files: list) -> bool:
        tags_parsed: int = 0
        for file in files:
            if type(file) is str:
                self.log.info("Adding source file item {}".format(file))
                self.disser.addFileSource(file)
                tags_parsed += 1
            elif type(file) is dict:
                parse = self.parse_file_with_destination(file)
                if parse is None:
                    self.log.error(
                        "Unable to parse file {} with desination.".format(file)
                    )
                else:
                    self.log.info(
                        "Adding source item {} with destination {}.".format(
                            parse[0], parse[1]
                        )
                    )
                    self.disser.addFileSource(parse[0], parse[1])
                    tags_parsed += 1
            else:
                self.log.error(
                    "File {} not parsed as str or dict with destination. Parsed as {}.".format(
                        file, type(file)
                    )
                )
        self.log.info("Parsed {} tags in Source Files".format(tags_parsed))
        return tags_parsed > 0

    def parse_file_with_destination(self, file: dict):
        filename: str = ""
        destination: str = ""
        if len(file) != 2:
            self.log.error(
                "Invalid file '{}' from dict item. Requires 2 items, but has {}.".format(
                    file, len(file)
                )
            )
            return None
        if file.get("destination") is None:
            self.log.error(
                "Missing destination key. Keys present are '{}'".format(file.keys())
            )
            return None
        if type(file["destination"]) is not str:
            self.log.error(
                "Destination is not str type. Type is {}".format(
                    type(file["destination"])
                )
            )
            return None

        destination = file["destination"]
        # Not sure we need this
        if len(destination) == 0:
            self.log.error("Destination empty for {}".format(file))
            return None

        for fd in file:
            if fd != "destination":
                if len(fd) == 0:
                    self.log.error("Filename must not be blank")
                    return None
                else:
                    filename = fd

        return (filename, destination)

    def parse_scripts_tag(self, scripts: list) -> bool:
        tags_parsed: int = 0
        for file in scripts:
            if type(file) is str:
                self.log.info("Adding source script item {}".format(file))
                self.disser.addScriptSource(file)
                tags_parsed += 1
            elif type(file) is dict:
                parse = self.parse_file_with_destination(file)
                if parse is None:
                    self.log.error(
                        "Unable to parse script {} with desination.".format(file)
                    )
                else:
                    self.log.info(
                        "Adding source script {} with destination {}.".format(
                            parse[0], parse[1]
                        )
                    )
                    self.disser.addFileSource(parse[0], parse[1])
                    tags_parsed += 1
            else:
                self.log.error(
                    "File {} not parsed as str or dict with destination. Parsed as {}.".format(
                        file, type(file)
                    )
                )
        self.log.info("Parsed {} tags in Source Scripts".format(tags_parsed))
        return tags_parsed > 0

    # Targets
    def parse_targets_tag(self, targets: dict) -> bool:
        return True
