import SocketServer
import SimpleHTTPServer
import os
import random
import threading
import urlparse
import time
import binascii
from modules import Errors
from modules.Config import Config
from shove import Shove
from modules.Log import log, ServerLogAdapter, log_method


def add_traffic_for(type, name, bytes):
    if type + "/" + name not in Server.traffic:
        Server.traffic[type + "/" + name] = bytes
    else:
        Server.traffic[type + "/" + name] += bytes

class Server(object):
    from modules import API
    httpd = None

    test = False
    traffic = None

    def __init__(self, test=False, port=None):
        ServerLogAdapter.thread_local = threading.local()
        Server.traffic = Shove('file://traffic_log/')
        Server.test = test
        port = port or Config.get("http/port", 8080)
        ip = Config.get("http/ip", "0.0.0.0")
        Server.httpd = SocketServer.ThreadingTCPServer((ip, port), self.Proxy)
        print("Starting HTTP server on " + ip + " port " + str(port) + "...")
        Server.httpd.serve_forever()

    class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):

        def do_GET(self):
            if Config.get("app/debug"):
                ServerLogAdapter.thread_local.remote = self.client_address
                ServerLogAdapter.thread_local.id = threading.current_thread().name.split("-")[1]
                ServerLogAdapter.thread_local.started = time.time()
                ServerLogAdapter.thread_local.user = "nobody"
                log.debug("GET " + self.path + " {" + self.headers.headers.__repr__() + "}")
            api_version = "default"
            path = self.path
            if self.path.count('/') > 1:
                api_version = self.path.lstrip("/").split("/", 1)[0]
                path = self.path.lstrip("/").split("/", 1)[1]
            action = "serve_" + (path.split("?")[0].strip("/") or "index")
            try:
                endpoint = getattr(Server.API, api_version)(self)
            except AttributeError:
                self.send_error(501, "API-endpoint does not exist")
                return
            if hasattr(endpoint, action) and hasattr(getattr(endpoint, action), "__call__"):
                log.debug("Request from " + self.client_address[0] + " calls " + action + " (" + api_version + ")")
                try:
                    getattr(endpoint, action)()
                except Errors.RequestError, e:
                    endpoint.handle_exception(e)
            if hasattr(ServerLogAdapter.thread_local, "started"):
                log.debug("Ended after " + str(time.time() - ServerLogAdapter.thread_local.started) + "s")
            # If the test suite started this, we need to stop the server
            if Server.test:
                Server.httpd.shutdown()
            Server.traffic.sync()

        def parse_params(self):
            try:
                return urlparse.parse_qs(self.path.split("?", 1)[1])
            except IndexError:
                return {}

        def require_params(self, params):
            errors = []
            for param in params:
                if param not in self.parse_params():
                    errors.append(param)
            if errors.__len__() > 0:
                self.send_error(400, 'Missing required GET parameters ' + ', '.join(errors))
                return False
            return True

        @log_method
        def send_response(self, code, message=None):
            self.log_request(code)
            if message is None:
                if code in self.responses:
                    message = self.responses[code][0]
                else:
                    message = ''
                if self.request_version != 'HTTP/0.9':
                    self.wfile.write("%s %d %s\r\n" %
                                     (self.protocol_version, code, message))

        @log_method
        def send_error(self, code, message=None):
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if message is not None:
                self.wfile.write(message)
