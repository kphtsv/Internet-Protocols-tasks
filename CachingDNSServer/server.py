import DNSServer

config = DNSServer.get_full_address_from_config()
SERVER_IPADDRESS = config["server_ip"]
SERVER_PORT = config["server_port"]

server = DNSServer.Server(SERVER_IPADDRESS, SERVER_PORT)
data, full_address = server.receive()
print(data.decode('utf-8'))
