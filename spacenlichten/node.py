import sys
import threading
import socket
import time
import datetime
import re
import ipaddress
import functools

from spacenlichten import aliasing
from spacenlichten import api

class NodeError(Exception):
    pass

def _log(string):
    now_string = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    
    print("[" + now_string + "] spacenlichten> " + string)

def _decode_data(data):
    """
    Generate a python string from utf-8 encoded data and
    strip the http header if present.
    """
    
    dec_data = None
    
    try:
        dec_data = data.decode("utf-8")
        
        # strip http header if present
        first_line = dec_data.split("\n")[0]
        
        http_match = re.search("HTTP", first_line)
                    
        if http_match:
            http_strip_match = re.search("\r?\n(\r?\n)+", dec_data, re.MULTILINE)
            
            if http_strip_match:
                dec_data = dec_data[http_strip_match.end():]
    except:
        error = sys.exc_info()[0]
        
        _log("Invalid data. I will not bother the handler with this mess.")
        _log(str(error))
    
    return dec_data

def _encode_data(string):
    """
    Generate utf-8 encoded data from a python string.
    """
    
    return string.encode("utf-8")

def _common_broadcast(string, udp_server, tcp_server):
    udp_server._broadcast_sender(string)
    tcp_server._broadcast_sender(string)

class UDPServerThread(threading.Thread):
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
        
        try:
            if self._ip_version == 4:
                addr_info = socket.getaddrinfo(self._ip, self._port, 0, 0, socket.SOL_UDP, socket.AF_INET)
                
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                self._sock.bind(addr_info[0][4])
            elif self_.ip_version == 6:
                # UNTESTED
                if not socket.has_ipv6:
                    _log("[UDP] No IPv6 in here, dude. Go play with v4 again.")
                
                addr_info = socket.getaddrinfo(self._ip, self._port, 0, 0, socket.SOL_UDP, socket.AF_INET6)
                
                self._sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                self._sock.bind(addr_info[0][4])
            else:
                raise NodeError("Is this even IP?!")
        except socket.error:
            _log("[UDP] No socket for you. Sockets are out.")
            _log("[UDP] " + str(socket.error))
            
            self._stopped = True
        except:
            _log("[UDP] Something really went wrong.")
            
            self._stopped = True
    
    def run(self):
        while not self._stopped:
            try:
                # buffer size necessary to handle for example large pixel matrices
                data, self._current_addr = self._sock.recvfrom(self._buffer_size)
                
                _log("[UDP] Connection from " + addr[0] + " to " + self._ip + "...")
                
                dec_data = _decode_data(data)
                
                if dec_data != None:
                    try:
                        self._callback(dec_data)
                    except:
                        error = sys.exc_info()[0]
                        
                        _log("[UDP] Could not call the handler. Meh.")
                        _log("[UDP] " + str(error))
            except:
                # uhm. well, fuck...
                error = sys.exc_info()[0]
                
                _log("[UDP] " + str(error))
        
        if self._sock != None:
            self._sock.close()
    
    def _sender(self, string):
        if self._sock != None and self._current_addr != None:
            enc_data = None
            
            try:
                enc_data = _encode_data(string)
            except:
                _log("[UDP] Could not encode the string given by the client.")
            
            try:
                self._sock.sendto(enc_data, (self._current_addr, self._port))
            except:
                _log("[UDP] Could not send data. We're fucked.")
    
    def _broadcast_sender(self, string):
        if self._sock != None:
            enc_data = None
            
            try:
                enc_data = _encode_data(string)
            except:
                _log("[UDP] Could not encode the string given by the client.")
            
            try:
                self._sock.sendto(enc_data, ("<broadcast>", self._port))
            except:
                _log("[UDP] Could not broadcast data. We're fucked.")
    
    def terminate(self):
        self._stopped = True
        self.join()

