import urllib
import urllib2
import requests
from modules.Config import Config

__author__ = 'bauerj'


def get_user_agent():
    return Config.get("http/user-agent", "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) "
                                         "Chrome/41.0.2228.0 Safari/537.36")


class Request:
    method = "GET"
    url = None
    payload = {}

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
        user_agent = get_user_agent()
        opener.addheaders = [("User-Agent", user_agent)]
        if self.get_method() == "GET":
            url = self.url
            if len(self.payload) > 0:
                url = url + "?" + urllib.urlencode(self.payload)
            return opener.open(url)
        else:
            return opener.open(self.url, data=self.payload)

    def send(self):
        if self.method == "GET":
            return requests.get(self.url, params=self.payload, headers={"User-Agent": get_user_agent()})
        elif self.method == "POST":
            return requests.post(self.url, data=self.payload, headers={"User-Agent": get_user_agent()})
