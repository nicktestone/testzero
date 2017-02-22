from socket import socket, AF_INET, SOCK_STREAM
import json
import random

#make data stream
s = socket(AF_INET, SOCK_STREAM)
s.connect(('localhost', 7050))

# Sample test data
a='{"Header":1, "Lines": {"A" : 1, "C" : 1} }'
s.send(a.encode('utf-8'))
print(s.recv(1024).decode('utf-8'))
a='{"Header":2, "Lines": {"E" : 5} }'
s.send(a.encode('utf-8'))
print(s.recv(1024).decode('utf-8'))
a='{"Header":3, "Lines": {"D" : 4} }'
s.send(a.encode('utf-8'))
print(s.recv(1024).decode('utf-8'))
a='{"Header":4, "Lines": {"A" : 1, "C" : 1} }'
s.send(a.encode('utf-8'))
print(s.recv(1024).decode('utf-8'))
a='{"Header":5, "Lines": {"B" : 3} }'
s.send(a.encode('utf-8'))
print(s.recv(1024).decode('utf-8'))
a='{"Header":6, "Lines": {"D" : 4} }'
s.send(a.encode('utf-8'))
print(s.recv(1024).decode('utf-8'))

print("DONE...")
