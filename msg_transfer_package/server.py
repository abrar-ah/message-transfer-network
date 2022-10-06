"""
Network server module
"""

import socket
import sys
import json
import pickle
import logging
import xmltodict
from .utils import decrypt_message, get_params


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="SERVER: %(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("server_log.log"), logging.StreamHandler()],
)
HEADER_SIZE = 16


class Server(socket.socket):
    """
    Server class to receive requests and data from client
    """

    def __init__(self, host_addr: str, addr_port: int, output_option="file", *args, **kwargs):
        """
        host: ip address or hostname of the receiving server
        port: The port of the receiving server
        output_option: Output to terminal or save to file, allowed values: (file, print)
        """

        super().__init__(*args, **kwargs)
        self.host_addr = host_addr
        self.addr_port = addr_port
        self.output_option = output_option

    def run_server(self):
        """
        Bind and listen for new client connections
        """

        self.bind((self.host_addr, self.addr_port))

        # number of unaccepted incoming connections before refusing new connections
        self.listen(5)
        logger.info(
            "[*] Listening at {}:{}".format(self.host_addr, self.addr_port))

        while True:
            try:
                client_socket, address = self.accept()
            except KeyboardInterrupt:
                logger.info("Server {}:{} shutdown.".format(
                    self.host_addr, self.addr_port))
                sys.exit()
            logger.info("[+] {} is connected.".format(address))
            # receive using client socket, not server socket
            self.receive_data(client_socket, address)

    @staticmethod
    def receive_object(received: bytes, metadata: dict, output_option: str):
        """
        Receive the bytes and deserializes according to the received metadata
        """

        if metadata["encrypt"]:
            received = decrypt_message(received)

        if metadata["serialize"].lower() == "binary":
            received_parse = pickle.loads(received)
        elif metadata["serialize"].lower() == "xml":
            received_parse = xmltodict.parse(received)
            if "msg" in received_parse:
                received_parse = received_parse["msg"]
        elif metadata["serialize"].lower() == "json":
            received_parse = json.loads(received)
        else:
            logger.warning("Incorrect serialization method provided")
            raise ValueError("Incorrect serialization method provided")

        if output_option == "print":
            logger.info("Received object: serialization: {}, encrypted: {}, type={}".format(
                metadata["serialize"].lower(), metadata["encrypt"], type(received_parse)))
        else:
            # The default file name if an object is sent
            filename = "received_file.txt"
            # Saves the recevied data to file
            with open(filename, "wb") as file:
                file.write(json.dumps(received_parse))
            logger.info("Received object saved to file: {}, serialization: {}, encrypted: {}, type={}".format(
                filename,  metadata["serialize"].lower(), metadata["encrypt"], type(received_parse)))

        return received_parse

    @staticmethod
    def receive_file(received: bytes, metadata: dict, output_option: str):
        """
        Receive the file bytes and deserializes according to the received metadata
        """
        logger.info("Received File, encrypted: {}".format(metadata["encrypt"]))

        if metadata["encrypt"]:
            received = decrypt_message(received)
        if output_option == "print":
            logger.info("Recevied data:\n{}".format(received))
        else:
            # The default file name if an object is sent
            filename = "received_"+metadata["filename"]
            # Saves the recevied data to file
            with open(filename, "wb") as file:
                file.write(received)
            logger.info("Recevied data saved to file: {}".format(filename))

        return received

    def receive_data(self, sock: socket.socket, address: str):
        """
        While loop for receiving and processing the requests and sending responses
        """

        while True:
            full_msg = b""
            new_msg = True
            close_connection = False
            while True:
                try:
                    msg = sock.recv(8192)
                    if not msg:
                        close_connection = True
                        logger.info("Client {} disconnected.".format(address))
                        break
                except ConnectionResetError:
                    close_connection = True
                    logger.info("Client {} disconnected.".format(address))
                    break
                if new_msg:
                    try:
                        msg_params = get_params(msg, HEADER_SIZE)
                    except ValueError as val:
                        logger.info(val)
                        continue
                    new_msg = False

                full_msg += msg

                if len(full_msg) - 4 * HEADER_SIZE == msg_params["length"]:
                    logger.info("Received message from {}".format(address))
                    if not msg_params:
                        continue
                    msg = full_msg[4 * HEADER_SIZE:]

                    # logger.info("Metadata: {}".format(msg_params))

                    if msg_params["type"] == "file":
                        full_msg = self.receive_file(
                            msg, msg_params, self.output_option)
                        send_msg = b"Received File successfully"
                    elif msg_params["type"] == "object":
                        try:
                            full_msg = self.receive_object(
                                msg, msg_params, self.output_option)
                            send_msg = b"Received Object successfully"
                        except ValueError:
                            continue

                    # Sends reply back to client
                    sock.sendall(
                        bytes(f"{len(send_msg):<{HEADER_SIZE}}",
                              "utf-8") + send_msg
                    )
                    full_msg = b""
                    new_msg = True
            if close_connection:
                break
