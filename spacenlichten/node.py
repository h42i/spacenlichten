import sys
import os
import threading
import socket
import time
import datetime
import re
import ipaddress
import functools
import json


import logger
import aliasing
import handler

IPC_HOST = "localhost"
IPC_PORT = 3001
IPC_BUFFER_SIZE = 2**10

class NodeError(Exception):
    pass

class Node(threading.Thread):
    """
    Node server managing the different handlers.
    """
    
    def __init__(self, port, interface, interface_tool, handlers_directory):
        threading.Thread.__init__(self)
        
        self._port = port
        self._interface = interface
        self._interface_tool = interface_tool
        self._handlers_directory = os.path.abspath(handlers_directory)
        
        self._alias_control = aliasing.AliasControl(self._interface,
                                                    self._interface_tool)
        
        self._handlers = []
        
        self._ipc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ipc_sock.bind((IPC_HOST, IPC_PORT))
        self._ipc_sock.listen(1)
        
        self._ipc_buffer_size = 2**8
        
        self._stopped = False
        
        for config_filename in os.listdir(self._handlers_directory):
            if config_filename.endswith(".handler"):
                new_handler = handler.Handler(self._handlers_directory,
                                              config_filename,
                                              self._port)
                
                self._handlers.append(new_handler)
                
                logger.log("Aliasing ip " + new_handler.ip + ".")
                self._alias_control.add_alias(new_handler.ip, 8)
    
    def __del__(self):
        self.stop_all_handlers()
        self._alias_control.remove_all_aliases()
    
    def run(self):
        self.start_all_handlers()
        
        while not self._stopped:
            conn, addr = self._ipc_sock.accept()
            
            try:
                # one recv should be enough for all data; yolo
                data = json.loads(conn.recv(IPC_BUFFER_SIZE).decode("utf-8"))
                
                if data["command"] == "start":
                    self.start_handler(data["handler"])
                elif data["command"] == "stop":
                    self.stop_handler(data["handler"])
                elif data["command"] == "status":
                    pass
            except:
                pass
            
            conn.close()
        
        self._ipc_sock.close()
        
        self.stop_all_handlers()
        self._alias_control.remove_all_aliases()
    
    def start_handler(self, handler_name):
        for handler in self._handlers:
            if handler.name == handler_name:
                try:
                    logger.log("Starting " + handler.name + ".")
                    
                    if handler.stopped:
                        handler = handler.recreate()
                    
                    handler.start()
                    handler.initialize()
                except RuntimeError:
                    logger.log(handler.name + " is already running.")
    
    def start_all_handlers(self):
        for handler in self._handlers:
            try:
                logger.log("Starting " + handler.name + ".")
                
                if handler.stopped:
                    handler = handler.recreate()
                
                handler.start()
                handler.initialize()
            except RuntimeError:
                logger.log(handler.name + " is already running.")
    
    def _dummy_connect_tcp(self, host, port):
        dummy_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dummy_conn.connect((host, port))
        dummy_conn.send("".encode("utf-8"))
        
        dummy_conn.close()
    
    def _dummy_connect_udp(self, host, port):
        dummy_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dummy_conn.sendto("".encode("utf-8"), (host, port))
    
    def stop_handler(self, handler_name):
        for handler in self._handlers:
            if handler.name == handler_name and not handler.stopped:
                logger.log("Stopping " + handler.name + ".")
                
                handler.terminate()
                
                # wake up thread so they can finish correctly
                self._dummy_connect_udp(handler.ip, self._port)
                self._dummy_connect_tcp(handler.ip, self._port)
    
    def stop_all_handlers(self):
        for handler in self._handlers:
            if not handler.stopped:
                logger.log("Stopping " + handler.name + ".")
                
                handler.terminate()
                
                # wake up thread so they can finish correctly
                self._dummy_connect_udp(handler.ip, self._port)
                self._dummy_connect_tcp(handler.ip, self._port)
    
    def terminate(self):
        self.stop_all_handlers()
        self._alias_control.remove_all_aliases()
        
        self._stopped = True
        self.join()
