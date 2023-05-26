import datetime
import time
import SNTPServer
import json


# PRIMARY_TIME_SERVER = '0.ru.pool.ntp.org'
PRIMARY_TIME_SERVER = '195.218.227.166'
SERVER_IPADDRESS = '127.0.0.1'
PORT = 123
CONFIG_FILENAME = 'conf.json'


def timestamp_to_date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def get_delay():
    with open(CONFIG_FILENAME, 'r') as c_file:
        d = json.load(c_file)
        return d['delay']


server = SNTPServer.Server(SERVER_IPADDRESS, PORT, PRIMARY_TIME_SERVER, delay=get_delay())  # delay = 5 min

act_time = time.time()
print('Actual time:\t\t\t', act_time, timestamp_to_date(act_time))

before_sync = server.get_current_time()
print('Server time before syncing:\t', before_sync, timestamp_to_date(before_sync))
server.synchronize()

print('Clock offset:\t\t\t', server.clock_offset)
after_sync = server.get_current_time()
print('Server time after syncing:\t', after_sync, timestamp_to_date(after_sync))

server.process_request()
