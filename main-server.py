"""
Starts the server part of network
"""
import configparser
import os
from msg_transfer_package.server import Server


config_file_path = os.path.dirname(__file__) + "/config_server.cfg"

if not os.path.isfile(config_file_path):
    print("Invalid config file path")
    exit(1)

config = configparser.ConfigParser()
config.read(config_file_path)


SERVER_ADDR_HOST = "0.0.0.0"
SERVER_ADDR_PORT = 7000

try:
    SERVER_ADDR_HOST = config.get("SERVER_OPTIONS", "ip_addr")
except configparser.NoOptionError:
    print("Missing a valid SERVER_OPTIONS.ip_addr in config file")
    exit(1)

try:
    SERVER_ADDR_PORT = config.getint("SERVER_OPTIONS", "port")
except configparser.NoOptionError:
    print("Missing a valid SERVER_OPTIONS.port in config file")
    exit(1)

try:
    OUTPUT_OPTION = config.get("SERVER_OPTIONS", "output_option")
except configparser.NoOptionError:
    print("Missing a valid SERVER_OPTIONS.output_option in config file")
    exit(1)
if OUTPUT_OPTION != "print" and OUTPUT_OPTION != "file":
    print('invalid parameter "output_option", allowed values are: print, file')
    exit(1)

s = Server(SERVER_ADDR_HOST, SERVER_ADDR_PORT, OUTPUT_OPTION)
s.run_server()
