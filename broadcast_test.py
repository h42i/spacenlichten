"""
Usage: python bulb_test.py [bulb] [true/false]
"""

import socket
import sys

ip = '10.23.42.20' + sys.argv[1]
port = 20000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((ip, port))
print(s.recv(1024))

s.close()
