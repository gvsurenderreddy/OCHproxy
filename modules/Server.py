import SocketServer
import SimpleHTTPServer
import urlparse
import auth
from modules.Config import Config
from modules.Hoster import Hoster


class Server:
    httpd = None
    hoster = None
    test = False

    def __init__(self, test=False, port=None):
        global hoster
        Server.test = test
        hoster = Hoster()
        port = port or Config.get("http/port", 8080)
        ip = Config.get("http/ip", "0.0.0.0")
        Server.httpd = SocketServer.ThreadingTCPServer((ip, port), self.Proxy)
        print "Starting HTTP server on ", ip, "port", port, "..."
        Server.httpd.serve_forever()

    class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
        global hoster

        def do_GET(self):
            try:
                action = "serve_" + (self.path.split("?")[0].strip("/") or "index")
                if hasattr(self, action):
                    getattr(self, action)()
            except TypeError:
                self.serve_index()
            # If the test suite started this, we need to stop the server
            if Server.test:
                Server.httpd.shutdown()

        def serve_get(self):
            if not self.require_params(["link"]):
                return
            if not auth.auth(self.parse_params(), self.client_address):
                self.send_error(403)
                return
            link = self.parse_params()["link"]
            handle = hoster.handle_link(link[0])
            if handle is None:
                self.send_error(500, "The server was unable to process your request")
                return
            self.send_response(200)
            for h in self.headers.headers:
                h = h.split(":", maxsplit=1)
                if "Range" in h[0]:
                    handle.add_header(h[0], h[1])
            handle = handle.open()
            if hasattr(handle.info(), "headers"):
                headers = handle.info().headers
                for h in headers:
                    self.send_header(h.split(": ")[0], h.split(": ")[1].strip())
            self.end_headers()
            self.copyfile(handle, self.wfile)

        def serve_index(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open("static/index.html") as f:
                self.copyfile(f, self.wfile)

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
