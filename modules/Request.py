import Cookie
import urllib
import urllib2
import requests
from modules.Config import Config

__author__ = 'bauerj'


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
        opener = urllib2.build_opener(self.MyHTTPRedirectHandler)
        host = Request.get_host_from_url(self.url)
        headers = get_default_headers()
        opener.addheaders = []
        for (k, v) in dict(headers, **self.headers).iteritems():
            opener.addheaders.append((k, v))
        opener.addheaders.append(
            ('Cookie', "; ".join('%s=%s' % (k, v) for k, v in Request.get_cookies_for(host).items())))
        if self.get_method() == "GET":
            r = opener.open(self.get_parametrized_url())
        else:
            r = opener.open(self.url, data=self.payload)
        try:
            cookies = r.info().getheader('Set-Cookie')
            Request.set_cookies_from_header(cookies, host)
        except AttributeError:
            pass
        return r

    def send(self):
        host = Request.get_host_from_url(self.url)
        headers = get_default_headers()
        if not hasattr(requests, self.method.lower()):
            raise Exception("Method should be either POST or GET")
        m = getattr(requests, self.method.lower())
        args = {"headers": headers, "cookies": Request.get_cookies_for(host),
                "params" if self.method.lower() == "get" else "data": self.payload}
        r = m(self.url, **args)
        for r in [r] + r.history:
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
            return {}
        return Request.cookies[host]

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

    class MyHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
        def __init__(self):
            pass

        def http_error_302(self, req, fp, code, msg, headers):
            host = Request.get_host_from_url(req.get_full_url())
            for h in headers:
                if "set-cookie" == h.lower():
                    Request.set_cookies_from_header(headers[h], host)
            req.headers['Cookie'] = "; ".join('%s=%s' % (k, v) for k, v in Request.get_cookies_for(host).items())
            return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)

        http_error_301 = http_error_303 = http_error_307 = http_error_302

    @staticmethod
    def set_cookies_from_header(cookies, host):
        cookies = Cookie.SimpleCookie(cookies)
        for c in cookies.iteritems():
            n, v = c
            Request.set_cookie_for(host, n, v.value)
