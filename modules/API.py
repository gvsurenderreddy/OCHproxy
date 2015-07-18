import json
import socket
import time
from modules import Errors
from modules.Config import Config
from modules.Decorators import needs_auth
from modules.Hoster import Hoster
from modules.Server import add_traffic_for


class v1(object):
    def __init__(self, server):
        self.server = server

    @needs_auth
    def serve_get(self, user=None):
        if not self.server.require_params(["link"]):
            self.server.print_debug("Request didn't contain a link to download")
            return
        link = self.server.parse_params()["link"]
        try:
            plugin, handle = Hoster.handle_link(link[0])
        except TypeError:
            plugin = handle = None
        if handle is None:
            self.server.send_error(500, "The server was unable to process your request")
            self.server.print_debug("Link handler returned None")
            return
        if user.connections >= Config.get("app/max_connections_per_user", 20):
            self.server.print_debug("User has already " + str(user.connections) + " connections open, can't open more.")
            self.server.send_error(421)
            return
        user.connections += 1
        start_time = time.time()
        content_length = self.send_handle_to_user(handle)
        user.connections -= 1
        download_details = (content_length, time.time() - start_time)
        add_traffic_for("user", user.username, download_details)
        add_traffic_for("hoster", plugin.plugin_name, download_details)
        plugin.add_downloaded_bytes(content_length)

    def send_handle_to_user(self, handle):
        self.server.send_response(200)
        for h in self.server.headers.headers:
            h = h.split(":", 1)
            if "Range" in h[0]:
                self.server.print_debug("Forwarding range header " + h[0] + ":" + h[1])
                handle.add_header(h[0], h[1])
        self.server.print_debug("Opening connection to " + handle.get_url())
        try:
            handle = handle.open()
        except socket.timeout:
            self.server.print_debug("Upstream timeout")
            self.server.send_error(500, "Upstream timeout")
            return
        self.server.print_debug("Connection established, forwarding headers to client...")
        cl = 0
        if hasattr(handle.info(), "headers"):
            headers = handle.info().headers
            for h in headers:
                self.server.send_header(h.split(": ")[0], h.split(": ")[1].strip())
                if "Content-Length:" in h:
                    cl = int(h.split(":", 1)[1].strip())
        self.server.end_headers()
        self.server.print_debug("Copying file to client")
        self.server.copyfile(handle, self.server.wfile)
        self.server.print_debug("Finished")
        return cl

    def serve_index(self):
        self.server.send_response(200)
        self.server.send_header("Content-Type", "text/html; charset=utf-8")
        self.server.end_headers()
        with open("static/index.html") as f:
            self.server.copyfile(f, self.server.wfile)

    @needs_auth
    def serve_account(self, user=None):
        response = {"status":
                    {"active": True,
                     "max_connections": Config.get("app/max_connections_per_user", 20)
                     }
                    }
        self.server.wfile.write(json.dumps(response))

    @needs_auth
    def serve_links(self, user=None):
        formats = []
        for h in Hoster.hoster:
            if isinstance(h.__class__.link_format, basestring):
                formats.append(h.__class__.link_format)
            elif h.__class__.link_format is not None:
                formats += h.__class__.link_format
        # distinct
        formats = list(set(formats))
        self.server.send_response(200)
        self.server.send_header("Content-Type", "application/json")
        self.server.end_headers()
        self.server.wfile.write(json.dumps(formats))

    def handle_exception(self, exception):
        if not isinstance(exception, Errors.RequestError):
            exception = Errors.RequestError
        self.server.send_response(500)
        self.server.send_header("Content-Type", "application/json")
        self.server.end_headers()
        self.server.wfile.write(json.dumps({"code": exception.code, "message": exception.message}))

default = v1
