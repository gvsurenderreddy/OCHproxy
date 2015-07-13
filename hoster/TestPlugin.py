import random
from modules import Request

# This "plugin" is only used to measure the performance of OCHproxy.
# You can only trigger it if you enable debug mode and use http://get.testfile/ as a link.

# A list of download speed test links found publicly available on the Internet.
from modules.BasePlugin import *
from modules.Config import Config

class TestPlugin(BasePlugin):
    links = [
        "http://ovh.net/files/100Mio.dat",  # 100MB
        "http://ovh.net/files/100Mb.dat",  # 12,5MB
        "http://speedtest.netcologne.de/test_20mb.bin",  # 20MB
        "http://ipv4.download.thinkbroadband.com/50MB.zip",  # 50MB
        "http://mirror.internode.on.net/pub/test/1meg.test",  # 1MB
        "http://speedtest.reliableservers.com/10MBtest.bin",  # 10MB
        "http://speedtest.tweak.nl/25mb.bin",  # 25MB
        "http://speedtest.tele2.net/100MB.zip",  # 100MB
        "http://www.as35662.net/10.log",  # 10MB
        "http://speedtest.ftp.otenet.gr/files/test10Mb.db",  # 10MB
        "http://test.gorillaservers.com/100mb.bin",  # 100MB
        "http://cachecefly.cachefly.net/100mb.test",  # 100MB
        "http://speedtest.ams01.softlayer.com/downloads/test100.zip",  # 100MB
        "http://speedtest.tokyo.linode.com/100MB-tokyo.bin",  # 100MB
    ]
    priority = Priority.DIRECT_UNLIMITED

    def match(self, link):
        if not Config.get("app/debug", False):
            return False
        if link.startswith("http://get.testfile/"):
            return True

    @cache(1)
    def handle(self, link):
        link = random.choice(self.links)
        return Request.Request(url=link)
