import os
import yaml
import threading

import aliasing
import reflection
import udp
import tcp

from logger import log

class HandlerError(Exception):
    pass

class Handler(threading.Thread):
    """
    This is the configuration structure for a devices handler.
    
    A configuration file should look like the following:
    
    ip: 10.23.42.123
    script: path/to/handler.py
    """
    
    def __init__(self, handlers_dir, config_filename, port):
        threading.Thread.__init__(self)
        
        self._handlers_dir = handlers_dir
        self._config_filename = config_filename
        self._port = port
        
        path = os.path.join(self._handlers_dir, self._config_filename)
        
        try:
            with open(path, "r") as config_file:
                config = yaml.load(config_file)
                
                self.name = os.path.splitext(self._config_filename)[0]
                self.ip = config["ip"]
                self.script_path = config["script"]
                
                if not os.path.isabs(self.script_path):
                    self.script_path = os.path.join(handlers_dir,
                                                    self.script_path)
                
                self._mod = reflection._import_module(self.script_path)
        except:
            log.critical("Unable to use handler config file %s.",
                         config_filename)
        
        self._udp_server = udp.UDPServer(self.ip, port, self.receive)
        self._tcp_server = tcp.TCPServer(self.ip, port, self.receive)
        
        self._stopped = True
    
    def _common_broadcast(self, string):
        self._udp_server._broadcast_sender(string)
        self._tcp_server._broadcast_sender(string)
    
    def initialize(self):
        self._mod.initialize(self._common_broadcast)
    
    def receive(self, json_string, send):
        self._mod.receive(json_string, send)
    
    def run(self):
        log.info("Starting a servers on %s.", self.ip)
        
        self._udp_server.start()
        self._tcp_server.start()
        
        self._stopped = False
        
        while not self._stopped:
            self._mod.run()
    
    def recreate(self):
        return Handler(self._handlers_dir,
                       self._config_filename,
                       self._port)
    
    def terminate(self):
        self._stopped = True
        
        if self.is_alive():
            self.join()
        
        self._udp_server.terminate()
        self._tcp_server.terminate()
