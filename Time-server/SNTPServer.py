import socket
import time
import SNTPPacket
import SNTPClient

NTP_PORT = 123
TIME1970 = 2208988800


class Server:
    def __init__(self, self_ipaddress: str, port: int,  primary_time_server: str, delay=0):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self_ipaddress, port))
        self.client = SNTPClient.Client()  # клиент для отправки запроса в главный сервер
        self.client.socket.settimeout(5)

        self.reference_id = primary_time_server
        self.leap_indicator = 3
        self.precision = 0
        self.reference_timestamp = None

        self.clock_offset = 0
        self.delay = delay

    def get_current_time(self):
        return time.time() + self.clock_offset + self.delay

    def synchronize(self):
        self.client.send_request((self.reference_id, NTP_PORT))
        clock_offset = SNTPClient.calculate_clock_offset(*self.client.receive_response())

        self.clock_offset += clock_offset - TIME1970
        self.reference_timestamp = self.get_current_time()
        self.leap_indicator = 0

    def generate_response(self, request_packet: SNTPPacket, receive_timestamp: float):  # метод сервера
        response = SNTPPacket.Packet()

        response.version_number = request_packet.version_number
        response.mode = 4  # server
        response.stratum = 2
        response.poll = request_packet.poll
        response.precision = -6  # двоичная экспонента которого показывает точность системных часов TODO
        response.root_delay = SNTPPacket.measure_elapsed_time(self.reference_id)  # 76 мс до сервера TODO
        response.root_dispersion = 0  # максимальная ошибка из-за нестабильности часов TODO измерить настоящее значение!
        response.reference_id = self.reference_id  # IP-адрес для вторичных серверов, TODO в байты?

        response.reference_timestamp = self.reference_timestamp
        response.originate_timestamp = request_packet.transmit_timestamp
        response.receive_timestamp = receive_timestamp  # Время приёма запроса сервером

        return response

    def process_request(self):
        data, full_client_address = self.socket.recvfrom(1024)
        receive_timestamp = self.get_current_time()
        request = SNTPPacket.Packet(data)

        if request.mode != 3:  # такого быть в моём коде не может, но по идее эта проверка должна быть
            return

        response = self.generate_response(request, receive_timestamp)
        response.transmit_timestamp = self.get_current_time()  # время, в которое ответ покинул сервер

        self.socket.sendto(response.to_data(), full_client_address)
