import sys
import os
import threading
import socket
import time
import datetime
import re
import ipaddress
import functools

from spacenlichten import logger
from spacenlichten import aliasing
from spacenlichten import handler

class NodeError(Exception):
    pass

class Node:
    """
    Node server managing the different interfaces
    """
    
    def __init__(self, working_dir, iface, iface_tool):
        self._working_dir = os.path.abspath(working_dir)
        
        self._iface = iface
        self._iface_tool = iface_tool
        
        self._alias_ctrl = aliasing.AliasControl(iface, iface_tool)
        
        self._handlers = []
        
        for config_path in os.listdir(self._working_dir):
            if config_path.endswith(".handler"):
                new_handler = handler.Handler(config_path)
                self._handlers.append(new_handler)
                
                logger.log("Aliasing ip " + new_handler.ip + ".")
                self._alias_ctrl.add_alias(new_handler.ip, 8)
    
    def start(self):
        for handler in self._handlers:
            handler.start()
            handler.initialize()
    
    def stop(self):
        for handler in self._handlers:
            handler.terminate()
