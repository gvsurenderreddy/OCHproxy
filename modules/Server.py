import SocketServer
import SimpleHTTPServer
import logging
import urlparse
from modules.Config import Config
from shove import Shove


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
        Server.traffic = Shove('file://traffic_log/')
        Server.test = test
        port = port or Config.get("http/port", 8080)
        ip = Config.get("http/ip", "0.0.0.0")
        Server.httpd = SocketServer.ThreadingTCPServer((ip, port), self.Proxy)
        logging.info("Starting HTTP server on " + ip + " port " + str(port) + "...")
        Server.httpd.serve_forever()

    class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):

        def print_debug(self, message):
            logging.debug("<Request from " + self.client_address[0] + ">: " + message)

        def do_GET(self):
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
                logging.debug("Request from " + self.client_address[0] + " calls " + action + " (" + api_version + ")")
                getattr(endpoint, action)()
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

        def send_error(self, code, message=None):
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if message is not None:
                self.wfile.write(message)
