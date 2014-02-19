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

class TCPError(Exception):
    pass

class TCPServer(threading.Thread):
    def __init__(self, ip, port, callback):
        threading.Thread.__init__(self)
        
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
                addr_info = socket.getaddrinfo(self._ip, self._port, 0, 0, socket.SOL_TCP, socket.AF_INET)
                
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.bind(addr_info[0][4])
            elif self_.ip_version == 6:
                # UNTESTED
                if not socket.has_ipv6:
                    logger.log("[TCP] No IPv6 in here, dude. Go play with v4 again.")
                
                addr_info = socket.getaddrinfo(self._ip, self._port, 0, 0, socket.SOL_TCP, socket.AF_INET6)
                
                self._sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                self._sock.bind(addr_info[0][4])
            else:
                raise TCPError("Is this even IP?!")
            
            self._sock.listen(3)
        except socket.error:
            logger.log("[TCP] No socket for you. Sockets are out.")
            self._stopped = True
        except:
            logger.log("[TCP] Something really went wrong.")
            self._stopped = True
        
        while not self._stopped:
            try:
                logger.log("[TCP] Accepting clients...")
                
                conn, addr = self._sock.accept()                
                logger.log("[TCP] Connection from " + addr[0] + " to " + self._ip + "...")
                
                conn_thread = TCPServerConnection(self._conn_threads, conn, self._callback)
                self._conn_threads.append(conn_thread)
                
                conn_thread.start()
            except socket.error:
                # uhm. well, fuck...
                error = sys.exc_info()[0]
                logger.log("[TCP] " + str(error))
        
        if self._sock != None:
            self._sock.close()
    
    def _broadcast_sender(self, string):
        if self._sock != None:
            for conn_thread in self._conn_threads:
                try:
                    conn_thread._sender(string)
                except:
                    logger.log("[TCP] Could not send data to client while broadcasting. Shit.")
    
    def terminate(self):
        for conn_thread in self._conn_threads:
            conn_thread.terminate()
        
        if self._sock != None:
            self._sock.close()
        
        self._stopped = True
        self.join()

class TCPServerConnection(threading.Thread):
    def __init__(self, conn_threads, conn, callback):
        threading.Thread.__init__(self)
        
        self._conn = conn
        self._conn_threads = conn_threads
        
        self._callback = callback
        
        self._buffer_size = 2**16
    
    def run(self):
        # buffer size necessary to handle for example large pixel matrices
        data = self._conn.recv(self._buffer_size)
        
        dec_data = None
        
        try:
            dec_data = encoding.decode_data(data)
        except:
            error = sys.exc_info()[0]
            logger.log("[TCP] Invalid data. I will not bother the handler with this mess.")
        
        if dec_data != None:
            try:
                self._callback(dec_data, self._sender)
            except socket.error:
                error = sys.exc_info()[0]
                logger.log("[TCP] Could not call the handler. Meh.")
        
        self._conn.close()
        
        self._conn_threads.remove(self)
    
    def _sender(self, string):
        try:
            enc_data = encoding.encode_data(string)
        except:
            logger.log("[TCP] Could not encode the string given by the handler.")
        
        try:
            self._conn.send(enc_data)
        except socket.error:
            logger.log("[TCP] Could not send data. Mimimi!")
    
    def terminate(self):
        self._conn.close()
        self._conn_threads.remove(self)
        
        self.join()
