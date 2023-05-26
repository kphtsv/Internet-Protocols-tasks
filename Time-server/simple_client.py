import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(10)
address = ('127.0.0.1', 123)

print('Asking server for time.')
s.sendto(b'', address)

data, server = s.recvfrom(1024)
data = time.gmtime(float(data))
print('Received:', data)

s.close()
