Tested with:
Python 3.5.2 (v3.5.2:4def2a2901a5, Jun 25 2016, 22:27:18) [MSC v.1900 32 bit (Intel)] on win32

allocator.py:
	binds to a port 7070 on localhost
	modify port in case it is occupied

test.py:
	conncects to server on same port as scpecified in server


Assumption:
Assumed that unique Stream ID needs to be explicitly printed in the output to differentiate two orders
with same Header from two different streams.

Additionally printed some metadata as each order is processed.