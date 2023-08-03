import logging
import sys

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
Log_Only = True
Log_File = ""


def get_stdout_handler() -> logging.StreamHandler:
    stdout_console = logging.StreamHandler(sys.stdout)
    stdout_console.setFormatter(FORMATTER)
    stdout_console.setLevel(logging.DEBUG)
    return stdout_console


def get_stderr_handler() -> logging.StreamHandler:
    stderr_console = logging.StreamHandler(sys.stderr)
    stderr_console.setFormatter(FORMATTER)
    stderr_console.setLevel(logging.WARN)
    return stderr_console


def get_file_handler(filename: str) -> logging.FileHandler:
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger_console_only(logger_name: str) -> logging.Logger:
    global Log_Only
    global Log_File
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_stdout_handler())
    logger.addHandler(get_stderr_handler())
    logger.propagate = False
    Log_Only = False
    Log_File = ""
    return logger


def get_logger_file_only(logger_name: str, filename: str) -> logging.Logger:
    global Log_Only
    global Log_File
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler(filename))
    logger.propagate = False
    Log_Only = True
    Log_File = filename
    return logger


def get_logger(logger_name: str) -> logging.Logger:
    global Log_Only
    global Log_File
    if Log_Only:
        return get_logger_file_only(logger_name, Log_File)
    else:
        return get_logger_console_only(logger_name)
