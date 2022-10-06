from msg_transfer_package.server import Server
import logging
import unittest
from unittest import mock
import os


logging.disable(logging.CRITICAL)


class TestServer(unittest.TestCase):
    server = Server("", 7000)

    def removeLogFile(self):
        """
        Removes log file
        """

        try:
            os.remove("server_log.log")
        except FileNotFoundError:
            pass

    def test_recvall(self):
        pass

    @mock.patch("msg_transfer_package.server.xmltodict.parse")
    @mock.patch("msg_transfer_package.server.pickle.loads")
    @mock.patch("msg_transfer_package.server.json.loads")
    @mock.patch("msg_transfer_package.server.decrypt_message")
    def test_receive_object(self, mock_decrypt, mock_json, mock_pickle, mock_xml):
        """
        Test Receive Object function
        """

        mock_decrypt.return_value = "decrypted message"
        mock_json.return_value = "parsed json message"
        mock_pickle.return_value = "parsed pickled message"
        mock_xml.return_value = "parsed xml message"

        metadata = {}
        metadata["encrypt"] = True
        output_option = "file"
        metadata["serialize"] = "json"

        ret = self.server.receive_object("", metadata, output_option)
        mock_json.assert_called_with(mock_decrypt.return_value)
        self.assertEqual(mock_json.return_value, ret)

        metadata["encrypt"] = True
        metadata["serialize"] = "xml"

        ret = self.server.receive_object("", metadata, output_option)
        mock_xml.assert_called_with(mock_decrypt.return_value)
        self.assertEqual(mock_xml.return_value, ret)

        metadata["encrypt"] = False
        metadata["serialize"] = "binary"

        ret = self.server.receive_object("", metadata, output_option)
        mock_pickle.assert_called_with("")
        self.assertEqual(mock_pickle.return_value, ret)

    @mock.patch("msg_transfer_package.server.open")
    @mock.patch("msg_transfer_package.server.decrypt_message")
    def test_receive_file(self, mock_decrypt, mock_open):
        """
        Tests file receiving logic
        """

        mock_decrypt.return_value = "decrypted message"
        metadata = {"filename": "name.ext"}
        input_data = "path"

        # Test encrypted data
        metadata["encrypt"] = True
        output_option = "file"
        self.server.receive_file(input_data, metadata, output_option)
        mock_decrypt.assert_called_with(input_data)
        mock_open.return_value.__enter__.return_value.write.assert_called_with(
            mock_decrypt.return_value
        )

        # Test not encrypted data
        metadata["encrypt"] = False
        self.server.receive_file(input_data, metadata, output_option)
        mock_open.return_value.__enter__.return_value.write.assert_called_with(
            input_data
        )

    def test_receive_data(self):
        pass
