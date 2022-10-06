import logging
import unittest
import os
from unittest import mock

from msg_transfer_package.client import Client

logging.disable(logging.CRITICAL)


class TestClient(unittest.TestCase):
    client = Client("", 7000)

    def removeLogFile(self):
        """
        Removes log file
        """
        try:
            os.remove("client_log.log")
        except FileNotFoundError:
            pass

    @mock.patch("msg_transfer_package.client.Client.receive_data")
    @mock.patch("msg_transfer_package.client.Client.sendall")
    @mock.patch("msg_transfer_package.client.create_headers")
    @mock.patch("msg_transfer_package.client.encrypt_message")
    @mock.patch("msg_transfer_package.client.serialize_object")
    def test_transfer_object(
        self,
        serialize_object,
        encrypt_message,
        create_headers,
        sendall,
        receive_data,
    ):
        """
        Tests client object transfer logic
        """

        serialize_object.return_value = b"[1,2,3,4,5]"
        encrypt_message.return_value = b"encrypted message"
        create_headers.return_value = "metadata  "
        input_obj = [1, 2, 3, 4, 5]
        ser_method = "json"
        encrypt = True
        send_type = "object"

        self.client.transfer_object(ser_method, input_obj, encrypt=encrypt)
        serialize_object.assert_called_with(input_obj, ser_method)
        encrypt_message.assert_called_with(serialize_object.return_value)
        create_headers.assert_called_with(
            16, send_type, encrypt, ser_method, len(
                encrypt_message.return_value)
        )
        sendall.assert_called_with(
            bytes(create_headers.return_value, "utf-8") +
            encrypt_message.return_value
        )
        receive_data.assert_called_once()

        encrypt = False
        self.client.transfer_object(ser_method, input_obj, encrypt=encrypt)
        serialize_object.assert_called_with(input_obj, ser_method)

        encrypt_message.assert_called_once()
        create_headers.assert_called_with(
            16, send_type, encrypt, ser_method, len(
                serialize_object.return_value)
        )
        sendall.assert_called_with(
            bytes(create_headers.return_value, "utf-8") +
            serialize_object.return_value
        )
        self.assertEqual(receive_data.call_count, 2)

    @mock.patch("msg_transfer_package.client.Client.receive_data")
    @mock.patch("msg_transfer_package.client.Client.sendall")
    @mock.patch("msg_transfer_package.client.create_headers")
    @mock.patch("msg_transfer_package.client.encrypt_message")
    @mock.patch("msg_transfer_package.client.os.path.getsize")
    @mock.patch("msg_transfer_package.client.os.path.basename")
    @mock.patch("msg_transfer_package.client.open")
    @mock.patch("msg_transfer_package.client.bytes")
    def test_transfer_file(
        self,
        mock_bytes,
        mock_open,
        basename,
        getsize,
        encrypt_message,
        create_headers,
        sendall,
        receive_data,
    ):
        """
        Tests client file transfer logic
        """

        encrypt = True
        send_type = "file"
        getsize.return_value = 100
        basename.return_value = "file.txt"
        create_headers.return_value = "metadata  "
        file_reads = [b"y", b"abc", b"123", b""]
        mock_open.return_value.__enter__.return_value.read.side_effect = file_reads
        mock_bytes.return_value = b"x"
        encrypt_message.return_value = b"encrypted text"

        self.client.transfer_file("file.txt", encrypt=encrypt)

        mock_open.assert_called_with(basename.return_value, "rb")

        create_headers.assert_called_with(
            16, send_type, encrypt, basename.return_value, getsize.return_value
        )
        encrypt_message.assert_called_once_with(b"".join(file_reads))
        sendall.assert_called_once_with(
            mock_bytes.return_value + encrypt_message.return_value
        )
        receive_data.assert_called_once()

        encrypt = False
        mock_open.return_value.__enter__.return_value.read.side_effect = file_reads
        self.client.transfer_file("file.txt", encrypt=encrypt)
        sendall.assert_called_with(
            mock_bytes.return_value + b"".join(file_reads))

    @mock.patch("msg_transfer_package.client.Client.connect")
    def test__connect(self, mock_connect):
        """
        Tests addr_host and port connection
        """

        self.client.connection()
        mock_connect.assert_called_once_with(
            (self.client.host, self.client.host_port))

    def test_receive_data(self):
        pass
