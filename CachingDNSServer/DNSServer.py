import socket
import json


def get_full_address_from_config():
    with open('config.json', 'r') as config_file:
        data = json.load(config_file)
        return data


class Server:
    def __init__(self, self_ipaddress: str, self_port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self_ipaddress, self_port))

    def receive_request(self):
        data, full_client_address = self.socket.recvfrom(1024)
        return data, full_client_address
