"""
Starts the client using cmd arguments
"""

from msg_transfer_package.client import run_with_config
import argparse

CONFIG_FILE_PATH = ""
INPUT_FILE_PATH = ""

parser = argparse.ArgumentParser(
    description='Start client for sending file or parsed python dictionary from config')

parser.add_argument('-c', dest='config_path', default='config_client.cfg',
                    required=True,
                    help='the client config file path (required)')

parser.add_argument('-i', dest='input_file', default='',
                    help='the path of input file to send')

parser.add_argument('-e', dest='do_encrypt', default=False, action='store_true',
                    help='if the transfer data should be encrypted')

args = parser.parse_args()


run_with_config(args.config_path, args.input_file, args.do_encrypt)
