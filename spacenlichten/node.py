import threading
import socket
import time

import ipaddress

from spacenlichten import aliasing
from spacenlichten import api

#socket.setdefaulttimeout(6)

class NodeServerThroad(threading.Thread):
    def __init__(self, ip, port, callback):
        threading.Thread.__init__(self)
        
        self.__ip = ip
        self.__port = port
        self.__ip_version = ipaddress.ip_address(ip).version
        
        self.__callback = callback
        
        self.__sock = None
        self.__stopped = False
        
        try:
            if self.__ip_version == 4:
                addr_info = socket.getaddrinfo(self.__ip, self.__port, 0, 0, socket.SOL_TCP, socket.AF_INET)
                
                self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__sock.bind(addr_info[0][4])
            elif self__.ip_version == 6:
                # UNTESTED
                if not socket.has_ipv6:
                    print("spacenlichten> No IPv6 in here, dude. Go play with v4 again.")
                
                addr_info = socket.getaddrinfo(self.__ip, self.__port, 0, 0, socket.SOL_TCP, socket.AF_INET6)
                
                self.__sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                self.__sock.bind(addr_info[0][4])
            else:
                raise Exception("Is this even IP?!")
            
            self.__sock.listen(3)
        except socket.error:
            print("spacenlichten> No socket for you. Sockets are out. (" + str(socket.error) + ")")
            
            self.__stopped = True
        except:
            print("spacenlichten> Something really went wrong.")
            
            self.__stopped = True
    
    def run(self):
        while not self.__stopped:
            try:
                print("spacenlichten> Accepting clients...")
                
                conn, addr = self.__sock.accept()
                
                print("spacenlichten> Connection from " + addr[0] + " to " + self.__ip + "...")
                
                # buffer size necessary to handle for example large pixel matrices
                data = conn.recv(2**32)
                dec_data = None
                
                feedback = None
                enc_feedback = None
                
                try:
                    dec_data = api.decode(str(data, "utf-8"))
                except:
                    print("spacenlichten> Invalid JSON. I will not bother the handler with this mess.")
                
                try:
                    if dec_data != None:
                        feedback = self.__callback(dec_data)
                        
                    if feedback != None:
                        enc_feedback = bytes(api.encode(feedback), "utf-8")
                except:
                    print("spacenlichten> It seems the handler not even able to construct correct feedback.")
                
                try:
                    if enc_feedback != None:
                        conn.send(bytes(enc_feedback))
                except:
                    print("spacenlichten> Okay, okay. PANIC! I wasn't able to answer the client.")
                
                conn.close()
            except:
                pass
        
        if self.__sock != None:
            self.__sock.close()
    
    def terminate(self):
        self.__stopped = True
        self.join()

class Node:
    """Node server managing the different interfaces"""
    
    def __init__(self, iface, iface_tool):
        self.__iface = iface
        self.__iface_tool = iface_tool
        
        self.__alias_ctrl = aliasing.AliasControl(iface, iface_tool)
        
        self.__node_threads = []
    
    def register_device(self, ip, prefix_len, callback):
        print("spacenlichten> Aliasing ip " + ip + ".")
        
        self.__alias_ctrl.add_alias(ip, prefix_len)
        
        print("spacenlichten> Starting a node server on " + ip + ".")
        
        dev_server = NodeServerThroad(ip, 20000, callback)
        
        self.__node_threads.append(dev_server)
    
    def start(self):
        for node_thread in self.__node_threads:
            node_thread.start()
    
    def stop(self):
        for node_thread in self.__node_threads:
            node_thread.terminate()
