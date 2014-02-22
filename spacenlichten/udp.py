import sys
import os
import threading
import socket
import time
import datetime
import ipaddress
import functools

import encoding

from logger import log

UDP_BUFFER_SIZE = 2**16

class UDPError(Exception):
    pass

class UDPServer(threading.Thread):
    def __init__(self, ip, port, callback):
        threading.Thread.__init__(self)
        
        self.name = "UDP|" + ip + ":" + str(port)
        
        self._ip = ip
        self._port = port
        self._ip_version = ipaddress.ip_address(ip).version
        
        self._callback = callback
        
        self._sock = None
        self._cur_addr = None
        
        self._stopped = False
    
    def run(self):
        try:
            if self._ip_version == 4:
                addr_info = socket.getaddrinfo(self._ip,
                                               self._port,
                                               0,
                                               0,
                                               socket.SOL_UDP,
                                               socket.AF_INET)
                
                self._sock = socket.socket(socket.AF_INET,
                                           socket.SOCK_DGRAM)
                self._sock.setsockopt(socket.SOL_SOCKET,
                                      socket.SO_BROADCAST,
                                      1)
                self._sock.bind(addr_info[0][4])
            elif self_.ip_version == 6:
                # UNTESTED
                if not socket.has_ipv6:
                    log.critical("No IPv6 in here, dude. Go play with "
                                 "v4 again.")
                
                addr_info = socket.getaddrinfo(self._ip,
                                               self._port,
                                               0,
                                               0,
                                               socket.SOL_UDP,
                                               socket.AF_INET6)
                
                self._sock = socket.socket(socket.AF_INET6,
                                           socket.SOCK_DGRAM)
                self._sock.setsockopt(socket.SOL_SOCKET,
                                      socket.SO_BROADCAST,
                                      1)
                self._sock.bind(addr_info[0][4])
            else:
                log.critical("IP version not supported.")
                self._stopped = True
        except socket.error:
            logging.critical("No socket for you. Sockets are out.")
            self._stopped = True
        except:
            log.critical("Something really went wrong.")
            self._stopped = True
        
        while not self._stopped:
            try:
                data, self._cur_addr = self._sock.recvfrom(UDP_BUFFER_SIZE)
                
                log.info("Incomingn data from %s", self._cur_addr)
                
                dec_data = None
                
                try:
                    dec_data = encoding.decode_data(data)
                except:
                    log.error("Invalid data. I will not bother the "
                              "handler with this mess.")
                
                if dec_data != None and dec_data != "":
                    try:
                        self._callback(dec_data, self._sender)
                    except:
                        log.error("Error while calling the handler.")
            except:
                logging.critical("An unexpected error occured.")
                self._stopped = True
        
        log.info("Stopping.")
        
        if self._sock != None:
            self._sock.close()
    
    def _sender(self, string):
        if self._sock != None and self._cur_addr != None:
            enc_data = None
            
            try:
                enc_data = encoding.encode_data(string)
            except:
                log.info("Could not encode the string given by the "
                         "handler.")
            
            try:
                self._sock.sendto(enc_data, (self._cur_addr, self._port))
            except:
                log.info("Could not send data.")
    
    def _broadcast_sender(self, string):
        if self._sock != None:
            enc_data = None
            
            try:
                enc_data = encoding.encode_data(string)
            except:
                log.info("Could not encode the string given by the "
                         "handler.")
            
            try:
                self._sock.sendto(enc_data, ("<broadcast>", self._port))
            except:
                log.info("Could not broadcast data.")
    
    def terminate(self):
        self._stopped = True
        self.join()
