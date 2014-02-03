"""
Usage: python bulb_test.py [bulb] [true/false]
"""

import socket
import sys

ip = '10.23.42.20' + sys.argv[1]
port = 20000
message = 'HTTP 200 OK\nfavfvlfvnl\nvflaval\nvfnlnvfa\n\r\n{"on":' + sys.argv[2] + '}'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((ip, port))
s.send(bytes(message, 'utf-8'))

s.close()
