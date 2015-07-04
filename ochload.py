import logging
import socket
from modules.Config import Config
from modules.Server import Server

if Config.get("app/debug", False) is True:
    level = logging.DEBUG
else:
    level = logging.ERROR
socket.setdefaulttimeout(30)
logging.basicConfig(filename="ochload.log", level=level)
logging.info("Starting OCHload...")
Server()
