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

import aliasing
import handler

from logger import log

IPC_HOST = "" # "localhost" would make it a private server
IPC_PORT = 3001
IPC_BUFFER_SIZE = 2**10

ACTIVE_DIR_NAME = ".active"

class NodeError(Exception):
    pass

class Node(threading.Thread):
    """
    Node server managing the different handlers.
    """
    
    def __init__(self, port, interface, interface_tool, handlers_dir):
        threading.Thread.__init__(self)
        
        self.name = "node"
        
        self._port = port
        self._interface = interface
        self._interface_tool = interface_tool
        
        self.handlers_dir = os.path.abspath(handlers_dir)
        
        active_rel_dir = os.path.join(handlers_dir, ACTIVE_DIR_NAME)
        self._active_dir = os.path.abspath(active_rel_dir)
        
        self._alias_control = aliasing.AliasControl(self._interface,
                                                    self._interface_tool)
        
        self._handlers = {}
        
        self._ipc_sock = socket.socket(socket.AF_INET,
                                       socket.SOCK_STREAM)
        self._ipc_sock.bind((IPC_HOST, IPC_PORT))
        self._ipc_sock.listen(1)
        
        self._stopped = False
    
    def run(self):
        # enable all active handlers
        if os.path.exists(self._active_dir):
            for config_filename in os.listdir(self._active_dir):
                handler_name, ext = os.path.splitext(config_filename)
                
                if ext == ".handler":
                    self.enable_handler(handler_name)
        else:
            log.critical("Could not find %s directory in %s.",
                         ACTIVE_DIR_NAME,
                         os.path.abspath(handlers_dir))
        
        self.start_all_handlers()
        
        while not self._stopped:
            conn, addr = self._ipc_sock.accept()
            
            if True:
                # one recv should be enough for all data; yolo
                json_string = conn.recv(IPC_BUFFER_SIZE).decode("utf-8")
                request_data = json.loads(json_string)
                
                if request_data["command"] == "start":
                    self.start_handler(request_data["handler"])
                elif request_data["command"] == "stop":
                    self.stop_handler(request_data["handler"])
                elif request_data["command"] == "enable":
                    self.enable_handler(request_data["handler"])
                elif request_data["command"] == "disable":
                    self.disable_handler(request_data["handler"])
                elif request_data["command"] == "status":
                    status = "disabled"
                    
                    if request_data["handler"] in self._handlers:
                        handler = self._handlers[request_data["handler"]]
                        
                        if handler.is_alive():
                            status = "running"
                        else:
                            status = "stopped"
                    
                    response_data = { "status": status, "handler": request_data["handler"] }
                    conn.send(json.dumps(response_data).encode("utf-8"))
                elif request_data["command"] == "handlers_dir":
                    response_data = { "handlers_dir": self.handlers_dir }
                    conn.send(json.dumps(response_data).encode("utf-8"))
            #except:
            #    pass
            
            conn.close()
        
        self._ipc_sock.close()
        
        self.stop_all_handlers()
        self._alias_control.remove_all_aliases()
    
    def start_handler(self, handler_name):
        if handler_name in self._handlers:
            handler = self._handlers[handler_name]
            
            try:
                if not handler.is_alive():
                    self._handlers[handler_name] = handler.recreate()
                
                log.info("Starting %s.", handler_name)
                
                # start and stuff has to be performed directly on the
                # dict object, otherwise thread status isn't observable
                self._handlers[handler_name].start()
                self._handlers[handler_name].initialize()
            except RuntimeError:
                log.warning("%s is already running.",
                            handler_name)
    
    def start_all_handlers(self):
        for handler_name in self._handlers:
            handler = self._handlers[handler_name]
            
            try:
                if not handler.is_alive():
                    self._handlers[handler_name] = handler.recreate()
                
                log.info("Starting %s.", handler_name)
                
                # start and stuff has to be performed directly on the
                # dict object, otherwise thread status isn't observable
                self._handlers[handler_name].start()
                self._handlers[handler_name].initialize()
            except RuntimeError:
                log.warning("%s is already running.",
                            handler_name)
    
    def stop_handler(self, handler_name):
        if handler_name in self._handlers:
            handler = self._handlers[handler_name]
            
            if handler.is_alive():
                log.info("Stopping %s.", handler_name)
                handler.terminate()
    
    def stop_all_handlers(self):
        for handler_name in self._handlers:
            handler = self._handlers[handler_name]
            
            if handler.is_alive():
                log.info("Stopping %s.", handler_name)
                handler.terminate()
    
    def enable_handler(self, handler_name):
        if not handler_name in self._handlers:
            handler_filename = handler_name + ".handler"
            
            new_handler = handler.Handler(self._active_dir,
                                          handler_filename,
                                          self._port)
            
            log.info("Aliasing ip %s.", new_handler.ip)
            
            try:
                self._alias_control.add_alias(new_handler.ip, 8)
                self._handlers[handler_name] = new_handler
            except:
                log.critical("Could not create alias for %s. The "
                             "associated handler will not start. Are "
                             "you root?",
                             new_handler.ip)
        else:
            log.warning("%s is already enabled.", handler_name)
    
    def disable_handler(self, handler_name):
        if handler_name in self._handlers:
            handler = self._handlers[handler_name]
            
            if not handler.is_alive():
                log.info("Dealiasing ip %s.", handler.ip)
                self._alias_control.remove_alias(handler.ip, 8)
                
                del self._handlers[handler_name]
            else:
                log.error("Could not disable %s, it is still "
                          "running.",
                          handler_name)
    
    def _dummy_connect(self, host, port):
        dummy_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dummy_conn.connect((host, port))
        dummy_conn.send("".encode("utf-8"))
        dummy_conn.close()
    
    def terminate(self):
        self._stopped = True
        
        self.stop_all_handlers()
        self._alias_control.remove_all_aliases()
        
        if self.is_alive():
            self.join()
        
        self._dummy_connect(IPC_HOST, IPC_PORT)
