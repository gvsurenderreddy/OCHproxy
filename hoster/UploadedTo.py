from modules.BasePlugin import *
import base64
import logging
import re
from modules.Request import Request
from modules.Config import Config
from pyquery import PyQuery
from modules.Log import log


class UploadedTo(BasePlugin):
    hostname = ["uploaded.to", "ul.to", "uploaded.net"]
    priority = Priority.DIRECT_UNLIMITED
    config_values = ["id", "password"]

    def __init__(self):
        super(UploadedTo, self).__init__()
        self.ddl = False
        self.login()

    def login(self):
        r = Request("http://uploaded.net/io/login", method="POST")
        r.add_header("Origin", "http://uploaded.net")
        r.add_header("Referer", "http://uploaded.net/")
        r.add_header("X-Prototype-Version", "1.6.1")
        r.add_header("X-Requested-With", "XMLHttpRequest")
        r.set_payload({
            "id": Config.get("id"),
            "pw": Config.get("password"),
            "_": ""  # whatever
        })
        r = r.send()
        if r.status_code is not 200 or "err" in r.text:
            log.error("ul.to: Login failed.")
            self.deactivate()
            return
        # Try to find out if ddl is activated
        r = Request("http://uploaded.net/me").send()
        try:
            html = PyQuery(r.text)
            if len(html("#ddl")) > 0:
                if html("#ddl").attr("checked") == "checked":
                    self.ddl = True
        except:
            pass

    @cache(2*60)
    def handle(self, link):
        if self.ddl:
            return self.try_dl(Request(link))
        r = Request(link).send()
        if r.status_code is 404:
            raise Errors.InvalidLinkError
        html = PyQuery(r.text)
        if len(html("#download form")) < 1:
            log.error("ul.to: Could not find download link please consider enabling ddl.")
            raise Errors.PluginError
        link = html("#download form").attr("action")
        r =  Request(link, method="POST", payload={})
        r.add_header("Referer", link)
        return self.try_dl(r)

    def try_dl(self, request):
        r = request.open_for_user()
        try:
            if r.getcode() is 200:
                headers = dict([(h.split(":", 1)[0].lower(), h.split(":", 1)[1]) for h in r.headers.headers])
                if "etag" in headers or "last-modified" in headers:
                    return r
                if "content-length" in headers and headers["content-length"] > 1000:
                    return r
        except:
            pass
        log.debug(r)
        raise Errors.PluginError
