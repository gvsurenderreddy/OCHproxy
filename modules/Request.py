import json
import urllib
import urllib2
from cookielib import CookieJar
from modules.Config import Config
from modules.Log import log

__author__ = 'bauerj'
__all__ = ["Request"]


def get_default_headers():
    return {"User-Agent":
            Config.get("http/user-agent",
                       "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/41.0.2228.0 Safari/537.36"),
            "Accept-Language": "en-US",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            }


class Request(object):
    cookies = {}
    headers = {}
    cj = CookieJar()

    def __init__(self, url=None, payload=None, method="GET"):
        self.method = method
        self.url = url
        self.payload = payload or {}
        self.headers = {}

    def set_method(self, method):
        self.method = method
        return self

    def add_header(self, header, value):
        self.headers[header] = value
        return self

    def get_method(self):
        return self.method

    def set_url(self, url):
        self.url = url
        return self

    def get_url(self):
        return self.url or ""

    def set_payload(self, payload):
        self.payload = payload
        return self

    def get_payload(self):
        return self.payload

    def open(self):
        log.debug("opening " + self.url)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(Request.cj))
        headers = get_default_headers()
        opener.addheaders = []
        for (k, v) in dict(headers, **self.headers).iteritems():
            opener.addheaders.append((k, v))
        try:
            if self.get_method() == "GET":
                r = opener.open(self.get_parametrized_url())
            else:
                r = opener.open(self.url, data=urllib.urlencode(self.payload))
        except urllib2.HTTPError, e:
            r = e
        return r

    def send(self):
        return Request.Response(self.open())

    @staticmethod
    def get_host_from_url(url):
        url = url.split("://")[1]
        url = url.split("/")[0]
        try:
            if len(url.split(".", 1)[1]) > 5:
                return url.split(".", 1)[1]
        except IndexError:
            pass
        return url

    def get_parametrized_url(self):
        url = self.url
        if len(self.payload) > 0:
            url = url + "?" + urllib.urlencode(self.payload)
        return url

    class Response(object):
        def __init__(self, handle):
            assert isinstance(handle, urllib.addinfourl)
            self.handle = handle
            self._text = None

        @property
        def text(self):
            if self._text is not None:
                return self._text
            self._text = self.handle.read()
            return self._text

        @property
        def status_code(self):
            return self.handle.getcode()

        @property
        def size(self):
            try:
                return self.handle.info().getheaders("Content-Length")[0]
            except AttributeError:
                return len(self.text)

        @property
        def headers(self):
            try:
                return self.handle.info().getheaders()
            except AttributeError:
                return []

        @property
        def json(self):
            return json.loads(self.text)
