import socket
import sys

host = '<broadcast>'
port = 20000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind((host, port))

while 1:
    try:
        message = s.recv(8192)
        print(message)
    except KeyboardInterrupt:
        break 
