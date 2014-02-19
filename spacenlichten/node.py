import sys
import os
import threading
import socket
import time
import datetime
import re
import ipaddress
import functools

import logger
import aliasing
import handler

class NodeError(Exception):
    pass

class Node:
    """
    Node server managing the different handlers.
    """
    
    def __init__(self, port, interface, interface_tool, handlers_directory):
        self._port = port
        self._interface = interface
        self._interface_tool = interface_tool
        self._handlers_directory = os.path.abspath(handlers_directory)
        
        self._alias_control = aliasing.AliasControl(self._interface,
                                                    self._interface_tool)
        
        self._handlers = []
        
        for config_filename in os.listdir(self._handlers_directory):
            if config_filename.endswith(".handler"):
                new_handler = handler.Handler(self._handlers_directory,
                                              config_filename,
                                              self._port)
                
                self._handlers.append(new_handler)
                
                logger.log("Aliasing ip " + new_handler.ip + ".")
                self._alias_control.add_alias(new_handler.ip, 8)
    
    def start(self):
        for handler in self._handlers:
            handler.start()
            handler.initialize()
    
    def stop(self):
        for handler in self._handlers:
            handler.terminate()
