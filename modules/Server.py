import SocketServer
import SimpleHTTPServer
import urlparse
import auth
from modules.Config import Config
from modules.Hoster import Hoster


class Server:
    hoster = None

    def __init__(self):
        global hoster
        hoster = Hoster()
        port = Config.get("http/port", 81)
        ip = Config.get("http/ip", "0.0.0.0")
        httpd = SocketServer.ThreadingTCPServer((ip, port), self.Proxy)
        print "Starting HTTP server on ", ip, "port",  port, "..."
        httpd.serve_forever()

    class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
        global hoster

        def do_GET(self):
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
            if hasattr(handle.info(), "headers"):
                headers = handle.info().headers
                for h in headers:
                    self.send_header(h.split(": ")[0], h.split(": ")[1].strip())
            self.end_headers()
            self.copyfile(handle, self.wfile)

        def parse_params(self):
            return urlparse.parse_qs(self.path.strip("/?"))

        def require_params(self, params):
            errors = []
            for param in params:
                if param not in self.parse_params():
                    errors.append(param)
            if errors.__len__() > 0:
                self.send_error(400, 'Missing required GET parameters ' + ', '.join(errors))
                return False
            return True
