import SNTPClient
from server_v2 import SERVER_IPADDRESS
from SNTPServer import SERVER_PORT

client = SNTPClient.Client()
client.synchronize((SERVER_IPADDRESS, SERVER_PORT))

print('current time:', client.get_current_time())
print('clock offset:', client.clock_offset)

client.shutdown()
