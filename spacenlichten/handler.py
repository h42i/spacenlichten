import os
import yaml
import threading

import logger
import aliasing
import reflection
import udp
import tcp

class HandlerError(Exception):
    pass

class Handler(threading.Thread):
    """
    This is the configuration structure for a devices handler.
    
    A configuration file should look like the following:
    
    ip: 10.23.42.123
    script: path/to/handler.py
    """
    
    def __init__(self, handlers_directory, config_filename, port):
        threading.Thread.__init__(self)
        
        path = os.path.join(handlers_directory, config_filename)
        
        self._handlers_directory = handlers_directory
        self._config_filename = config_filename
        self._port = port
        
        try:
            with open(path, "r") as config_file:
                config = yaml.load(config_file)
                
                self.name = config["name"]
                self.ip = config["ip"]
                self.script_path = config["script"]
                
                if not os.path.isabs(self.script_path):
                    self.script_path = os.path.join(handlers_directory, self.script_path)
                
                self._mod = reflection._import_module(self.script_path)
        except:
            raise HandlerError("Unable to use handler configuration file " + config_filename + "!")
        
        self._udp_server = udp.UDPServer(self.ip, port, self.receive)
        self._tcp_server = tcp.TCPServer(self.ip, port, self.receive)
        
        self.stopped = False
    
    def _common_broadcast(self, string):
        self._udp_server._broadcast_sender(string)
        self._tcp_server._broadcast_sender(string)
    
    def initialize(self):
        self._mod.initialize(self._common_broadcast)
    
    def receive(self, json_string, send):
        self._mod.receive(json_string, send)
    
    def run(self):
        logger.log("Starting a node server on " + self.ip + ".")
        
        self._udp_server.start()
        self._tcp_server.start()
        
        while not self.stopped:
            self._mod.run()
    
    def recreate(self):
        return Handler(self._handlers_directory,
                       self._config_filename,
                       self._port)
    
    def terminate(self):
        self.stopped = True
        self.join()
        
        self._udp_server.terminate()
        self._tcp_server.terminate()
