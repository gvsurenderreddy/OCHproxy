import urllib
import urllib2
import requests
from modules.Config import Config

__author__ = 'bauerj'


def get_user_agent():
    return Config.get("http/user-agent", "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) "
                                         "Chrome/41.0.2228.0 Safari/537.36")


class Request:
    cookies = {}

    def __init__(self, url=None, payload=None, method="GET"):
        self.method = method
        self.url = url
        self.payload = payload or {}

    def set_method(self, method):
        self.method = method
        return self

    def get_method(self):
        return self.method

    def set_url(self, url):
        self.url = url
        return self

    def set_payload(self, payload):
        self.payload = payload
        return self

    def get_payload(self):
        return self.payload

    def open(self):
        opener = urllib2.build_opener()
        host = Request.get_host_from_url(self.url)
        user_agent = get_user_agent()
        opener.addheaders = [("User-Agent", user_agent)]
        opener.addheaders.append(
            ('Cookie', "; ".join('%s=%s' % (k, v) for k, v in Request.get_cookies_for(host).items())))
        if self.get_method() == "GET":
            url = self.url
            if len(self.payload) > 0:
                url = url + "?" + urllib.urlencode(self.payload)
            r = opener.open(url)
        else:
            r = opener.open(self.url, data=self.payload)
        try:
            cookies = r.getheader('Set-Cookie').split(";")
            for c in cookies:
                n, v = c.split(":")
                Request.set_cookie_for(host, n, v)
        except AttributeError:
            pass
        return r

    def send(self):
        host = Request.get_host_from_url(self.url)
        if self.method != "POST":
            r = requests.get(self.url, params=self.payload, headers={"User-Agent": get_user_agent()},
                             cookies=Request.get_cookies_for(host))
        else:
            r = requests.post(self.url, data=self.payload, headers={"User-Agent": get_user_agent()},
                              cookies=Request.get_cookies_for(host))
        for n, v in r.cookies.iteritems():
            Request.set_cookie_for(host, n, v)
        return r

    @staticmethod
    def set_cookie_for(host, name, value):
        if host not in Request.cookies:
            Request.cookies[host] = {}
        Request.cookies[host][name] = value

    @staticmethod
    def get_cookies_for(host):
        if host not in Request.cookies:
            return None
        return Request.cookies[host]

    @staticmethod
    def get_host_from_url(url):
        url = url.split("://")[1]
        return url.split("/")[0]
