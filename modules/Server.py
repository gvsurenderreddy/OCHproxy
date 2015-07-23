import SocketServer
import SimpleHTTPServer
import os
import threading
import urlparse
import time
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
        try:
            if os.geteuid != 0 and Config.get("app/user") is not None and Config.get("app/group") is not None:
                Server.drop_privileges(Config.get("app/user"), Config.get("app/group"))
        except AttributeError:
            pass
        Server.httpd.serve_forever()

    @staticmethod
    def drop_privileges(uid_name='nobody', gid_name='nogroup'):
        try:
            import os, pwd, grp
        except (OSError, ImportError):
            # This is Windows, I guess it won't be safe anyway.
            return
        if os.getuid() != 0:
            # We're not root so, like, whatever dude
            return

        # Get the uid/gid from the name
        running_uid = pwd.getpwnam(uid_name).pw_uid
        running_gid = grp.getgrnam(gid_name).gr_gid

        # Remove group privileges
        os.setgroups([])

        # Try setting the new uid/gid
        os.setgid(running_gid)
        os.setuid(running_uid)

        # Ensure a very conservative umask
        os.umask(077)

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
            if self.path.split("?", 1)[0].count('/') > 1:
                api_version = self.path.lstrip("/").split("/", 1)[0]
                path = self.path.lstrip("/").split("/", 1)[1]
            action = "serve_" + (path.split("?")[0].strip("/") or "index")
            try:
                from modules import API
                endpoint = getattr(API, api_version)
            except AttributeError:
                self.send_error(501, "API-endpoint does not exist")
                return
            endpoint = endpoint(self)
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
