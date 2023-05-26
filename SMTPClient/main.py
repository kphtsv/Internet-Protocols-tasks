import base64
import socket
import ssl
import json


def request(socket, request):
    socket.send((request + '\n').encode())
    recv_data = socket.recv(65535).decode()  # надо в цикле
    return recv_data


def message_prepare():
    with open('msg.txt') as msg_file:
        headers = f'from: {username_from}\n'
        headers += f'to: {username_to}\n'  # пока получатель один
        headers += f'subject: {subject}\n'  # пока короткая тема, на латинице
        headers += 'MIME-version: 1.0\n'
        boundary = 'bound.14238'
        headers += 'Content-Type: multipart/mixed;' \
                   f'    boundary="{boundary}"\n'

        msg_body = f'--{boundary}\n'
        msg_body += f'Content-type: text/plain; charset=utf-8\n\n'
        msg_text_content = msg_file.read()  # тело началось
        msg_body += msg_text_content + '\n'

        msg_body += f'--{boundary}\n'
        msg_body += 'Content-Disposition: attachment;' \
                    'filename="small_image.png"'
        msg_body += 'Content-Transfer-Encoding: base64'
        msg_body += 'Content-Type: image/png;\n\n'

        with open('test.jpg', 'rb') as picture_file:
            picture = base64.b64encode(picture_file.read()).decode('utf-8')
        msg_body += picture + '\n'
        msg_body += f'--{boundary}--'

        message = headers + '\n' + msg_body + '\n.\n'
        print(message)
        # print(request(client, message))

        return message


with open('config.json', 'r') as json_config:
    config = json.load(json_config)
    username_from = config['from']  # ваш логин на яндекс почте
    username_to = config['to']
    subject = config['subject']

host_addr = 'smtp.yandex.ru'
port = 465

with open("pswd.txt", "r", encoding="UTF-8") as config:  # пароль почтового приложения из настроек!
    password = config.read().strip()  # считываем пароль из файла

ssl_contex = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_contex.check_hostname = False
ssl_contex.verify_mode = ssl.CERT_NONE

with socket.create_connection((host_addr, port)) as sock:
    with ssl_contex.wrap_socket(sock, server_hostname=host_addr) as client:
        print(client.recv(1024))  # в smpt сервер первый говорит
        print(request(client, f'ehlo {username_from}'))
        base64login = base64.b64encode(username_from.encode()).decode()

        base64password = base64.b64encode(password.encode()).decode()
        print(request(client, 'AUTH LOGIN'))
        print(request(client, base64login))
        print(request(client, base64password))
        print(request(client, f'MAIL FROM:{username_from}'))
        print(request(client, f"RCPT TO:{username_to}"))
        print(request(client, 'DATA'))
        # with open('msg.txt') as config:
        #     msg = config.read() + '\n.\n'
        #     print(msg)
        #     print(request(client, msg))
        print(request(client, message_prepare()))
        # print(request(client, 'QUIT'))
pass

# TODO
# Обработка ошибок Сети
# MIME формат письма: присоединить картинки
# Заголовки письма: Subject, From и т. д.
# сделать конфиг: от кого, список адресов, имя папки с файлами для отправки
# N8 тема на руском языке, тема может быть длинная -> разбивается на несколько строк
# MIME-типы и подтипы можно определять по расширениям файла (взять готовый словарь)
