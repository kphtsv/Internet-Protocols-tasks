import SNTPServer

# тестирование синхронизации сервера

# TODO достучаться до ответа SNTP сервера
PRIMARY_TIME_SERVER = '0.ru.pool.ntp.org'  # приём-передача 76 мс, страта = 1
SERVER_IPADDRESS = 'localhost'

server = SNTPServer.Server(SERVER_IPADDRESS, PRIMARY_TIME_SERVER)
print('Time before syncing:\t', server.get_current_time())
server.synchronize()
print('Time after syncing:\t', server.get_current_time())
print('Clock offset:\t', server.clock_offset)

# byte_val = b'\x2a\x06'  # 10101000000110 -> 10758
# print(int.from_bytes(byte_val, "big"))
