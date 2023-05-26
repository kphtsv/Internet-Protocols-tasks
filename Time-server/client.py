from datetime import datetime
import SNTPClient

SERVER_IPADDRESS = '127.0.0.1'
PORT = 123

client = SNTPClient.Client()
print('Before sync time:', datetime.fromtimestamp(client.get_current_time()))

client.synchronize((SERVER_IPADDRESS, PORT))
print('Clock offset:', client.clock_offset)
print('After sync time:', datetime.fromtimestamp(client.get_current_time()))

client.shutdown()
