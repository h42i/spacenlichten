import sys
import os
import threading
import socket
import time
import datetime
import ipaddress
import functools

import logger
import encoding

class UDPError(Exception):
    pass

class UDPServer(threading.Thread):
    def __init__(self, ip, port, callback):
        threading.Thread.__init__(self)
        
        self._ip = ip
        self._port = port
        self._ip_version = ipaddress.ip_address(ip).version
        
        self._callback = callback
        
        self._sock = None
        self._buffer_size = 2**16
        
        self._current_addr = None
        
        self._stopped = False
    
    def run(self):
        try:
            if self._ip_version == 4:
                addr_info = socket.getaddrinfo(self._ip, self._port, 0, 0, socket.SOL_UDP, socket.AF_INET)
                
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                self._sock.bind(addr_info[0][4])
            elif self_.ip_version == 6:
                # UNTESTED
                if not socket.has_ipv6:
                    logger.log("[UDP] No IPv6 in here, dude. Go play with v4 again.")
                
                addr_info = socket.getaddrinfo(self._ip, self._port, 0, 0, socket.SOL_UDP, socket.AF_INET6)
                
                self._sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                self._sock.bind(addr_info[0][4])
            else:
                raise UDPError("Is this even IP?!")
        except socket.error:
            logger.log("[UDP] No socket for you. Sockets are out.")
            self._stopped = True
        except:
            logger.log("[UDP] Something really went wrong.")
            self._stopped = True
        
        while not self._stopped:
            try:
                # buffer size necessary to handle for example large pixel matrices
                data, self._current_addr = self._sock.recvfrom(self._buffer_size)
                
                logger.log("[UDP] Incomingn data from " + addr[0] + " to " + self._ip + "...")
                
                dec_data = None
                
                try:
                    dec_data = encoding.decode_data(data)
                except:
                    error = sys.exc_info()[0]
                    
                    logger.log("Invalid data. I will not bother the handler with this mess.")
                
                if dec_data != None:
                    try:
                        self._callback(dec_data, self._sender)
                    except:
                        error = sys.exc_info()[0]
                        logger.log("[UDP] Could not call the handler. Meh.")
            except:
                # uhm. well, fuck...
                error = sys.exc_info()[0]
        
        if self._sock != None:
            self._sock.close()
    
    def _sender(self, string):
        if self._sock != None and self._current_addr != None:
            enc_data = None
            
            try:
                enc_data = encoding.encode_data(string)
            except:
                logger.log("[UDP] Could not encode the string given by the handler.")
            
            try:
                self._sock.sendto(enc_data, (self._current_addr, self._port))
            except:
                logger.log("[UDP] Could not send data. We're fucked.")
    
    def _broadcast_sender(self, string):
        if self._sock != None:
            enc_data = None
            
            try:
                enc_data = encoding.encode_data(string)
            except socket.error:
                logger.log("[UDP] Could not encode the string given by the handler.")
            
            try:
                self._sock.sendto(enc_data, ("<broadcast>", self._port))
            except socket.error:
                logger.log("[UDP] Could not broadcast data. We're fucked.")
    
    def terminate(self):
        self._stopped = True
        self.join()
