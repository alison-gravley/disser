import log_config
import logging
import os
from paramiko import SSHConfig
from paramiko import SSHConfigDict
from enum import Enum

log: logging.Logger = log_config.get_logger("Server")


class Server:
    def __init__(
        self,
        name: str,
        hostname: str | None = None,
        username: str | None = None,
        password: str | None = None,
        port: int | None = 22,
        sshconfig: str | None = None,
        hostkey: str | None = None,
        identity: str | None = None,
    ) -> None:
        self.name = name
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.sshconfig = sshconfig
        self.hostkey = hostkey
        self.identity_file = identity

        if self.sshconfig is not None:
            self.parse_sshconfig()

        self.is_valid = self.config_is_valid()

    def _to_string(self) -> str:
        return "{}, hostname ({}), username ({}), password ({}), port ({}), sshconfig ({}), hostkey ({}), identity ({})".format(
            self.name,
            self.hostname,
            self.username,
            (lambda: "****", lambda: "NONE")[self.password is None](),
            self.port,
            self.sshconfig,
            self.hostkey,
            self.identity_file,
        )

    def parse_sshconfig(self):
        if self.sshconfig is None:
            return
        if self.hostkey is None:
            log.error(
                "sshconfig ({}) without hostkey. Did you put it under hostname?".format(
                    self.sshconfig
                )
            )
            return

        if not os.path.exists(self.sshconfig):
            log.error("sshconfig ({}) does not exist.".format(self.sshconfig))
            return

        with open(self.sshconfig) as config_file:
            hostname: str = ""
            config = SSHConfig()
            config.parse(config_file)
            host_config: SSHConfigDict = config.lookup(self.hostkey)

            for field in host_config.keys():
                match field:
                    case "hostname":
                        hostname = host_config[field]
                        if self.hostname is not None and self.hostname == hostname:
                            log.warn(
                                "Config file specified hostname ({}) when using sshconfig, but they match. If using sshconfig, hostname is unnecessary.".format(
                                    self.hostname
                                )
                            )
                        elif self.hostname is not None and self.hostname != hostname:
                            log.error(
                                "Config file specified hostname ({}) when sshconfig specified ({}). sshconfig takes precendence".format(
                                    self.hostname, hostname
                                )
                            )
                        self.hostname = hostname
                    case "port":
                        self.port = host_config.as_int(field)
                    case "identityfile":
                        if len(host_config[field]) > 1:
                            log.warn(
                                "Multiple identity files not supported. First identity ({}) will be used.".format(
                                    host_config[field][0]
                                )
                            )
                        self.identity_file = host_config[field][0]
                    case _:
                        log.warn(
                            "Unknown field ({}) in hostkey ({})".format(
                                field, self.hostkey
                            )
                        )

    def config_is_valid(self) -> bool:
        if self.hostname is None:
            log.error("Missing hostname from configuration. Invalid config.")
            return False
        if self.password is None and self.identity_file is None:
            log.error("Missing password without valid identity. Invalid config.")
            return False
        return True


def parse_string_tag(name: str, tag):
    if type(tag) is not str:
        log.error(
            "{} ({}) is not of type str. Type is ({}).".format(name, tag, type(tag))
        )
        return None
    elif len(tag) == 0:
        return None
    else:
        return tag


def parse_port_tag(port) -> int:
    if type(port) is not int:
        log.error(
            "Port ({}) is not of type int. Type is ({}).".format(port, type(port))
        )
        return 22
    else:
        return port


@staticmethod
def parse_server_tag(name: str, server: dict) -> Server | None:
    hostname = None
    username = None
    password = None
    sshconfig = None
    hostkey = None
    identity = None
    port: int = 22

    for keys in server:
        match keys:
            case "hostname":
                hostname = parse_string_tag(keys, server[keys])
            case "username":
                username = parse_string_tag(keys, server[keys])
            case "password":
                password = parse_string_tag(keys, server[keys])
            case "port":
                port = parse_port_tag(server[keys])
            case "sshconfig":
                sshconfig = parse_string_tag(keys, server[keys])
            case "hostkey":
                hostkey = parse_string_tag(keys, server[keys])
            case "identity":
                identity = parse_string_tag(keys, server[keys])
            case _:
                log.error("Unknown tag ({}) under Source. Ignoring.".format(keys))

    server_class = Server(
        name,
        hostname=hostname,
        username=username,
        password=password,
        port=port,
        sshconfig=sshconfig,
        hostkey=hostkey,
        identity=identity,
    )

    if server_class.is_valid:
        log.info("Successfully Parsed: {}".format(server_class._to_string()))
        return server_class
    else:
        return None
