import SNTPServer

PRIMARY_TIME_SERVER = 'vega.cbk.poznan.pl'  # приём-передача 76 мс, страта = 1
SERVER_IPADDRESS = 'localhost'
# SERVER_PORT = 123

server = SNTPServer.Server(SERVER_IPADDRESS, PRIMARY_TIME_SERVER)
server.process_request()