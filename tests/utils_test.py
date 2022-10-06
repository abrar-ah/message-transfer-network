from msg_transfer_package.example_data.example_data import DATA
from msg_transfer_package.utils import (
    encrypt_message,
    decrypt_message,
    serialize_object,
    create_headers,
    get_params,
)
import logging
import unittest
import json
import pickle
from ddt import ddt, data


logging.disable(logging.CRITICAL)


@ddt
class TestUtils(unittest.TestCase):
    @data(
        b"test1",
        b"ABCDEFGHIJKLMN",
        b"1234567890",
        b"{1:2, 3:4}",
        b"\x80\x05\x95\r\x00\x00\x00\x00\x00\x00\x00]\x94(K\x01K\x02K\x03K\x04e.",
        *[str.encode(json.dumps(obj)) for obj in DATA],
        *[pickle.dumps(obj) for obj in DATA],
    )
    def test_encryption(self, string):
        """
        Tests both encrypt_message and decrypt_message
        """

        encrpted = encrypt_message(string)
        self.assertNotEqual(encrpted, string)

        decryped = decrypt_message(encrpted)
        self.assertEqual(string, decryped)

    @data(*DATA)
    def test_serialization(self, obj):
        """
        Tests binary (pickle) and text (json) serialization
        """

        serialized = serialize_object(obj, "binary")
        self.assertIsInstance(serialized, bytes)
        self.assertNotEqual(serialized, obj)

        deserialized = pickle.loads(serialized)
        self.assertEqual(obj, deserialized)

        serialized = serialize_object(obj, "json")
        self.assertIsInstance(serialized, bytes)
        self.assertNotEqual(serialized, obj)

        deserialized = json.loads(serialized)
        self.assertEqual(obj, deserialized)

        self.assertNotEqual(
            serialize_object(obj, "json"), serialize_object(obj, "binary")
        )

    def test_create_headers(self):
        """
        Tests metadata header creation
        """

        header_size = 10
        send_type, encrypt, serialization_method, obj_length = (
            "file",
            True,
            "binary",
            23,
        )

        message = f"{send_type:<{header_size}}"
        message += f"{encrypt:<{header_size}}"
        message += f"{serialization_method:<{header_size}}"
        message += f"{obj_length:<{header_size}}"

        self.assertEqual(
            message,
            create_headers(
                header_size, send_type, encrypt, serialization_method, obj_length
            ),
        )

        message = (
            f"{send_type}      1         {serialization_method}    {obj_length}        "
        )
        self.assertEqual(
            message,
            create_headers(
                header_size, send_type, encrypt, serialization_method, obj_length
            ),
        )

    def test_get_params(self):
        """
        Tests metadata header parsing
        """

        msg = b"object    1         binary    100       "
        return_value = {
            "type": "object",
            "encrypt": True,
            "serialize": "binary",
            "length": 100,
        }

        self.assertEqual(return_value, get_params(msg, 10))

        msg = b"file      0         bin.txt    100       "
        return_value = {
            "type": "file",
            "encrypt": False,
            "filename": "bin.txt",
            "length": 100,
        }

        self.assertEqual(return_value, get_params(msg, 10))
