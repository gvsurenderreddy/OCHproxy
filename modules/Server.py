import SocketServer
import SimpleHTTPServer
import logging
import socket
import urlparse
from modules.Auth import Auth
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
        logging.info("Starting HTTP server on " + ip + " port " + str(port) + "...")
        Server.httpd.serve_forever()

    class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
        global hoster

        def print_debug(self, message):
            logging.debug("<Request from " + self.client_address[0] + ">: " + message)

        def do_GET(self):
            action = "serve_" + (self.path.split("?")[0].strip("/") or "index")
            if hasattr(self, action) and hasattr(getattr(self, action), "__call__"):
                logging.debug("Request from " + self.client_address[0] + " calls " + action)
                getattr(self, action)()

            # If the test suite started this, we need to stop the server
            if Server.test:
                Server.httpd.shutdown()

        def serve_get(self):
            if not self.require_params(["link"]):
                self.print_debug("Request didn't contain a link to download")
                return
            user = Auth.auth(self.parse_params(), self.client_address)
            if user is None:
                self.print_debug("Request could not be authenticated")
                self.send_error(401)
                return
            link = self.parse_params()["link"]
            handle = hoster.handle_link(link[0])
            if handle is None:
                self.send_error(500, "The server was unable to process your request")
                self.print_debug("Link handler returned None")
                return
            if user.connections >= Config.get("app/max_connections_per_user", 20):
                self.print_debug("User has already " + user.connections + " connections open, can't open more.")
                self.send_error(421)
                return
            user.connections += 1
            self.send_response(200)
            for h in self.headers.headers:
                h = h.split(":", 1)
                if "Range" in h[0]:
                    self.print_debug("Forwarding range header " + h[0] + ":" + h[1])
                    handle.add_header(h[0], h[1])
            self.print_debug("Opening connection to " + handle.get_url())
            try:
                handle = handle.open()
            except socket.timeout:
                user.connections -= 1
                self.print_debug("Upstream timeout")
                self.send_error(500, "Upstream timeout")
                return
            self.print_debug("Connection established, forwarding headers to client...")
            if hasattr(handle.info(), "headers"):
                headers = handle.info().headers
                for h in headers:
                    self.send_header(h.split(": ")[0], h.split(": ")[1].strip())
                    if "Content-Length" in h:
                        self.print_debug("Remote response: " + h)
            self.end_headers()
            self.print_debug("Copying file to client")
            self.copyfile(handle, self.wfile)
            self.print_debug("Finished")
            user.connections -= 1

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
