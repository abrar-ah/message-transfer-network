
# Client/Server Network Application
### Enf of module Group Project - Submitted to University of Liverpool
<img src="https://www.liverpool.ac.uk/logo-size-test/full-colour.svg" width="310px"/>

### Implements transferring messages between a server and client network using TCP 

# Install
### Cloning the repository

```shell
git clone https://github.com/abrar-ah/message-transfer-network.git
```

### Installing dependencies
```shell
pip install -r requirements.txt
```

# Run the application

## Server
Example server config file `config_server.cfg`
```cfg
[SERVER_OPTIONS]
ip_addr = 127.0.0.1
port = 7000
output_option = print
```
#### Change options in `config_server.cfg`, Start server
1. `ip_addr`: the IP Address to bind the server **(required)**
2. `port`: the port to user for server **(required)**
3. `output_option`: received data should saved to file or output to terminal, valid values: `print`, `file` **(required)**
### Run the server:
```shell
python3 main-server.py 
```

## Client
### Run the Client
```shell
python3 main-client.py -c config_client.cfg -e
```
Command line usage options for `main-client.py`
```shell
usage: main-client.py [-h] -c CONFIG_PATH [-i INPUT_FILE] [-e]

Start client for sending file or parsed python dictionary from config

options:
  -h, --help      show this help message and exit
  -c CONFIG_PATH  the client config file path (required)
  -i INPUT_FILE   the path of input file to send
  -e              if the transfer data should be encrypted
```

Example client config file `config_client.cfg`
```cfg
[SERVER_OPTIONS]
host = 127.0.0.1
host_port = 7000

[INPUT_OBJECT]
object = {"name": "John Doe", "age": 25, "city": "Liverpool", "country": "GB"}
serialize = json
```
#### Change options in `config_client.cfg`, Start client
1. `host`: the IP Address or Hostname of the server **(required)**
2. `port`: the port of the server **(required)**
3. `object`: will be parsed in python and transferred to the server (this is overridden by `-i` cmd option)
4. `serialize`: serialization method to use for object only, valid values `binary`, `json`, `xml`


# Tests
### For running tests, install test dependencies
```shell
pip install -r requirements-test.txt
```

#### Testing the server class
```shell
python3 -m unittest tests/server_test.py
```

#### Testing the client class
```shell
python3 -m unittest tests/client_test.py
```

#### Testing the util functions
```shell
python3 -m unittest tests/utils_test.py
```

#### Testing the formatting of all `.py` files according to PEP8 standards
```shell
python3 -m unittest tests/formatting_test.py
```


## Directory tree
Encryption keys are stored in `utils.py`
```shell
├── README.md
├── config_client.cfg
├── config_server.cfg
├── main-client.py
├── main-server.py
├── requirements-test.txt
├── requirements.txt
├── msg_transfer_package
│   ├── __init__.py
│   ├── client.py
│   ├── example_data
│   │   ├── __init__.py
│   │   ├── example_data.py
│   │   └── example_file.txt
│   ├── server.py
│   └── utils.py
└── tests
    ├── __init__.py
    ├── client_test.py
    ├── formatting_test.py
    ├── server_test.py
    └── utils_test.py
```

### Cleanup temp files
```shell
rm -f .coverage
rm -f received_example_file.txt
rm -f client_log.log
rm -f server_log.log
```