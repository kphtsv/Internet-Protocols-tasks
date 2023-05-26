import base64
import socket
import ssl
import json


def request(socket, request):
    socket.send((request + '\n').encode())
    recv_data = socket.recv(65535).decode('cp1251')  # надо в цикле
    return recv_data


def prepare_message(data_dict):
    msg = data_dict['method'] + ' ' + data_dict['url'] + ' HTTP/' + data_dict['version'] + '\n'
    for header, value in data_dict['headers'].items():
        msg += f'{header}: {value}\n'
    msg += '\n'

    if data_dict['body'] is not None:
        msg += data_dict['body']

    return msg


HOST_ADDR = 'somkural.ru'
PORT = 80

with socket.create_connection((HOST_ADDR, PORT)) as client:
    # В HTTP/1.1 первым говорит клиент
    message = prepare_message({
        'method': 'GET',
        'url': '/',
        'version': '1.1',
        'headers': {
            'Host': HOST_ADDR
        },
        'body': None
    })
    print(request(client, message))

pass

# TODO
# Обработка ошибок Сети
# request переписать в цикле