# Серверы точного времени: https://www.ntp-servers.net/servers.html
# Серверы SNTP: https://www.makak.ru/2009/12/01/spisok-sntp-serverov-vremeni-simple-network-time-protocol-dostupnykh-v-internete/
# SNTP RFC: https://www.rfc-editor.org/rfc/rfc4330.txt
# Packet timestamp RFC: https://datatracker.ietf.org/doc/html/rfc8877#name-ntp-64-bit-timestamp-format
# struct doc: https://docs.python.org/3/library/struct.html

import struct

# TODO: настроить получение времени от сервера
import time

PRIMARY_TIME_SERVER = 'vega.cbk.poznan.pl'  # приём-передача 76 мс, страта = 1

# TODO: test!
def int_to_time(seconds: int, fraction: int):
    return seconds + float(fraction) / (2 ** 32)

def time_to_int(time: float):
    seconds = int(time)
    fraction = (time - seconds) * (2 ** 32)
    return seconds, fraction


def measure_elapsed_time(address: str):
    return 0.076  # 76 мс до сервера 'vega.cbk.poznan.pl'


class SNTPPacket:
    # # bits 0-1
    # CORRECTION = {
    #     0: 'No correction',
    #     1: 'Last minute has 61 seconds',
    #     2: 'Last minute has 59 seconds',
    #     3: 'Time not synchronized'
    # }
    #
    # MODE = {
    #     0: 'Reserved',
    #     1: 'Symmetric, active',
    #     2: 'Symmetric, passive',
    #     3: 'Client',
    #     4: 'Server',
    #     5: 'Broadcast',
    #     6: 'Reserved for NTP control messages',
    #     7: 'Reserved for private use',
    # }

    FORMAT = '!B B B b 11I'

    def __init__(self):
        self.leap_indicator = 3  # время не синхронизировано
        self.version_number = 4
        self.mode = 0
        self.stratum = 0
        self.poll = 0
        self.precision = 0
        self.root_delay = 0
        self.root_dispersion = 0
        self.reference_id = ''
        self.reference_timestamp = 0.0
        self.originate_timestamp = 0.0
        self.receive_timestamp = 0.0
        self.transmit_timestamp =  0.0
        # опционально, в пакет класть не будем
        self.key_id = None
        self.message_digest = None


    def generate_request(self):  # клиентский метод
        print('generate request')
        self.mode = 3  # client
        self.originate_timestamp =  # Время отправки запроса клиентом, несинхрониз.
                    # time.time не совсем корректно? в этом файле генерируются и запросы, и ответы
        self.receive_timestamp =  # Время приёма запроса сервером/ответа клиентом
        self.transmit_timestamp =  # время, в кот. запрос покинул клиента, или ответ покинул сервер


    def generate_response(self, reference_id): # метод сервера
        print('generate response')
        self.mode = 4  # server
        self.stratum = 2
        self.poll = 4
        self.precision = -6 # двоичная экспонента которого показывает точность системных часов
        self.root_delay = measure_elapsed_time(reference_id) # 76 мс до сервера
        self.root_dispersion = 0    # максимальная ошибка из-за нестабильности часов
                                    # TODO: измерить настоящее значение!
        self.reference_id = reference_id  # IP-адрес для вторичных серверов
        # self.reference_timestamp = # update_syncing()
        # self.originate_timestamp =  # Время отправки запроса клиентом, несинхрониз.
        self.receive_timestamp =  # Время приёма запроса сервером/ответа клиентом
        self.transmit_timestamp =  # время, в кот. запрос покинул клиента, или ответ покинул сервер


    def from_data(self, data):
        try:
            unpacked = struct.unpack(SNTPPacket.FORMAT, data[0:struct.calcsize(SNTPPacket.FORMAT)])
        except struct.error:
            raise Exception("Invalid SNTP packet.")

        self.leap_indicator = unpacked[0] >> 6  # строка 1
        self.version_number = unpacked[0] >> 3 & 0x7
        self.mode = unpacked[0] & 0x7
        self.stratum = unpacked[1]
        self.poll = unpacked[2]
        self.precision = unpacked[3]
        self.root_delay = float(unpacked[4]) / (2 ** 16)  # строка 2, знаковое
        self.root_dispersion = float(unpacked[5]) / (2 ** 16) # с   трока 3, БЕЗЗНАКОВОЕ
        self.reference_id = unpacked[6]  # IP-адрес для вторичных серверов, 4 байта подряд
        self.reference_timestamp = int_to_time(unpacked[7], unpacked[8]) # TODO: когда системные часы последний раз были установлены или скорректированны
        self.originate_timestamp = int_to_time(unpacked[9], unpacked[10])# Время отправки запроса клиентом, несинхрониз.
        self.receive_timestamp = int_to_time(unpacked[11], unpacked[12]) # Время приёма запроса сервером
        self.transmit_timestamp = int_to_time(unpacked[13], unpacked[14]) # время, в кот. запрос покинул клиента, или ответ покинул сервер

    def to_data(self):
        li_vn_mode = (self.leap_indicator << 6 | self.version_number << 3 | self.mode)
        root_delay = self.root_delay * (2 ** 16)
        root_dispersion = self.root_dispersion * (2 ** 16)
        reference_timestamp_sec, reference_timestamp_frac = time_to_int(self.reference_timestamp)
        originate_timestamp_sec, originate_timestamp_frac = time_to_int(self.originate_timestamp)
        receive_timestamp_sec, receive_timestamp_frac = time_to_int(self.receive_timestamp)
        transmit_timestamp_sec, transmit_timestamp_frac = time_to_int(self.transmit_timestamp)

        try:
            packed = struct.pack(SNTPPacket.FORMAT,
                                 li_vn_mode,
                                 self.stratum,
                                 self.poll,
                                 self.precision,
                                 root_delay,
                                 root_dispersion,
                                 reference_timestamp_sec, reference_timestamp_frac,
                                 originate_timestamp_sec, originate_timestamp_frac,
                                 receive_timestamp_sec, receive_timestamp_frac,
                                 transmit_timestamp_sec, transmit_timestamp_frac)
        except struct.error:
            raise Exception('Invalid SNTP packet fields')
        return packed


    def update_syncing(self, primary_time_server):
        print() # mode 3 -> 0
        self.mode = 0
        # self.precision = measure_elapsed_time(primary_time_server)
        self.precision = 0.076
        self.reference_timestamp = time.time()  # TODO а точно?
                                                # когда системные часы последний раз были уст. или скорректированы