class TCPServerThread(threading.Thread):
    def __init__(self, ip, port, callback):
        threading.Thread.__init__(self)
        
        self._ip = ip
        self._port = port
        self._ip_version = ipaddress.ip_address(ip).version
        
        self._callback = callback
        
        self._sock = None
        
        self._conn_threads = []
        
        self._stopped = False
        
        try:
            if self._ip_version == 4:
                addr_info = socket.getaddrinfo(self._ip, self._port, 0, 0, socket.SOL_TCP, socket.AF_INET)
                
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.bind(addr_info[0][4])
            elif self_.ip_version == 6:
                # UNTESTED
                if not socket.has_ipv6:
                    _log("[TCP] No IPv6 in here, dude. Go play with v4 again.")
                
                addr_info = socket.getaddrinfo(self._ip, self._port, 0, 0, socket.SOL_TCP, socket.AF_INET6)
                
                self._sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                self._sock.bind(addr_info[0][4])
            else:
                raise NodeError("Is this even IP?!")
            
            self._sock.listen(3)
        except socket.error:
            _log("[TCP] No socket for you. Sockets are out.")
            _log("[TCP] " + str(socket.error))
            
            self._stopped = True
        except:
            _log("[TCP] Something really went wrong.")
            
            self._stopped = True
    
    def run(self):
        while not self._stopped:
            try:
                _log("[TCP] Accepting clients...")
                
                conn, addr = self._sock.accept()
                
                _log("[TCP] Connection from " + addr[0] + " to " + self._ip + "...")
                
                conn_thread = TCPServerConnectionThread(self._conn_threads, conn, self._callback)
                print('len before: ' + str(len(self._conn_threads)))
                self._conn_threads.append(conn_thread)
                self._conn_threads.append(conn_thread)
                self._conn_threads.append(conn_thread)
                print('len after: ' + str(len(self._conn_threads)))
                conn_thread.start()
            except:
                # uhm. well, fuck...
                error = sys.exc_info()[0]
                
                _log("[TCP] " + str(error))
        
        if self._sock != None:
            self._sock.close()
    
    def _broadcast_sender(self, string):
        if self._sock != None:
            enc_data = None
            
            try:
                enc_data = _encode_data(string)
            except:
                _log("[TCP] Could not encode the string given by the client.")
            
            for conn_thread in self._conn_threads:
                try:
                    print('iaeaie')
                    conn_thread._sender_raw(enc_data)
                except:
                    _log("[TCP] Could not send data to client while broadcasting. Shit.")
    
    def terminate(self):
        for conn_thread in self._conn_threads:
            conn_thread.terminate()
        
        if self._sock != None:
            self._sock.close()
        
        self._stopped = True
        self.join()

class TCPServerConnectionThread(threading.Thread):
    def __init__(self, conn_threads, conn, callback):
        threading.Thread.__init__(self)
        
        self._conn = conn
        self._conn_threads = conn_threads
        
        self._callback = callback
        
        self._buffer_size = 2**16
    
    def run(self):
        # buffer size necessary to handle for example large pixel matrices
        data = self._conn.recv(self._buffer_size)
        
        dec_data = _decode_data(data)
        
        if dec_data != None:
            try:
                self._callback(dec_data)
            except:
                error = sys.exc_info()[0]
                
                _log("[TCP] It seems the handler is not even able to construct correct feedback.")
                _log("[TCP] " + str(error))
            
            try:
                self._callback(dec_data)
            except:
                error = sys.exc_info()[0]
                
                _log("[TCP] Could not call the handler. Meh.")
                _log("[TCP] " + str(error))
        
        self._conn.close()
        
        self._conn_threads.remove(self)
    
    def _sender_raw(self, enc_data):
        self._conn.send(enc_data)
    
    def terminate(self):
        self._conn.close()
        self._conn_threads.remove(self)
        
        self.join()

class Node:
    """
    Node server managing the different interfaces
    """
    
    def __init__(self, iface, iface_tool):
        self._iface = iface
        self._iface_tool = iface_tool
        
        self._alias_ctrl = aliasing.AliasControl(iface, iface_tool)
        
        self._udp_threads = []
        self._tcp_threads = []
    
    def register_device(self, ip, prefix_len, callback):
        _log("Aliasing ip " + ip + ".")
        
        self._alias_ctrl.add_alias(ip, prefix_len)
        
        _log("Starting a node server on " + ip + ".")
        
        udp_server = UDPServerThread(ip, 20000, callback)
        tcp_server = TCPServerThread(ip, 20000, callback)
        
        self._udp_threads.append(udp_server)
        self._tcp_threads.append(tcp_server)
        
        return functools.partial(_common_broadcast, udp_server=udp_server, tcp_server=tcp_server)
    
    def start(self):
        for tcp_thread in self._tcp_threads:
            tcp_thread.start()
        
        for udp_thread in self._udp_threads:
            udp_thread.start()
    
    def stop(self):
        for tcp_thread in self._tcp_threads:
            tcp_thread.terminate()
        
        for udp_thread in self._udp_threads:
            udp_thread.terminate()
