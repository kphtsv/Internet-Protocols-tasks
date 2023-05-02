import base64
import socket
import ssl


def request(socket, request):
    socket.send((request + '\n').encode())
    recv_data = socket.recv(65535).decode()  # надо в цикле
    return recv_data


host_addr = 'smtp.yandex.ru'
port = 465
user_name = 'coolershades@yandex.ru'  # ваш логин на яндекс почте
with open("pswd.txt", "r", encoding="UTF-8") as file:
    password = file.read().strip()  # считываем пароль из файла

ssl_contex = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_contex.check_hostname = False
ssl_contex.verify_mode = ssl.CERT_NONE

with socket.create_connection((host_addr, port)) as sock:
    with ssl_contex.wrap_socket(sock, server_hostname=host_addr) as client:
        print(client.recv(1024))  # в smpt сервер первый говорит
        print(request(client, f'ehlo {user_name}'))
        base64login = base64.b64encode(user_name.encode()).decode()

        base64password = base64.b64encode(password.encode()).decode()
        print(request(client, 'AUTH LOGIN'))
        print(request(client, base64login))
        print(request(client, base64password))
        print(request(client, f'MAIL FROM:{user_name}'))
        print(request(client, f"RCPT TO:{user_name}"))
        print(request(client, 'DATA'))
        with open('msg.txt') as file:
            msg = file.read() + '\n.\n'
            print(msg)
            print(request(client, msg))

##TODO
##Обработка ошибок Сети
##MIME формат письма: присоединить картинки
##Заголовки письма: Subject, From и т. д.
