import yaml
import threading

from spacenlichten import logger
from spacenlichten import aliasing
from spacenlichten import reflection
from spacenlichten import udp
from spacenlichten import tcp

class HandlerError(Exception):
    pass

class Handler(threading.Thread):
    """
    This is the configuration structure for a devices handler.
    
    Such a file should look like the following:
    
    ip: 10.23.42.123
    script: path/to/handler.py
    """
    
    def __init__(self, path):
        threading.Thread.__init__(self)
        
        try:
            with open(path, "r") as config_file:
                config = yaml.load(config_file)
                
                self.ip = config["ip"]
                self._mod = reflection._import_module(config["script"])
        except:
            raise HandlerError("Unable to use handler configuration file \"" + path + "\"")
        
        self._udp_server = udp.UDPServer(self.ip, 20000, self.receive)
        self._tcp_server = tcp.TCPServer(self.ip, 20000, self.receive)
    
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
        
        while True:
            self._mod.run()
