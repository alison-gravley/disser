import argparse
import log_config


def main(input_file: str, log_file):
    if log_file is None or len(log_file) == 0:
        main_logger = log_config.get_logger_console_only("main")
        main_logger.info("Log to console only")
    else:
        main_logger = log_config.get_logger_file_only("main", log_file)
        main_logger.info("Logging to file")

    # Now start the import
    import read_config

    if input_file is None:
        main_logger.error("Input File is None")
    else:
        config = read_config.DisserImport(args.input_file)
        import_ok = config.import_config()

        if import_ok:
            main_logger.info("Successfully loaded configuration.")
            config.disser.get_file_list()
        else:
            main_logger.error("Failed to import configuration.")


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="disser", description="Disseminate files and commands to multiple servers"
    )

    parser.add_argument(
        "-f",
        "--file",
        dest="input_file",
        required=True,
        help="Configuration file to import.",
    )
    parser.add_argument(
        "-l", "--log", dest="log_file", required=False, help="Log output of disser"
    )
    args = parser.parse_args()
    main(args.input_file, args.log_file)
