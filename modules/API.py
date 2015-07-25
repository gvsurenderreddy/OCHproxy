import json
import socket
import time
from modules.Log import log, log_method
from modules import Errors
from modules.Config import Config
from modules.Decorators import needs_auth
from modules.Hoster import Hoster
from modules.Request import Request
from modules.Server import add_traffic_for


class v1(object):
    def __init__(self, server):
        self.server = server

    @needs_auth
    def serve_get(self, user=None):
        if not self.server.require_params(["link"]):
            return
        link = self.server.parse_params()["link"]
        try:
            plugin, handle = Hoster.handle_link(link[0])
        except TypeError:
            plugin = handle = None
        if handle is None:
            raise Errors.PluginError
        if user.connections >= Config.get("app/max_connections_per_user", 20):
            log.info("User", user.username, " has opened more than ", user.connections, "connections.")
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

    @log_method
    def send_handle_to_user(self, handle):
        self.server.send_response(200)
        if isinstance(handle, Request):
            handle = self.open_request_for_user(handle)
        cl = 0
        if hasattr(handle.info(), "headers"):
            headers = handle.info().headers
            for h in headers:
                self.server.send_header(h.split(": ")[0], h.split(": ")[1].strip())
                if "Content-Length:" in h:
                    cl = int(h.split(":", 1)[1].strip())
        self.server.end_headers()
        log.debug("Copying file to client")
        self.server.copyfile(handle, self.server.wfile)
        return cl

    def open_request_for_user(self, handle):
        for h in self.server.headers.headers:
            h = h.split(":", 1)
            if "Range" in h[0] or "If-" in h[0]:
                log.debug("Forwarding header " + h[0] + ":" + h[1])
                handle.add_header(h[0], h[1])
        log.debug("Opening connection to " + handle.get_url())
        try:
            handle = handle.open()
        except socket.timeout:
            self.server.send_error(500, "Upstream timeout")
            raise Errors.PluginError
        return handle

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
            if isinstance(h.__class__.hostname, basestring):
                formats.append(h.__class__.hostname)
            elif h.__class__.hostname is not None:
                formats += h.__class__.hostname
        # distinct
        formats = list(set(formats))
        formats.sort()
        self.server.send_response(200)
        self.server.send_header("Content-Type", "application/json")
        self.server.end_headers()
        self.server.wfile.write(json.dumps(formats))

    @log_method
    def handle_exception(self, exception):
        if not isinstance(exception, Errors.RequestError):
            exception = Errors.RequestError
        self.server.send_response(exception.http_code)
        self.server.send_header("Content-Type", "application/json")
        self.server.end_headers()
        self.server.wfile.write(json.dumps({"code": exception.code, "message": exception.message}))

default = v1
