import os
import socket
from shove import Shove
import time
from modules import Stats
from modules.Config import Config
from modules.Server import Server
from modules.Log import log
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

try:
    if os.geteuid() == 0:
        # Oh no, someone started OCHproxy as root!
        # But maybe we can drop the priviliges after getting the port.
        if Config.get("app/user", None) is None or Config.get("app/group", None) is None:
            # There can't be a good reason to do this, can it?
            print "Hey, you shouldn't run this as root!"
            print "If you want to use a priviliged port (80 is a good choice), you can set a group and user in"
            print "config.json for OCHproxy to use after binding the port."
            print "You need to wait at least 5 seconds if you insist on this reckless behaviour."
            for _i in xrange(1, 5):
                print "."
                time.sleep(1)
except AttributeError:
    pass  # This is Windows.

log.info("Starting OCHproxy...")

socket.setdefaulttimeout(30)
Server()
