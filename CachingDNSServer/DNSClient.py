import socket


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(10)

    def send(self, data: bytes, full_server_addr: tuple):
        self.socket.sendto(data, full_server_addr)

    def close(self):
        self.socket.close()

    def send_request(self, full_server_addr: tuple):
        pass
