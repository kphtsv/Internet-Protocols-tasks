import socket
import time
import json
from SNTPServer import SERVER_PORT


CONFIG_FILENAME = 'conf.json'
PRIMARY_TIME_SERVER = 'vega.cbk.poznan.pl'  # приём-передача 76 мс, страта = 1


def write_delay(delay_time: float):
    '''
    Записывает время, на которое "врёт" сервер, в конфигурационный файл.
    :param delay_time: float - время задержки
    :return: None
    '''
    with open(CONFIG_FILENAME, 'w') as c_file:
        json.dump({'delay': delay_time}, c_file)


def get_delay():
    '''
    Возвращает время задержки из конфигурационного файла
    :return: float - время задержки
    '''
    with open(CONFIG_FILENAME, 'r') as c_file:
        d = json.load(c_file)
        return d['delay']


delay = get_delay()  # in seconds

print('Port:', SERVER_PORT)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', SERVER_PORT))

_, address = s.recvfrom(1024)

print('Query received. Sending.')
time_encoded = bytes(str(time.time() + delay), 'utf-8')
s.sendto(time_encoded, address)

# conn.close()