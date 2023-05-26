from DNSClient import Client
import DNSServer

config = DNSServer.get_full_address_from_config()
SERVER_IPADDRESS = config["server_ip"]
SERVER_PORT = config["server_port"]

client = Client()
data = b'Hello!'
print(f'Sending: {data.decode()}')
client.send(data, (SERVER_IPADDRESS, SERVER_PORT))

