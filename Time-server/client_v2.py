import SNTPClient
import SNTPServer

SERVER_PORT = 123
PRIMARY_TIME_SERVER = 'vega.cbk.poznan.pl'  # приём-передача 76 мс, страта = 1
SERVER_ADDRESS = 'localhost'

client = SNTPClient.Client()
server = SNTPServer.Server(SERVER_ADDRESS, PRIMARY_TIME_SERVER)


