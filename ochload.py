import logging
import socket
from shove import Shove
from modules import Stats
from modules.Config import Config
from modules.Server import Server
import argparse

parser = argparse.ArgumentParser(description='OCHproxy is an API that eases downloading from one-click hosters.')
parser.add_argument("--show-traffic", nargs='?', help="Prints the traffic statistics and exits.", choices=["user", "hoster", "all"])
args = parser.parse_args()
if args.show_traffic:
    choice = [args.show_traffic]
    if choice == ["all"]:
        choice = ["user", "hoster"]
    traffic_data = Shove('file://traffic_log/')
    for name in choice:
        Stats.make_stats(traffic_data, name)
    exit()

if Config.get("app/debug", False) is True:
    level = logging.DEBUG
else:
    level = logging.ERROR
socket.setdefaulttimeout(30)
logging.basicConfig(filename="ochload.log", level=level)
logging.info("Starting OCHload...")
Server()
