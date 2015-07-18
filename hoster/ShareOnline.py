from modules.BasePlugin import *
import base64
import logging
import re
from modules.Request import Request
from modules.Config import Config
from pyquery import PyQuery


class ShareOnline(BasePlugin):
    hostname = "share-online.biz"
    priority = Priority.DIRECT_UNLIMITED
    config_values = ["user", "password"]

    def __init__(self):
        super(ShareOnline, self).__init__()
        self.autoload_enabled = None
        self.login()

    def login(self):
        # Login
        Request("https://www.share-online.biz/user/login", method="POST", payload={
            "user": Config.get("user"),
            "pass": Config.get("password"),
            "l_rememberme": 1
        }).add_header("referer", "https://www.share-online.biz/").send()

    @cache(2*60)
    def handle(self, link):
        r = Request(link)
        if self.autoload_enabled is True:
            return r
        # We just need to check the headers to find out if Direct Download is enabled. If it is, close the connection
        # and don't load the file. That way, this check won't be as suspicious.
        h = r.open()
        if self.autoload_enabled is None:
            if "/dl?" in h.url:
                self.autoload_enabled = True
                h.close()
                logging.debug("Direct Download for Share-Online.biz is enabled")
                return r
        logging.debug("Direct Download for Share-Online.biz is not enabled")
        response = PyQuery(h.read())
        link = response("#download script").text()
        if link is None:
            raise Exception("invalid download link (ShareOnline)")
        try:
            link = re.search("var dl.?=.?\"(.*?)\"", link).group(1)
            link = base64.b64decode(link)
        except IndexError:
            raise Exception("Could not extract download link. Please consider enabling Direct Download")
        return Request(link)
