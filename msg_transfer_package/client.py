"""
Network client module
"""

import configparser
import logging
import os
import socket
from .utils import encrypt_message, serialize_object, create_headers

logger = logging.getLogger(__name__)

logging.basicConfig(
    format="CLIENT: %(asctime)s %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("client_log.log"), logging.StreamHandler()],
)

BUFFER_SIZE = 8192
HEADER_SIZE = 16


class Client(socket.socket):
    """
    Client class to send data to the receiving server
    """

    def __init__(self, host: str, host_port: int, *args, **kwargs):
        """
        host: ip address or hostname of the receiving server
        host_port: The port of the receiving server
        """

        super().__init__(*args, **kwargs)
        self.host = host
        self.host_port = host_port

    def connection(self):
        """
        Make connection to the server
        """

        self.connect((self.host, self.host_port))
        logger.info("Connected to Host: {}, Port: {}".format(
            self.host, self.host_port))

    def receive_data(self):
        """
        Received the reply from server
        """

        message_header = self.recv(HEADER_SIZE)
        # print(message_header.decode())
        message_length = int(message_header.decode("utf-8").strip())
        message = self.recv(message_length)
        logger.info("Server reply: {}".format(message))

    def transfer_object(self, serialization_method: str, obj: any, encrypt=True):
        """
        Transfers a python object to the server
        serialization_method: enum (binary, json or xml).
        """

        converted_object = serialize_object(obj, serialization_method)
        if encrypt:
            converted_object = encrypt_message(converted_object)

        metadata = create_headers(
            HEADER_SIZE, "object", encrypt, serialization_method, len(
                converted_object)
        )
        # send object:
        self.sendall(bytes(metadata, "utf-8") + converted_object)
        logger.info("Serialized object sent to server")

        self.receive_data()

    def transfer_file(self, input_file_path: str, encrypt=True):
        """
        Transfers a file to the server.
        """

        # get the file name and size
        filename = os.path.basename(input_file_path)
        filesize = os.path.getsize(input_file_path)

        metadata = create_headers(
            HEADER_SIZE, "file", encrypt, filename, filesize)

        file_data = b""

        # start sending the file
        logger.info("Sending file {} to server ...".format(filename))

        with open(input_file_path, "rb") as file:
            while True:
                # read the buffer size of bytes from the file
                bytes_read = file.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transfer is complete
                    break
                file_data += bytes_read

        # Encrypt the file data bytes
        if encrypt:
            file_data = encrypt_message(file_data)

        self.sendall(bytes(metadata, "utf-8") + file_data)
        logger.info("{} transfer complete".format(filename))
        self.receive_data()


def run_with_config(config_file_path="", input_file: str = None, do_encryot: bool = False):
    """
    Starts running the client using provided config file, server hostname/ip address and server port
    """

    if not os.path.isfile(config_file_path):
        print("Invalid config file path")
        return

    config = configparser.ConfigParser()
    config.read(config_file_path)

    host = ""
    host_port = ""
    ser_method = ""
    # Parse host and IP Address from the config file

    # Parse host
    try:
        host = config.get("SERVER_OPTIONS", "host")
    except configparser.NoOptionError:
        print("Missing a valid SERVER_OPTIONS.host in config file")
        return

    # Parse port
    try:
        host_port = config.getint("SERVER_OPTIONS", "host_port")
    except configparser.NoOptionError:
        print("Missing a valid SERVER_OPTIONS.host_port in config file")
        return

    # If input file is specified
    if input_file != "":
        if not os.path.isfile(input_file):
            print("Invalid input file path")
            return
    else:
        # else use the input object from config file
        try:
            obj = eval(config["INPUT_OBJECT"]["object"])
        except Exception as e:
            print("[INPUT_OBJECT] object is not valid. Error:", e)
            return
        ser_method = config["INPUT_OBJECT"]["serialize"]

    try:
        host = config["SERVER_OPTIONS"]["host"]
        host_port = int(config["SERVER_OPTIONS"]["host_port"])
        client = Client(host, host_port)
        client.connection()
        if input_file != "":
            client.transfer_file(input_file, do_encryot)
        else:
            client.transfer_object(ser_method, obj, do_encryot)

    except OSError:
        print(f"Could not connect to {host}{host_port}")
