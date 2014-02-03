import sys
import threading
import socket
import time

import ipaddress

from spacenlichten import aliasing
from spacenlichten import api

class NodeError(Exception):
    pass

class NodeServerThroad(threading.Thread):
    def __init__(self, ip, port, callback):
        threading.Thread.__init__(self)
        
        self._ip = ip
        self._port = port
        self._ip_version = ipaddress.ip_address(ip).version
        
        self._callback = callback
        
        self._sock = None
        self._buffer_size = 2**16
        
        self._stopped = False
        
        try:
            if self._ip_version == 4:
                addr_info = socket.getaddrinfo(self._ip, self._port, 0, 0, socket.SOL_TCP, socket.AF_INET)
                
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.bind(addr_info[0][4])
            elif self_.ip_version == 6:
                # UNTESTED
                if not socket.has_ipv6:
                    print("spacenlichten> No IPv6 in here, dude. Go play with v4 again.")
                
                addr_info = socket.getaddrinfo(self._ip, self._port, 0, 0, socket.SOL_TCP, socket.AF_INET6)
                
                self._sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                self._sock.bind(addr_info[0][4])
            else:
                raise Exception("Is this even IP?!")
            
            self._sock.listen(3)
        except socket.error:
            print("spacenlichten> No socket for you. Sockets are out. (" + str(socket.error) + ")")
            
            self._stopped = True
        except:
            print("spacenlichten> Something really went wrong.")
            
            self._stopped = True
    
    def run(self):
        while not self._stopped:
            try:
                print("spacenlichten> Accepting clients...")
                
                conn, addr = self._sock.accept()
                
                print("spacenlichten> Connection from " + addr[0] + " to " + self._ip + "...")
                
                # buffer size necessary to handle for example large pixel matrices
                data = conn.recv(_buffer_size)
                dec_data = None
                
                feedback = None
                enc_feedback = None
                
                try:
                    dec_data = data.decode("utf-8")
                    
                    # strip http header if present
                    first_line_match = re.search("/^(.*)$/m", ec_data)
                    
                    if first_line_match:
                        first_line = first_line_match.group(0)
                        
                        http_match = re.search("HTTP", first_line)
                        http_strip_match = re.search("\r?\n(\r?\n)+", dec_data, re.MULTILINE)
                        
                        if http_strip_match:
                            dec_data = dec_data[match.end():]
                    
                except:
                    error = sys.exc_info()[0]
                    
                    print("spacenlichten> Invalid data. I will not bother the handler with this mess.")
                    print("spacenlichten>>> " + str(error))
                
                try:
                    if dec_data != None:
                        feedback = self._callback(dec_data)
                    
                    if feedback != None:
                        enc_feedback = feedback.encode("utf-8")
                except:
                    error = sys.exc_info()[0]
                    
                    print("spacenlichten> It seems the handler is not even able to construct correct feedback.")
                    print("spacenlichten>>> " + str(error))
                
                try:
                    if enc_feedback != None:
                        conn.send(enc_feedback)
                except:
                    error = sys.exc_info()[0]
                    
                    print("spacenlichten> Okay, okay. PANIC! I wasn't able to answer the client.")
                    print("spacenlichten>>> " + str(error))
                
                conn.close()
            except socket.error:
                # uhm. well...
                error= sys.exc_info()[0]
                
                print("spacenlichten>>> " + str(error))
        
        if self._sock != None:
            self._sock.close()
    
    def terminate(self):
        self._stopped = True
        self.join()

class Node:
    """Node server managing the different interfaces"""
    
    def __init__(self, iface, iface_tool):
        self._iface = iface
        self._iface_tool = iface_tool
        
        self._alias_ctrl = aliasing.AliasControl(iface, iface_tool)
        
        self._node_threads = []
    
    def register_device(self, ip, prefix_len, callback):
        print("spacenlichten> Aliasing ip " + ip + ".")
        
        self._alias_ctrl.add_alias(ip, prefix_len)
        
        print("spacenlichten> Starting a node server on " + ip + ".")
        
        dev_server = NodeServerThroad(ip, 20000, callback)
        
        self._node_threads.append(dev_server)
    
    def start(self):
        for node_thread in self._node_threads:
            node_thread.start()
    
    def stop(self):
        for node_thread in self._node_threads:
            node_thread.terminate()
