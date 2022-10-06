"""
Helper functions which provide support to the core functionality
"""

import hashlib
import logging
import pickle
import json
from Crypto.Cipher import AES
import xmltodict


# The secret key is sha256 hashed and converted to bytes
KEY = hashlib.sha256(
    "my-secret-key-78944b2001d847aea48e246688e9bf88".encode()).digest()
IV = "8e357d48b52f448f"  # IV for encrypting the message


def encrypt_message(message: bytes):
    """
    Encrypts message using AES CFB mode and returns the encrypted bytes
    """
    obj = AES.new(KEY, AES.MODE_CFB, IV.encode())
    ciphertext = obj.encrypt(message)
    return ciphertext


def decrypt_message(ciphertext: bytes) -> bytes:
    # Decrypts the message using the same private key and IV

    obj2 = AES.new(KEY, AES.MODE_CFB, IV.encode())
    message = obj2.decrypt(ciphertext)
    return message


def serialize_object(obj: any, serialization_method: str) -> bytes:
    """
    Serializes the python object

    serialization_method is enum: binary, json or xml
    """

    if serialization_method.lower() == "json":
        # Text serialization
        logging.info("Converting object to json format")
        data = str.encode(json.dumps(obj))
    elif serialization_method.lower() == "xml":
        # Text serialization
        logging.info("Converting object to xml format")
        data = str.encode(xmltodict.unparse({"msg": obj}))
    elif serialization_method.lower() == "binary":
        # Binary serialization
        logging.info("Converting object to binary format")
        data = pickle.dumps(obj, -1)
    else:
        logging.error(
            "Incorrect method. Please provide one of json or binary.")
        data = None
    return data


def create_headers(block_size: int, *args):
    """
    Creates metadata headers for differenting between file and object transfers
    """

    headers = "".join([f"{arg:<{block_size}}" for arg in args])
    return headers


def get_params(msg: bytes, header_size: int) -> dict:
    """
    Parses the metadata part from headers
    """

    data_type = msg[:header_size]
    encrypt = msg[header_size: 2 * header_size]
    param3 = msg[2 * header_size: 3 * header_size]
    length = msg[3 * header_size: 4 * header_size]

    metadata = {
        "type": data_type.strip().decode(),
        "encrypt": bool(int(encrypt)),
        "length": int(length),
    }

    if metadata["type"] == "object":
        metadata["serialize"] = param3.strip().decode()
    elif metadata["type"] == "file":
        metadata["filename"] = param3.strip().decode()

    return metadata
