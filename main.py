import argparse
import log
import read_config
import os

parser : argparse.ArgumentParser =  argparse.ArgumentParser(
    prog='disser',
    description='Disseminate files and commands to multiple servers')

parser.add_argument('-f','--file',
                    dest='input_file',
                    required=True,
                    help= "Configuration file to import.")
parser.add_argument('-l','--log',
                    dest='log_file',
                    required=False,
                    help= "Log output of disser")

args = parser.parse_args()

if args.log_file is None:
    main_logger = log.get_logger_console_only("main")
    main_logger.info("Log to console only")
else:
    main_logger = log.get_logger_file_only("main", args.log_file)
    main_logger.info("Logging to file")

if args.input_file is None:
    main_logger.error("Input File is None")
else:
    config = read_config.DisserImport(args.input_file)
    import_ok = config.import_config()
  
    

    
    