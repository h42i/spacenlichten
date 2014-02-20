import sys
import os
import argparse

import node
import aliasing
import config
import logger
import reflection

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(prog='spacenlichten',
                                         formatter_class=lambda prog:
                                             argparse.HelpFormatter(prog, max_help_position=42))
    
    arg_parser.add_argument("-c",
                            "--config",
                            help="configuration file",
                            action="store",
                            default="spacenlichten.conf")
    
    arg_parser.add_argument("-l",
                            "--log",
                            help="log file",
                            action="store",
                            default=None)
    
    arg_parser.add_argument("-v",
                            "--verbose",
                            help="run in verbose mode",
                            action="store_true")
    
    args = arg_parser.parse_args()
    
    logger.verbose = args.verbose
    logger.log_path = args.log
    
    main_config = config.Config(args.config)
    
    selected_interface_tool = None
    
    if main_config.interface_tool == "ip":
        selected_interface_tool = aliasing.IP
    elif main_config.interface_tool == "ifconfig":
        selected_interface_tool = aliasing.IFCONFIG
    
    main_node = node.Node(main_config.port,
                          main_config.interface,
                          selected_interface_tool,
                          main_config.handlers_directory)
    
    main_node.start()
    
    try:
        while input() != "die":
            pass
    except:
        pass
    
    main_node.terminate()
