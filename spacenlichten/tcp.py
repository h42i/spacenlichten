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

TCP_BUFFER_SIZE = 2**16

class TCPError(Exception):
    pass

class TCPServer(threading.Thread):
    def __init__(self, ip, port, callback):
        threading.Thread.__init__(self)
        
        self.name = "TCP|" + ip + ":" + str(port)
        
        self._ip = ip
        self._port = port
        self._ip_version = ipaddress.ip_address(ip).version
        
        self._callback = callback
        
        self._sock = None
        
        self._conn_threads = []
        
        self._stopped = False
    
    def run(self):
        try:
            if self._ip_version == 4:
                addr_info = socket.getaddrinfo(self._ip,
                                               self._port,
                                               0,
                                               0,
                                               socket.SOL_TCP,
                                               socket.AF_INET)
                
                self._sock = socket.socket(socket.AF_INET,
                                           socket.SOCK_STREAM)
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
                                               socket.SOL_TCP,
                                               socket.AF_INET6)
                
                self._sock = socket.socket(socket.AF_INET6,
                                           socket.SOCK_STREAM)
                self._sock.bind(addr_info[0][4])
            else:
                log.critical("IP version not supported.")
                self._stopped = True
            
            self._sock.listen(3)
        except socket.error:
            log.critical("No socket for you. Sockets are out.")
            self._stopped = True
        except:
            log.critical("Something really went wrong.")
            self._stopped = True
        
        while not self._stopped:
            try:
                log.info("Accepting clients.")
                
                conn, addr = self._sock.accept()
                
                log.info("Connection from %s.", addr[0])
                
                conn_thread = TCPServerConnection(self._conn_threads,
                                                  conn,
                                                  self._callback)
                
                self._conn_threads.append(conn_thread)
                
                conn_thread.start()
            except:
                log.critical("An unexpected error occured.")
                self._stopped = True
        
        log.info("Stopping.")
        
        if self._sock != None:
            self._sock.close()
    
    def _broadcast_sender(self, string):
        if self._sock != None:
            for conn_thread in self._conn_threads:
                try:
                    conn_thread._sender(string)
                except:
                    log.error("Could not send data to client while "
                              "broadcasting.")
    
    def terminate(self):
        for conn_thread in self._conn_threads:
            conn_thread.join()
        
        self._stopped = True
        self.join()

class TCPServerConnection(threading.Thread):
    def __init__(self, conn_threads, conn, callback):
        threading.Thread.__init__(self)
        
        self._conn = conn
        self._conn_threads = conn_threads
        
        self._callback = callback
    
    def run(self):
        data = self._conn.recv(TCP_BUFFER_SIZE)
        
        dec_data = None
        
        try:
            dec_data = encoding.decode_data(data)
        except:
            log.error("Invalid data. I will not bother the handler "
                      "with this mess.")
        
        if dec_data != None and dec_data != "":
            try:
                self._callback(dec_data, self._sender)
            except:
                log.error("Could not call the handler.")
        
        self._conn.close()
        self._conn_threads.remove(self)
    
    def _sender(self, string):
        try:
            enc_data = encoding.encode_data(string)
        except:
            log.error("Could not encode the string given by the "
                      "handler.")
        
        try:
            self._conn.send(enc_data)
        except:
            log.error("Could not send data.")
