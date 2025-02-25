# CobblemonStats-Backend

This is the backend for the CobblemonStats project. It is a simple REST API that allows you to get data about the Cobblemon game.

## Starting the server

To start the server, you need to have Python 3 installed on your machine. You can find an help message by running the following command:
```bash
wiibleyde@SomeOVHServer:~$ /bin/python3 main.py -h
usage: main.py [-h] [--host HOST] [--port PORT] [--debug DEBUG] [--path PATH]

Wiibleyde Stat Maker

options:
  -h, --help     show this help message and exit
  --host HOST    Host
  --port PORT    Port
  --debug DEBUG  Debug
  --path PATH    Path
```

You can start the server by running the following command:
```bash
wiibleyde@SomeOVHServer:~$ /bin/python3 main.py
```

## API

The API is very simple. It has only one endpoint that allows you to get the stats of a Cobblemon. The endpoint `/api/v1/` gives you a list of all endpoints available.
